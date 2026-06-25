import os

def collect_culane_samples(root_dir):
    samples = []

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
                        samples.append((img_path, label_path))

    return samples


root = "/Users/apple/Downloads/CULane"
samples = collect_culane_samples(root)

print("Total samples:", len(samples))
print("Example samples:")
print(samples[:5])