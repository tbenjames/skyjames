from src.dataset import CULaneDataset

root = "/Users/apple/Downloads/CULane"

dataset = CULaneDataset(root)

print("Dataset size:", len(dataset))

sample = dataset[0]
print(sample["img_path"])
print(sample["lines"][:3])