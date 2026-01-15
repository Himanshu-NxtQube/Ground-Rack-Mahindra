import pandas as pd

class CSVUtils:
    def __init__(self):
        self.structure_data = pd.read_csv("data/structure_data.csv", index_col="part number")

    def get_boxes_per_layer(self, part_number):
        try:
            return self.structure_data.loc[part_number, 'boxes per layer']
        except KeyError:
            print("Boxes per layer not found for part number: ", part_number)
            return None

    def get_layering(self, part_number):
        try:
            return self.structure_data.loc[part_number, 'layering']
        except KeyError:
            print("Layering not found for part number: ", part_number)
            return None

    def get_layers(self, part_number):
        try:
            return self.structure_data.loc[part_number, 'layers']
        except KeyError:
            print("Layers not found for part number: ", part_number)
            return None        
