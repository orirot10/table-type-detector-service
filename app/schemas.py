from pydantic import BaseModel
from typing import Optional, List, Any


class TablePrediction(BaseModel):
    predicted_label: str
    confidence: float
    boxes: Optional[List[Any]] = None  # Can be changed later if returning boxes


class HealthResponse(BaseModel):
    status: str
    message: str
