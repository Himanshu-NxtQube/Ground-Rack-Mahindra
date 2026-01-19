from ultralytics import YOLO
import numpy as np
import cv2

class BoxDetector:
    def __init__(self):
        self.model = YOLO("models/Ground Box model.pt", verbose=False)

        self.layer_wise_depth_diff = {  2: [30], 
                                        3: [30, 70], 
                                        4: [15, 30, 45] }

        self.front_layer_threshold = 30

    def classify_boxes(self, boxes, pallet, total_layers, depth_map):
        if not total_layers:
            print("No layers found! Defaulting to 2 layers.")
            total_layers = 2
            
        boxes_classified = [[] for _ in range(total_layers)]
        if pallet is not None:
            cx = int((pallet[0] + pallet[2])/2)
            cy = int((pallet[1] + pallet[3])/2)
        else:
            print("Pallet not detected!")
            return boxes_classified


        pallet_depth = depth_map[cy][cx]

        thresholds = self.layer_wise_depth_diff[total_layers]

        front_min_depth = pallet_depth            
        for box in boxes:
            cx = int((box[0] + box[2])/2)
            cy = int((box[1] + box[3])/2)
            
            box_depth = depth_map[cy][cx]
            
            diff = int(pallet_depth) - int(box_depth)

            if diff < self.front_layer_threshold:
                front_min_depth = min(front_min_depth, box_depth)

        for box in boxes:
            bcx = int((box[0] + box[2])/2)
            bcy = int((box[1] + box[3])/2)
            
            box_depth = depth_map[bcy][bcx]
            
            diff = int(front_min_depth) - int(box_depth)
            
            assigned = False
            for i, threshold in enumerate(thresholds):
                if diff < threshold:
                    boxes_classified[i].append(box)
                    assigned = True
                    break
            
            if not assigned:
                boxes_classified[-1].append(box)

        return boxes_classified

    def detect(self, image_path, boundaries, left_pallet, right_pallet):
        left_line_x, right_line_x, upper_line_y, lower_line_y = boundaries
        image = cv2.imread(image_path)
        h, w, _ = image.shape
        predictions = self.model.predict(image, verbose=False)
        boxes = predictions[0].boxes

        left_boxes = []
        right_boxes = []

        for conf, box in zip(boxes.conf, boxes.xyxy):
            if conf < 0.8:
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
