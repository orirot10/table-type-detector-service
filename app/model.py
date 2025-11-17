import io
from typing import Tuple, List, Optional

from PIL import Image
from ultralytics import YOLO

from .config import settings


class TableTypeModel:
    """
    Wrapper around a YOLO model for table-type detection.

    This class is responsible for:
    - Loading a YOLO model from a given path.
    - Managing the mapping between numeric class IDs and human-readable labels.
    - Running inference on input images (provided as bytes).
    - Returning the most confident prediction (label + confidence score).

    Typical use:
        model = TableTypeModel("model/table_type_identification.pt", ["balance", "activity"])
        label, confidence = model.predict(image_bytes)
    """

    def __init__(self, model_path: str, labels: List[str]) -> None:
        """
        Initialize the TableTypeModel.

        Parameters
        ----------
        model_path : str
            Filesystem path to the YOLO model file (e.g. a .pt checkpoint).
        labels : List[str]
            A list of label names corresponding to the model classes.
            If this list is shorter than the model's internal `names`,
            the class will fall back to using `model.names` instead.

        Notes
        -----
        - `ultralytics.YOLO` exposes a `names` attribute which is typically
          a dict: {class_id: class_name}.
        - If you want to override these names, you can pass them in `labels`
          via environment variable TABLE_LABELS or directly.
        """
        # Load the YOLO model from disk
        self.model = YOLO(model_path)

        # If user-provided labels are valid and at least as long as model classes,
        # use them; otherwise, fallback to the labels provided by the model itself.
        if labels and len(labels) >= len(self.model.names):
            self.labels = labels
        else:
            # YOLO stores class names like: {0: "balance", 1: "activity", ...}
            # We convert that into a list ordered by class index.
            names_dict = self.model.names
            self.labels = [names_dict[i] for i in sorted(names_dict.keys())]

    def predict(self, image_bytes: bytes) -> Tuple[str, float]:
        """
        Run inference on an image and return the most confident table-type prediction.

        Parameters
        ----------
        image_bytes : bytes
            Raw bytes of an image file (e.g. uploaded via FastAPI UploadFile.read()).

        Returns
        -------
        Tuple[str, float]
            A tuple of:
            - predicted label (str): e.g. "balance", "activity", or "unknown"
            - confidence (float): confidence score in the range [0.0, 1.0]

        Behavior
        --------
        - The method:
          1. Decodes the image from bytes using Pillow.
          2. Runs the YOLO model to obtain detections.
          3. Selects the detection with the highest confidence.
          4. Maps its class ID to a human-readable label.
        - If no detections are found, it returns:
          ("unknown", 0.0)
        """
        # Decode the input bytes into a PIL Image and ensure RGB format
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Run the YOLO model on the image
        results = self.model(image)
        r = results[0]  # YOLO returns a list-like structure; we take the first result

        # If there are no detections, return a fallback prediction
        if r.boxes is None or len(r.boxes) == 0:
            return "unknown", 0.0

        # YOLO result object:
        # - r.boxes.conf: confidence scores for each detection
        # - r.boxes.cls: class IDs for each detection
        boxes = r.boxes
        confs = boxes.conf  # tensor of shape [N]
        classes = boxes.cls  # tensor of shape [N]

        # Select the detection with the highest confidence
        best_idx = int(confs.argmax().item())
        cls_id = int(classes[best_idx].item())
        confidence = float(confs[best_idx].item())

        # Map the class ID to a label string; if out of range, return a generic name
        if 0 <= cls_id < len(self.labels):
            label = self.labels[cls_id]
        else:
            label = f"class_{cls_id}"

        return label, confidence


# Global singleton instance for the model.
# This allows us to load the model once at process startup and reuse it for all requests.
_model_instance: Optional[TableTypeModel] = None


def get_model() -> TableTypeModel:
    """
    Retrieve a singleton instance of TableTypeModel.

    This function ensures that the YOLO model is loaded only once
    per process, which is important for performance in a production
    micro-service.

    Returns
    -------
    TableTypeModel
        A shared instance of the model that can be reused across requests.

    Behavior
    --------
    - On the first call:
        - It reads labels from `settings.LABELS` (comma-separated string),
          e.g. "balance,activity".
        - It creates a new TableTypeModel with `settings.MODEL_PATH` and the parsed labels.
        - It stores that instance in the global `_model_instance`.
    - On subsequent calls:
        - It simply returns the already initialized `_model_instance`.
    """
    global _model_instance

    if _model_instance is None:
        # Parse labels from config: "balance,activity" -> ["balance", "activity"]
        labels = [l.strip() for l in settings.LABELS.split(",")]
        _model_instance = TableTypeModel(settings.MODEL_PATH, labels)

    return _model_instance
