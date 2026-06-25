"""
Metrics for evaluation
"""

import numpy as np

def compute_iou(pred_mask, true_mask):
    """Compute Intersection over Union"""
    pred = pred_mask > 0.5
    true = true_mask > 0.5
    
    intersection = np.logical_and(pred, true).sum()
    union = np.logical_or(pred, true).sum()
    
    if union == 0:
        return 0.0
    
    return intersection / union

def compute_accuracy(pred, true):
    """Compute accuracy"""
    pred = (pred > 0.5).astype(np.float32)
    true = (true > 0.5).astype(np.float32)
    
    correct = np.sum(pred == true)
    total = pred.size
    
    return correct / total

def compute_frame_consistency(lines_history):
    """Compute consistency of lines across frames"""
    if len(lines_history) < 2:
        return 1.0
    
    # Calculate variance of line positions
    positions = []
    for line in lines_history:
        if line is not None:
            positions.extend(line)
    
    if not positions:
        return 0.0
    
    positions = np.array(positions)
    variance = np.var(positions)
    
    # Normalize variance (higher variance = less consistent)
    consistency = 1.0 / (1.0 + variance / 100)
    
    return consistency

def compute_collision_risk(predicted_path, obstacle_bbox):
    """Compute collision risk with obstacle"""
    # Simplified collision risk
    if predicted_path is None or obstacle_bbox is None:
        return 0.0
    
    # Extract obstacle position (center of bbox)
    x1, y1, x2, y2 = obstacle_bbox
    obstacle_center = ((x1 + x2) / 2, (y1 + y2) / 2)
    
    # Check if obstacle is in path
    # Simple distance-based risk
    path_points = np.array(predicted_path)
    if len(path_points) == 0:
        return 0.0
    
    distances = np.linalg.norm(path_points - obstacle_center, axis=1)
    min_distance = np.min(distances)
    
    # Risk increases as distance decreases
    if min_distance < 50:  # pixels
        return 1.0 - (min_distance / 50)
    
    return 0.0
