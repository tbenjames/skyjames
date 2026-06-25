#!/bin/bash
# Fix all Streamlit files

echo "🔧 Fixing Streamlit parameters..."

# Find all Python files with use_container_width and replace with use_column_width
find . -name "*.py" -type f -exec sed -i '' 's/use_container_width/use_column_width/g' {} \;

echo "✅ All files fixed!"
echo ""
echo "Files updated:"
grep -l "use_column_width" scripts/*.py 2>/dev/null || echo "No files found"
