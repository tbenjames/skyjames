"""
Visualization utilities
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt

def visualize_lanes(image, left_line, right_line, color_left=(0, 0, 255), color_right=(255, 0, 0)):
    """Visualize lane lines on image"""
    result = np.copy(image)
    
    if left_line is not None:
        x1, y1, x2, y2 = left_line
        cv2.line(result, (x1, y1), (x2, y2), color_left, 6)
    
    if right_line is not None:
        x1, y1, x2, y2 = right_line
        cv2.line(result, (x1, y1), (x2, y2), color_right, 6)
    
    return result

def create_debug_view(original, edges, masked, result):
    """Create a debug view with multiple panels"""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    axes[0, 0].imshow(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))
    axes[0, 0].set_title('Original')
    axes[0, 0].axis('off')
    
    axes[0, 1].imshow(edges, cmap='gray')
    axes[0, 1].set_title('Canny Edges')
    axes[0, 1].axis('off')
    
    axes[1, 0].imshow(masked, cmap='gray')
    axes[1, 0].set_title('Masked Edges')
    axes[1, 0].axis('off')
    
    axes[1, 1].imshow(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
    axes[1, 1].set_title('Result')
    axes[1, 1].axis('off')
    
    plt.tight_layout()
    return fig

def overlay_metrics(frame, fps, safety_status, detections_count):
    """Overlay metrics on frame"""
    result = np.copy(frame)
    
    # FPS
    cv2.putText(result, f"FPS: {fps:.1f}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # Safety status
    color = (0, 255, 0) if safety_status else (0, 0, 255)
    status = "SAFE" if safety_status else "UNSAFE"
    cv2.putText(result, f"SAFETY: {status}", (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    
    # Detections count
    cv2.putText(result, f"Objects: {detections_count}", (10, 90), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
    
    return result
