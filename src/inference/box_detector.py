from ultralytics import YOLO
import cv2

class BoxDetector:
    def __init__(self):
        self.model = YOLO("models/mahindra_box_model.pt", verbose=False)

    def detect(self, image_path, boundaries ):
        left_line_x, right_line_x, upper_line_y, lower_line_y = boundaries
        image = cv2.imread(image_path)
        h, w, _ = image.shape
        predictions = self.model.predict(image, verbose=False)
        boxes = predictions[0].boxes

        left_boxes = []
        right_boxes = []

        for conf, box in zip(boxes.conf, boxes.xyxy):
            if conf < 0.75:
                continue
            
            cx = (box[0] + box[2])/2
            cy = (box[1] + box[3])/2

            if (left_line_x > cx) or (cx > right_line_x) or (upper_line_y > cy) or (cy > lower_line_y):
                continue

            if cx < w/2:
                left_boxes.append(box)
            else:
                right_boxes.append(box)
        
        return left_boxes, right_boxes