from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html
from .schemas import TablePrediction, HealthResponse
from .model import get_model
from .config import settings  # Important: ensure settings exists
from PIL import Image, UnidentifiedImageError
import io
import uuid
import time
import os
import logging

logger = logging.getLogger("table_type_detector")
logger.setLevel(logging.INFO)



app = FastAPI()

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "templates", "index.html")



# ===== General Settings =====

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5MB
MAX_IMAGE_DIM = 3000  # pixels (maximum long side)

API_KEY_HEADER_NAME = "x-api-key"


def raise_http_error(status_code: int, error_code: str, message: str) -> None:
    """
    Helper for throwing HTTPException in a uniform format.
    """
    raise HTTPException(
        status_code=status_code,
        detail={
            "error_code": error_code,
            "message": message,
        },
    )


def validate_image_bytes(image_bytes: bytes) -> None:
    """
    Basic input validation:
    - Not empty
    - Not too large
    - Actually a valid image
    - Not extreme resolution
    """
    if not image_bytes:
        raise_http_error(400, "EMPTY_FILE", "Empty file received. Please upload a valid image.")

    if len(image_bytes) > MAX_FILE_SIZE_BYTES:
        raise_http_error(
            400,
            "FILE_TOO_LARGE",
            f"File too large. Maximum allowed size is {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB.",
        )

    # Image validity check
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()  # Basic check that this is an image file
    except UnidentifiedImageError:
        raise_http_error(400, "INVALID_IMAGE", "Uploaded file is not a valid image.")
    except Exception:
        raise_http_error(400, "INVALID_IMAGE", "Could not process the uploaded image.")

    # Need to reopen after verify
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    w, h = img.size
    if w < 100 or h < 100:
        raise_http_error(
            400,
            "IMAGE_TOO_SMALL",
            "Image is too small. Please upload a clearer/larger image.",
        )

    if max(w, h) > MAX_IMAGE_DIM:
        # Not throwing error - but could do resize here in the future if desired
        # Currently just soft logic (can be hardened if chosen)
        pass


# ===== API Level Security - API Key =====

def verify_api_key(x_api_key: str | None = Header(default=None, alias=API_KEY_HEADER_NAME)):
    """
    Simple API key validation:
    - If settings.API_KEY is set → require it
    - If not set → don't check (dev mode)
    """
    expected = getattr(settings, "API_KEY", None)

    if expected:
        if x_api_key is None:
            raise_http_error(401, "MISSING_API_KEY", f"Missing {API_KEY_HEADER_NAME} header.")
        if x_api_key != expected:
            raise_http_error(401, "INVALID_API_KEY", "Invalid API key.")
    # If no setting - do nothing (dev mode)
    return x_api_key


# ===== FastAPI Application =====

app = FastAPI(
    title="Financial Table Type Detector API",
    version="1.0.0",
    description="""
    A microservice that receives an image of a table and returns the detected table type.
    Supports balance tables (financial statements) and activity tables (cash flow, transactions).
    """,
    docs_url=None,
    redoc_url=None,
    openapi_tags=[
        {"name": "Prediction", "description": "🤖 Core ML inference endpoints"},
        {"name": "Health", "description": "💚 Service monitoring and status endpoints"},
        {"name": "Demo", "description": "🎨 Interactive web interface for testing"},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Can be hardened later to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def load_model_on_startup():
    try:
        _ = get_model()
        logger.info("Model loaded successfully at startup")
    except Exception as e:
        logger.exception("Failed to load model on startup")



@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title=f"{app.title} - Interactive Docs",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
        swagger_ui_parameters={
            "defaultModelsExpandDepth": -1,
            "syntaxHighlight.theme": "monokai",
            "tryItOutEnabled": True,
        },
    )


# simple landing page (unchanged)
@app.get("/", response_class=HTMLResponse)
async def demo_interface():
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        html = f.read()
    return HTMLResponse(content=html)

@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health Check",
    description="Verify that the service is running and the model is loaded",
)
def health_check():
    try:
        _ = get_model()
        return HealthResponse(status="ok", message="service and model are up and running")
    except Exception as e:
        raise_http_error(500, "HEALTH_CHECK_FAILED", f"Health check failed: {e}")


@app.post(
    "/predict",
    response_model=TablePrediction,
    tags=["Prediction"],
    summary="Classify Table Type",
    description="Upload a financial statement image and get instant classification",
)
async def predict_table_type(
    file: UploadFile = File(..., description="Financial statement image (PNG/JPEG)"),
    _api_key: str | None = Depends(verify_api_key),  # Security
):
    """
    Analyze a financial statement image and classify the table type.
    """
    # File type validation
    if file.content_type not in ("image/png", "image/jpeg", "image/jpg"):
        raise_http_error(
            400,
            "UNSUPPORTED_MEDIA_TYPE",
            "Unsupported file type. Please upload PNG or JPEG image.",
        )

    # File reading
    try:
        image_bytes = await file.read()
    except Exception:
        raise_http_error(400, "FILE_READ_ERROR", "Could not read uploaded file.")

    # Basic image validation
    validate_image_bytes(image_bytes)

    # Runtime measurement (not required, but nice for logs)
    request_id = str(uuid.uuid4())
    t0 = time.time()

    try:
        model = get_model()
        label, conf = model.predict(image_bytes)
    except HTTPException:
        # If someone inside threw HTTPException - pass it along as is
        raise
    except Exception as e:
        logger.exception(f"prediction failed for request_id={request_id}")
        raise_http_error(500, "PREDICTION_FAILED", "Prediction failed due to internal error.")

    latency_ms = int((time.time() - t0) * 1000)
    logger.info(
        f"prediction completed",
        extra={
            "request_id": request_id,
            "label": label,
            "confidence": float(conf),
            "latency_ms": latency_ms,
        },
    )


    return TablePrediction(
        predicted_label=label,
        confidence=conf,
        boxes=None,
    )