import os
import sys
import cv2
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from inference.box_detector import BoxDetector
from inference.pallet_detector import PalletDetector
from inference.boundary_detection import BoundaryDetector

box_detector = BoxDetector()
pallet_detector = PalletDetector()
boundary_detector = BoundaryDetector()

images_dir ='/mnt/productive/Work/Marico Inventory code/images/test images'


def initialize(image_path):
    # These are independent tasks
    boundaries = boundary_detector.get_boundaries(image_path)
    pallets = pallet_detector.detect(image_path)
    boxes = box_detector.detect(image_path)
    return boundaries, pallets, boxes

def visualize_box_dimensions(image_path, left_boxes, right_boxes, left_sorted, right_sorted):
    image = cv2.imread(image_path)

    for i, box in enumerate(left_boxes):
        cv2.rectangle(image, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 255, 0), 2)
        bcx = (int(box[0]) + int(box[2]))/2
        bcy = (int(box[1]) + int(box[3]))/2
        cv2.putText(image, f"{i}", (int(box[0]+10), int(box[1]+35)), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)
        cv2.putText(image, f"{left_sorted[i][4]:.2f}", (int(bcx), int(bcy)), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 3)

    for i, box in enumerate(right_boxes):
        cv2.rectangle(image, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 255, 0), 2)
        bcx = (int(box[0]) + int(box[2]))/2
        bcy = (int(box[1]) + int(box[3]))/2
        cv2.putText(image, f"{i}", (int(box[0]+10), int(box[1]+35)), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)
        cv2.putText(image, f"{right_sorted[i][4]:.2f}", (int(bcx) - 35, int(bcy)), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 3)
    cv2.imwrite("output/visualized/" + image_path.split("/")[-1], image)
        

def process_single_image(image_path):
    boundaries, pallets, boxes = initialize(image_path)
    left_pallet, right_pallet = pallet_detector.filter_and_split_pallets(pallets, boundaries, cv2.imread(image_path).shape[1])
    left_boxes, right_boxes = box_detector.map_boxes(boxes, left_pallet, right_pallet)
    # combined_boxes = left_boxes + right_boxes
    

    left_pallet_area = (int(left_pallet[2]) - int(left_pallet[0])) * (int(left_pallet[3]) - int(left_pallet[1]))
    right_pallet_area = (int(right_pallet[2]) - int(right_pallet[0])) * (int(right_pallet[3]) - int(right_pallet[1]))

    left_pallet_height = int(left_pallet[3]) - int(left_pallet[1])
    right_pallet_height = int(right_pallet[3]) - int(right_pallet[1])

    left_sorted = []
    right_sorted = []

    for i, box in enumerate(left_boxes):
        l = round(int(box[2]) - int(box[0]), 2)
        h = round(int(box[3]) - int(box[1]), 2)
        # print(f"\t\t{i}: {l} x {h} => {l/h:.2f} => {(h)/left_pallet_height*3.14:.2f}")
        left_sorted.append((i, l, h, l/h, (h)/left_pallet_height*3.14))
        # left_sorted.append((i, l, h, l/h, (l*h)/left_pallet_area))

    print("- "*30)

    for i, box in enumerate(right_boxes):
        l = round(int(box[2]) - int(box[0]), 2)
        h = round(int(box[3]) - int(box[1]), 2)
        # print(f"\t\t{i}: {l} x {h} => {l/h:.2f} => {(h)/right_pallet_height*3.14:.2f}")
        right_sorted.append((i, l, h, l/h, (h)/right_pallet_height*3.14))
        # right_sorted.append((i, l, h, l/h, (l*h)/right_pallet_area))

    # left_sorted.sort(key=lambda x: x[4])
    # right_sorted.sort(key=lambda x: x[4])

    for box in left_sorted:
        print(f"\t\t{box[0]}: {box[1]} x {box[2]} => {box[3]:.2f} => {box[4]:.2f}") 

    print("- "*30)

    for box in right_sorted:
        print(f"\t\t{box[0]}: {box[1]} x {box[2]} => {box[3]:.2f} => {box[4]:.2f}")

    visualize_box_dimensions(image_path, left_boxes, right_boxes, left_sorted, right_sorted)

    

if __name__ == "__main__":
    for image in sorted(os.listdir(images_dir)):
        print("\n\nProcessing:", image)
        if image.lower().endswith(".png") or image.lower().endswith(".jpg"):           
            try:
                process_single_image(os.path.join(images_dir, image))
            except Exception as e:
                print("Error processing image:", image)
                print(e)