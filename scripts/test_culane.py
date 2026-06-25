"""
Test CULane dataset loading
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.data.culane_loader import CULaneDataset, create_dataloader
import matplotlib.pyplot as plt
import numpy as np

def test_culane():
    config = Config()
    
    print("=" * 60)
    print("Testing CULane Dataset")
    print("=" * 60)
    print(f"CULane path: {config.CULANE_PATH}")
    print(f"Exists: {os.path.exists(config.CULANE_PATH)}")
    
    # Check list directory
    list_dir = os.path.join(config.CULANE_PATH, "list")
    print(f"List directory: {list_dir}")
    print(f"Exists: {os.path.exists(list_dir)}")
    
    if os.path.exists(list_dir):
        print("\nList files:")
        for f in os.listdir(list_dir):
            print(f"  - {f}")
    
    # Try loading dataset
    print("\nLoading dataset (max 10 samples)...")
    dataset = CULaneDataset(config, split='train', max_samples=10)
    
    print(f"\nDataset size: {len(dataset)}")
    
    if len(dataset) > 0:
        # Get a sample
        sample = dataset[0]
        print(f"Sample keys: {sample.keys()}")
        print(f"Image shape: {sample['image'].shape}")
        print(f"Mask shape: {sample['mask'].shape}")
        print(f"Image path: {sample['image_path']}")
        
        # Display sample
        try:
            fig, axes = plt.subplots(1, 2, figsize=(10, 5))
            
            img = sample['image'].numpy().transpose(1, 2, 0)
            mask = sample['mask'].numpy().squeeze()
            
            axes[0].imshow(img)
            axes[0].set_title('Image')
            axes[0].axis('off')
            
            axes[1].imshow(mask, cmap='gray')
            axes[1].set_title('Lane Mask')
            axes[1].axis('off')
            
            plt.tight_layout()
            plt.show()
        except Exception as e:
            print(f"Could not display image: {e}")
        
        print("\n✓ Dataset loaded successfully!")
        return True
    else:
        print("\n✗ Failed to load dataset")
        print("Possible issues:")
        print("  - Wrong CULane path")
        print("  - Missing list files")
        print("  - Wrong file structure")
        return False

if __name__ == "__main__":
    success = test_culane()
    sys.exit(0 if success else 1)
