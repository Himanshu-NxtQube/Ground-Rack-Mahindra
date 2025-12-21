import pandas as pd

class BoxCounter():
    def __init__(self):
        self.pallet_len_inches = 46
        self.pallet_width_inches = 40
        self.back_layers = pd.read_csv("data/part_numbers.csv", index_col="part number")
        # self.interlock_strcture = {"horizontal": 3, "vertical": 2}
        self.interlock_strcture = pd.read_csv("data/interlock.csv", index_col="part number")

    def count_boxes_per_layer(self, box_stacks, part_number, avg_box_length, avg_box_width, stacking_type, gap_in_inches):
        if stacking_type == "interlock":
            if part_number and part_number not in self.interlock_strcture.index:
                pallet_area = self.pallet_len_inches * (self.pallet_width_inches - gap_in_inches)
                box_area = avg_box_length * avg_box_width
                
                boxes_per_layer = pallet_area // box_area
                return boxes_per_layer
            else:
                return self.interlock_strcture["horizontal"][part_number] + self.interlock_strcture["vertical"][part_number]
        elif stacking_type == "normal":
            avg_stack = sum([len(stack) for stack in box_stacks])/len(box_stacks)
            avg_stack = round(avg_stack)
            
            try:
                return avg_stack * int(self.back_layers.loc[part_number, 'layer'])
            except:
                print(f"{part_number} is not found in part_number.csv")
                return None
    
    def count_extra_boxes(self, stacking_type, avg_box_length, avg_box_width, avg_box_height, part_number, box_list, back_box_list, fartest_box_list, stack_count, pallet_status, boxes_per_layer, box_stacks):
        if stacking_type == "normal":
            try:
                layers = int(self.back_layers.loc[part_number, 'layer'])
            except:
                print(f"{part_number} is not found in part_number.csv")
                layers = 0
            if pallet_status == "partial":
                if not boxes_per_layer:
                    return 0
                # top_sorted = sorted(box_list, key=lambda b: (b[1]+b[3])/2)

                # i = -1
                # current_count = stack_count
                # while stack_count == current_count:
                #     i+=1
                #     second_top_box = top_sorted[i] if i < len(top_sorted) else None
                #     if second_top_box == None:
                #         break
                #     rx = second_top_box[2] - 150
                #     lx = second_top_box[0] + 150
                #     cy = (second_top_box[1]+second_top_box[3])/2

                #     count11 = sum(1 for b in box_list if b[0] <= lx <= b[2] and b[1] >= cy)
                #     count12 = sum(1 for b in box_list if b[0] <= rx <= b[2] and b[1] >= cy)
                #     current_count = max(count11, count12)
                # return i + boxes_per_layer//2
                front_boxes = len(box_stacks[0])*layers if len(box_stacks) > 0 and len(box_stacks) == stack_count + 1 else 0
                back_boxes = max(len(back_box_list)*(layers - 1), 0)
                fartest_boxes = max(len(fartest_box_list)*(layers - 2), 0)
                return front_boxes + back_boxes + fartest_boxes

        elif stacking_type == "interlock":
            if pallet_status == "partial":
                if not boxes_per_layer:
                    return 0
                # top_sorted = sorted(box_list, key=lambda b: (b[1]+b[3])/2)

                # i = -1
                # current_count = stack_count
                # front_boxes_list = []
                # while stack_count == current_count:
                #     i+=1
                #     second_top_box = top_sorted[i] if i < len(top_sorted) else None
                #     if second_top_box == None:
                #         break
                #     rx = second_top_box[2] - 150
                #     lx = second_top_box[0] + 150
                #     cy = (second_top_box[1]+second_top_box[3])/2

                #     count11 = sum(1 for b in box_list if b[0] <= lx <= b[2] and b[1] >= cy)
                #     count12 = sum(1 for b in box_list if b[0] <= rx <= b[2] and b[1] >= cy)
                #     current_count = max(count11, count12)
                #     if stack_count == current_count:
                #       front_boxes_list.append(second_top_box)
                # return i + boxes_per_layer//2
                front_boxes_list = box_stacks[0] if len(box_stacks) > 0 and len(box_stacks) == stack_count + 1 else []
                if part_number and part_number not in self.interlock_strcture.index:
                    most_matching_record = min(
                        self.interlock_strcture[['box_length', 'box_width', 'box_height', 'horizontal', 'vertical']].values,
                        key=lambda x: (
                            abs(x[0] - avg_box_length) + 
                            abs(x[1] - avg_box_width) + 
                            abs(x[2] - avg_box_height)
                        )
                    ) if len(self.interlock_strcture) > 0 else None
                    
                    if most_matching_record:
                        most_matching_horizontal = most_matching_record[3]
                        most_matching_vertical = most_matching_record[4]
                    else:
                        most_matching_horizontal = 0
                        most_matching_vertical = 0
                else:
                    most_matching_horizontal = self.interlock_strcture["horizontal"][part_number]
                    most_matching_vertical = self.interlock_strcture["vertical"][part_number]

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
                
                print("front horizontal boxes", len(front_horizontal_boxes))
                print("front vertical boxes", len(front_vertical_boxes))
                print("back horizontal boxes", len(back_horizontal_boxes))
                print("back vertical boxes", len(back_vertical_boxes))
                print("fartest horizontal boxes", len(fartest_horizontal_boxes))
                print("fartest vertical boxes", len(fartest_vertical_boxes))

                total_extra_boxes += len(front_horizontal_boxes) * most_matching_horizontal
                total_extra_boxes += len(front_vertical_boxes) * most_matching_vertical
                total_extra_boxes += len(back_horizontal_boxes) * max(most_matching_horizontal - 1, 0)
                total_extra_boxes += len(back_vertical_boxes) * max(most_matching_vertical - 1, 0)
                total_extra_boxes += len(fartest_horizontal_boxes) * max(most_matching_horizontal - 2, 0)
                total_extra_boxes += len(fartest_vertical_boxes) * max(most_matching_vertical - 2, 0)

                return total_extra_boxes
            
        return 0
    
    def get_box_stack(self, boxes):
        if not boxes:
            return []
        boxes_per_stack_sum = 0
        sorted_boxes = sorted(boxes, key=lambda x: (x[1]+x[3])/2)
        box_stacks = []
        last_y = None
        for box in sorted_boxes:
            center_y = (box[1] + box[3])/2 
            if not last_y:
                last_y = center_y
                box_stacks.append([box])
                continue
            if abs(last_y - center_y) < 75:
                box_stacks[-1].append(box)
            else:
                box_stacks.append([box])
            last_y = center_y
        
        # [print(stack) for stack in box_stacks]
        # avg_stack = sum([len(stack) for stack in box_stacks])/len(box_stacks)
        # print(avg_stack)
        # return round(avg_stack)

        return box_stacks
