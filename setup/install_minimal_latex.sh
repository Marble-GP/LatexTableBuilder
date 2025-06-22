#!/bin/bash

echo "LaTeX Table Builder - Minimal LaTeX Installation"
echo "================================================"
echo ""
echo "This script installs the minimal packages needed for LaTeX preview."
echo "Total download size: ~50-100MB (much smaller than full LaTeX distribution)"
echo ""

# Detect distribution
if command -v apt-get &> /dev/null; then
    echo "Detected Debian/Ubuntu system"
    echo ""
    echo "Installing minimal packages:"
    echo "- texlive-latex-base: Core LaTeX functionality"
    echo "- texlive-latex-recommended: Includes booktabs, longtable, multirow"
    echo "- texlive-fonts-recommended: Basic fonts"
    echo "- imagemagick: For PNG conversion"
    echo ""
    
    read -p "Continue with installation? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Installing packages..."
        sudo apt-get update
        sudo apt-get install -y texlive-latex-base texlive-latex-recommended texlive-fonts-recommended imagemagick
        
        echo ""
        echo "Testing installation..."
        if command -v pdflatex &> /dev/null && command -v convert &> /dev/null; then
            echo "✓ Installation successful!"
            echo "✓ pdflatex found: $(which pdflatex)"
            echo "✓ convert found: $(which convert)"
            echo ""
            echo "You can now restart the LaTeX Table Builder to enable preview functionality."
        else
            echo "✗ Installation may have failed. Please check for errors above."
        fi
    else
        echo "Installation cancelled."
    fi

elif command -v dnf &> /dev/null; then
    echo "Detected Fedora system"
    echo ""
    echo "Installing minimal packages:"
    echo "- texlive-latex: Core LaTeX functionality"
    echo "- ImageMagick: For PNG conversion"
    echo ""
    
    read -p "Continue with installation? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Installing packages..."
        sudo dnf install -y texlive-latex ImageMagick
        
        echo ""
        echo "Testing installation..."
        if command -v pdflatex &> /dev/null && command -v convert &> /dev/null; then
            echo "✓ Installation successful!"
            echo "You can now restart the LaTeX Table Builder to enable preview functionality."
        else
            echo "✗ Installation may have failed. Please check for errors above."
        fi
    else
        echo "Installation cancelled."
    fi

elif command -v pacman &> /dev/null; then
    echo "Detected Arch Linux system"
    echo ""
    echo "Installing minimal packages:"
    echo "- texlive-core: Core LaTeX functionality"
    echo "- imagemagick: For PNG conversion"
    echo ""
    
    read -p "Continue with installation? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Installing packages..."
        sudo pacman -S texlive-core imagemagick
        
        echo ""
        echo "Testing installation..."
        if command -v pdflatex &> /dev/null && command -v convert &> /dev/null; then
            echo "✓ Installation successful!"
            echo "You can now restart the LaTeX Table Builder to enable preview functionality."
        else
            echo "✗ Installation may have failed. Please check for errors above."
        fi
    else
        echo "Installation cancelled."
    fi

else
    echo "Unsupported package manager. Please install manually:"
    echo ""
    echo "You need these packages:"
    echo "1. LaTeX distribution with pdflatex"
    echo "2. ImageMagick (for convert command)"
    echo ""
    echo "Distribution-specific commands:"
    echo "• Ubuntu/Debian: sudo apt-get install texlive-latex-base texlive-fonts-recommended imagemagick"
    echo "• Fedora: sudo dnf install texlive-latex ImageMagick"
    echo "• Arch: sudo pacman -S texlive-core imagemagick"
    echo "• macOS: brew install --cask basictex && brew install imagemagick"
fi

echo ""
echo "Note: This installs only the minimal packages needed for preview."
echo "For full LaTeX document creation, you may need additional packages."