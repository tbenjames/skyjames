import os
from torch.utils.data import Dataset
from PIL import Image


class CULaneDataset(Dataset):
    def __init__(self, root_dir):
        self.samples = []

        for driver in os.listdir(root_dir):
            driver_path = os.path.join(root_dir, driver)

            if not os.path.isdir(driver_path):
                continue

            for video in os.listdir(driver_path):
                video_path = os.path.join(driver_path, video)

                if not os.path.isdir(video_path):
                    continue

                for file in os.listdir(video_path):
                    if file.endswith(".jpg"):
                        img_path = os.path.join(video_path, file)
                        label_path = img_path.replace(".jpg", ".lines.txt")

                        if os.path.exists(label_path):
                            self.samples.append((img_path, label_path))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label_path = self.samples[idx]

        image = Image.open(img_path).convert("RGB")

        with open(label_path, "r") as f:
            lines = f.readlines()

        return {
            "img_path": img_path,
            "image": image,
            "lines": lines
        }