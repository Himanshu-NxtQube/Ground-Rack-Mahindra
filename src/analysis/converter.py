class Converter():
    def __init__(self):
        self.pallet_len_inches = 46
        self.pallet_width_inches = 40
    def get_box_dimensions(self, boxes, pallet):
        if pallet is None:
            return []
        
        pallet_pixel_width = pallet[2] - pallet[0]
        self.conversion_const = self.pallet_width_inches / pallet_pixel_width

        box_dimensions = []
        for box in boxes:
            box_pixel_length = box[2] - box[0]
            box_pixel_height = box[3] - box[1]
            box_length = box_pixel_length * self.conversion_const
            box_height = box_pixel_height * self.conversion_const

            box_dimensions.append((box_length, box_height))
        
        return box_dimensions
    
    def convert_gap_in_inches(self, gap):
        return round(float(gap * self.conversion_const), 2)