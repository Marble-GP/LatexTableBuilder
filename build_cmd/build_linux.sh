#!/bin/bash

echo "=== LaTeX Table Builder - Linux Build Script ==="
echo

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "Error: main.py not found. Please run this script from the project root directory."
    exit 1
fi

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/ *.spec

# Create the Linux binary
echo "Building Linux binary..."
pyinstaller \
    --onefile \
    --windowed \
    --name "LatexTableBuilder" \
    --add-data "CLAUDE.md:." \
    --add-data "README.md:." \
    --distpath "dist/linux" \
    main.py

# Check if build was successful
if [ -f "dist/linux/LatexTableBuilder" ]; then
    echo
    echo "✅ Linux binary built successfully!"
    echo "📁 Location: dist/linux/LatexTableBuilder"
    echo "📊 Size: $(du -h dist/linux/LatexTableBuilder | cut -f1)"
    echo
    echo "To run the application:"
    echo "  cd dist/linux"
    echo "  ./LatexTableBuilder"
    echo
else
    echo "❌ Build failed! Check the output above for errors."
    exit 1
fi