from ultralytics import YOLO
import cv2
from utils.logger import get_logger

logger = get_logger(__name__)

class PalletDetector:
    def __init__(self):
        self.model = YOLO("models/Marico_Pallet.pt", verbose=False)
        self.conf_threshold = 0.6
        logger.info("PalletDetector model loaded")
    
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
        try:
            image = cv2.imread(image_path)
            predictions = self.model.predict(image, verbose=False)
            return predictions[0].boxes
        except Exception:
            logger.error(f"Error in PalletDetector.detect")
            return None
    
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
        
        if left_pallet is None:
            logger.error('Left pallet is not detected!')
        
        if right_pallet is None:
            logger.error('Right pallet is not detected!')
        
        return left_pallet, right_pallet