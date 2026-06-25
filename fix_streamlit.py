#!/usr/bin/env python
"""
Fix Streamlit parameter names in all Python files
"""

import os
import re
import glob

def fix_file(filepath):
    """Replace use_column_width with use_column_width in a file"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Check if file contains use_column_width
        if 'use_column_width' not in content:
            return False
        
        # Replace all occurrences
        new_content = content.replace('use_column_width', 'use_column_width')
        
        with open(filepath, 'w') as f:
            f.write(new_content)
        
        return True
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    print("🔧 Fixing Streamlit parameters...")
    print("=" * 50)
    
    # Find all Python files in scripts and src directories
    files = []
    for pattern in ['scripts/*.py', 'src/**/*.py', '*.py']:
        files.extend(glob.glob(pattern, recursive=True))
    
    # Also include specific files
    additional_files = ['scripts/dashboard_app.py', 'scripts/model_dashboard_final.py']
    for f in additional_files:
        if os.path.exists(f) and f not in files:
            files.append(f)
    
    fixed_count = 0
    for filepath in files:
        if fix_file(filepath):
            print(f"✅ Fixed: {filepath}")
            fixed_count += 1
    
    print("=" * 50)
    print(f"✅ Fixed {fixed_count} files!")
    
    # Show files that still have use_column_width (if any)
    print("\n📋 Checking remaining files...")
    remaining = []
    for filepath in files:
        with open(filepath, 'r') as f:
            if 'use_column_width' in f.read():
                remaining.append(filepath)
    
    if remaining:
        print("⚠️ Still contains use_column_width:")
        for f in remaining:
            print(f"  - {f}")
    else:
        print("✅ All files fixed!")

if __name__ == "__main__":
    main()
