import pandas as pd

class CSVUtils:
    def __init__(self):
        self.structure_data = pd.read_csv("data/structure_data.csv", index_col="part number")

    def get_boxes_per_layer(self, part_number):
        try:
            return self.structure_data.loc[part_number, 'boxes per layer']
        except (KeyError, TypeError, ValueError):
            print("Boxes per layer not found for part number: ", part_number)
            return None

    def get_odd_layering(self, part_number):
        try:
            return self.structure_data.loc[part_number, 'odd layering']
        except (KeyError, TypeError, ValueError):
            print("Odd layering not found for part number: ", part_number)
            return None

    def get_even_layering(self, part_number):
        try:
            return self.structure_data.loc[part_number, 'even layering']
        except (KeyError, TypeError, ValueError):
            print("Even layering not found for part number: ", part_number)
            return None

    def get_layers(self, part_number):
        try:
            return self.structure_data.loc[part_number, 'layers']
        except (KeyError, TypeError, ValueError):
            print("Layers not found for part number: ", part_number)
            return None        

    def get_stacking_type(self, part_number):
        try:
            return self.structure_data.loc[part_number, 'stacking type']
        except (KeyError, TypeError, ValueError):
            print("Stacking type not found for part number: ", part_number)
            return None
    
    def get_layer_wise_depth_diff(self, part_number):
        try:
            depth_values = self.structure_data.loc[part_number, 'depth values']
            depth_values = map(int, depth_values.split('/'))
            return list(depth_values)
        except (KeyError, TypeError, ValueError):
            print("Layer wise depth diff not found for part number: ", part_number)
            return None
    
    def get_all_part_info(self, part_number):
        return {
            "boxes_per_layer": self.get_boxes_per_layer(part_number),
            "odd_layering": self.get_odd_layering(part_number),
            "even_layering": self.get_even_layering(part_number),
            "layers": self.get_layers(part_number),
            "stacking_type": self.get_stacking_type(part_number),
            "layer_wise_depth_diff": self.get_layer_wise_depth_diff(part_number)
        }