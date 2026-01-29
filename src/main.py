import os
import cv2
import json
from analysis.stacking_analyzer import StackingAnalyzer
from analysis.box_counter import BoxCounter 
from analysis.converter import Converter
from inference.box_detector import BoxDetector
from inference.pallet_detector import PalletDetector
from inference.depth_estimation import DepthEstimator
from inference.stack_validator import StackValidator
from inference.pallet_status import PalletStatus
from inference.gap_detector import find_gap
from inference.boundary_detection import BoundaryDetector
from inference.rack_box_extraction import RackBoxExtractor
from inference.google_ocr import OCRClient
from inference.infer_func import infer_Q3_Q4
from utils.csv_utils import CSVUtils
from utils.visualizer import Visualizer
from utils.rds_operator import RDSOperator
from utils.s3_operator import upload_images

box_detector = BoxDetector()
box_counter = BoxCounter()
pallet_detector = PalletDetector()
converter = Converter()
rds_operator = RDSOperator()
ocr_client = OCRClient()
visualizer = Visualizer()
stack_analyzer = StackingAnalyzer()
depth_estimator = DepthEstimator("depth_anything_v2")
pallet_status_estimator = PalletStatus()
stack_validator = StackValidator()
rack_box_extractor = RackBoxExtractor()
boundary_detector = BoundaryDetector()
csv_utils = CSVUtils()
images_dir = "images/"
upload = False

