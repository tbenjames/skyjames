"""
Check actual CULane directory structure
"""

import os
import glob

culane_path = "/Users/apple/Downloads/CULane"

print("=" * 60)
print("Checking CULane Structure")
print("=" * 60)

# Check driver directories
driver_dirs = glob.glob(os.path.join(culane_path, "driver_*"))
print(f"\nDriver directories: {len(driver_dirs)}")
for d in driver_dirs[:3]:
    print(f"  - {os.path.basename(d)}")
    # Check subdirectories
    subdirs = glob.glob(os.path.join(d, "**", "*.MP4"), recursive=True)
    if subdirs:
        print(f"    Subdirs with .MP4: {len(subdirs)}")
        # Check images in first subdir
        if subdirs:
            images = glob.glob(os.path.join(subdirs[0], "*.jpg"))
            print(f"    Images in {os.path.basename(subdirs[0])}: {len(images)}")
            if images:
                print(f"    Sample: {os.path.basename(images[0])}")

# Check label directories
label_dirs = glob.glob(os.path.join(culane_path, "laneseg_label_*"))
print(f"\nLabel directories: {len(label_dirs)}")
for d in label_dirs:
    print(f"  - {os.path.basename(d)}")
    # Check subdirectories
    subdirs = glob.glob(os.path.join(d, "driver_*"))
    print(f"    Driver subdirs: {len(subdirs)}")
    if subdirs:
        # Check one subdir
        label_subdir = glob.glob(os.path.join(subdirs[0], "*.MP4"))
        if label_subdir:
            labels = glob.glob(os.path.join(label_subdir[0], "*.png"))
            print(f"    Labels in first subdir: {len(labels)}")
            if labels:
                print(f"    Sample label: {os.path.basename(labels[0])}")

# Test loading one image
print("\n" + "=" * 60)
print("Testing image-label matching")
print("=" * 60)

# Find one driver directory with images
for d in driver_dirs[:1]:
    images = glob.glob(os.path.join(d, "**", "*.jpg"), recursive=True)
    if images:
        test_img = images[0]
        print(f"\nTest image: {test_img}")
        print(f"  Exists: {os.path.exists(test_img)}")
        
        # Find corresponding label
        img_name = os.path.basename(test_img)
        img_dir = os.path.dirname(test_img)
        img_parent = os.path.basename(os.path.dirname(img_dir))
        driver_name = os.path.basename(os.path.dirname(os.path.dirname(test_img)))
        
        # Try different label paths
        label_paths = [
            test_img.replace('driver', 'laneseg_label_w16').replace('.jpg', '.png'),
            os.path.join(culane_path, 'laneseg_label_w16', driver_name, img_parent, img_name.replace('.jpg', '.png')),
            os.path.join(culane_path, 'laneseg_label_w16', driver_name, img_name.replace('.jpg', '.png')),
        ]
        
        for i, lp in enumerate(label_paths):
            print(f"  Label path {i+1}: {lp}")
            print(f"    Exists: {os.path.exists(lp)}")
        
        break

print("\n" + "=" * 60)
