import pandas as pd

class BoxCounter():
    def __init__(self):
        self.pallet_len_inches = 46
        self.pallet_width_inches = 40
        self.back_layers = pd.read_csv("data/part_numbers.csv", index_col="part number")

    def count_boxes_per_layer(self, box_list, part_number, avg_box_length, avg_box_width, stacking_type):
        if stacking_type == "interlock":
            pallet_area = self.pallet_len_inches * self.pallet_width_inches
            box_area = avg_box_length * avg_box_width
            
            boxes_per_layer = pallet_area // box_area
            return boxes_per_layer
        elif stacking_type == "normal":
            bottom_boxes = []
            bottom_most_box = max(box_list, key=lambda x: x[3])
            for box in box_list:
                if abs(bottom_most_box[3] - box[3]) < 75:
                    bottom_boxes.append(box)
            try:
                print("Bottom boxes:", len(bottom_boxes))
                return len(bottom_boxes) * int(self.back_layers.loc[part_number, 'layer'])
            except:
                return None
    
    def count_extra_boxes(self, box_list, stack_count, pallet_status, boxes_per_layer):
        if pallet_status == "partial":
            if not boxes_per_layer:
                return 0
            top_sorted = sorted(box_list, key=lambda b: (b[1]+b[3])/2)

            i = -1
            current_count = stack_count
            while stack_count == current_count:
                i+=1
                second_top_box = top_sorted[i] if i < len(top_sorted) else None
                if second_top_box == None:
                    break
                rx = second_top_box[2] - 150
                lx = second_top_box[0] + 150
                cy = (second_top_box[1]+second_top_box[3])/2
                current_count = sum(1 for b in box_list if b[0] <= rx <= b[2] and b[1] >= cy)
            return i + boxes_per_layer//2
        return 0