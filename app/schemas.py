from pydantic import BaseModel
from typing import Optional, List, Any


class TablePrediction(BaseModel):
    predicted_label: str
    confidence: float
    boxes: Optional[List[Any]] = None  # אפשר לשנות בהמשך אם תחזיר בוקסים


class HealthResponse(BaseModel):
    status: str
    message: str
