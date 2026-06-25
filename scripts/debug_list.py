"""
Debug the CULane list file to see actual paths
"""

import os

culane_path = "/Users/apple/Downloads/CULane"
list_file = os.path.join(culane_path, "list", "train.txt")

print("=" * 60)
print("Debugging CULane List File")
print("=" * 60)
print(f"List file: {list_file}")
print(f"Exists: {os.path.exists(list_file)}")

if os.path.exists(list_file):
    with open(list_file, 'r') as f:
        lines = f.readlines()
    
    print(f"\nTotal lines: {len(lines)}")
    print("\nFirst 10 lines:")
    for i, line in enumerate(lines[:10]):
        print(f"  {i+1}: {line.strip()}")
    
    # Check if paths exist
    print("\nChecking first 5 paths:")
    for i, line in enumerate(lines[:5]):
        line = line.strip()
        if not line:
            continue
        
        # Try different path combinations
        full_path = os.path.join(culane_path, line)
        print(f"\n  Path {i+1}: {line}")
        print(f"    Full: {full_path}")
        print(f"    Exists: {os.path.exists(full_path)}")
        
        # Try without 'driver_' prefix
        if line.startswith('driver_'):
            alt_path = os.path.join(culane_path, line.replace('driver_', ''))
            print(f"    Alt: {alt_path}")
            print(f"    Alt exists: {os.path.exists(alt_path)}")
        
        # Check if it's just a filename
        base_name = os.path.basename(line)
        search_paths = [
            os.path.join(culane_path, base_name),
            os.path.join(culane_path, "driver_*", base_name),
        ]
        for sp in search_paths:
            if '*' in sp:
                import glob
                matches = glob.glob(sp)
                if matches:
                    print(f"    Glob match: {matches[0]}")
            else:
                print(f"    Search: {sp} - {os.path.exists(sp)}")

if __name__ == "__main__":
    debug_list()
