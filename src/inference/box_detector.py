from ultralytics import YOLO
import numpy as np
import cv2

class BoxDetector:
    def __init__(self):
        self.model = YOLO("models/Mahindra_g_box_17_back.pt", verbose=False)

    def filter_front_boxes(self, left_boxes, right_boxes, left_pallet, right_pallet, depth_map):
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

        filter_left_boxes = []
        filter_right_boxes = []

        back_left_boxes = []
        back_right_boxes = []

        fartest_left_boxes = []
        fartest_right_boxes = []

        for box in left_boxes:
            b_cx = int((box[0] + box[2])/2)
            b_cy = int((box[1] + box[3])/2)
            
            box_depth = depth_map[b_cy][b_cx]
            diff = np.abs(np.float64(left_pallet_depth) - np.float64(box_depth))

            if diff >= 30 and diff <= 60:
                back_left_boxes.append(box)
            elif diff > 60:
                fartest_left_boxes.append(box)
            else:
                filter_left_boxes.append(box)

        for box in right_boxes:
            b_cx = int((box[0] + box[2])/2)
            b_cy = int((box[1] + box[3])/2)
            
            box_depth = depth_map[b_cy][b_cx]
            diff = np.abs(np.float64(right_pallet_depth) - np.float64(box_depth))

            if diff >= 30 and diff <= 60:
                back_right_boxes.append(box)
            elif diff > 60:
                fartest_right_boxes.append(box)
            else:
                filter_right_boxes.append(box)

        return filter_left_boxes, filter_right_boxes, back_left_boxes, back_right_boxes, fartest_left_boxes, fartest_right_boxes

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
