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
