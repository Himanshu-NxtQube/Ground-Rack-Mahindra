def find_gap(pallet, boxes):
    if pallet is None:
        return 0 
    pallet_width = pallet[2] - pallet[0]

    bottom_len_of_boxes = 0
    sorted_boxes = sorted(boxes, key = lambda x: (x[1]+ x[3])/2, reverse=True)
    last_y = None
    for box in sorted_boxes:
        cy = (box[1] + box[3])/2
        if (last_y is None) or (abs(last_y - cy) < 75):
            last_y = cy
            print("counted as bottom box")
            bottom_len_of_boxes += box[2] - box[0]
        else:
            break
    
    return pallet_width - bottom_len_of_boxes
