# LaTeX Table Builder

A cross-platform LaTeX table builder application with a modern GUI interface.

## Features

- **Spreadsheet-like table editor** with merged cell support
- **Multiple LaTeX formats**: tabular, longtable, booktabs, array, IEEE-style
- **Live LaTeX preview** (requires LaTeX installation)
- **One-click clipboard export**
- **Table preset save/load functionality**
- **Cross-platform compatibility** (Windows, macOS, Linux)

## Installation

### Prerequisites

1. **Python 3.7+**

2. **For LaTeX Preview (MINIMAL - ~150-200MB)**:
   ```bash
   # Ubuntu/Debian (recommended for preview only)
   sudo apt-get install texlive-latex-base texlive-latex-recommended texlive-fonts-recommended imagemagick
   
   # Or use the included script
   ./install_minimal_latex.sh
   ```
   
3. **For Full LaTeX Support (OPTIONAL - ~1GB+)**:
   ```bash
   # Only if you need complete LaTeX document creation
   sudo apt-get install texlive-latex-base texlive-latex-extra texlive-fonts-recommended
   ```

4. **For other distributions**:
   - **Fedora**: `sudo dnf install texlive-latex ImageMagick`
   - **Arch**: `sudo pacman -S texlive-core imagemagick`
   - **macOS**: `brew install --cask basictex && brew install imagemagick`
   - **Windows**: Install [MiKTeX](https://miktex.org/) (minimal) or [TeX Live](https://www.tug.org/texlive/)

5. **Clipboard support** (Linux only):
   - `sudo apt-get install xclip` or `sudo apt-get install xsel`
   - macOS and Windows: Built-in support

### Setup

1. Clone or download this repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

```bash
python main.py
```

## Usage

1. **Create Table**: Adjust rows/columns using the spinboxes
2. **Edit Cells**: Click on any cell to edit its content
3. **Merge Cells**: Select a range and click "Merge Cells" or use right-click menu
4. **Set Alignment**: Select cells and choose alignment (Left/Center/Right)
5. **Choose LaTeX Style**: Select from tabular, longtable, booktabs, or array
6. **Export**: Click "Copy to Clipboard" to get the LaTeX code
7. **Preview**: View live LaTeX rendering (if LaTeX is installed)
8. **Zoom Control**: Use the zoom slider, +/- buttons, or keyboard shortcuts to inspect table details
9. **Save/Load Presets**: Save table configurations for reuse
10. **System Info**: Use Help → System Info to check what tools are available
11. **Installation Guide**: Use Help → Installation Guide for setup instructions

### Preview Zoom Features
- **Zoom Slider**: Drag to zoom from 25% to 500%
- **+/- Buttons**: Quick zoom in 25% increments
- **Percentage Display**: Shows current zoom level
- **Reset Button**: Return to 100% zoom
- **Fit Button**: Auto-fit image to window size
- **Keyboard Shortcuts**: Ctrl+Plus/Minus for quick zooming

### IEEE Journal Format Support
- **IEEE-style format**: Complete table environment with caption and label
- **Professional booktabs styling**: \toprule, \midrule, \bottomrule (requires texlive-latex-recommended)
- **Bold headers**: Automatic \textbf{} formatting for header rows
- **Proper positioning**: [htbp] positioning for IEEE standards
- **Complete document**: Generate full IEEEtran document templates

### Graceful Degradation

The application works even without optional dependencies:

- **Without LaTeX**: Preview shows helpful installation instructions instead of blank screen
- **Without clipboard support**: Offers to save LaTeX code to temporary file with clear error messages
- **Missing tools**: Help menu provides specific installation commands for your system

## Keyboard Shortcuts

### Table Editing
- **Tab**: Move to next cell
- **Shift+Tab**: Move to previous cell
- **Delete**: Clear selected cells

### File Operations
- **Ctrl+N**: New table
- **Ctrl+O**: Open file
- **Ctrl+S**: Save file
- **Ctrl+L**: Copy LaTeX code to clipboard

### Preview Zoom
- **Ctrl++**: Zoom in
- **Ctrl+-**: Zoom out
- **Ctrl+0**: Reset zoom to 100%

## Building Executables

To create standalone executables:

```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile --windowed main.py

# Windows (with icon)
pyinstaller --onefile --windowed --icon=icon.ico main.py
```

## Project Structure

```
├── main.py                 # Application entry point
├── gui/
│   ├── main_window.py     # Main application window
│   ├── table_editor.py    # Table editing widget
│   └── preview_widget.py  # LaTeX preview pane
├── core/
│   ├── table_model.py     # Table data model
│   ├── latex_generator.py # LaTeX code generation
│   └── preset_manager.py  # Preset save/load
├── utils/
│   └── clipboard.py       # Clipboard operations
└── requirements.txt       # Python dependencies
```

## License

This project is open source and available under the MIT License.