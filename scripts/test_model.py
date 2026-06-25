"""
Test the trained lane detection model
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import torch
import numpy as np
import matplotlib.pyplot as plt
from src.perception.lane_net_cpu import OptimizedLaneDetector
from src.config import Config
from src.data.culane_loader import CULaneDataset

def test_model():
    config = Config()
    
    print("=" * 60)
    print("Testing Trained Model")
    print("=" * 60)
    
    # Check if model exists
    model_path = os.path.join(config.MODEL_DIR, 'lane_net_optimized.pth')
    if os.path.exists(model_path):
        print(f"✓ Model found: {model_path}")
        print(f"  Size: {os.path.getsize(model_path) / (1024*1024):.2f} MB")
    else:
        print(f"✗ Model not found: {model_path}")
        return
    
    # Initialize detector with trained model
    print("\nInitializing detector with trained model...")
    detector = OptimizedLaneDetector(config, model_path=model_path)
    
    # Load a sample from dataset
    print("\nLoading sample image...")
    dataset = CULaneDataset(config, split='val', max_samples=1)
    if len(dataset) == 0:
        print("No samples available")
        return
    
    sample = dataset[0]
    img = sample['image'].numpy().transpose(1, 2, 0)
    mask_gt = sample['mask'].numpy().squeeze()
    
    # Convert to BGR for processing
    img_bgr = (img * 255).astype(np.uint8)
    img_bgr = cv2.cvtColor(img_bgr, cv2.COLOR_RGB2BGR)
    
    print(f"Image shape: {img_bgr.shape}")
    
    # Process with neural network
    print("\nProcessing with neural network...")
    result, left_line, right_line = detector.process_frame(img_bgr, use_neural=True)
    
    # Process with traditional method for comparison
    print("Processing with traditional method...")
    result_trad, left_trad, right_trad = detector.process_frame(img_bgr, use_neural=False)
    
    # Display results
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    # Original
    axes[0, 0].imshow(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
    axes[0, 0].set_title('Original')
    axes[0, 0].axis('off')
    
    # Ground Truth
    axes[0, 1].imshow(mask_gt, cmap='gray')
    axes[0, 1].set_title('Ground Truth Mask')
    axes[0, 1].axis('off')
    
    # Neural Network Result
    axes[0, 2].imshow(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
    axes[0, 2].set_title(f'Neural Network\nLeft: {left_line is not None}, Right: {right_line is not None}')
    axes[0, 2].axis('off')
    
    # Traditional Result
    axes[1, 0].imshow(cv2.cvtColor(result_trad, cv2.COLOR_BGR2RGB))
    axes[1, 0].set_title(f'Traditional\nLeft: {left_trad is not None}, Right: {right_trad is not None}')
    axes[1, 0].axis('off')
    
    # Combined
    combined = cv2.addWeighted(result, 0.5, result_trad, 0.5, 0)
    axes[1, 1].imshow(cv2.cvtColor(combined, cv2.COLOR_BGR2RGB))
    axes[1, 1].set_title('Combined (NN + Traditional)')
    axes[1, 1].axis('off')
    
    # Metrics
    axes[1, 2].axis('off')
    axes[1, 2].text(0.1, 0.3, f'Model: {os.path.basename(model_path)}', fontsize=10)
    axes[1, 2].text(0.1, 0.5, f'Left line: {left_line}', fontsize=8)
    axes[1, 2].text(0.1, 0.7, f'Right line: {right_line}', fontsize=8)
    
    plt.tight_layout()
    plt.show()
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)

if __name__ == "__main__":
    test_model()
