from ultralytics import YOLO
import numpy as np
import cv2

class BoxDetector:
    def __init__(self):
        self.model = YOLO("models/New Ground Box model.pt", verbose=False)

        self.layer_wise_depth_diff = {  2: [30], 
                                        3: [20, 40], 
                                        4: [15, 30, 45] }

        self.front_layer_threshold = 30

    def classify_boxes(self, left_boxes, right_boxes, left_pallet, right_pallet, total_layers, depth_map):
        if left_pallet is not None:
            lp_cx = int((left_pallet[0] + left_pallet[2])/2)
            lp_cy = int((left_pallet[1] + left_pallet[3])/2)
            # lp_cy = int(left_pallet[1])
        else:
            lp_cx = 0
            lp_cy = 0

        if right_pallet is not None:
            rp_cx = int((right_pallet[0] + right_pallet[2])/2)
            rp_cy = int((right_pallet[1] + right_pallet[3])/2)
            # rp_cy = int(right_pallet[1])
        else:
            rp_cx = 0
            rp_cy = 0

        left_pallet_depth = depth_map[lp_cy][lp_cx]
        right_pallet_depth = depth_map[rp_cy][rp_cx]

        left_boxes_classified = [[] for _ in range(total_layers)]
        right_boxes_classified = [[] for _ in range(total_layers)]

        thresholds = self.layer_wise_depth_diff[total_layers]

        # for box in left_boxes:
        #     cx = int((box[0] + box[2])/2)
        #     cy = int((box[1] + box[3])/2)
            
        #     box_depth = depth_map[cy][cx]
            
        #     diff = abs(int(left_pallet_depth) - int(box_depth))
            
        #     assigned = False
        #     for i, threshold in enumerate(thresholds):
        #         if diff < threshold:
        #             left_boxes_classified[i].append(box)
        #             assigned = True
        #             break
            
        #     if not assigned:
        #         left_boxes_classified[-1].append(box)
        
        # for box in right_boxes:
        #     cx = int((box[0] + box[2])/2)
        #     cy = int((box[1] + box[3])/2)
            
        #     box_depth = depth_map[cy][cx]

        #     diff = abs(int(right_pallet_depth) - int(box_depth))
            
        #     assigned = False
        #     for i, threshold in enumerate(thresholds):
        #         if diff < threshold:
        #             right_boxes_classified[i].append(box)
        #             assigned = True
        #             break
            
        #     if not assigned:
        #         right_boxes_classified[-1].append(box)


        left_front_min_depth = float('inf')            
        for box in left_boxes:
            cx = int((box[0] + box[2])/2)
            cy = int((box[1] + box[3])/2)
            
            box_depth = depth_map[cy][cx]
            
            diff = int(left_pallet_depth) - int(box_depth)

            if diff < self.front_layer_threshold:
                left_front_min_depth = min(left_front_min_depth, box_depth)

        right_front_min_depth = float('inf')            
        for box in right_boxes:
            cx = int((box[0] + box[2])/2)
            cy = int((box[1] + box[3])/2)
            
            box_depth = depth_map[cy][cx]
            
            diff = int(right_pallet_depth) - int(box_depth)

            if diff < self.front_layer_threshold:
                right_front_min_depth = min(right_front_min_depth, box_depth)
        
        for box in left_boxes:
            cx = int((box[0] + box[2])/2)
            cy = int((box[1] + box[3])/2)
            
            box_depth = depth_map[cy][cx]
            
            diff = int(left_front_min_depth) - int(box_depth)

            assigned = False
            for i, threshold in enumerate(thresholds):
                if diff < threshold:
                    left_boxes_classified[i].append(box)
                    assigned = True
                    break
            
            if not assigned:
                left_boxes_classified[-1].append(box)

        for box in right_boxes:
            cx = int((box[0] + box[2])/2)
            cy = int((box[1] + box[3])/2)
            
            box_depth = depth_map[cy][cx]
            
            diff = int(right_front_min_depth) - int(box_depth)

            assigned = False
            for i, threshold in enumerate(thresholds):
                if diff < threshold:
                    right_boxes_classified[i].append(box)
                    assigned = True
                    break
            
            if not assigned:
                right_boxes_classified[-1].append(box)

        return left_boxes_classified, right_boxes_classified

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
