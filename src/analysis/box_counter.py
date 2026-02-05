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
            if not boxes_per_layer:
                avg_stack = sum([len(stack) for stack in box_stacks])/len(box_stacks)
                avg_stack = round(avg_stack)
                
                if layers:
                    return avg_stack * layers
                else:
                    return 0
            
            return boxes_per_layer
    
    def count_extra_boxes(self, stacking_type, avg_box_length, avg_box_width, avg_box_height, layers, odd_layering, even_layering, box_list, stack_count, pallet_status, boxes_per_layer, box_stacks):
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
                if not boxes_per_layer or ((not odd_layering or pd.isna(odd_layering)) and (not even_layering or pd.isna(even_layering))):
                    return 0
                
                if (stack_count+1)%2 == 1:
                    layering = odd_layering.split("/")
                else:
                    layering = even_layering.split("/")

                print("Layering:", layering)

                front_boxes_list = box_stacks[0] if len(box_stacks) > 0 and len(box_stacks) == stack_count + 1 else []

                partial_stack_boxes = [front_boxes_list]
                partial_stack_boxes.extend(box_list[1:])

                print("Partial Stack Boxes:", partial_stack_boxes)

                total_extra_boxes = boxes_per_layer

                # overlapping_H = 0
                overlapping_V = 0

                # previous_overlapping_H = 0
                # previous_overlapping_V = 0


                for layer, box_layers in enumerate(partial_stack_boxes):
                    H, V = layering[layer].split('.')
                    
                    if H[-1] != '*':
                        H = int(H)
                    else:
                        H = int(H[:-1])
                        # overlapping_H += 1

                    if V[-1] != '*':
                        V = int(V)
                    else:
                        V = int(V[:-1])
                        overlapping_V += 1
                    
                    partial_box_layer_found = False
                    if box_layers:
                        partial_box_layer_found = True
                        detected_H = 0
                        detected_V = 0
                        for box in box_layers:
                            if abs((avg_box_height / (box[3] - box[1]) * (box[2] - box[0])) - avg_box_length) > \
                                abs((avg_box_height / (box[3] - box[1]) * (box[2] - box[0])) - avg_box_width):
                                H -= 1
                                detected_H += 1
                                print(f"Horizontal box detected {detected_H}")
                            else:
                                V -= 1
                                detected_V += 1
                                print(f"Vertical box detected {detected_V}")
                        
                        if detected_H == 0 and detected_V == 1 and overlapping_V > 0:
                            # h0v1_overlap_case = True
                            if layer+1 < len(partial_stack_boxes):
                                next_layer = partial_stack_boxes[layer+1]

                                next_layer_H, next_layer_V = layering[layer+1].split('.')
                                if next_layer_H[-1] != '*':
                                    next_layer_H = int(next_layer_H)
                                else:
                                    next_layer_H = int(next_layer_H[:-1])
                                    # overlapping_H += 1

                                if next_layer_V[-1] != '*':
                                    next_layer_V = int(next_layer_V)
                                else:
                                    next_layer_V = int(next_layer_V[:-1])
                                    overlapping_V += 1

                                next_layer_detected_H = 0
                                next_layer_detected_V = 0
                                for box in next_layer:
                                    if abs((avg_box_height / (box[3] - box[1]) * (box[2] - box[0])) - avg_box_length) > \
                                        abs((avg_box_height / (box[3] - box[1]) * (box[2] - box[0])) - avg_box_width):
                                        next_layer_detected_H += 1
                                        print(f"Next layer horizontal box detected {next_layer_detected_H}")
                                    else:
                                        next_layer_detected_V += 1
                                        print(f"Next layer vertical box detected {next_layer_detected_V}")

                                # if (next_layer_H + next_layer_V) - (next_layer_detected_H + next_layer_detected_V) != 1:
                                total_extra_boxes -= (next_layer_H - next_layer_detected_H)
                                print(f"Removing back horizontal visible boxes {(next_layer_H - next_layer_detected_H)}")
                                    
                                
                                
                    total_extra_boxes -= H
                    total_extra_boxes -= V
                    print("Removed:", (H+V))

                    # previous_overlapping_H = overlapping_H
                    # previous_overlapping_V = overlapping_V
                    # overlapping_H = 0
                    # overlapping_V = 0

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
