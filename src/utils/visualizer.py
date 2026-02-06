import cv2
class Visualizer():
    def __init__(self):
        pass

    def visualize(self, image_path, left_boxes, right_boxes, left_pallet, right_pallet, depth_map):
        image = cv2.imread(image_path)
        
        colors = [
            (0, 255, 0),     # Green
            (0, 255, 255),   # Yellow
            (0, 165, 255),   # Orange
            (0, 0, 255),      # Red
            (0, 0, 0)
        ]

        for i, box_layer in enumerate(left_boxes):
            for box in box_layer:
                cv2.rectangle(image, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), colors[i], 2)
                bcx = (box[0] + box[2])/2
                bcy = (box[1] + box[3])/2
                cv2.putText(image, f"{depth_map[int(bcy)][int(bcx)]}", (int(bcx), int(bcy)), cv2.FONT_HERSHEY_SIMPLEX, 3, colors[i], 3)
        
        for i, box_layer in enumerate(right_boxes):
            for box in box_layer:
                cv2.rectangle(image, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), colors[i], 2)
                bcx = (box[0] + box[2])/2
                bcy = (box[1] + box[3])/2
                cv2.putText(image, f"{depth_map[int(bcy)][int(bcx)]}", (int(bcx), int(bcy)), cv2.FONT_HERSHEY_SIMPLEX, 3, colors[i], 3)

        if left_pallet is not None:
            pcx = (left_pallet[0] + left_pallet[2])/2
            pcy = (left_pallet[1] + left_pallet[3])/2
            cv2.putText(image, f"{depth_map[int(pcy)][int(pcx)]}", (int(pcx), int(pcy)), cv2.FONT_HERSHEY_SIMPLEX, 3, colors[0], 3)
            cv2.rectangle(image, (int(left_pallet[0]), int(left_pallet[1])), (int(left_pallet[2]), int(left_pallet[3])), colors[0], 2)

        if right_pallet is not None:
            pcx = (right_pallet[0] + right_pallet[2])/2
            pcy = (right_pallet[1] + right_pallet[3])/2
            cv2.putText(image, f"{depth_map[int(pcy)][int(pcx)]}", (int(pcx), int(pcy)), cv2.FONT_HERSHEY_SIMPLEX, 3, colors[0], 3)
            cv2.rectangle(image, (int(right_pallet[0]), int(right_pallet[1])), (int(right_pallet[2]), int(right_pallet[3])), colors[0], 2)

        cv2.imwrite("output/visualized/" + image_path.split("/")[-1].split(".")[0] + "_visualized.jpg", image)
    
    # def visualize_box_dimensions(self, image_path, side, boxes, pallet, depth_map):
    #     image = cv2.imread(image_path)

    #     colors = [
    #         (0, 255, 0),     # Green
    #         (0, 255, 255),   # Yellow
    #         (0, 165, 255),   # Orange
    #         (0, 0, 255)      # Red
    #     ]
    #     for i, box_layer in enumerate(boxes):
    #         for box in box_layer:
    #             cv2.rectangle(image, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), colors[i], 2)
    #             bcx = (box[0] + box[2])/2
    #             bcy = (box[1] + box[3])/2
    #             cv2.putText(image, f"{depth_map[int(bcy)][int(bcx)]}", (int(bcx), int(bcy)), cv2.FONT_HERSHEY_SIMPLEX, 3, colors[i], 3)
        
    #     # for box in box_dimensions:
    #     #     cv2.rectangle(image, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 255, 255), 2)
    #     #     bcx = (box[0] + box[2])/2
    #     #     bcy = (box[1] + box[3])/2
    #     #     cv2.putText(image, f"{depth_map[int(bcy)][int(bcx)]}", (int(bcx), int(bcy)), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 255), 3)

    #     # for box in box_dimensions:
    #     #     cv2.rectangle(image, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 0, 255), 2)
    #     #     bcx = (box[0] + box[2])/2
    #     #     bcy = (box[1] + box[3])/2
    #     #     cv2.putText(image, f"{depth_map[int(bcy)][int(bcx)]}", (int(bcx), int(bcy)), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 3)

    #     if pallet is not None:
    #         pcx = (pallet[0] + pallet[2])/2
    #         pcy = (pallet[1] + pallet[3])/2
    #         cv2.putText(image, f"{depth_map[int(pcy)][int(pcx)]}", (int(pcx), int(pcy)), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 3)
    #         # cv2.putText(image, f"{dimension[0]:.2f}x{dimension[1]:.2f}", (int(box[0]), int(box[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 3)  
    #         cv2.rectangle(image, (int(pallet[0]), int(pallet[1])), (int(pallet[2]), int(pallet[3])), (0, 255, 0), 2)

    #     cv2.imwrite("output/visualized/" + image_path.split("/")[-1].split(".")[0] + "_" + side + ".jpg", image)
        
            
        
