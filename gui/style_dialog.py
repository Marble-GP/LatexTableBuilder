from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, 
                               QCheckBox, QRadioButton, QComboBox, QSpinBox, 
                               QDoubleSpinBox, QLineEdit, QPushButton, QLabel,
                               QButtonGroup, QGridLayout, QMessageBox, QListWidget)
from PySide6.QtCore import Qt
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class TableStyle:
    """Data class to hold all table styling options"""
    name: str = "Default"
    
    # Line controls
    all_rows_lines: bool = True
    all_columns_lines: bool = True
    
    # Header line styling
    header_rows_thick: bool = False
    header_rows_style: str = "thick"  # thick, very_thick, double
    header_columns_thick: bool = False
    header_columns_style: str = "thick"
    
    # Border controls
    top_bottom_borders: bool = True
    left_right_borders: bool = False
    
    # Title
    include_title: bool = False
    title_text: str = "Unnamed Table"
    
    # Default font styles
    header_default_font: str = "bold"  # normal, bold, italic
    data_default_font: str = "normal"  # normal, bold, italic
    
    

class StyleConfigDialog(QDialog):
    def __init__(self, parent=None, current_style=None):
        super().__init__(parent)
        self.setWindowTitle("Table Style Configuration")
        self.setModal(True)
        self.resize(500, 600)
        
        # Load existing styles
        self.styles_file = Path.home() / ".latex_table_builder" / "table_styles.json"
        self.styles_file.parent.mkdir(exist_ok=True)
        self.saved_styles = self.load_styles()
        
        # Current style being edited
        self.current_style = current_style or TableStyle()
        
        self.setup_ui()
        self.load_current_style()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Style preset section
        preset_group = self.create_preset_section()
        layout.addWidget(preset_group)
        
        # Line controls section
        lines_group = self.create_lines_section()
        layout.addWidget(lines_group)
        
        # Header styling section
        header_group = self.create_header_section()
        layout.addWidget(header_group)
        
        # Border controls section
        borders_group = self.create_borders_section()
        layout.addWidget(borders_group)
        
        # Title section
        title_group = self.create_title_section()
        layout.addWidget(title_group)
        
        # Font defaults section
        font_group = self.create_font_defaults_section()
        layout.addWidget(font_group)
        
        # Dialog buttons
        buttons_layout = self.create_buttons()
        layout.addLayout(buttons_layout)
    
    def create_preset_section(self):
        group = QGroupBox("Style Presets")
        layout = QVBoxLayout(group)
        
        
        # Save preset
        save_layout = QHBoxLayout()
        save_layout.addWidget(QLabel("Save as:"))
        
        self.preset_name_edit = QLineEdit()
        self.preset_name_edit.setPlaceholderText("Enter preset name...")
        save_layout.addWidget(self.preset_name_edit)
        
        save_btn = QPushButton("Save Preset")
        save_btn.clicked.connect(self.save_preset)
        save_layout.addWidget(save_btn)
        
        layout.addLayout(save_layout)
        
        return group
    
    def create_lines_section(self):
        group = QGroupBox("Table Lines")
        layout = QVBoxLayout(group)
        
        self.all_rows_check = QCheckBox("Draw lines on all rows")
        layout.addWidget(self.all_rows_check)
        
        self.all_columns_check = QCheckBox("Draw lines on all columns")
        layout.addWidget(self.all_columns_check)
        
        return group
    
    def create_header_section(self):
        group = QGroupBox("Header Line Styling")
        layout = QGridLayout(group)
        
        # Header rows
        self.header_rows_check = QCheckBox("Make header row lines thicker")
        layout.addWidget(self.header_rows_check, 0, 0, 1, 2)
        
        layout.addWidget(QLabel("Header row style:"), 1, 0)
        self.header_rows_style_combo = QComboBox()
        self.header_rows_style_combo.addItems(["Single Line", "Double Line"])
        layout.addWidget(self.header_rows_style_combo, 1, 1)
        
        # Header columns
        self.header_columns_check = QCheckBox("Make header column lines thicker")
        layout.addWidget(self.header_columns_check, 2, 0, 1, 2)
        
        layout.addWidget(QLabel("Header column style:"), 3, 0)
        self.header_columns_style_combo = QComboBox()
        self.header_columns_style_combo.addItems(["Single Line", "Double Line"])
        layout.addWidget(self.header_columns_style_combo, 3, 1)
        
        # Enable/disable style combos based on checkboxes
        self.header_rows_check.toggled.connect(self.header_rows_style_combo.setEnabled)
        self.header_columns_check.toggled.connect(self.header_columns_style_combo.setEnabled)
        
        return group
    
    def create_borders_section(self):
        group = QGroupBox("Table Borders")
        layout = QVBoxLayout(group)
        
        self.top_bottom_borders_check = QCheckBox("Draw lines at top and bottom borders")
        layout.addWidget(self.top_bottom_borders_check)
        
        self.left_right_borders_check = QCheckBox("Draw lines at left and right borders")
        layout.addWidget(self.left_right_borders_check)
        
        return group
    
    def create_title_section(self):
        group = QGroupBox("Table Title")
        layout = QVBoxLayout(group)
        
        self.include_title_check = QCheckBox("Include table title")
        layout.addWidget(self.include_title_check)
        
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("Title text:"))
        
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Unnamed Table")
        title_layout.addWidget(self.title_edit)
        
        layout.addLayout(title_layout)
        
        # Enable/disable title edit based on checkbox
        self.include_title_check.toggled.connect(self.title_edit.setEnabled)
        
        return group
    
    def create_font_defaults_section(self):
        group = QGroupBox("Default Font Styles")
        layout = QGridLayout(group)
        
        # Header default font
        layout.addWidget(QLabel("Default font for header cells:"), 0, 0)
        self.header_font_combo = QComboBox()
        self.header_font_combo.addItems(["Normal", "Bold", "Italic"])
        layout.addWidget(self.header_font_combo, 0, 1)
        
        # Data default font
        layout.addWidget(QLabel("Default font for data cells:"), 1, 0)
        self.data_font_combo = QComboBox()
        self.data_font_combo.addItems(["Normal", "Bold", "Italic"])
        layout.addWidget(self.data_font_combo, 1, 1)
        
        # Info label
        info_label = QLabel("Note: These are defaults applied when creating new tables. Individual cells can still be formatted using B/I/R buttons.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("font-style: italic; color: #666666; font-size: 10px;")
        layout.addWidget(info_label, 2, 0, 1, 2)
        
        return group
    
    def create_buttons(self):
        layout = QHBoxLayout()
        
        layout.addStretch()
        
        # Standard dialog buttons
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setDefault(True)
        layout.addWidget(ok_btn)
        
        return layout
    
    def load_current_style(self):
        """Load current style settings into the UI"""
        style = self.current_style
        
        # Lines
        self.all_rows_check.setChecked(style.all_rows_lines)
        self.all_columns_check.setChecked(style.all_columns_lines)
        
        # Header styling
        self.header_rows_check.setChecked(style.header_rows_thick)
        self.header_columns_check.setChecked(style.header_columns_thick)
        
        # Map style names to combo indexes (single=0, double=1)
        style_map = {"single": 0, "double": 1}
        self.header_rows_style_combo.setCurrentIndex(style_map.get(style.header_rows_style, 1))  # Default to double
        self.header_columns_style_combo.setCurrentIndex(style_map.get(style.header_columns_style, 1))  # Default to double
        
        # Borders
        self.top_bottom_borders_check.setChecked(style.top_bottom_borders)
        self.left_right_borders_check.setChecked(style.left_right_borders)
        
        # Title
        self.include_title_check.setChecked(style.include_title)
        self.title_edit.setText(style.title_text)
        
        # Font defaults
        font_map = {"normal": 0, "bold": 1, "italic": 2}
        self.header_font_combo.setCurrentIndex(font_map.get(style.header_default_font, 1))  # Default to bold
        self.data_font_combo.setCurrentIndex(font_map.get(style.data_default_font, 0))  # Default to normal
        
        # Enable/disable controls
        self.header_rows_style_combo.setEnabled(style.header_rows_thick)
        self.header_columns_style_combo.setEnabled(style.header_columns_thick)
        self.title_edit.setEnabled(style.include_title)
    
    def get_current_style(self) -> TableStyle:
        """Extract current settings from UI into TableStyle object"""
        # Map UI text to style names
        style_names = ["single", "double"]  # Maps to "Single Line", "Double Line"
        font_names = ["normal", "bold", "italic"]  # Maps to "Normal", "Bold", "Italic"
        
        return TableStyle(
            name=self.preset_name_edit.text() or "Custom",
            all_rows_lines=self.all_rows_check.isChecked(),
            all_columns_lines=self.all_columns_check.isChecked(),
            header_rows_thick=self.header_rows_check.isChecked(),
            header_rows_style=style_names[self.header_rows_style_combo.currentIndex()],
            header_columns_thick=self.header_columns_check.isChecked(),
            header_columns_style=style_names[self.header_columns_style_combo.currentIndex()],
            top_bottom_borders=self.top_bottom_borders_check.isChecked(),
            left_right_borders=self.left_right_borders_check.isChecked(),
            include_title=self.include_title_check.isChecked(),
            title_text=self.title_edit.text() or "Unnamed Table",
            header_default_font=font_names[self.header_font_combo.currentIndex()],
            data_default_font=font_names[self.data_font_combo.currentIndex()]
        )
    
    def load_styles(self) -> Dict[str, TableStyle]:
        """Load saved styles from file"""
        try:
            if self.styles_file.exists():
                with open(self.styles_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return {name: TableStyle(**style_data) for name, style_data in data.items()}
        except Exception as e:
            print(f"Error loading styles: {e}")
        
        # Return default styles if loading fails
        return {
            "Simple": TableStyle(name="Simple", all_rows_lines=False, all_columns_lines=False, 
                               top_bottom_borders=True, left_right_borders=False),
            "Full Grid": TableStyle(name="Full Grid", all_rows_lines=True, all_columns_lines=True,
                                  top_bottom_borders=True, left_right_borders=True),
            "Header Only": TableStyle(name="Header Only", all_rows_lines=False, all_columns_lines=False,
                                    header_rows_thick=True, top_bottom_borders=True)
        }
    
    def save_styles(self):
        """Save styles to file"""
        try:
            with open(self.styles_file, 'w', encoding='utf-8') as f:
                data = {name: asdict(style) for name, style in self.saved_styles.items()}
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving styles: {e}")
    
    
    def save_preset(self):
        """Save current settings as a new preset"""
        name = self.preset_name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Warning", "Please enter a preset name.")
            return
        
        if name in self.saved_styles:
            reply = QMessageBox.question(self, "Confirm", 
                                       f"Preset '{name}' already exists. Overwrite?",
                                       QMessageBox.Yes | QMessageBox.No)
            if reply != QMessageBox.Yes:
                return
        
        style = self.get_current_style()
        style.name = name
        self.saved_styles[name] = style
        self.save_styles()
        
        
        QMessageBox.information(self, "Success", f"Preset '{name}' saved successfully!")
    
    
    
    def accept(self):
        """Accept dialog and return current style"""
        self.current_style = self.get_current_style()
        super().accept()
    
    def get_result_style(self) -> TableStyle:
        """Get the final configured style"""
        return self.current_style