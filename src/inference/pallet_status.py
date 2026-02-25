from utils.logger import get_logger

logger = get_logger(__name__)

def get_pallet_status(box_stacks, boxes, layers, stacking_type, odd_layering, even_layering, front_boxes):
    if not layers:
        return ""
    all_empty = True
    for i in range(1,layers):
        if len(boxes[i]) > 0:
            return "partial"

    if len(box_stacks) == 0:
        return "empty"
    top_stack = box_stacks[0]
    if stacking_type == "interlock":
        if len(box_stacks)%2 == 0:
            front_layer = even_layering.split('/')[0]
        else:
            front_layer = odd_layering.split('/')[0]
        H, V = front_layer.split('.')
        boxes = int(H[0]) + int(V[0])
        if boxes == len(top_stack): 
            return "full"
        else:
            return "partial"
    elif stacking_type == "normal":
        if len(top_stack) == front_boxes:
            return "full"
        else:
            return "partial"