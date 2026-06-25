"""
Debug CULane dataset structure
"""

import os
import glob

culane_path = "/Users/apple/Downloads/CULane"

print("=" * 60)
print("Debugging CULane Dataset")
print("=" * 60)
print(f"Path: {culane_path}")
print(f"Exists: {os.path.exists(culane_path)}")

if os.path.exists(culane_path):
    print("\nContents:")
    for item in os.listdir(culane_path):
        full_path = os.path.join(culane_path, item)
        if os.path.isdir(full_path):
            print(f"  📁 {item}/")
        else:
            print(f"  📄 {item}")
    
    # Check for driver directories
    print("\nDriver directories:")
    driver_dirs = glob.glob(os.path.join(culane_path, "driver_*"))
    for d in driver_dirs[:5]:
        print(f"  - {os.path.basename(d)}")
        # Check if there are images
        images = glob.glob(os.path.join(d, "*.jpg"))
        print(f"    Images: {len(images)}")
        if images:
            print(f"    Sample: {os.path.basename(images[0])}")
    
    # Check for label directories
    print("\nLabel directories:")
    label_dirs = glob.glob(os.path.join(culane_path, "laneseg_label_*"))
    for d in label_dirs:
        print(f"  - {os.path.basename(d)}")
        # Check if there are label files
        label_files = glob.glob(os.path.join(d, "**", "*.png"), recursive=True)
        print(f"    Label files: {len(label_files)}")
        if label_files:
            print(f"    Sample: {os.path.basename(label_files[0])}")
    
    # Check list directory
    list_dir = os.path.join(culane_path, "list")
    if os.path.exists(list_dir):
        print("\nList directory:")
        for f in os.listdir(list_dir):
            print(f"  - {f}")
    else:
        print("\n⚠️ List directory not found - using glob fallback")

if __name__ == "__main__":
    debug_culane()
