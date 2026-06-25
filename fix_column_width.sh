#!/bin/bash
echo "🔧 Fixing use_column_width deprecation warnings..."

# Replace in all Python files
find . -name "*.py" -type f -exec sed -i '' 's/use_column_width/use_container_width/g' {} \;

echo "✅ All files fixed!"
echo ""
echo "The 'use_column_width' parameter has been replaced with 'use_container_width'"
echo "in all Python files."
