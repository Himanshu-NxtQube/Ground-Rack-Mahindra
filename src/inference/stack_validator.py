import cv2

class StackValidator:
    def count_stack(self, box_list, box_stacks, pallet_status, pallet, status_bbox, odd_layering, even_layering, stacking_type, boxes_per_layer, layers):
        if pallet_status is None:
            return 0
        stack_count1 = self.count_stacks_using_boxes(box_list, box_stacks, pallet_status, odd_layering, even_layering, stacking_type, boxes_per_layer, layers)
        # stack_count2 = self.count_stacks_using_pallet_status_bbox(pallet, box_list, status_bbox, pallet_status)
        return stack_count1
        
    def count_stacks_using_boxes(self, box_list, box_stacks, pallet_status, odd_layering, even_layering, stacking_type, boxes_per_layer, layers):
        if pallet_status == "full":
            return len(box_stacks)
        elif pallet_status == "partial":
            if stacking_type == "interlock":
                if (not odd_layering and not even_layering):
                    return 0
                
                top_stack = box_stacks[0]
                if len(box_stacks)%2 == 0:
                    front_layer = even_layering.split('/')[0]
                else:
                    front_layer = odd_layering.split('/')[0]
                H, V = front_layer.split('.')
                boxes = int(H[0]) + int(V[0])
                if boxes == len(top_stack):
                    return len(box_stacks)
                return len(top_stack) - 1
            elif stacking_type == "normal":
                boxes = boxes_per_layer//layers
                if boxes == len(box_stacks[0]):
                    return len(box_stacks)
                return len(box_stacks[0]) - 1
        
        return 0
        # if not box_list:
        #     return 0
        
        # top_sorted = sorted(box_list, key=lambda b: (b[1]+b[3])/2)
        # top1 = top_sorted[0]
        # top2 = top_sorted[1] if len(top_sorted) > 1 else None
        
        # rx = top1[2] - 150
        # lx = top1[0] + 150
        # cy = (top1[1]+top1[3])/2
        # count11 = sum(1 for b in box_list if b[0] <= rx <= b[2] and b[1] >= cy)
        # count12 = sum(1 for b in box_list if b[0] <= lx <= b[2] and b[1] >= cy)
        
        # if top2 == None:
        #     return max(count11, count12) + 1

        # rx = top2[2] - 150
        # lx = top2[0] + 150
        # cy = (top2[1]+top2[3])/2
        # count21 = sum(1 for b in box_list if b[0] <= rx <= b[2] and b[1] >= cy)
        # count22 = sum(1 for b in box_list if b[0] <= lx <= b[2] and b[1] >= cy)


        # top_stack_len = len(box_stacks[0])
        # # print("Top stack Len:", top_stack_len)
        # if len(box_stacks) > 1:
        #     stack_sum = 0
        #     for stack in box_stacks[1:]:
        #         stack_sum += len(stack)
        #     avg_boxes_per_stack = round(stack_sum/(len(box_stacks) - 1))
        #     # print("Avg boxes Per stack:", avg_boxes_per_stack)
        # elif len(box_stacks) == 1:
        #     avg_boxes_per_stack = len(box_stacks[0])
        # else:
        #     avg_boxes_per_stack = None
        # if avg_boxes_per_stack and top_stack_len == avg_boxes_per_stack:
        #     return max(count11, count12, count21, count22) + 1

        # if len(box_stacks) > 0:
        #     #               top_stack rightmost box's x2 - top_stack leftmost box's x1
        #     top_stack_pix_len = box_stacks[0][-1][2] - box_stacks[0][0][0]
        #     #               bottom_stack rightmost box's x2 - bottom_stack leftmost box's x1
        #     bottom_stack_pix_len = box_stacks[-1][-1][2] - box_stacks[-1][0][0]

        #     print("Top stack pix len:", top_stack_pix_len)
        #     print("Bottom stack pix len:", bottom_stack_pix_len)
        #     if abs(top_stack_pix_len - bottom_stack_pix_len) < 20:
        #         return max(count11, count12, count21, count22) + 1
        
        # for b in box_list:
        #     print(b['x1'], b['x2'])
        # print(f"count11: ",count11)
        # print(f"count12: ",count12)
        # print(f"count21: ",count21)
        # print(f"count22: ",count22)

        # if pallet_status == "partial":
        #     return max(count11, count12, count21, count22)
        # return max(count11, count12, count21, count22) + 1

    def count_stacks_using_pallet_status_bbox(self, pallet, boxes, status_bbox, pallet_status):
        if not boxes:
            return 0
        status_bbox_height = status_bbox[3] - status_bbox[1]
        status_bbox_height -= (pallet[3] - pallet[1]) if pallet is not None else 0
        avg_box_height_sum = 0
        for box in boxes:
            avg_box_height_sum += (box[3] - box[1])
        avg_box_height = avg_box_height_sum / len(boxes)
        stack_count = status_bbox_height // avg_box_height
        if pallet_status == "partial":
            return stack_count - 1
        return stack_count
