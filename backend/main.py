from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import torch
import cv2
import numpy as np
from PIL import Image
import io
from typing import List, Dict, Any
import logging
import traceback

from models.propaganda_detector import PropagandaDetector
from utils.image_processor import ImageProcessor
from schemas.response_models import AnalysisResponse, BoundingBox, HighlightedWord

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Propaganda Spotter API",
    description="API for detecting and analyzing propaganda elements in images",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:3000", 
        "http://localhost:8081",  # Added for frontend on port 8081
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8081"   # Added for frontend on port 8081
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize models and processors
propaganda_detector = None
image_processor = None

@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    global propaganda_detector, image_processor
    try:
        logger.info("Loading propaganda detection model...")
        propaganda_detector = PropagandaDetector()
        image_processor = ImageProcessor()
        logger.info("Models loaded successfully!")
    except Exception as e:
        logger.error(f"Failed to load models: {e}")
        raise e

@app.get("/")
async def root():
    return {"message": "Propaganda Spotter API is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "models_loaded": propaganda_detector is not None and image_processor is not None
    }

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_image(file: UploadFile = File(...)):
    """
    Analyze an uploaded image for propaganda elements
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read and process the image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert('RGB')

        # Perform propaganda analysis
        logger.info(f"Analyzing image: {file.filename}")
        analysis_result = await propaganda_detector.analyze_image(image)
        
        # Process results for frontend
        bounding_boxes = []
        highlighted_words = []
        
        # Convert detection results to bounding boxes
        for detection in analysis_result.get('detections', []):
            bbox = BoundingBox(
                id=detection['id'],
                x=detection['bbox'][0],
                y=detection['bbox'][1], 
                width=detection['bbox'][2],
                height=detection['bbox'][3],
                label=detection['label'],
                color=detection['color'],
                confidence=detection['confidence']
            )
            bounding_boxes.append(bbox)
            
            # Create highlighted words for analysis text
            highlighted_word = HighlightedWord(
                word=detection['label'].replace('_', ' ').title(),
                id=detection['id'],
                color=detection['color']
            )
            highlighted_words.append(highlighted_word)
        
        response = AnalysisResponse(
            success=True,
            analysis_text=analysis_result.get('analysis_text', ''),
            bounding_boxes=bounding_boxes,
            highlighted_words=highlighted_words,
            confidence_score=analysis_result.get('overall_confidence', 0.0),
            processing_time=analysis_result.get('processing_time', 0.0)
        )
        
        logger.info(f"Analysis completed successfully for {file.filename}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing image: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
