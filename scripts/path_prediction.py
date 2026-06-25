import numpy as np
def predict_path(left_line, right_line):
    if left_line is None or right_line is None:
        return None
    # Calculate center of lane
    center = ((left_line[0] + right_line[0]) // 2, 
              (left_line[1] + right_line[1]) // 2)
    # Predict next points
    return center
