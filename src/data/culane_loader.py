"""
CULane Dataset Loader - Corrected for actual structure
"""

import os
import cv2
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm
import glob
from src.config import Config

class CULaneDataset(Dataset):
    """CULane dataset loader with correct path handling"""
    
    def __init__(self, config=None, split='train', max_samples=None):
        self.config = config or Config()
        self.root = self.config.CULANE_PATH
        self.split = split
        self.image_size = self.config.IMAGE_SIZE
        self.max_samples = max_samples
        
        self.image_paths = []
        self.mask_paths = []
        
        self._load_data()
        
        print(f"Loaded {len(self.image_paths)} samples from CULane {split} set")
    
    def _load_data(self):
        """Load data using the correct path structure"""
        print(f"Loading from {self.root}...")
        
        # Find all images in driver directories
        # Pattern: driver_*/**/*.jpg
        image_pattern = os.path.join(self.root, "driver_*", "**", "*.jpg")
        all_images = glob.glob(image_pattern, recursive=True)
        
        print(f"Found {len(all_images)} total images")
        
        # Limit samples if specified
        if self.max_samples:
            all_images = all_images[:self.max_samples]
        
        # For each image, find the corresponding label
        for img_path in tqdm(all_images, desc=f"Loading {self.split} set"):
            # Get relative path from root
            rel_path = os.path.relpath(img_path, self.root)
            parts = rel_path.split(os.sep)
            
            if len(parts) >= 3:
                driver = parts[0]  # e.g., driver_23_30frame
                subdir = parts[1]  # e.g., 05170823_0713.MP4
                filename = parts[-1]  # e.g., 01760.jpg
                filename_png = filename.replace('.jpg', '.png')
                
                # Build label path: laneseg_label_w16/driver/subdir/filename.png
                label_path = os.path.join(self.root, 'laneseg_label_w16', driver, subdir, filename_png)
                
                # Check if label exists
                if not os.path.exists(label_path):
                    # Try without one level (sometimes labels are directly in driver folder)
                    label_path_alt = os.path.join(self.root, 'laneseg_label_w16', driver, filename_png)
                    if os.path.exists(label_path_alt):
                        label_path = label_path_alt
                    else:
                        # Try in test label directory
                        label_path_test = os.path.join(self.root, 'laneseg_label_w16_test', driver, subdir, filename_png)
                        if os.path.exists(label_path_test):
                            label_path = label_path_test
                        else:
                            # No label found, use None
                            label_path = None
                
                self.image_paths.append(img_path)
                self.mask_paths.append(label_path)
            else:
                # Skip if path doesn't match expected format
                self.image_paths.append(img_path)
                self.mask_paths.append(None)
        
        # Count how many have labels
        has_label = sum(1 for p in self.mask_paths if p is not None and os.path.exists(p))
        print(f"Images with labels: {has_label}/{len(self.image_paths)}")
    
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        mask_path = self.mask_paths[idx] if idx < len(self.mask_paths) else None
        
        # Load image
        image = cv2.imread(img_path)
        if image is None:
            return self._get_dummy_sample()
        
        # Resize image
        image = cv2.resize(image, (self.image_size[1], self.image_size[0]))
        image = image.astype(np.float32) / 255.0
        
        # Load mask
        if mask_path and os.path.exists(mask_path):
            mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
            if mask is not None:
                mask = cv2.resize(mask, (self.image_size[1], self.image_size[0]))
                mask = (mask > 0).astype(np.float32)
            else:
                mask = np.zeros((self.image_size[0], self.image_size[1]), dtype=np.float32)
        else:
            # Create mask from image edges as fallback
            mask = self._create_dummy_mask(image)
        
        # Convert to tensors
        image_tensor = torch.from_numpy(image.transpose(2, 0, 1)).float()
        mask_tensor = torch.from_numpy(mask).float().unsqueeze(0)
        
        return {
            'image': image_tensor,
            'mask': mask_tensor,
            'image_path': img_path
        }
    
    def _get_dummy_sample(self):
        h, w = self.image_size
        return {
            'image': torch.zeros((3, h, w), dtype=torch.float32),
            'mask': torch.zeros((1, h, w), dtype=torch.float32),
            'image_path': 'dummy'
        }
    
    def _create_dummy_mask(self, image):
        """Create a dummy mask from image edges (fallback)"""
        gray = cv2.cvtColor((image * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        return (edges > 0).astype(np.float32)

def create_dataloader(config=None, split='train', batch_size=None, max_samples=None):
    """Create a DataLoader for CULane dataset"""
    config = config or Config()
    batch_size = batch_size or config.BATCH_SIZE
    
    dataset = CULaneDataset(config, split, max_samples)
    
    if len(dataset) == 0:
        print(f"Warning: No samples loaded for {split} set!")
        return None
    
    dataloader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=(split == 'train'),
        num_workers=0,
        pin_memory=False,
        drop_last=False
    )
    
    return dataloader
