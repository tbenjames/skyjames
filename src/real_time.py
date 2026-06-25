import torch
import cv2
import numpy as np

from src.model import LaneNet


# ======================
# LOAD MODEL
# ======================
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

model = LaneNet().to(DEVICE)
model.load_state_dict(torch.load("lanenet_best.pth", map_location=DEVICE))
model.eval()


# ======================
# PREPROCESS FRAME
# ======================
def preprocess(frame):
    frame = cv2.resize(frame, (256, 256))
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    tensor = torch.from_numpy(frame_rgb).permute(2, 0, 1).float() / 255.0
    return tensor.unsqueeze(0).to(DEVICE)


# ======================
# POSTPROCESS MASK
# ======================
def postprocess(mask):
    mask = torch.sigmoid(mask)[0][0].detach().cpu().numpy()
    mask = (mask > 0.5).astype(np.uint8) * 255
    mask = cv2.resize(mask, (frame_width, frame_height))
    return mask


# ======================
# OVERLAY FUNCTION
# ======================
def overlay_lane(frame, mask):
    color_mask = np.zeros_like(frame)
    color_mask[:, :, 1] = mask  # GREEN lanes

    return cv2.addWeighted(frame, 1.0, color_mask, 0.5, 0)


# ======================
# VIDEO SOURCE
# ======================
video_path = "/Users/apple/Downloads/CULane/demo.mp4"  # change if needed
cap = cv2.VideoCapture(video_path)  # or 0 for webcam


frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))


# ======================
# REAL-TIME LOOP
# ======================
print("Starting real-time lane detection...")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    input_tensor = preprocess(frame)

    with torch.no_grad():
        output = model(input_tensor)

    mask = postprocess(output)

    result = overlay_lane(frame, mask)

    cv2.imshow("Lane Detection", result)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()