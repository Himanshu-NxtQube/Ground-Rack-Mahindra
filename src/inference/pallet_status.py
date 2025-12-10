import cv2
from ultralytics import YOLO


class PalletStatus:
    def __init__(self):
        self.pallet_status_estimator = YOLO("./models/new pallet status model.pt")

    def get_status(self, img_dims, depth_map):
        center_w, center_h = img_dims[0]//2, img_dims[1]//2

        # Apply plasma colormap
        colored_depth = cv2.applyColorMap(depth_map, cv2.COLORMAP_PLASMA)

        results = self.pallet_status_estimator.predict(colored_depth, verbose=False)
        class_names = self.pallet_status_estimator.names

        left_boxes = []
        right_boxes = []

        for box in results[0].boxes:  # xyxy format: [x1, y1, x2, y2]
            # print(box.xyxy)
            x1, y1, x2, y2 = box.xyxy[0]
            cv2.rectangle(colored_depth, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 4)
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            # Filter out within ROI

            class_id = int(box.cls[0])            
            class_name = class_names[class_id]

            if cx < center_w:
                left_boxes.append([cx, class_name, (x1, y1, x2, y2)])
            else:
                right_boxes.append([cx, class_name, (x1, y1, x2, y2)])
        cv2.imwrite("output/visualized/pallet_status.png", colored_depth)

        left_box_result = None
        right_box_result = None

        left_bbox = None
        right_bbox = None

        if left_boxes:
            left_box_result = min(left_boxes,key=lambda x:x[0])[1]
            left_bbox = min(left_boxes,key=lambda x:x[0])[2]
        if right_boxes:
            right_box_result = max(right_boxes,key=lambda x:x[0])[1]
            right_bbox = max(right_boxes,key=lambda x:x[0])[2]

        # return left_box_result, right_box_result
        return {"left_status": left_box_result, "right_status": right_box_result,
                "left_bbox": left_bbox,           "right_bbox": right_bbox}

