import numpy as np
import cv2


def generate_lane_mask(image_shape, lines):
    h, w = image_shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)

    for line in lines:
        coords = list(map(float, line.strip().split()))

        if len(coords) < 4:
            continue

        points = []

        for i in range(0, len(coords), 2):
            x, y = coords[i], coords[i + 1]

            if x >= 0 and y >= 0:
                points.append((int(x), int(y)))

        for i in range(len(points) - 1):
            cv2.line(mask, points[i], points[i + 1], 255, 2)

    return mask