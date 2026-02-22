import pandas as pd
from utils.logger import get_logger

logger = get_logger(__name__)

class CSVUtils:
    def __init__(self):
        self.structure_data = pd.read_csv("data/structure_data.csv", index_col="part number")
        logger.info("Structure data loaded successfully")

    def get_boxes_per_layer(self, part_number):
        try:
            return self.structure_data.loc[part_number, 'boxes per layer']
        except (KeyError, TypeError, ValueError):
            logger.error("Boxes per layer not found for part number: %s", part_number)
            return None

    def get_odd_layering(self, part_number):
        try:
            return self.structure_data.loc[part_number, 'odd layering']
        except (KeyError, TypeError, ValueError):
            logger.error("Odd layering not found for part number: %s", part_number)
            return None

    def get_even_layering(self, part_number):
        try:
            return self.structure_data.loc[part_number, 'even layering']
        except (KeyError, TypeError, ValueError):
            logger.error("Even layering not found for part number: %s", part_number)
            return None

    def get_layers(self, part_number):
        try:
            return self.structure_data.loc[part_number, 'layers']
        except (KeyError, TypeError, ValueError):
            logger.error("Layers not found for part number: %s", part_number)
            return None        

    def get_stacking_type(self, part_number):
        try:
            return self.structure_data.loc[part_number, 'stacking type']
        except (KeyError, TypeError, ValueError):
            logger.error("Stacking type not found for part number: %s", part_number)
            return None
    
    def get_layer_wise_depth_diff(self, part_number):
        try:
            depth_values = self.structure_data.loc[part_number, 'depth values']
            depth_values = map(int, depth_values.split('/'))
            return list(depth_values)
        except (KeyError, TypeError, ValueError, AttributeError):
            logger.error("Layer wise depth diff not found for part number: %s", part_number)
            return None

    def get_ratio(self, part_number):
        try:
            ratio = self.structure_data.loc[part_number, 'ratio']
            ratio = map(float, ratio.split('/'))
            return list(ratio)
        except (KeyError, TypeError, ValueError, AttributeError):
            logger.error("Ratio not found for part number: %s", part_number)
            return None
    
    def get_front_boxes(self, part_number):
        try:
            return self.structure_data.loc[part_number, 'front boxes']
        except (KeyError, TypeError, ValueError):
            logger.error("Front boxes not found for part number: %s", part_number)
            return None

    def get_all_part_info(self, part_number):
        return {
            "boxes_per_layer": self.get_boxes_per_layer(part_number),
            "odd_layering": self.get_odd_layering(part_number),
            "even_layering": self.get_even_layering(part_number),
            "layers": self.get_layers(part_number),
            "stacking_type": self.get_stacking_type(part_number),
            "layer_wise_depth_diff": self.get_layer_wise_depth_diff(part_number),
            "ratio": self.get_ratio(part_number),
            "front_boxes": self.get_front_boxes(part_number)
        }