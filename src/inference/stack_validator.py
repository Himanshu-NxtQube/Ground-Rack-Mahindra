import cv2

class StackValidator:
    def count_stack(self, box_list, pallet_status, pallet, status_bbox):
        if pallet_status is None:
            return 0
        stack_count1 = self.count_stacks_using_boxes(box_list, pallet_status)
        stack_count2 = self.count_stacks_using_pallet_status_bbox(pallet, box_list, status_bbox, pallet_status)

        print("Stack count1:", stack_count1)
        print("Stack count2:", stack_count2)
        return max(stack_count1, stack_count2)
        
    def count_stacks_using_boxes(self, box_list, pallet_status):
        if not box_list:
            return 0
        
        top_sorted = sorted(box_list, key=lambda b: (b[1]+b[3])/2)
        top1 = top_sorted[0]
        top2 = top_sorted[1] if len(top_sorted) > 1 else None
        
        rx = top1[2] - 150
        lx = top1[0] + 150
        cy = (top1[1]+top1[3])/2
        count11 = sum(1 for b in box_list if b[0] <= rx <= b[2] and b[1] >= cy)
        count12 = sum(1 for b in box_list if b[0] <= lx <= b[2] and b[1] >= cy)
        
        if top2 == None:
            return max(count11, count12) + 1

        rx = top2[2] - 150
        lx = top2[0] + 150
        cy = (top2[1]+top2[3])/2
        count21 = sum(1 for b in box_list if b[0] <= rx <= b[2] and b[1] >= cy)
        count22 = sum(1 for b in box_list if b[0] <= lx <= b[2] and b[1] >= cy)



        # for b in box_list:
        #     print(b['x1'], b['x2'])
        # print(f"count11: ",count11)
        # print(f"count12: ",count12)
        # print(f"count21: ",count21)
        # print(f"count22: ",count22)
        if pallet_status == "partial":
            return max(count11, count12, count21, count22)
        return max(count11, count12, count21, count22) + 1

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
