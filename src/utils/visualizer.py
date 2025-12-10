import cv2
class Visualizer():
    def __init__(self):
        pass
    
    def visualize_box_dimensions(self, image_path, side, boxes, box_dimensions):
        image = cv2.imread(image_path)
        for box, dimension in zip(boxes, box_dimensions):
            cv2.rectangle(image, (int(box[0]), int(box[1])), (int(box[2]), int(box[3])), (0, 255, 0), 2)
            cv2.putText(image, f"{dimension[0]:.2f}x{dimension[1]:.2f}", (int(box[0]), int(box[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 3)  
            cv2.imwrite("output/visualized/" + image_path.split("/")[-1].split(".")[0] + "_" + side + ".jpg", image)
            
            
        