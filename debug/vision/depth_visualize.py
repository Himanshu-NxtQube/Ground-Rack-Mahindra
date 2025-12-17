import cv2
import sys
import os
import matplotlib.pyplot as plt

# Add parent directory to path to allow importing from inference
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from src.inference.depth_estimation import DepthEstimator

# Initialize with the correct model name
depth_estimator = DepthEstimator("depth_anything_v2")

image_path = "images/DJI_0019.JPG"
# Ensure the image path is correct relative to where the script is run or absolute
if not os.path.exists(image_path):
    # Try finding it relative to src if run from there
    possible_path = os.path.join("..", "images", "DJI_0017.JPG")
    if os.path.exists(possible_path):
        image_path = possible_path
    else:
        # Try finding it from utils if run from there
        possible_path = os.path.join("..", "..", "images", "DJI_0021.JPG")
        if os.path.exists(possible_path):
            image_path = possible_path

depth_map = depth_estimator.get_depth_map(image_path)
image = cv2.imread(image_path)
# Convert BGR to RGB for Matplotlib
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

def on_move(event):
    if event.inaxes:
        x, y = int(event.xdata), int(event.ydata)
        # Check bounds just in case
        if 0 <= x < depth_map.shape[1] and 0 <= y < depth_map.shape[0]:
            depth_val = depth_map[y, x]
            print(f"Depth at ({x}, {y}): {depth_val}")

fig, ax = plt.subplots()
ax.imshow(image_rgb)
ax.set_title("Depth Estimator - Move mouse to see depth")
fig.canvas.mpl_connect('motion_notify_event', on_move)

print("Move mouse over the image to see depth values. Close window to exit.")
plt.show()
