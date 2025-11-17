from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .schemas import TablePrediction, HealthResponse
from .model import get_model


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    description="Micro-service for table type detection (balance / activity).",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # ב-production כדאי להגביל
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def load_model_on_startup():
    _ = get_model()


@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(status="ok", message="service is up")


@app.post("/predict", response_model=TablePrediction)
async def predict_table_type(file: UploadFile = File(...)):
    if file.content_type not in ("image/png", "image/jpeg", "image/jpg"):
        raise HTTPException(status_code=400, detail="Unsupported file type")

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        model = get_model()
        label, conf = model.predict(image_bytes)
        return TablePrediction(
            predicted_label=label,
            confidence=conf,
            boxes=None,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")
