"""
Script to test lane detection on a single image
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import matplotlib.pyplot as plt
from src.lane_detector import LaneDetector
from src.utils import ensure_directory, get_timestamp

def main():
    # Get image path
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = "data/test/test_image.jpg"
    
    if not os.path.exists(image_path):
        print(f"Error: Image not found: {image_path}")
        print("Usage: python process_image.py <image_path>")
        return
    
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not load image: {image_path}")
        return
    
    # Initialize detector
    detector = LaneDetector()
    detector.frame_height, detector.frame_width = img.shape[:2]
    
    # Process image with debug visualization
    result, edges, masked = detector.process_frame(img, draw_debug=True)
    
    # Create output directory
    output_dir = "data/output"
    ensure_directory(output_dir)
    
    # Save result
    timestamp = get_timestamp()
    output_path = f"{output_dir}/image_result_{timestamp}.jpg"
    cv2.imwrite(output_path, result)
    print(f"Result saved to: {output_path}")
    
    # Display results
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    axes[0, 0].imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    axes[0, 0].set_title('Original')
    axes[0, 0].axis('off')
    
    axes[0, 1].imshow(edges, cmap='gray')
    axes[0, 1].set_title('Edges')
    axes[0, 1].axis('off')
    
    axes[1, 0].imshow(masked, cmap='gray')
    axes[1, 0].set_title('Masked')
    axes[1, 0].axis('off')
    
    axes[1, 1].imshow(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
    axes[1, 1].set_title('Result')
    axes[1, 1].axis('off')
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
