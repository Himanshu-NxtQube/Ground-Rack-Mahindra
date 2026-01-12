import torch
import cv2
import numpy as np
from PIL import Image
from transformers import AutoProcessor, AutoModelForDepthEstimation, pipeline

# Import the V3 specific API
try:
    from depth_anything_3.api import DepthAnything3
except ImportError:
    print("Please install V3: pip install -e . inside the Depth-Anything-3 folder")

class DepthEstimator:
    def __init__(self, model_name):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_type = model_name  # Renamed to avoid confusion with model objects
        
        if self.model_type == "apple_depth_pro":
            self.apple_depth_processor = AutoProcessor.from_pretrained("apple/DepthPro-hf")
            self.apple_depth_model = AutoModelForDepthEstimation.from_pretrained("apple/DepthPro-hf").to(self.device)
            
        elif self.model_type == "depth_anything_v2":
            # V2 is supported directly by Hugging Face pipeline
            self.depth_estimator = pipeline(task="depth-estimation", model="depth-anything/Depth-Anything-V2-Large-hf", device=0 if torch.cuda.is_available() else -1)

        elif self.model_type == "depth_anything_v3":
            # V3 uses its own custom API for high-resolution & multi-view features
            # 'da3-base' is a good middle ground; use 'da3-large' for higher quality
            self.da3_model = DepthAnything3.from_pretrained("depth-anything/da3-base").to(self.device)

    def get_depth_map(self, image_path):
        # Load image once
        raw_cv2_image = cv2.imread(image_path)
        if raw_cv2_image is None:
            raise ValueError(f"Could not read image at {image_path}")
            
        # Convert for PIL-based models
        pil_image = Image.fromarray(cv2.cvtColor(raw_cv2_image, cv2.COLOR_BGR2RGB))
        orig_w, orig_h = pil_image.size

        if self.model_type == "apple_depth_pro":
            inputs = self.apple_depth_processor(images=pil_image, return_tensors="pt").to(self.device)
            with torch.no_grad():
                outputs = self.apple_depth_model(**inputs)
                depth_map = outputs.predicted_depth.squeeze().cpu().numpy()
            
            # Post-processing (Metric to 0-255)
            depth_map = cv2.resize(depth_map, (orig_w, orig_h))
            depth_map = (depth_map - depth_map.min()) / (depth_map.max() - depth_map.min())
            return (depth_map * 255).astype("uint8")

        elif self.model_type == "depth_anything_v2":
            result = self.depth_estimator(pil_image)
            return np.array(result['depth'])

        elif self.model_type == "depth_anything_v3":
            # Using V3 API with high-res processing
            results = self.da3_model.inference(
                image=[pil_image], 
                process_res=1008, 
                process_res_method="upper_bound_resize"
            )
            # V3 returns a numpy array. We resize it to match the input exactly.
            depth_map = results.depth.squeeze()
            depth_map = cv2.resize(depth_map, (orig_w, orig_h), interpolation=cv2.INTER_LINEAR)
            
            # Invert so Near = Bright (as we discussed)
            depth_map = depth_map.max() - depth_map
            
            # Normalize to 0-255
            depth_norm = cv2.normalize(depth_map, None, 0, 255, cv2.NORM_MINMAX)
            return depth_norm.astype("uint8")