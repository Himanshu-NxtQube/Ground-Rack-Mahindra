import os
import cv2
from analysis.stacking_analyzer import StackingAnalyzer
from analysis.box_counter import BoxCounter 
from analysis.converter import Converter
from inference.box_detector import BoxDetector
from inference.pallet_detector import PalletDetector
from inference.depth_estimation import DepthEstimator
from inference.stack_validator import StackValidator
from inference.pallet_status import PalletStatus
from inference.boundary_detection import BoundaryDetector
from inference.ocr_parser import OCRParser
from inference.google_ocr import OCRClient

# filter and split pallet
# filter and map boxes with pallet
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
ocr_parser = OCRParser()
boundary_detector = BoundaryDetector()
csv_utils = CSVUtils()
IMAGES_DIR = "images/"
UPLOAD = False

def initialize(image_path):
    # These are independent tasks
    boundaries = boundary_detector.get_boundaries(image_path)
    annotations = ocr_client.get_annotations(image_path)
    depth_map = depth_estimator.get_depth_map(image_path)
    pallets = pallet_detector.detect(image_path)
    boxes = box_detector.detect(image_path)
    return boundaries, annotations, depth_map, pallets, boxes

def process_single_image(image_path, report_id, debug=False, upload=False):
    image_name = os.path.basename(image_path)
    image_shape = cv2.imread(image_path).shape

    # get initial predictions
    boundaries, annotations, depth_map, pallets, boxes = initialize(image_path)

    # filter and split pallet
    left_pallet, right_pallet = pallet_detector.filter_and_split_pallets(pallets, boundaries, image_shape[1])
    
    # map boxes with pallet
    left_boxes, right_boxes = box_detector.map_boxes(boxes, left_pallet, right_pallet)

    # OCR Operations -------------------------------------------------------
    # rack_dict = ocr_parser.get_rack_ids(annotations, boundaries, image_shape)

    ## TEMPORARY CHANGE: passing IMAGE_NAME as PART_NUMBER
    left_part_number = f"{image_name.split('.')[0]}_L"
    right_part_number = f"{image_name.split('.')[0]}_R"
    # ----------------------------------------------------------------------

    # CSV Operations -------------------------------------------------------
    left_part_info = csv_utils.get_all_part_info(left_part_number)
    right_part_info = csv_utils.get_all_part_info(right_part_number)
    # -----------------------------------------------------------------------

    left_boxes = box_detector.classify_boxes(boxes=left_boxes, 
                                            pallet=left_pallet, 
                                            total_layers=left_part_info["layers"], 
                                            depth_map=depth_map, 
                                            layer_wise_depth_diff=left_part_info["layer_wise_depth_diff"])

    right_boxes = box_detector.classify_boxes(boxes=right_boxes, 
                                            pallet=right_pallet, 
                                            total_layers=right_part_info["layers"], 
                                            depth_map=depth_map, 
                                            layer_wise_depth_diff=right_part_info["layer_wise_depth_diff"])

    if debug:
        visualizer.visualize(image_path, left_boxes, right_boxes, left_pallet, right_pallet, depth_map)

    front_left_boxes = left_boxes[0]
    front_right_boxes = right_boxes[0]

    left_box_dimensions = converter.get_box_dimensions(front_left_boxes, left_pallet)
    right_box_dimensions = converter.get_box_dimensions(front_right_boxes, right_pallet)

    left_structure = stack_analyzer.analyze(left_box_dimensions, left_part_info["stacking_type"])
    right_structure = stack_analyzer.analyze(right_box_dimensions, right_part_info["stacking_type"])

    left_box_stacks = box_counter.get_box_stack(front_left_boxes)
    right_box_stacks = box_counter.get_box_stack(front_right_boxes)

    pallet_status_result = pallet_status_estimator.get_status(image_path, depth_map)

    left_pallet_status = pallet_status_result['left_status']
    right_pallet_status = pallet_status_result['right_status']

    left_stack_count = stack_validator.count_stack(box_stacks=left_box_stacks, 
                                                    pallet_status=left_pallet_status, 
                                                    odd_layering=left_part_info["odd_layering"],
                                                    even_layering=left_part_info["even_layering"],
                                                    stacking_type=left_part_info["stacking_type"],
                                                    boxes_per_layer=left_part_info["boxes_per_layer"],
                                                    layers=left_part_info["layers"])
    
    right_stack_count = stack_validator.count_stack(box_stacks=right_box_stacks, 
                                                    pallet_status=right_pallet_status, 
                                                    odd_layering=right_part_info["odd_layering"],
                                                    even_layering=right_part_info["even_layering"],
                                                    stacking_type=right_part_info["stacking_type"],
                                                    boxes_per_layer=right_part_info["boxes_per_layer"],
                                                    layers=right_part_info["layers"])

    extra_left_box_count = box_counter.count_extra_boxes(stacking_type=left_part_info["stacking_type"], 
                                                        avg_box_length=left_structure['avg_box_length'], 
                                                        avg_box_width=left_structure['avg_box_width'], 
                                                        avg_box_height=left_structure['avg_box_height'], 
                                                        layers=left_part_info["layers"], 
                                                        odd_layering=left_part_info["odd_layering"],
                                                        even_layering=left_part_info["even_layering"],
                                                        box_list=left_boxes, 
                                                        stack_count=left_stack_count, 
                                                        pallet_status=left_pallet_status, 
                                                        boxes_per_layer=left_part_info["boxes_per_layer"], 
                                                        box_stacks=left_box_stacks)

    extra_right_box_count = box_counter.count_extra_boxes(stacking_type=right_part_info["stacking_type"], 
                                                        avg_box_length=right_structure['avg_box_length'], 
                                                        avg_box_width=right_structure['avg_box_width'], 
                                                        avg_box_height=right_structure['avg_box_height'], 
                                                        layers=right_part_info["layers"], 
                                                        odd_layering=right_part_info["odd_layering"],
                                                        even_layering=right_part_info["even_layering"],
                                                        box_list=right_boxes, 
                                                        stack_count=right_stack_count, 
                                                        pallet_status=right_pallet_status, 
                                                        boxes_per_layer=right_part_info["boxes_per_layer"], 
                                                        box_stacks=right_box_stacks)

    if left_part_info["boxes_per_layer"] is not None and left_stack_count is not None:
        total_left_boxes = (left_part_info["boxes_per_layer"] * left_stack_count) + extra_left_box_count
    else:
        total_left_boxes = None
    
    if right_part_info["boxes_per_layer"] is not None and right_stack_count is not None:
        total_right_boxes = (right_part_info["boxes_per_layer"] * right_stack_count) + extra_right_box_count
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
    print(f"{'Stacking Type':<20} | {format_value(left_part_info['stacking_type'], 15)} | {format_value(right_part_info['stacking_type'], 15)}")
    print(f"{'Avg Box Length':<20} | {format_value(left_structure['avg_box_length'], 15, 2)} | {format_value(right_structure['avg_box_length'], 15, 2)}")
    print(f"{'Avg Box Width':<20} | {format_value(left_structure['avg_box_width'], 15, 2)} | {format_value(right_structure['avg_box_width'], 15, 2)}")
    print(f"{'Pallet Status':<20} | {format_value(left_pallet_status, 15)} | {format_value(right_pallet_status, 15)}")
    # print(f"{'Gap':<20} | {format_value(left_gap_in_inches, 15)} | {format_value(right_gap_in_inches, 15)}")
    print(f"{'Box Count Per Layer':<20} | {format_value(left_part_info['boxes_per_layer'], 15)} | {format_value(right_part_info['boxes_per_layer'], 15)}")
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

    # print("Box Stacks:")
    # for i in range(max(len(left_box_stacks), len(right_box_stacks))):
    #     left_box_stack_len = len(left_box_stacks[i]) if i < len(left_box_stacks) else 0
    #     right_box_stack_len = len(right_box_stacks[i]) if i < len(right_box_stacks) else 0
    #     print('📦'*left_box_stack_len + '\t\t' + '📦'*right_box_stack_len)

def process_dir(dir_name, upload=False):
    report_id = 0
    if upload:
        report_id = rds_operator.create_report(14)
    for image_name in sorted(os.listdir(dir_name)):
        print("Image:",image_name)
        image_path = os.path.join(dir_name, image_name) 

        try:
            process_single_image(image_path, report_id, debug=True, upload=upload)
        except Exception as e:
            print("Error processing image:", image_name)
            print(e)

if __name__ == "__main__":
    process_dir(IMAGES_DIR, upload=UPLOAD)
