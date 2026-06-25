import cv2
from src.dataset import CULaneDataset
from src.mask_generator import generate_lane_mask

root = "/Users/apple/Downloads/CULane"

dataset = CULaneDataset(root)

sample = dataset[0]

image = cv2.imread(sample["img_path"])
mask = generate_lane_mask(image.shape, sample["lines"])

cv2.imwrite("mask_test.png", mask)

print("Saved mask_test.png")