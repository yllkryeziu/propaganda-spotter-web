import cv2
import numpy as np
from PIL import Image
from typing import Tuple, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ImageProcessor:
    """
    Image processing utilities for propaganda detection
    """
    
    def __init__(self):
        self.max_size = (1024, 1024)  # Maximum image size for processing
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for analysis
        """
        try:
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large
            if image.size[0] > self.max_size[0] or image.size[1] > self.max_size[1]:
                image.thumbnail(self.max_size, Image.Resampling.LANCZOS)
            
            return image
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            raise e
    
    def enhance_contrast(self, image: Image.Image, factor: float = 1.2) -> Image.Image:
        """
        Enhance image contrast for better analysis
        """
        try:
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(image)
            return enhancer.enhance(factor)
        except Exception as e:
            logger.error(f"Error enhancing contrast: {e}")
            return image
    
    def detect_text_regions(self, image: Image.Image) -> List[Dict[str, Any]]:
        """
        Detect text regions in the image using OpenCV
        """
        try:
            # Convert PIL to OpenCV format
            img_array = np.array(image)
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Use MSER (Maximally Stable Extremal Regions) for text detection
            mser = cv2.MSER_create()
            regions, _ = mser.detectRegions(gray)
            
            text_regions = []
            for i, region in enumerate(regions):
                # Get bounding box
                x, y, w, h = cv2.boundingRect(region.reshape(-1, 1, 2))
                
                # Filter out very small regions
                if w > 20 and h > 10:
                    # Convert to percentages
                    img_h, img_w = gray.shape
                    x_pct = (x / img_w) * 100
                    y_pct = (y / img_h) * 100
                    w_pct = (w / img_w) * 100
                    h_pct = (h / img_h) * 100
                    
                    text_regions.append({
                        'id': f'text_{i}',
                        'bbox': [x_pct, y_pct, w_pct, h_pct],
                        'type': 'text'
                    })
            
            return text_regions[:10]  # Return top 10 text regions
            
        except Exception as e:
            logger.error(f"Error detecting text regions: {e}")
            return []
    
    def detect_faces(self, image: Image.Image) -> List[Dict[str, Any]]:
        """
        Detect faces in the image using OpenCV Haar cascades
        """
        try:
            # Convert PIL to OpenCV format
            img_array = np.array(image)
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Load face cascade
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            face_regions = []
            for i, (x, y, w, h) in enumerate(faces):
                # Convert to percentages
                img_h, img_w = gray.shape
                x_pct = (x / img_w) * 100
                y_pct = (y / img_h) * 100
                w_pct = (w / img_w) * 100
                h_pct = (h / img_h) * 100
                
                face_regions.append({
                    'id': f'face_{i}',
                    'bbox': [x_pct, y_pct, w_pct, h_pct],
                    'type': 'face'
                })
            
            return face_regions
            
        except Exception as e:
            logger.error(f"Error detecting faces: {e}")
            return []
    
    def analyze_color_composition(self, image: Image.Image) -> Dict[str, Any]:
        """
        Analyze color composition for propaganda indicators
        """
        try:
            img_array = np.array(image)
            
            # Calculate color histograms
            hist_r = cv2.calcHist([img_array], [0], None, [256], [0, 256])
            hist_g = cv2.calcHist([img_array], [1], None, [256], [0, 256])
            hist_b = cv2.calcHist([img_array], [2], None, [256], [0, 256])
            
            # Calculate dominant colors
            pixels = img_array.reshape(-1, 3)
            
            # Simple dominant color detection (could be improved with k-means)
            unique_colors, counts = np.unique(pixels, axis=0, return_counts=True)
            dominant_indices = np.argsort(counts)[-5:]  # Top 5 colors
            dominant_colors = unique_colors[dominant_indices]
            
            # Analyze for propaganda-typical color schemes
            propaganda_indicators = {
                'red_dominant': np.mean(img_array[:, :, 0]) > np.mean(img_array[:, :, 1:]),
                'high_contrast': np.std(cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)) > 50,
                'monochromatic_tendency': self._is_monochromatic(img_array),
                'dominant_colors': dominant_colors.tolist()
            }
            
            return propaganda_indicators
            
        except Exception as e:
            logger.error(f"Error analyzing color composition: {e}")
            return {}
    
    def _is_monochromatic(self, img_array: np.ndarray, threshold: float = 30) -> bool:
        """
        Check if image has monochromatic tendency (common in propaganda)
        """
        try:
            # Calculate color variance
            color_std = np.std(img_array, axis=(0, 1))
            return np.mean(color_std) < threshold
        except:
            return False
    
    def create_overlay_mask(self, image_size: Tuple[int, int], bboxes: List[Dict[str, Any]]) -> np.ndarray:
        """
        Create overlay mask for visualization
        """
        try:
            w, h = image_size
            mask = np.zeros((h, w, 3), dtype=np.uint8)
            
            for bbox in bboxes:
                # Convert percentages back to pixels
                x = int((bbox['bbox'][0] / 100) * w)
                y = int((bbox['bbox'][1] / 100) * h)
                box_w = int((bbox['bbox'][2] / 100) * w)
                box_h = int((bbox['bbox'][3] / 100) * h)
                
                # Parse color (hex to RGB)
                color_hex = bbox['color'].lstrip('#')
                color_rgb = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
                
                # Draw filled rectangle with transparency
                cv2.rectangle(mask, (x, y), (x + box_w, y + box_h), color_rgb, -1)
            
            return mask
            
        except Exception as e:
            logger.error(f"Error creating overlay mask: {e}")
            return np.zeros((100, 100, 3), dtype=np.uint8)
