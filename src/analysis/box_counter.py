import pandas as pd

class BoxCounter():
    def __init__(self):
        self.pallet_len_inches = 46
        self.pallet_width_inches = 40

    def count_boxes_per_layer(self, box_stacks, boxes_per_layer, layers,  avg_box_length, avg_box_width, stacking_type, gap_in_inches):
        if stacking_type == "interlock":
            if not boxes_per_layer:
                pallet_area = self.pallet_len_inches * (self.pallet_width_inches - gap_in_inches)
                box_area = avg_box_length * avg_box_width
                
                boxes_per_layer = pallet_area // box_area
                return boxes_per_layer
            
            return boxes_per_layer
        elif stacking_type == "normal":
            avg_stack = sum([len(stack) for stack in box_stacks])/len(box_stacks)
            avg_stack = round(avg_stack)
            
            if layers:
                return avg_stack * layers
            else:
                return 0
    
    def count_extra_boxes(self, stacking_type, avg_box_length, avg_box_width, avg_box_height, layers, layering, box_list, stack_count, pallet_status, boxes_per_layer, box_stacks):
        if stacking_type == "normal":
            if pallet_status == "partial":
                if not boxes_per_layer:
                    return 0
                
                extra_boxes = 0
                front_boxes = len(box_stacks[0])*layers if len(box_stacks) > 0 and len(box_stacks) == stack_count + 1 else 0
                for i, box_layer in enumerate(box_list[1:]):
                    extra_boxes += len(box_layer)*(layers - i - 1)
                return front_boxes + extra_boxes
            else:
                return 0

        elif stacking_type == "interlock":
            if pallet_status == "partial":
                if not boxes_per_layer:
                    return 0
                
                layering = layering.split("/")

                front_boxes_list = box_stacks[0] if len(box_stacks) > 0 and len(box_stacks) == stack_count + 1 else []

                partial_stack_boxes = [front_boxes_list]
                partial_stack_boxes.extend(box_list[1:])

                total_extra_boxes = boxes_per_layer

                for layer, box_layers in enumerate(partial_stack_boxes):
                    H, V = map(int, layering[layer].split('.'))
                    
                    partial_box_layer_found = False
                    if box_layers:
                        for box in box_layers:
                            if abs((avg_box_height / (box[3] - box[1]) * (box[2] - box[0])) - avg_box_length) < abs((avg_box_height / (box[3] - box[1]) * (box[2] - box[0])) - avg_box_width):
                                H -= 1
                            else:
                                V -= 1
                        partial_box_layer_found = True
                    total_extra_boxes -= (H + V)
                    if partial_box_layer_found:
                        break
                
                return total_extra_boxes
            
        return 0
    
    def get_box_stack(self, boxes):
        if not boxes:
            return []
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