def process_single_image(image_path, report_id, debug=False, upload=False):
    image_name = os.path.basename(image_path)
    boundaries = boundary_detector.get_boundaries(image_path)
    annotations = ocr_client.get_annotations(image_path)
    rack_dict = rack_box_extractor.extract_rack_info(annotations, boundaries, cv2.imread(image_path).shape)
    rack_dict = infer_Q3_Q4(rack_dict)

    depth_map = depth_estimator.get_depth_map(image_path)
    
    left_pallet, right_pallet = pallet_detector.detect(image_path, boundaries)
    left_boxes, right_boxes = box_detector.detect(image_path, boundaries, left_pallet, right_pallet)

    # TEMPORARY CHANGE: passing IMAGE_NAME as PART_NUMBER
    left_part_number = f"{image_name.split('.')[0]}_L"
    right_part_number = f"{image_name.split('.')[0]}_R"

    left_layers = csv_utils.get_layers(left_part_number)
    right_layers = csv_utils.get_layers(right_part_number)

    left_layer_wise_depth_diff = csv_utils.get_layer_wise_depth_diff(left_part_number)
    right_layer_wise_depth_diff = csv_utils.get_layer_wise_depth_diff(right_part_number)

    left_boxes = box_detector.classify_boxes(left_boxes, left_pallet, left_layers, depth_map, left_layer_wise_depth_diff)
    right_boxes = box_detector.classify_boxes(right_boxes, right_pallet, right_layers, depth_map, right_layer_wise_depth_diff)

    if debug:
        visualizer.visualize_box_dimensions(image_path, "left", left_boxes, left_pallet, depth_map)
        visualizer.visualize_box_dimensions(image_path, "right", right_boxes, right_pallet, depth_map)

    front_left_boxes = left_boxes[0]
    front_right_boxes = right_boxes[0]

    left_box_dimensions = converter.get_box_dimensions(front_left_boxes, left_pallet)
    right_box_dimensions = converter.get_box_dimensions(front_right_boxes, right_pallet)

    left_structure = stack_analyzer.analyze(left_box_dimensions)
    right_structure = stack_analyzer.analyze(right_box_dimensions)

    left_stacking_type = csv_utils.get_stacking_type(left_part_number)
    right_stacking_type = csv_utils.get_stacking_type(right_part_number)

    left_box_stacks = box_counter.get_box_stack(front_left_boxes)
    right_box_stacks = box_counter.get_box_stack(front_right_boxes)

    # print("Box Stacks:")
    # for left_box_stack, right_box_stack in zip(left_box_stacks, right_box_stacks):
    #     print(f"{left_box_stack} | {right_box_stack}") 
    
    # print(json.dumps(right_box_stacks, indent=4))
    print("Box Stacks:")
    for i in range(max(len(left_box_stacks), len(right_box_stacks))):
        left_box_stack_len = len(left_box_stacks[i]) if i < len(left_box_stacks) else 0
        right_box_stack_len = len(right_box_stacks[i]) if i < len(right_box_stacks) else 0
        print('📦'*left_box_stack_len + '\t\t' + '📦'*right_box_stack_len)

    pallet_status_result = pallet_status_estimator.get_status(image_path, depth_map)

    left_pallet_status = pallet_status_result['left_status']
    right_pallet_status = pallet_status_result['right_status']

    left_status_bbox = pallet_status_result['left_bbox']
    right_status_bbox = pallet_status_result['right_bbox']

    
    left_gap = find_gap(left_pallet, front_left_boxes)
    right_gap = find_gap(right_pallet, front_right_boxes)

    left_gap_in_inches = converter.convert_gap_in_inches(left_gap)
    right_gap_in_inches = converter.convert_gap_in_inches(right_gap)

    left_boxes_per_layer = csv_utils.get_boxes_per_layer(left_part_number)
    right_boxes_per_layer = csv_utils.get_boxes_per_layer(right_part_number)

    left_box_count_per_layer = box_counter.count_boxes_per_layer(box_stacks=left_box_stacks, 
                                                                boxes_per_layer=left_boxes_per_layer,
                                                                layers=left_layers,
                                                                avg_box_length=left_structure['avg_box_length'], 
                                                                avg_box_width=left_structure['avg_box_width'], 
                                                                stacking_type=left_structure['stacking_type'], 
                                                                gap_in_inches=left_gap_in_inches)
    right_box_count_per_layer = box_counter.count_boxes_per_layer(box_stacks=right_box_stacks, 
                                                                  boxes_per_layer=right_boxes_per_layer,
                                                                  layers=right_layers,
                                                                  avg_box_length=right_structure['avg_box_length'], 
                                                                  avg_box_width=right_structure['avg_box_width'], 
                                                                  stacking_type=right_structure['stacking_type'], 
                                                                  gap_in_inches=right_gap_in_inches)

    left_odd_layering = csv_utils.get_odd_layering(left_part_number)
    left_even_layering = csv_utils.get_even_layering(left_part_number)
    right_odd_layering = csv_utils.get_odd_layering(right_part_number)
    right_even_layering = csv_utils.get_even_layering(right_part_number)

    left_stack_count = stack_validator.count_stack(box_list=front_left_boxes, 
                                                    box_stacks=left_box_stacks, 
                                                    pallet_status=left_pallet_status, 
                                                    pallet=left_pallet, 
                                                    status_bbox=left_status_bbox,
                                                    odd_layering=left_odd_layering,
                                                    even_layering=left_even_layering,
                                                    stacking_type=left_structure['stacking_type'],
                                                    boxes_per_layer=left_boxes_per_layer,
                                                    layers=left_layers)
    
    right_stack_count = stack_validator.count_stack(box_list=front_right_boxes, 
                                                    box_stacks=right_box_stacks, 
                                                    pallet_status=right_pallet_status, 
                                                    pallet=right_pallet, 
                                                    status_bbox=right_status_bbox,
                                                    odd_layering=right_odd_layering,
                                                    even_layering=right_even_layering,
                                                    stacking_type=right_structure['stacking_type'],
                                                    boxes_per_layer=right_boxes_per_layer,
                                                    layers=right_layers)

    extra_left_box_count = box_counter.count_extra_boxes(stacking_type=left_structure['stacking_type'], 
                                                        avg_box_length=left_structure['avg_box_length'], 
                                                        avg_box_width=left_structure['avg_box_width'], 
                                                        avg_box_height=left_structure['avg_box_height'], 
                                                        layers=left_layers, 
                                                        odd_layering=left_odd_layering,
                                                        even_layering=left_even_layering,
                                                        box_list=left_boxes, 
                                                        stack_count=left_stack_count, 
                                                        pallet_status=left_pallet_status, 
                                                        boxes_per_layer=left_box_count_per_layer, 
                                                        box_stacks=left_box_stacks)
    extra_right_box_count = box_counter.count_extra_boxes(stacking_type=right_structure['stacking_type'], 
                                                        avg_box_length=right_structure['avg_box_length'], 
                                                        avg_box_width=right_structure['avg_box_width'], 
                                                        avg_box_height=right_structure['avg_box_height'], 
                                                        layers=right_layers, 
                                                        odd_layering=right_odd_layering,
                                                        even_layering=right_even_layering,
                                                        box_list=right_boxes, 
                                                        stack_count=right_stack_count, 
                                                        pallet_status=right_pallet_status, 
                                                        boxes_per_layer=right_box_count_per_layer, 
                                                        box_stacks=right_box_stacks)

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
    print(f"{'Pallet Status':<20} | {format_value(left_pallet_status, 15)} | {format_value(right_pallet_status, 15)}")
    print(f"{'Gap':<20} | {format_value(left_gap_in_inches, 15)} | {format_value(right_gap_in_inches, 15)}")
    print(f"{'Box Count Per Layer':<20} | {format_value(left_box_count_per_layer, 15)} | {format_value(right_box_count_per_layer, 15)}")
    print(f"{'Stack Count':<20} | {format_value(left_stack_count, 15)} | {format_value(right_stack_count, 15)}")
    print(f"{'Extra Boxes':<20} | {format_value(extra_left_box_count, 15)} | {format_value(extra_right_box_count, 15)}")
    print(f"{'Total Boxes':<20} | {format_value(total_left_boxes, 15)} | {format_value(total_right_boxes, 15)}")
    print("\n")

    if upload:
        s3_key, s3_url = upload_images(image_path)
        key_id = rds_operator.store_img_info(image_path)
                                #  image_name, rack_id, box_number, invoice_number, box_quantity, part_number, image_obj_key_id, unique_id="", user_id=14, exclusion="", barcode=""
        rds_operator.insert_record(image_name, report_id, rack_dict['Q3'], total_left_boxes, left_pallet_status, "NA", "", key_id, exclusion="" if left_pallet_status != "N/A" else "empty rack")
        rds_operator.insert_record(image_name, report_id, rack_dict['Q4'], total_right_boxes, right_pallet_status, "NA", "", key_id, exclusion="" if right_pallet_status != "N/A" else "empty rack")

def process_dir(dir_name, upload=False):
    report_id = 0
    if upload:
        report_id = rds_operator.create_report(14)
    for image_name in sorted(os.listdir(dir_name)):
        print("Image:",image_name)
        image_path = os.path.join(images_dir, image_name) 

        try:
            process_single_image(image_path, report_id, debug=True, upload=upload)
        except Exception as e:
            print("Error processing image:", image_name)
            print(e)

if __name__ == "__main__":
    process_dir(images_dir, upload=upload)
