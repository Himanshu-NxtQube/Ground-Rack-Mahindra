import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.inference import boundary_detection, depth_estimation, pallet_detector, box_detector
from src.utils import visualizer

boundary_detector = boundary_detection.BoundaryDetector()
depth_estimator = depth_estimation.DepthEstimator("depth_anything_v2")
pallet_detector = pallet_detector.PalletDetector()
box_detector = box_detector.BoxDetector()
visualizer = visualizer.Visualizer()

images_dir = 'images/'

def process_single_image(image_path):
    boundaries = boundary_detector.get_boundaries(image_path)
    depth_map = depth_estimator.get_depth_map(image_path)
    
    left_pallet, right_pallet = pallet_detector.detect(image_path, boundaries)
    left_boxes, right_boxes = box_detector.detect(image_path, boundaries, left_pallet, right_pallet)
    
    visualizer.visualize_box_dimensions(image_path, "left", [left_boxes], left_pallet, depth_map)
    visualizer.visualize_box_dimensions(image_path, "right", [right_boxes], right_pallet, depth_map)

def process_dir(dir_name):
    for image_name in sorted(os.listdir(dir_name)):
        print("Image:",image_name)
        image_path = os.path.join(images_dir, image_name) 

        try:
            process_single_image(image_path)
        except Exception as e:
            print("Error processing image:", image_name)
            print(e)

if __name__ == "__main__":
    process_dir(images_dir)