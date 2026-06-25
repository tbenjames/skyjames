import cv2
import torch
import numpy as np
from model import LaneNet

model = LaneNet()
model.load_state_dict(torch.load("models/lane_model.pth", map_location="cpu"))
model.eval()

def predict(frame):
    img = cv2.resize(frame, (256, 128))
    img = img / 255.0
    img = torch.tensor(img, dtype=torch.float).permute(2,0,1).unsqueeze(0)

    with torch.no_grad():
        mask = model(img)[0][0].numpy()

    mask = (mask > 0.5).astype(np.uint8) * 255
    mask = cv2.resize(mask, (frame.shape[1], frame.shape[0]))

    return mask

def run_video(video_path):
    cap = cv2.VideoCapture(video_path)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        mask = predict(frame)

        overlay = frame.copy()
        overlay[mask > 0] = (0, 255, 0)

        cv2.imshow("Lane Detection", overlay)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()