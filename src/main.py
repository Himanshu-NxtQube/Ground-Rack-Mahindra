import os
import cv2
from dotenv import load_dotenv
from analysis.box_counter import BoxCounter 
from inference.box_detector import BoxDetector
from inference.pallet_detector import PalletDetector
from inference.depth_estimation import DepthEstimator
from inference.stack_validator import count_stack
from inference.pallet_status import get_pallet_status
from inference.boundary_detection import BoundaryDetector
from inference.ocr_parser import OCRParser
from inference.google_ocr import OCRClient
from utils.csv_utils import CSVUtils
from utils.rds_operator import RDSOperator
from utils.logger import setup_logging, get_logger
from utils.visualizer import visualize

cv2.setLogLevel(2)
load_dotenv()

setup_logging(os.getenv("environment"))
logger = get_logger(__name__)

box_detector = BoxDetector()
box_counter = BoxCounter()
pallet_detector = PalletDetector()
rds_operator = RDSOperator()
ocr_client = OCRClient()
depth_estimator = DepthEstimator("depth_anything_v2")
ocr_parser = OCRParser()
boundary_detector = BoundaryDetector()
csv_utils = CSVUtils()
IMAGES_DIR = "images/"
UPLOAD = False

def initialize(image_path):
    # These are independent tasks
    boundaries = boundary_detector.get_boundaries(image_path)
    annotations = ocr_client.get_annotations(image_path)
    # annotations = 0
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
    # rack_dict = ocr_parser.get_rack_ids(annotations, boundaries, image_path)

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
        visualize(image_path, left_boxes, right_boxes, left_pallet, right_pallet, depth_map)

    front_left_boxes = left_boxes[0]
    front_right_boxes = right_boxes[0]

    # left_box_dimensions = converter.get_box_dimensions(front_left_boxes, left_pallet)
    # right_box_dimensions = converter.get_box_dimensions(front_right_boxes, right_pallet)

    # left_structure = stack_analyzer.analyze(left_box_dimensions, left_part_info["stacking_type"])
    # right_structure = stack_analyzer.analyze(right_box_dimensions, right_part_info["stacking_type"])

    left_box_stacks = box_counter.get_box_stack(front_left_boxes)
    right_box_stacks = box_counter.get_box_stack(front_right_boxes)

    # pallet_status_result = pallet_status_estimator.get_status(image_path, depth_map)

    # left_pallet_status = pallet_status_result['left_status']
    # right_pallet_status = pallet_status_result['right_status']
    left_pallet_status = get_pallet_status(left_box_stacks, left_boxes, left_part_info["layers"], left_part_info["stacking_type"], left_part_info["odd_layering"], left_part_info["even_layering"], left_part_info["front_boxes"])
    right_pallet_status = get_pallet_status(right_box_stacks, right_boxes, right_part_info["layers"], right_part_info["stacking_type"], right_part_info["odd_layering"], right_part_info["even_layering"], right_part_info["front_boxes"])

    left_stack_count = count_stack(box_stacks=left_box_stacks, 
                                                    pallet_status=left_pallet_status, 
                                                    odd_layering=left_part_info["odd_layering"],
                                                    even_layering=left_part_info["even_layering"],
                                                    stacking_type=left_part_info["stacking_type"],
                                                    boxes_per_layer=left_part_info["boxes_per_layer"],
                                                    layers=left_part_info["layers"])
    
    right_stack_count = count_stack(box_stacks=right_box_stacks, 
                                                    pallet_status=right_pallet_status, 
                                                    odd_layering=right_part_info["odd_layering"],
                                                    even_layering=right_part_info["even_layering"],
                                                    stacking_type=right_part_info["stacking_type"],
                                                    boxes_per_layer=right_part_info["boxes_per_layer"],
                                                    layers=right_part_info["layers"])

    extra_left_box_count = box_counter.count_extra_boxes(stacking_type=left_part_info["stacking_type"], 
                                                        ratio=left_part_info["ratio"], 
                                                        layers=left_part_info["layers"], 
                                                        odd_layering=left_part_info["odd_layering"],
                                                        even_layering=left_part_info["even_layering"],
                                                        box_list=left_boxes, 
                                                        stack_count=left_stack_count, 
                                                        pallet_status=left_pallet_status, 
                                                        boxes_per_layer=left_part_info["boxes_per_layer"], 
                                                        box_stacks=left_box_stacks)

    extra_right_box_count = box_counter.count_extra_boxes(stacking_type=right_part_info["stacking_type"], 
                                                        ratio=right_part_info["ratio"], 
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
    print(f"{'Pallet Status':<20} | {format_value(left_pallet_status, 15)} | {format_value(right_pallet_status, 15)}")
    # print(f"{'Gap':<20} | {format_value(left_gap_in_inches, 15)} | {format_value(right_gap_in_inches, 15)}")
    print(f"{'Box Count Per Layer':<20} | {format_value(left_part_info['boxes_per_layer'], 15)} | {format_value(right_part_info['boxes_per_layer'], 15)}")
    print(f"{'Stack Count':<20} | {format_value(left_stack_count, 15)} | {format_value(right_stack_count, 15)}")
    print(f"{'Extra Boxes':<20} | {format_value(extra_left_box_count, 15)} | {format_value(extra_right_box_count, 15)}")
    print(f"{'Total Boxes':<20} | {format_value(total_left_boxes, 15)} | {format_value(total_right_boxes, 15)}")
    print("\n")

    if upload:
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
        logger.debug("Image: %s", image_name)
        print("Image:", image_name)
        image_path = os.path.join(dir_name, image_name) 

        # try:
        process_single_image(image_path, report_id, debug=True, upload=upload)
        # except Exception as e:
            # print("Error processing image:", image_name)
            # print(e)

if __name__ == "__main__":
    process_dir(IMAGES_DIR, upload=UPLOAD)
