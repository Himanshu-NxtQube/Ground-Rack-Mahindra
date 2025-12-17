import pandas as pd

class BoxCounter():
    def __init__(self):
        self.pallet_len_inches = 46
        self.pallet_width_inches = 40
        self.back_layers = pd.read_csv("data/part_numbers.csv", index_col="part number")
        self.interlock_strcture = {"horizontal": 3, "vertical": 2}

    def count_boxes_per_layer(self, box_stacks, part_number, avg_box_length, avg_box_width, stacking_type, gap_in_inches):
        if stacking_type == "interlock":
            pallet_area = self.pallet_len_inches * (self.pallet_width_inches - gap_in_inches)
            box_area = avg_box_length * avg_box_width
            
            boxes_per_layer = pallet_area // box_area
            return boxes_per_layer
        elif stacking_type == "normal":
            # bottom_boxes = []
            # bottom_most_box = max(box_list, key=lambda x: x[3])
            # for box in box_list:
            #     if abs(bottom_most_box[3] - box[3]) < 75:
            #         bottom_boxes.append(box)
            # try:
            #     print("Bottom boxes:", len(bottom_boxes))
            #     return len(bottom_boxes) * int(self.back_layers.loc[part_number, 'layer'])
            # except:
            #     return None
            [print(stack) for stack in box_stacks]
            avg_stack = sum([len(stack) for stack in box_stacks])/len(box_stacks)
            avg_stack = round(avg_stack)
            
            try:
                return avg_stack * int(self.back_layers.loc[part_number, 'layer'])
            except:
                print(f"{part_number} is not found in part_number.csv")
                return None
    
    def count_extra_boxes(self, stacking_type, avg_box_length, avg_box_width, avg_box_height, part_number, box_list, back_box_list, fartest_box_list, stack_count, pallet_status, boxes_per_layer):
        if stacking_type == "normal":
            try:
                layers = int(self.back_layers.loc[part_number, 'layer'])
            except:
                print(f"{part_number} is not found in part_number.csv")
                layers = 0
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

                    count11 = sum(1 for b in box_list if b[0] <= lx <= b[2] and b[1] >= cy)
                    count12 = sum(1 for b in box_list if b[0] <= rx <= b[2] and b[1] >= cy)
                    current_count = max(count11, count12)
                # return i + boxes_per_layer//2
                front_boxes = i*layers
                back_boxes = max(len(back_box_list)*(layers - 1), 0)
                fartest_boxes = max(len(fartest_box_list), 0)
                return front_boxes + back_boxes + fartest_boxes
        elif stacking_type == "interlock":
            if pallet_status == "partial":
                if not boxes_per_layer:
                    return 0
                top_sorted = sorted(box_list, key=lambda b: (b[1]+b[3])/2)

                i = -1
                current_count = stack_count
                front_boxes_list = []
                while stack_count == current_count:
                    i+=1
                    second_top_box = top_sorted[i] if i < len(top_sorted) else None
                    if second_top_box == None:
                        break
                    rx = second_top_box[2] - 150
                    lx = second_top_box[0] + 150
                    cy = (second_top_box[1]+second_top_box[3])/2

                    count11 = sum(1 for b in box_list if b[0] <= lx <= b[2] and b[1] >= cy)
                    count12 = sum(1 for b in box_list if b[0] <= rx <= b[2] and b[1] >= cy)
                    current_count = max(count11, count12)
                    front_boxes_list.append(second_top_box)
                # return i + boxes_per_layer//2
                front_horizontal_boxes = []
                front_vertical_boxes = []

                back_horizontal_boxes = []
                back_vertical_boxes = []

                fartest_horizontal_boxes = []
                fartest_vertical_boxes = []

                total_extra_boxes = 0

                for box in front_boxes_list:
                    if abs((box[2] - box[0]) - avg_box_length) < abs((box[2] - box[0]) - avg_box_width):
                        front_horizontal_boxes.append(box)
                    else:
                        front_vertical_boxes.append(box)
                
                for box in back_box_list:
                    # normal_box_height / back_box_height -> relative height factor
                    # relative height factor * back_box_width -> width of box as if the box is at front 
                    if abs((avg_box_height / (box[3] - box[1]) * (box[2] - box[0])) - avg_box_length) < abs((avg_box_height / (box[3] - box[1]) * (box[2] - box[0])) - avg_box_width):
                        back_horizontal_boxes.append(box)
                    else:
                        back_vertical_boxes.append(box)
                
                for box in fartest_box_list:
                    if abs((avg_box_height / (box[3] - box[1]) * (box[2] - box[0])) - avg_box_length) < abs((avg_box_height / (box[3] - box[1]) * (box[2] - box[0])) - avg_box_width):
                        fartest_horizontal_boxes.append(box)
                    else:
                        fartest_vertical_boxes.append(box)

                total_extra_boxes += len(front_horizontal_boxes) * self.interlock_strcture["horizontal"]
                total_extra_boxes += len(front_vertical_boxes) * self.interlock_strcture["vertical"]
                total_extra_boxes += len(back_horizontal_boxes) * max(self.interlock_strcture["horizontal"] - 1, 0)
                total_extra_boxes += len(back_vertical_boxes) * max(self.interlock_strcture["vertical"] - 1, 0)
                total_extra_boxes += len(fartest_horizontal_boxes) * max(self.interlock_strcture["horizontal"] - 2, 0)
                total_extra_boxes += len(fartest_vertical_boxes) * max(self.interlock_strcture["vertical"] - 2, 0)

                return total_extra_boxes
            
        return 0
    
    def get_boxes_per_stack(self, boxes):
        if not boxes:
            return 0
        boxes_per_stack_sum = 0
        sorted_boxes = sorted(boxes, key=lambda x: (x[1]+x[3])/2)
        box_stacks = []
        last_y = None
        for box in sorted_boxes:
            center_y = (box[1] + box[3])/2 
            if not last_y:
                last_y = center_y
                box_stacks.append([int(center_y)])
                continue
            if abs(last_y - center_y) < 75:
                box_stacks[-1].append(int(center_y))
            else:
                box_stacks.append([int(center_y)])
            last_y = center_y
        
        # [print(stack) for stack in box_stacks]
        # avg_stack = sum([len(stack) for stack in box_stacks])/len(box_stacks)
        # print(avg_stack)
        # return round(avg_stack)

        return box_stacks
