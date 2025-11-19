import io
from typing import Tuple, List, Optional, Dict

from PIL import Image
from ultralytics import YOLO

from .config import settings


class TableTypeModel:
    """
    Wrapper around a YOLO model for table-type detection.

    This class is responsible for:
    - Loading a YOLO model from a given path.
    - Managing the mapping between YOLO class IDs and semantic labels.
    - Running inference on input images (provided as bytes).
    - Collapsing multi-class detections into a binary label: "balance" / "activity".

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
            A list of label names corresponding to the *output* classes you want
            to expose to the API (e.g. ["balance", "activity"]).
            NOTE: Internally the YOLO model may have many more classes, like:
                  'table_balances', 'table_activities', 'column_text', etc.
        """
        print(f"[TableTypeModel] Loading YOLO model from: {model_path}")
        self.model = YOLO(model_path)

        # Store the model's internal class-name mapping
        # Example:
        #   {0: 'account_opinion', 1: 'column_clarification', ...,
        #    5: 'table_activities', 6: 'table_balances', ...}
        self.model_names: Dict[int, str] = {
            int(k): str(v) for k, v in self.model.names.items()
        }
        print(f"[TableTypeModel] YOLO model loaded. model.names = {self.model_names}")

        # Exposed labels (what the API returns) - usually ["balance", "activity"]
        self.exposed_labels: List[str] = labels
        print(f"[TableTypeModel] Exposed labels (API level) = {self.exposed_labels}")

        # Map YOLO internal class names to "balance"/"activity"
        # We assume the training used these names:
        #   'table_balances'   -> balance
        #   'table_activities' -> activity
        self.balance_class_id: Optional[int] = None
        self.activity_class_id: Optional[int] = None

        for cid, name in self.model_names.items():
            if name == "table_balances":
                self.balance_class_id = cid
            elif name == "table_activities":
                self.activity_class_id = cid

        print(
            f"[TableTypeModel] balance_class_id={self.balance_class_id}, "
            f"activity_class_id={self.activity_class_id}"
        )

        if self.balance_class_id is None or self.activity_class_id is None:
            raise ValueError(
                "Could not find 'table_balances' or 'table_activities' in model.names. "
                "Please verify the trained model classes."
            )

    def predict(self, image_bytes: bytes) -> Tuple[str, float]:
        """
        Run inference on an image and return a collapsed table-type prediction.

        Parameters
        ----------
        image_bytes : bytes
            Raw bytes of an image file (e.g. uploaded via FastAPI UploadFile.read()).

        Returns
        -------
        Tuple[str, float]
            A tuple of:
            - predicted_label (str): "balance", "activity", or "unknown"
            - confidence (float): confidence score in the range [0.0, 1.0]

        Behavior
        --------
        - Run YOLO and look at all detections.
        - Collect confidences only for:
            - class == table_balances  -> "balance"
            - class == table_activities -> "activity"
        - Take the maximum confidence for each of these two groups.
        - Compare them:
            - If both are zero/absent -> ("unknown", 0.0)
            - Else choose the higher one and map to "balance"/"activity".
        """
        # Decode the input bytes into a PIL Image and ensure RGB format
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Run the YOLO model on the image
        results = self.model(image)
        r = results[0]  # first (and only) batch element

        # If there are no detections at all, return "unknown"
        if r.boxes is None or len(r.boxes) == 0:
            print("[TableTypeModel.predict] No boxes detected -> unknown")
            return "unknown", 0.0

        boxes = r.boxes
        confs = boxes.conf  # tensor [N]
        classes = boxes.cls  # tensor [N]

        balance_confs: List[float] = []
        activity_confs: List[float] = []

        # Iterate over all detections and collect confidences for relevant classes
        for c, conf in zip(classes, confs):
            cid = int(c.item())
            cval = float(conf.item())

            if cid == self.balance_class_id:
                balance_confs.append(cval)
            elif cid == self.activity_class_id:
                activity_confs.append(cval)

        # If neither balance nor activity was detected
        if not balance_confs and not activity_confs:
            print(
                "[TableTypeModel.predict] No table_balances/table_activities detected "
                "-> unknown"
            )
            return "unknown", 0.0

        best_balance = max(balance_confs) if balance_confs else 0.0
        best_activity = max(activity_confs) if activity_confs else 0.0

        print(
            f"[TableTypeModel.predict] best_balance={best_balance:.4f}, "
            f"best_activity={best_activity:.4f}"
        )

        if best_balance >= best_activity:
            return "balance", best_balance
        else:
            return "activity", best_activity


# Global singleton instance for the model.
_model_instance: Optional[TableTypeModel] = None


def get_model() -> TableTypeModel:
    """
    Retrieve a singleton instance of TableTypeModel.

    Ensures that the YOLO model is loaded only once per process,
    which is important for performance in production.
    """
    global _model_instance

    if _model_instance is None:
        print(
            f"[get_model] Initializing TableTypeModel with MODEL_PATH="
            f"{settings.MODEL_PATH}"
        )
        labels = [l.strip() for l in settings.LABELS.split(",")]
        print(f"[get_model] Parsed LABELS from settings: {labels}")
        _model_instance = TableTypeModel(settings.MODEL_PATH, labels)
    else:
        print("[get_model] Reusing existing TableTypeModel singleton")

    return _model_instance
