from ultralytics import YOLO
import cv2

class PalletDetector:
    def __init__(self):
        self.model = YOLO("models/new_mahindra_gpallet_12_12_25.pt", verbose=False)
        self.conf_threshold = 0.6
    
    def filter_and_split_pallets(self, pallets, boundaries, w):
        """
        pallets: list of pallets
        boundaries: left_x, right_x, top_y, bottom_y
        w: width of the image

        returns: left_pallet, right_pallet
        """
        pallets = self.filter_pallets(pallets, boundaries)
        left_pallet, right_pallet = self.split_pallets(pallets, w)
        return left_pallet, right_pallet

    def detect(self, image_path):
        image = cv2.imread(image_path)
        predictions = self.model.predict(image, verbose=False)
        return predictions[0].boxes
    
    def filter_pallets(self, pallets, boundaries):
        left_x, right_x, top_y, bottom_y = boundaries
        filtered = []

        for conf, box in zip(pallets.conf, pallets.xyxy):
            if conf < self.conf_threshold:
                continue
            
            cx = (box[0] + box[2]) / 2
            cy = (box[1] + box[3]) / 2

            if left_x < cx < right_x and top_y < cy < bottom_y:
                filtered.append(box)

        return filtered
    
    def split_pallets(self, pallets, w):
        left_pallet = None
        right_pallet = None

        # select the pallet with max area
        left_max_area = 0
        right_max_area = 0
        for box in pallets:
            cx = (box[0] + box[2])/2
            # cy = (box[1] + box[3])/2

            pallet_width = box[2] - box[0]
            pallet_height = box[3] - box[1]

            area = pallet_height * pallet_width

            if cx < w/2 and area > left_max_area:
                left_max_area = area
                left_pallet = box
            elif cx > w/2 and area > right_max_area:
                right_max_area = area
                right_pallet = box
        
        return left_pallet, right_pallet

    # def detect1(self, image_path, boundaries):
    #     left_line_x, right_line_x, upper_line_y, lower_line_y = boundaries
    #     image = cv2.imread(image_path)
    #     h, w, _ = image.shape
    #     predictions = self.model.predict(image, verbose=False)
    #     boxes = predictions[0].boxes

    #     left_pallets = []
    #     right_pallets = []

    #     for conf, box in zip(boxes.conf, boxes.xyxy):
    #         if conf < 0.75:
    #             continue
            
    #         cx = (box[0] + box[2])/2
    #         cy = (box[1] + box[3])/2

    #         if (left_line_x > cx > right_line_x) or (upper_line_y > cy > lower_line_y):
    #             continue

    #         pallet_width = box[2] - box[0]
    #         pallet_height = box[3] - box[1]

    #         area = pallet_height * pallet_width
            
    #         if cy < h/2:
    #             continue

    #         if cx < w/2:
    #             left_pallets.append((box, area))
    #         else:
    #             right_pallets.append((box, area))
        
    #     if left_pallets:
    #         left_pallet = max(left_pallets, key= lambda x: x[1])
    #         left_pallet_box = left_pallet[0]
    #     else:
    #         left_pallet_box = None
        
    #     if right_pallets:
    #         right_pallet = max(right_pallets, key= lambda x: x[1])
    #         right_pallet_box = right_pallet[0]
    #     else:
    #         right_pallet_box = None
        
    #     return left_pallet_box, right_pallet_box
