#!/bin/bash

echo "LaTeX Table Builder - Clipboard Fix"
echo "=================================="
echo ""
echo "Installing clipboard support for Linux..."
echo ""

# Check if xclip is already installed
if command -v xclip &> /dev/null; then
    echo "✓ xclip is already installed"
else
    echo "Installing xclip..."
    sudo apt-get update
    sudo apt-get install -y xclip
    
    if command -v xclip &> /dev/null; then
        echo "✓ xclip installed successfully"
    else
        echo "✗ Failed to install xclip"
        echo ""
        echo "Please try manually:"
        echo "  sudo apt-get install xclip"
        exit 1
    fi
fi

echo ""
echo "Testing clipboard functionality..."

# Test clipboard
echo "test" | xclip -selection clipboard
if [ $? -eq 0 ]; then
    echo "✓ Clipboard test successful"
    echo ""
    echo "Clipboard functionality is now working!"
    echo "Restart the LaTeX Table Builder to use clipboard features."
else
    echo "✗ Clipboard test failed"
    echo ""
    echo "You may need to log out and log back in for clipboard to work properly."
fi

echo ""
echo "Note: You may need to restart your session for clipboard changes to take effect."