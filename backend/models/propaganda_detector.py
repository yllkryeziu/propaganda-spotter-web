import torch
import torch.nn.functional as F
from transformers import CLIPProcessor, CLIPModel, BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import numpy as np
import cv2
import time
from typing import Dict, List, Any, Tuple
import logging
import warnings
from torchcam.methods import GradCAMpp
from torchcam.utils import overlay_mask
from torchvision.transforms.functional import to_pil_image, to_tensor

# Suppress specific model warnings
warnings.filterwarnings("ignore", message=".*BlipModel.*deprecated.*")
warnings.filterwarnings("ignore", message=".*weights.*not initialized.*")

logger = logging.getLogger(__name__)


class PropagandaDetector:
    """
    Propaganda detection model using CLIP for visual-textual analysis
    and Grad-CAM for explainable AI.
    """
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
        # Load CLIP model for propaganda detection
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self.clip_model.to(self.device)
        self.clip_model.eval() # Set to evaluation mode

        # Initialize Grad-CAM++ extractor
        self.cam_extractor = GradCAMpp(self.clip_model, target_layer='vision_model.post_layernorm')

        # Load BLIP model for image captioning
        self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.blip_model.to(self.device)
        self.blip_model.eval()
        
        self.propaganda_concepts = [
            "authority figure in uniform", "military propaganda poster", "political rally with flags",
            "emotional manipulation imagery", "fear-inducing propaganda", "patriotic symbols and colors",
            "leader worship imagery", "us versus them messaging", "call to action propaganda",
            "historical propaganda art", "war propaganda poster", "political campaign imagery"
        ]
        
        self.color_map = {
            "authority": "#ef4444", "emotional": "#f97316", "fear": "#dc2626",
            "patriotic": "#3b82f6", "leader": "#8b5cf6", "conflict": "#059669",
            "action": "#eab308", "historical": "#6b7280"
        }
    
    async def analyze_image(self, image: Image.Image) -> Dict[str, Any]:
        start_time = time.time()
        logger.info("--- Starting New Image Analysis ---")
        try:
            caption = await self._generate_caption(image)
            
            inputs = self.clip_processor(
                text=self.propaganda_concepts, images=image, return_tensors="pt", padding=True
            ).to(self.device)
            
            detections, clip_outputs = await self._detect_propaganda_elements(inputs)
            
            attention_maps = self._generate_attention_maps(inputs, detections, clip_outputs)
            
            bounding_boxes = self._create_bounding_boxes(attention_maps, detections)
            
            analysis_text = await self._generate_analysis_text(caption, detections)
            
            processing_time = time.time() - start_time
            overall_confidence = np.mean([det['confidence'] for det in detections]) if detections else 0.0
            
            logger.info(f"--- Analysis Complete in {processing_time:.2f}s. Found {len(bounding_boxes)} bounding boxes. ---")

            return {
                'detections': bounding_boxes,
                'analysis_text': analysis_text,
                'overall_confidence': float(overall_confidence),
                'processing_time': processing_time,
                'image_caption': caption
            }
        except Exception as e:
            logger.error(f"Error in propaganda analysis: {e}", exc_info=True)
            raise e
    
    async def _generate_caption(self, image: Image.Image) -> str:
        try:
            inputs = self.blip_processor(image, return_tensors="pt").to(self.device)
            with torch.no_grad():
                out = self.blip_model.generate(**inputs, max_length=50)
                caption = self.blip_processor.decode(out[0], skip_special_tokens=True)
            return caption
        except Exception as e:
            logger.error(f"Error generating caption: {e}")
            return "Unable to generate caption"
    
    async def _detect_propaganda_elements(self, inputs) -> Tuple[List[Dict[str, Any]], Any]:
        logger.info("Step 1: Detecting propaganda elements...")
        try:
            detections = []
            outputs = self.clip_model(**inputs)
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1)
            
            logger.info("CLIP Model Confidence Scores:")
            for i, concept in enumerate(self.propaganda_concepts):
                confidence = float(probs[0][i])
                logger.info(f"  - '{concept}': {confidence:.4f}")
                if confidence > 0.10:  # Lowered threshold for debugging
                    concept_type = self._categorize_concept(concept)
                    detection = {
                        'id': f"detection_{len(detections)}", 'concept': concept, 'type': concept_type,
                        'confidence': confidence, 'label': concept_type.replace('_', ' ').title(),
                        'color': self.color_map.get(concept_type, "#6b7280"), 'class_index': i
                    }
                    detections.append(detection)
            
            detections.sort(key=lambda x: x['confidence'], reverse=True)
            logger.info(f"Found {len(detections)} potential concepts above threshold.")
            
            return detections[:5], outputs
        except Exception as e:
            logger.error(f"Error detecting propaganda elements: {e}", exc_info=True)
            return [], None

    def _categorize_concept(self, concept: str) -> str:
        concept_lower = concept.lower()
        if "authority" in concept_lower or "uniform" in concept_lower: return "authority"
        if "emotional" in concept_lower or "manipulation" in concept_lower: return "emotional"
        if "fear" in concept_lower: return "fear"
        if "patriotic" in concept_lower or "flag" in concept_lower: return "patriotic"
        if "leader" in concept_lower or "worship" in concept_lower: return "leader"
        if "war" in concept_lower or "versus" in concept_lower: return "conflict"
        if "action" in concept_lower or "call" in concept_lower: return "action"
        if "historical" in concept_lower: return "historical"
        return "general"

    def _generate_attention_maps(self, inputs, detections: List[Dict[str, Any]], clip_outputs) -> List[np.ndarray]:
        logger.info(f"Step 2: Generating {len(detections)} attention maps...")
        try:
            attention_maps = []
            if not detections: return attention_maps

            # Use the full logits from the clip model output
            scores = clip_outputs.logits_per_image

            for detection in detections:
                class_index = detection['class_index']

                # We need to clear grads before each new computation
                self.clip_model.zero_grad()
                cams = self.cam_extractor(class_idx=class_index, scores=scores)
                
                if not cams or not isinstance(cams[0], torch.Tensor):
                    logger.warning(f"  - CAM generation failed for concept: {detection['concept']}")
                    continue

                # Process CAM for output
                cam = to_pil_image(cams[0].squeeze(0), mode='F')
                cam_np = np.array(cam)
                cam_np = cv2.resize(cam_np, (inputs.pixel_values.shape[3], inputs.pixel_values.shape[2]))
                cam_np = (cam_np - np.min(cam_np)) / (np.max(cam_np) - np.min(cam_np) + 1e-8)
                attention_maps.append(cam_np)
                logger.info(f"  - Successfully generated CAM for: {detection['concept']}")

            return attention_maps
        except Exception as e:
            logger.error(f"Error generating attention maps: {e}", exc_info=True)
            return []

    def _create_bounding_boxes(self, attention_maps: List[np.ndarray], detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        logger.info(f"Step 3: Creating bounding boxes from {len(attention_maps)} attention maps...")
        try:
            bounding_boxes = []
            for i, (attention_map, detection) in enumerate(zip(attention_maps, detections)):
                if attention_map.size == 0: continue

                threshold = np.quantile(attention_map, 0.85) # Top 15% of attention
                logger.info(f"  - For '{detection['concept']}', attention threshold set to {threshold:.4f}")
                binary_mask = (attention_map > threshold).astype(np.uint8)
                
                contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                logger.info(f"  - Found {len(contours)} contours.")

                if contours:
                    largest_contour = max(contours, key=cv2.contourArea)
                    x, y, w, h = cv2.boundingRect(largest_contour)
                    
                    img_h, img_w = attention_map.shape
                    x_pct, y_pct = (x / img_w) * 100, (y / img_h) * 100
                    w_pct, h_pct = (w / img_w) * 100, (h / img_h) * 100
                    
                    bbox = {
                        'id': detection['id'], 'bbox': [x_pct, y_pct, w_pct, h_pct],
                        'label': detection['label'], 'color': detection['color'],
                        'confidence': detection['confidence'], 'type': detection['type']
                    }
                    bounding_boxes.append(bbox)
                    logger.info(f"  - Created bounding box for '{detection['concept']}'.")
                else:
                    logger.warning(f"  - No contours found for '{detection['concept']}', skipping bounding box.")
            
            logger.info(f"Successfully created {len(bounding_boxes)} bounding boxes.")
            return bounding_boxes
        except Exception as e:
            logger.error(f"Error creating bounding boxes: {e}", exc_info=True)
            return []
    
    async def _generate_analysis_text(self, caption: str, detections: List[Dict[str, Any]]) -> str:
        """Generate comprehensive analysis text"""
        try:
            if not detections:
                return "No significant propaganda elements detected in this image."
            
            analysis_parts = [
                f"**Image Analysis**: {caption}\n",
                "**Detected Propaganda Elements**:\n"
            ]
            
            # Group detections by type
            type_groups = {}
            for detection in detections:
                concept_type = detection['type']
                if concept_type not in type_groups:
                    type_groups[concept_type] = []
                type_groups[concept_type].append(detection)
            
            # Generate analysis for each type
            type_descriptions = {
                'authority': "**Authority Appeal**: The presence of authority figures or institutional symbols designed to inspire trust and compliance through perceived credibility and power.",
                'emotional': "**Emotional Manipulation**: Visual elements crafted to evoke strong emotional responses, bypassing rational analysis and critical thinking.",
                'fear': "**Fear-based Messaging**: Imagery designed to create anxiety, worry, or fear to motivate specific behaviors or beliefs.",
                'patriotic': "**Patriotic Symbolism**: Use of national symbols, colors, or imagery to create emotional resonance with patriotic sentiments and national identity.",
                'leader': "**Leadership Cult**: Imagery promoting reverence or worship of specific leaders or personalities.",
                'conflict': "**Us vs Them Framing**: Visual elements that create clear divisions between groups, promoting in-group loyalty and out-group hostility.",
                'action': "**Call to Action**: Visual cues designed to motivate specific behaviors or responses from the viewer.",
                'historical': "**Historical References**: Use of historical imagery or references to legitimize current messages or create emotional connections."
            }
            
            for concept_type, group_detections in type_groups.items():
                if concept_type in type_descriptions:
                    analysis_parts.append(type_descriptions[concept_type])
                    
                    # Add confidence information
                    avg_confidence = np.mean([d['confidence'] for d in group_detections])
                    analysis_parts.append(f"*Confidence: {avg_confidence:.1%}\n")
            
            # Add overall assessment
            overall_confidence = np.mean([d['confidence'] for d in detections])
            if overall_confidence > 0.3:
                analysis_parts.append("**Overall Assessment**: This image shows strong indicators of propaganda techniques. The combination of visual elements appears designed to influence opinion or behavior through emotional and psychological appeals rather than factual argumentation.")
            elif overall_confidence > 0.2:
                analysis_parts.append("**Overall Assessment**: This image contains moderate propaganda elements. Some visual techniques may be intended to influence perception, though the overall effect is less pronounced.")
            else:
                analysis_parts.append("**Overall Assessment**: This image shows minimal propaganda characteristics. While some persuasive elements may be present, they appear relatively subtle or incidental.")
            
            return "\n\n".join(analysis_parts)
            
        except Exception as e:
            logger.error(f"Error generating analysis text: {e}")
            return "Error generating analysis text."