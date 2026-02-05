import os
import sys
import cv2
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.inference.boundary_detection import BoundaryDetector
from src.inference.box_detector import BoxDetector
from src.inference.pallet_detector import PalletDetector

boundary_detector = BoundaryDetector()
box_detector = BoxDetector()
pallet_detector = PalletDetector()

images_dir = 'images/'

def visualize_box_dimensions(image_path, boxes):
    image = cv2.imread(image_path)

    for i, box in enumerate(boxes):
        cv2.rectangle(image, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 255, 0), 2)
        bcx = (box[0] + box[2])/2
        bcy = (box[1] + box[3])/2
        cv2.putText(image, f"{i}", (int(bcx), int(bcy)), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 3)
    cv2.imwrite("output/visualized/" + image_path.split("/")[-1], image)
        

def process_single_image(image_path):
    boundaries = boundary_detector.get_boundaries(image_path)
    left_pallet, right_pallet = pallet_detector.detect(image_path, boundaries)
    left_boxes, right_boxes = box_detector.detect(image_path, boundaries, left_pallet, right_pallet)
    combined_boxes = left_boxes + right_boxes
    
    visualize_box_dimensions(image_path, combined_boxes)
    # visualize_box_dimensions(image_path, right_boxes)

    for i, box in enumerate(combined_boxes):
        l = round(box[2] - box[0], 2)
        h = round(box[3] - box[1], 2)
        print(f"\t\t{i}: {l} x {h} => {l/h:.2f}")

    

if __name__ == "__main__":
    for image in sorted(os.listdir(images_dir)):
        print("\n\nProcessing:", image)
        if image.endswith(".JPG"):
            process_single_image(images_dir + image)

        
    
    