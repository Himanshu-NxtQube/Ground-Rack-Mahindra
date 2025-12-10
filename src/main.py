import os
import cv2
from analysis.stacking_analyzer import StackingAnalyzer
from analysis.box_counter import BoxCounter 
from inference.box_detector import BoxDetector
from inference.pallet_detector import PalletDetector
from analysis.converter import Converter
from utils.visualizer import Visualizer
from inference.depth_estimation import DepthEstimator
from inference.stack_validator import StackValidator
from inference.pallet_status import PalletStatus
from inference.boundary_detection import BoundaryDetector

box_detector = BoxDetector()
box_counter = BoxCounter()
pallet_detector = PalletDetector()
converter = Converter()
visualizer = Visualizer()
stack_analyzer = StackingAnalyzer()
depth_estimator = DepthEstimator("depth_anything_v2")
pallet_status_estimator = PalletStatus()
stack_validator = StackValidator()
boundary_detector = BoundaryDetector()
images_dir = "images/"

def process_single_image(image_path, debug=False):
    boundaries = boundary_detector.get_boundaries(image_path)
    
    left_boxes, right_boxes = box_detector.detect(image_path, boundaries)
    left_pallet, right_pallet = pallet_detector.detect(image_path, boundaries)

    left_box_dimensions = converter.get_box_dimensions(left_boxes, left_pallet)
    right_box_dimensions = converter.get_box_dimensions(right_boxes, right_pallet)

    left_structure = stack_analyzer.analyze(left_box_dimensions)
    right_structure = stack_analyzer.analyze(right_box_dimensions)

    depth_map = depth_estimator.get_depth_map(image_path)
    pallet_status_result = pallet_status_estimator.get_status(cv2.imread(image_path).shape, depth_map)

    left_pallet_status = pallet_status_result['left_status']
    right_pallet_status = pallet_status_result['right_status']

    left_status_bbox = pallet_status_result['left_bbox']
    right_status_bbox = pallet_status_result['right_bbox']

    if debug:
        visualizer.visualize_box_dimensions(image_path, "left", left_boxes, left_box_dimensions)
        visualizer.visualize_box_dimensions(image_path, "right", right_boxes, right_box_dimensions)
    
    # TEMPORARY CHANGE: passing IMAGE_NAME as PART_NUMBER
    left_box_count_per_layer = box_counter.count_boxes_per_layer(left_boxes, f"{os.path.basename(image_path).split('.')[0]}_L", left_structure['avg_box_length'], left_structure['avg_box_width'], left_structure['stacking_type'])
    right_box_count_per_layer = box_counter.count_boxes_per_layer(right_boxes, f"{os.path.basename(image_path).split('.')[0]}_R", right_structure['avg_box_length'], right_structure['avg_box_width'], right_structure['stacking_type'])

    left_stack_count = stack_validator.count_stack(left_boxes, left_pallet_status, left_pallet, left_status_bbox)
    right_stack_count = stack_validator.count_stack(right_boxes, right_pallet_status, right_pallet, right_status_bbox)

    extra_left_box_count = box_counter.count_extra_boxes(left_boxes, left_stack_count, left_pallet_status, left_box_count_per_layer)
    extra_right_box_count = box_counter.count_extra_boxes(right_boxes, right_stack_count, right_pallet_status, right_box_count_per_layer)

    if left_box_count_per_layer is not None and left_stack_count is not None:
        total_left_boxes = (left_box_count_per_layer * left_stack_count) + extra_left_box_count
    else:
        total_left_boxes = None
    
    if right_box_count_per_layer is not None and right_stack_count is not None:
        total_right_boxes = (right_box_count_per_layer * right_stack_count) + extra_right_box_count
    else:
        total_right_boxes = None

    
    def format_value(value, width, precision=None):
        if value is None:
            return f"{'N/A':<{width}}"
        if precision is not None:
            return f"{value:<{width}.{precision}f}"
        return f"{value:<{width}}"

    print(f"{'':<20} | {'Left':<15} | {'Right':<15}")
    print(f"{'-'*20} | {'-'*15} | {'-'*15}")
    print(f"{'Stacking Type':<20} | {format_value(left_structure['stacking_type'], 15)} | {format_value(right_structure['stacking_type'], 15)}")
    print(f"{'Avg Box Length':<20} | {format_value(left_structure['avg_box_length'], 15, 2)} | {format_value(right_structure['avg_box_length'], 15, 2)}")
    print(f"{'Avg Box Width':<20} | {format_value(left_structure['avg_box_width'], 15, 2)} | {format_value(right_structure['avg_box_width'], 15, 2)}")
    print(f"{'Left Pallet Status':<20} | {format_value(left_pallet_status, 15)} | {format_value(right_pallet_status, 15)}")
    print(f"{'Box Count Per Layer':<20} | {format_value(left_box_count_per_layer, 15)} | {format_value(right_box_count_per_layer, 15)}")
    print(f"{'Stack Count':<20} | {format_value(left_stack_count, 15)} | {format_value(right_stack_count, 15)}")
    print(f"{'Extra Boxes':<20} | {format_value(extra_left_box_count, 15)} | {format_value(extra_right_box_count, 15)}")
    print(f"{'Total Boxes':<20} | {format_value(total_left_boxes, 15)} | {format_value(total_right_boxes, 15)}")
    print("\n")

for image_name in os.listdir(images_dir):
    # if int(image_name[4:8]) != 13:
    #     continue
    print("Image:",image_name)
    image_path = os.path.join(images_dir, image_name) 
    process_single_image(image_path, debug=True)