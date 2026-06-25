import cv2
import torch
import numpy as np

from src.model import LaneNet

MODEL_PATH = "models/best_lane_model.pth"

device = torch.device("cpu")

# Load model
model = LaneNet().to(device)
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.eval()


def predict_image(image_path):
    image = cv2.imread(image_path)

    original = image.copy()

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.resize(image, (256, 128))

    image = image / 255.0

    image = torch.tensor(
        image,
        dtype=torch.float32
    ).permute(2, 0, 1)

    image = image.unsqueeze(0)

    with torch.no_grad():
        output = model(image)

    mask = output.squeeze().cpu().numpy()

    mask = (mask > 0.5).astype(np.uint8) * 255

    cv2.imshow("Original", original)
    cv2.imshow("Predicted Mask", mask)

    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    predict_image(
        "/Users/apple/Downloads/CULane/driver_23_30frame/05151649_0422.MP4/00000.jpg"
    )