from pydantic import BaseModel
from typing import List, Optional

class BoundingBox(BaseModel):
    id: str
    x: float  # x coordinate as percentage
    y: float  # y coordinate as percentage  
    width: float  # width as percentage
    height: float  # height as percentage
    label: str
    color: str
    confidence: float

class HighlightedWord(BaseModel):
    word: str
    id: str
    color: str

class AnalysisResponse(BaseModel):
    success: bool
    analysis_text: str
    bounding_boxes: List[BoundingBox]
    highlighted_words: List[HighlightedWord]
    confidence_score: float
    processing_time: float
    error_message: Optional[str] = None
