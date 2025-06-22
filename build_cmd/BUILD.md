# Build Instructions

This document provides instructions for building LaTeX Table Builder binaries for different platforms.

## Prerequisites

- Python 3.12 or higher
- All dependencies from `requirements.txt`
- PyInstaller (`pip install pyinstaller`)

## Quick Build (Automated)

### Linux
```bash
# Make the script executable
chmod +x build_linux.sh

# Run the build
./build_linux.sh
```

The binary will be created at `dist/linux/LatexTableBuilder`.

### Windows
```batch
# Run the build script
build_windows.bat
```

The binary will be created at `dist\windows\LatexTableBuilder.exe`.

## Manual Build

### All Platforms
```bash
# Install PyInstaller
pip install pyinstaller

# Build the binary
pyinstaller \
    --onefile \
    --windowed \
    --name "LatexTableBuilder" \
    --add-data "CLAUDE.md:." \
    --add-data "README.md:." \
    main.py
```

**Note**: On Windows, use semicolon (`;`) instead of colon (`:`) in `--add-data` paths.

## GitHub Actions (Recommended for Release)

The project includes a GitHub Actions workflow (`.github/workflows/build.yml`) that automatically builds binaries for Linux, Windows, and macOS when you push a git tag.

### To create a release:

1. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Release version 1.0.0"
   ```

2. **Create and push a tag**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

3. **GitHub Actions will automatically**:
   - Build binaries for all platforms
   - Create a GitHub release
   - Attach all binaries to the release

## Manual Cross-Platform Building

### Using GitHub Codespaces or VMs

If you need to build for other platforms manually:

1. **Windows**: Use GitHub Codespaces or a Windows VM
2. **macOS**: Use GitHub Codespaces or a macOS machine
3. **Linux**: Use any Linux machine or WSL

### Building Windows Binary on Linux (Advanced)

While not recommended, you can try using Wine:

```bash
# Install Wine (Ubuntu/Debian)
sudo apt install wine

# Set up Wine
winecfg

# Install Python in Wine
# Download Python installer and run it in Wine

# Build in Wine environment
# (This is complex and not guaranteed to work)
```

**Recommendation**: Use GitHub Actions or a Windows machine for reliable Windows builds.

## Build Outputs

### Linux
- **File**: `dist/linux/LatexTableBuilder`
- **Size**: ~65MB
- **Type**: ELF executable
- **Run**: `./LatexTableBuilder`

### Windows  
- **File**: `dist/windows/LatexTableBuilder.exe`
- **Size**: ~60-70MB
- **Type**: PE executable
- **Run**: `LatexTableBuilder.exe`

### macOS
- **File**: `dist/macos/LatexTableBuilder`
- **Size**: ~65MB
- **Type**: Mach-O executable
- **Run**: `./LatexTableBuilder`

## Troubleshooting

### Common Issues

1. **"Module not found" errors**:
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Try: `pip install pyinstaller[all]`

2. **Missing libraries on Linux**:
   ```bash
   # Install missing Qt libraries
   sudo apt install libxcb-cursor0 libxcb-keysyms1 libxcb-xinerama0
   ```

3. **Large binary size**:
   - This is normal for PyInstaller binaries
   - The binary includes Python interpreter and all dependencies
   - Consider using `--exclude-module` for unused modules

4. **Permission denied (Linux/macOS)**:
   ```bash
   chmod +x dist/*/LatexTableBuilder*
   ```

### Build Optimization

To reduce binary size:

```bash
pyinstaller \
    --onefile \
    --windowed \
    --name "LatexTableBuilder" \
    --exclude-module tkinter \
    --exclude-module matplotlib \
    --exclude-module numpy \
    --add-data "CLAUDE.md:." \
    --add-data "README.md:." \
    main.py
```

## Testing Built Binaries

### Linux
```bash
cd dist/linux
./LatexTableBuilder
```

### Windows
```batch
cd dist\windows
LatexTableBuilder.exe
```

### Automated Testing
The binaries should:
1. Launch without errors
2. Display the main window
3. Allow creating and editing tables
4. Generate LaTeX output
5. Copy to clipboard (if clipboard tools are available)

## Distribution

### Creating Release Packages

```bash
# Create distribution directories
mkdir -p release/linux release/windows release/macos

# Copy binaries
cp dist/linux/LatexTableBuilder release/linux/
cp dist/windows/LatexTableBuilder.exe release/windows/
cp dist/macos/LatexTableBuilder release/macos/

# Add documentation
cp README.md CLAUDE.md release/
cp install_minimal_latex.sh fix_clipboard.sh release/linux/

# Create archives
cd release
tar -czf LatexTableBuilder-Linux-v1.0.0.tar.gz linux/
zip -r LatexTableBuilder-Windows-v1.0.0.zip windows/
tar -czf LatexTableBuilder-macOS-v1.0.0.tar.gz macos/
```

### Release Checklist

- [ ] All binaries built and tested
- [ ] Documentation updated
- [ ] Version numbers updated
- [ ] GitHub release created
- [ ] Installation instructions verified
- [ ] Optional dependencies documented

## Advanced Build Options

### Including Icons
```bash
# Windows with icon
pyinstaller --onefile --windowed --icon=icon.ico main.py

# macOS with icon  
pyinstaller --onefile --windowed --icon=icon.icns main.py
```

### Debug Build
```bash
# Include console for debugging
pyinstaller --onefile --console main.py
```

### Hooks for Additional Modules
If you encounter import errors, create a custom hook file:

```python
# hooks/hook-mymodule.py
from PyInstaller.utils.hooks import collect_all

datas, binaries, hiddenimports = collect_all('mymodule')
```

Use with: `pyinstaller --additional-hooks-dir=hooks main.py`