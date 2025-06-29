#!/bin/bash

echo "ImageMagick 7.x Installation Script"
echo "===================================="
echo ""
echo "This script will install ImageMagick 7.x with the modern 'magick' command."
echo "This requires sudo privileges for installing dependencies."
echo ""

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "Do not run this script as root. Run as normal user with sudo access."
   exit 1
fi

# Install build dependencies
echo "Installing build dependencies..."
sudo apt update
sudo apt install -y build-essential wget pkg-config \
    libjpeg-dev libpng-dev libtiff-dev libwebp-dev \
    libfontconfig1-dev libfreetype6-dev \
    libxml2-dev libbz2-dev liblzma-dev

# Create local directory
mkdir -p ~/local/src
cd ~/local/src

# Download ImageMagick 7
echo "Downloading ImageMagick 7.1.1-47..."
wget https://github.com/ImageMagick/ImageMagick/archive/refs/tags/7.1.1-47.tar.gz -O imagemagick-7.tar.gz
tar -xzf imagemagick-7.tar.gz
cd ImageMagick-7.1.1-47

# Configure and build
echo "Configuring ImageMagick..."
./configure --prefix=$HOME/local \
    --enable-shared \
    --disable-static \
    --with-modules \
    --with-jpeg \
    --with-png \
    --with-tiff \
    --with-webp \
    --with-fontconfig \
    --with-freetype

echo "Building ImageMagick (this may take several minutes)..."
make -j$(nproc)

echo "Installing ImageMagick to ~/local..."
make install

# Add to PATH
echo ""
echo "Adding ~/local/bin to PATH..."
if ! grep -q "export PATH=\$HOME/local/bin:\$PATH" ~/.bashrc; then
    echo 'export PATH=$HOME/local/bin:$PATH' >> ~/.bashrc
    echo 'export LD_LIBRARY_PATH=$HOME/local/lib:$LD_LIBRARY_PATH' >> ~/.bashrc
    echo 'export PKG_CONFIG_PATH=$HOME/local/lib/pkgconfig:$PKG_CONFIG_PATH' >> ~/.bashrc
fi

# Source the updated bashrc
source ~/.bashrc

echo ""
echo "Installation complete!"
echo ""
echo "Please run the following command to update your current shell:"
echo "  source ~/.bashrc"
echo ""
echo "Then test the installation with:"
echo "  magick --version"
echo ""
echo "You may need to restart your terminal or log out and back in."