import cv2
class Visualizer():
    def __init__(self):
        pass
    
    def visualize_box_dimensions(self, image_path, side, boxes, box_dimensions, pallet, depth_map):
        image = cv2.imread(image_path)
        for box, dimension in zip(boxes, box_dimensions):
            cv2.rectangle(image, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 255, 0), 2)
            bcx = (box[0] + box[2])/2
            bcy = (box[1] + box[3])/2
            cv2.putText(image, f"{depth_map[int(bcy)][int(bcx)]}", (int(bcx), int(bcy)), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 3)

            pcx = (pallet[0] + pallet[2])/2
            pcy = (pallet[1] + pallet[3])/2
            cv2.putText(image, f"{depth_map[int(pcy)][int(pcx)]}", (int(pcx), int(pcy)), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 3)

            # cv2.putText(image, f"{dimension[0]:.2f}x{dimension[1]:.2f}", (int(box[0]), int(box[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 3)  
            cv2.rectangle(image, (int(pallet[0]), int(pallet[1])), (int(pallet[2]), int(pallet[3])), (0, 255, 0), 2)
            cv2.imwrite("output/visualized/" + image_path.split("/")[-1].split(".")[0] + "_" + side + ".jpg", image)
            
            
        
