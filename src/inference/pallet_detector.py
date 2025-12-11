from ultralytics import YOLO
import cv2

class PalletDetector:
    def __init__(self):
        self.model = YOLO("models/Mahindra_ground_pallet.pt", verbose=False)

    def detect(self, image_path, boundaries):
        left_line_x, right_line_x, upper_line_y, lower_line_y = boundaries
        image = cv2.imread(image_path)
        h, w, _ = image.shape
        predictions = self.model.predict(image, verbose=False)
        boxes = predictions[0].boxes

        left_pallets = []
        right_pallets = []

        for conf, box in zip(boxes.conf, boxes.xyxy):
            if conf < 0.75:
                continue
            
            cx = (box[0] + box[2])/2
            cy = (box[1] + box[3])/2

            if (left_line_x > cx > right_line_x) or (upper_line_y > cy > lower_line_y):
                continue

            pallet_width = box[2] - box[0]
            pallet_height = box[3] - box[1]

            area = pallet_height * pallet_width
            
            if cy < h/2:
                continue

            if cx < w/2:
                left_pallets.append((box, area))
            else:
                right_pallets.append((box, area))
        
        if left_pallets:
            left_pallet = max(left_pallets, key= lambda x: x[1])
            left_pallet_box = left_pallet[0]
        else:
            left_pallet_box = None
        
        if right_pallets:
            right_pallet = max(right_pallets, key= lambda x: x[1])
            right_pallet_box = right_pallet[0]
        else:
            right_pallet_box = None
        
        return left_pallet_box, right_pallet_box