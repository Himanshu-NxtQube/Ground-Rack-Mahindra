from ultralytics import YOLO
import numpy as np
import cv2

class BoxDetector:
    def __init__(self):
        self.model = YOLO("models/190groundbox.pt", verbose=False)
        self.conf_threshold = 0.6
        self.back_box_threshold = 90
    
    def map_boxes(self, boxes, left_pallet, right_pallet):
        left_boxes = []
        right_boxes = []
        
        for conf, box in zip(boxes.conf, boxes.xyxy):
            if conf < self.conf_threshold:
                continue
            
            cx = int((box[0] + box[2])/2)
            cy = int((box[1] + box[3])/2)
            
            left_margin = 0.1 * (left_pallet[2] - left_pallet[0])
            right_margin = 0.1 * (right_pallet[2] - right_pallet[0])
            
            if left_pallet is not None and left_pallet[0] + left_margin < cx < left_pallet[2] - left_margin:
                left_boxes.append(box)
            elif right_pallet is not None and right_pallet[0] + right_margin < cx < right_pallet[2] - right_margin:
                right_boxes.append(box)
        
        return left_boxes, right_boxes

    def classify_boxes(self, boxes, pallet, total_layers, depth_map, layer_wise_depth_diff):
        if not total_layers:
            print("No layers found! Defaulting to 2 layers.")
            total_layers = 2

        boxes_classified = [[] for _ in range(total_layers)]
        
        if not layer_wise_depth_diff:
            return boxes_classified

        if pallet is not None:
            cx = int((pallet[0] + pallet[2])/2)
            cy = int((pallet[1] + pallet[3])/2)
        else:
            print("Pallet not detected!")
            return boxes_classified


        pallet_depth = depth_map[cy][cx]

        thresholds = layer_wise_depth_diff

        front_min_depth = pallet_depth            
        for box in boxes:
            cx = int((box[0] + box[2])/2)
            cy = int((box[1] + box[3])/2)
            
            box_depth = depth_map[cy][cx]
            
            diff = int(pallet_depth) - int(box_depth)

            if diff < thresholds[0]:
                front_min_depth = min(front_min_depth, box_depth)

        for box in boxes:
            bcx = int((box[0] + box[2])/2)
            bcy = int((box[1] + box[3])/2)
            
            box_depth = depth_map[bcy][bcx]
            
            diff = int(front_min_depth) - int(box_depth)

            # to eliminate back boxes
            if pallet_depth - box_depth >= self.back_box_threshold:
                continue
            
            assigned = False
            for i, threshold in enumerate(thresholds):
                if diff < threshold:
                    boxes_classified[i].append(box)
                    assigned = True
                    break
            
            if not assigned:
                boxes_classified[-1].append(box)

        return boxes_classified

    def detect(self, image_path):
        image = cv2.imread(image_path)
        predictions = self.model.predict(image, verbose=False)
        return predictions[0].boxes

    def detect1(self, image_path, boundaries, left_pallet, right_pallet):
        left_line_x, right_line_x, upper_line_y, lower_line_y = boundaries
        image = cv2.imread(image_path)
        h, w, _ = image.shape
        predictions = self.model.predict(image, verbose=False)
        boxes = predictions[0].boxes

        left_boxes = []
        right_boxes = []

        for conf, box in zip(boxes.conf, boxes.xyxy):
            if conf < 0.6:
                continue
            
            cx = (box[0] + box[2])/2
            cy = (box[1] + box[3])/2

            if (left_line_x > cx) or (cx > right_line_x) or (upper_line_y > cy) or (cy > lower_line_y):
                continue
            
            box = [round(float(c), 2) for c in box]
        
            if left_pallet is not None and left_pallet[0] < cx < left_pallet[2]:
                left_boxes.append(box)
            elif right_pallet is not None and right_pallet[0] < cx < right_pallet[2]:
                right_boxes.append(box)
        
        return left_boxes, right_boxes
