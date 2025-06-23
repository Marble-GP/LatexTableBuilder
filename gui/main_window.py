from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QMenuBar, QToolBar, QStatusBar, QSplitter, 
                               QPushButton, QSpinBox, QLabel, QComboBox, QDialog, QLineEdit)
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QAction
from gui.table_editor import TableEditor
from core.table_model import TableModel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.table_model = TableModel()
        self.current_table_style = None  # Current style settings
        
        # Load saved theme preference
        self.dark_theme = self.load_theme_preference()
        
        self.setup_ui()
        self.setup_menus()
        self.setup_toolbar()
        self.setup_statusbar()
        
        # Apply initial theme
        self.apply_theme()
        
        # Initialize preview
        self.update_preview()
        
    def setup_ui(self):
        self.setWindowTitle("LaTeX Table Builder")
        self.setGeometry(100, 100, 1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([900, 300])  # Reduce preview width
        
    def create_left_panel(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        table_controls = self.create_table_controls()
        layout.addWidget(table_controls)
        
        self.table_editor = TableEditor(self.table_model)
        self.table_editor.cell_changed.connect(self.on_table_changed)
        self.table_editor.toggle_headers_requested.connect(self.toggle_headers)
        layout.addWidget(self.table_editor)
        
        return widget
    
    def create_table_controls(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        layout.addWidget(QLabel("Rows:"))
        self.rows_spinbox = QSpinBox()
        self.rows_spinbox.setRange(1, 50)
        self.rows_spinbox.setValue(self.table_model.rows)
        self.rows_spinbox.valueChanged.connect(self.resize_table)
        layout.addWidget(self.rows_spinbox)
        
        layout.addWidget(QLabel("Columns:"))
        self.cols_spinbox = QSpinBox()
        self.cols_spinbox.setRange(1, 20)
        self.cols_spinbox.setValue(self.table_model.cols)
        self.cols_spinbox.valueChanged.connect(self.resize_table)
        layout.addWidget(self.cols_spinbox)
        
        layout.addWidget(QLabel("Alignment:"))
        self.alignment_combo = QComboBox()
        self.alignment_combo.addItems(["Left", "Center", "Right"])
        self.alignment_combo.currentTextChanged.connect(self.change_alignment)
        layout.addWidget(self.alignment_combo)
        
        merge_btn = QPushButton("Merge Cells")
        merge_btn.clicked.connect(self.merge_selected_cells)
        layout.addWidget(merge_btn)
        
        unmerge_btn = QPushButton("Unmerge Cells")
        unmerge_btn.clicked.connect(self.unmerge_selected_cells)
        layout.addWidget(unmerge_btn)
        
        # Font formatting toggle buttons
        layout.addWidget(QLabel("|"))  # Separator
        
        bold_btn = QPushButton("B")
        bold_btn.setCheckable(True)
        bold_btn.setToolTip("Bold")
        bold_btn.setFixedWidth(30)
        bold_btn.setStyleSheet("font-weight: bold;")
        bold_btn.clicked.connect(lambda: self.toggle_font_style("bold"))
        layout.addWidget(bold_btn)
        self.bold_btn = bold_btn
        
        italic_btn = QPushButton("I")
        italic_btn.setCheckable(True)
        italic_btn.setToolTip("Italic")
        italic_btn.setFixedWidth(30)
        italic_btn.setStyleSheet("font-style: italic;")
        italic_btn.clicked.connect(lambda: self.toggle_font_style("italic"))
        layout.addWidget(italic_btn)
        self.italic_btn = italic_btn
        
        roman_btn = QPushButton("R")
        roman_btn.setCheckable(True)
        roman_btn.setToolTip("Roman (Normal)")
        roman_btn.setFixedWidth(30)
        roman_btn.clicked.connect(lambda: self.toggle_font_style("roman"))
        layout.addWidget(roman_btn)
        self.roman_btn = roman_btn
        
        reset_font_btn = QPushButton("Reset")
        reset_font_btn.setToolTip("Reset font formatting")
        reset_font_btn.clicked.connect(self.reset_font_formatting)
        layout.addWidget(reset_font_btn)
        
        layout.addStretch()
        return widget
    
    def create_right_panel(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        latex_controls = self.create_latex_controls()
        layout.addWidget(latex_controls)
        
        from gui.preview_widget import PreviewWidget
        self.preview_widget = PreviewWidget()
        layout.addWidget(self.preview_widget)
        
        export_controls = self.create_export_controls()
        layout.addWidget(export_controls)
        
        return widget
    
    def create_latex_controls(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # Style configuration button
        self.style_config_btn = QPushButton("Configure Table Style...")
        self.style_config_btn.clicked.connect(self.open_style_dialog)
        layout.addWidget(self.style_config_btn)
        
        # Current style indicator
        self.current_style_label = QLabel("Current: Default")
        self.current_style_label.setStyleSheet("font-style: italic; color: #666666;")
        layout.addWidget(self.current_style_label)
        
        layout.addStretch()
        
        # Header specification controls
        layout.addWidget(QLabel("Header Rows:"))
        self.header_rows_input = QLineEdit()
        self.header_rows_input.setPlaceholderText("e.g., 1, 1-2, 1,3-5")
        self.header_rows_input.setToolTip("Specify header rows using 1-based indexing (e.g., '1', '1,2', '1-3', '1,3-5')")
        self.header_rows_input.textChanged.connect(self.on_header_spec_changed)
        layout.addWidget(self.header_rows_input)
        
        layout.addWidget(QLabel("Header Columns:"))
        self.header_cols_input = QLineEdit()
        self.header_cols_input.setPlaceholderText("e.g., 1, 1-2, 1,3-5")
        self.header_cols_input.setToolTip("Specify header columns using 1-based indexing (e.g., '1', '1,2', '1-3', '1,3-5')")
        self.header_cols_input.textChanged.connect(self.on_header_spec_changed)
        layout.addWidget(self.header_cols_input)
        
        clear_headers_btn = QPushButton("Clear Headers")
        clear_headers_btn.clicked.connect(self.clear_header_specifications)
        layout.addWidget(clear_headers_btn)
        
        return widget
    
    def create_export_controls(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        copy_btn = QPushButton("Copy to Clipboard")
        copy_btn.clicked.connect(self.copy_to_clipboard)
        layout.addWidget(copy_btn)
        
        layout.addStretch()
        return widget
    
    def setup_menus(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_table)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open...", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        edit_menu = menubar.addMenu("&Edit")
        
        paste_action = QAction("&Paste", self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.paste_from_clipboard)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        copy_latex_action = QAction("Copy &LaTeX", self)
        copy_latex_action.setShortcut(QKeySequence("Ctrl+L"))
        copy_latex_action.triggered.connect(self.copy_to_clipboard)
        edit_menu.addAction(copy_latex_action)
        
        help_menu = menubar.addMenu("&Help")
        
        system_info_action = QAction("System &Info", self)
        system_info_action.triggered.connect(self.show_system_info)
        help_menu.addAction(system_info_action)
        
        install_guide_action = QAction("&Installation Guide", self)
        install_guide_action.triggered.connect(self.show_installation_guide)
        help_menu.addAction(install_guide_action)
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # View menu for theme switching
        view_menu = menubar.addMenu("&View")
        
        self.dark_theme_action = QAction("&Dark Theme", self)
        self.dark_theme_action.setCheckable(True)
        self.dark_theme_action.setChecked(self.dark_theme)
        self.dark_theme_action.triggered.connect(self.toggle_dark_theme)
        view_menu.addAction(self.dark_theme_action)
        
        light_theme_action = QAction("&Light Theme", self)
        light_theme_action.setCheckable(True)
        light_theme_action.setChecked(not self.dark_theme)
        light_theme_action.triggered.connect(self.toggle_light_theme)
        view_menu.addAction(light_theme_action)
        
        # Create theme action group for mutual exclusivity
        from PySide6.QtGui import QActionGroup
        self.theme_group = QActionGroup(self)
        self.theme_group.addAction(self.dark_theme_action)
        self.theme_group.addAction(light_theme_action)
    
    def setup_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        toolbar.addAction("New", self.new_table)
        toolbar.addAction("Open", self.open_file)
        toolbar.addAction("Save", self.save_file)
        toolbar.addSeparator()
        toolbar.addAction("Paste", self.paste_from_clipboard)
        toolbar.addAction("Copy LaTeX", self.copy_to_clipboard)
    
    def setup_statusbar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready")
    
    def resize_table(self):
        new_rows = self.rows_spinbox.value()
        new_cols = self.cols_spinbox.value()
        
        if self.table_model.resize(new_rows, new_cols):
            self.table_editor.refresh_table()
            self.update_preview()
            self.statusbar.showMessage(f"Table resized to {new_rows}×{new_cols}")
    
    def on_table_changed(self, row: int, col: int, content: str):
        """Called whenever a table cell is modified"""
        self.update_preview()
    
    def change_alignment(self, alignment_text):
        alignment_map = {"Left": "l", "Center": "c", "Right": "r"}
        alignment = alignment_map.get(alignment_text, "l")
        
        selected_ranges = self.table_editor.get_selected_ranges()
        for start_row, start_col, end_row, end_col in selected_ranges:
            for row in range(start_row, end_row + 1):
                for col in range(start_col, end_col + 1):
                    self.table_model.set_cell_alignment(row, col, alignment)
        
        self.table_editor.refresh_table()
        self.update_preview()
    
    def merge_selected_cells(self):
        selected_ranges = self.table_editor.get_selected_ranges()
        if not selected_ranges:
            self.statusbar.showMessage("No cells selected")
            return
        
        start_row, start_col, end_row, end_col = selected_ranges[0]
        
        if self.table_model.merge_cells(start_row, start_col, end_row, end_col):
            self.table_editor.refresh_table()
            self.update_preview()
            self.statusbar.showMessage("Cells merged")
        else:
            self.statusbar.showMessage("Cannot merge selected cells")
    
    def unmerge_selected_cells(self):
        selected_ranges = self.table_editor.get_selected_ranges()
        if not selected_ranges:
            self.statusbar.showMessage("No cells selected")
            return
        
        start_row, start_col, _, _ = selected_ranges[0]
        
        if self.table_model.unmerge_cells(start_row, start_col):
            self.table_editor.refresh_table()
            self.update_preview()
            self.statusbar.showMessage("Cells unmerged")
        else:
            self.statusbar.showMessage("No merged cells at selection")
    
    def update_preview(self):
        from core.latex_generator import LaTeXGenerator
        
        # Use styled generator if custom style is set
        if self.current_table_style:
            generator = LaTeXGenerator(self.table_model, self.current_table_style)
            latex_code = generator.generate("styled")
        else:
            generator = LaTeXGenerator(self.table_model)
            latex_code = generator.generate("tabular")  # Default style
        
        self.preview_widget.update_preview(latex_code)
    
    def toggle_headers(self):
        """Smart header toggle based on selection type"""
        selection_type, data = self.table_editor.get_selection_type()
        
        if selection_type == "none":
            # No selection, toggle row 0 as default
            is_header = self.table_model.toggle_row_header(0)
            action = "marked as" if is_header else "unmarked as"
            self.statusbar.showMessage(f"Row 1 {action} header")
            
        elif selection_type == "rows":
            # Toggle header status for selected rows
            messages = []
            for row in data:
                is_header = self.table_model.toggle_row_header(row)
                action = "marked as" if is_header else "unmarked as"
                messages.append(f"Row {row + 1} {action} header")
            self.statusbar.showMessage("; ".join(messages))
            
        elif selection_type == "columns":
            # Toggle header status for selected columns
            messages = []
            for col in data:
                is_header = self.table_model.toggle_column_header(col)
                action = "marked as" if is_header else "unmarked as"
                messages.append(f"Column {col + 1} {action} header")
            self.statusbar.showMessage("; ".join(messages))
            
        elif selection_type == "cells":
            # Toggle header status for individual cells
            # Check if any selected cell is currently a header
            any_header = any(
                self.table_model.get_cell(row, col) and self.table_model.get_cell(row, col).is_header
                for row, col in data
            )
            # Toggle to opposite state
            self.table_model.set_cells_as_header(data, not any_header)
            action = "marked as" if not any_header else "unmarked as"
            self.statusbar.showMessage(f"{len(data)} cells {action} headers")
            
        elif selection_type == "mixed":
            # Handle mixed selection
            messages = []
            for row in data.get("rows", []):
                is_header = self.table_model.toggle_row_header(row)
                action = "marked as" if is_header else "unmarked as"
                messages.append(f"Row {row + 1} {action} header")
            for col in data.get("columns", []):
                is_header = self.table_model.toggle_column_header(col)
                action = "marked as" if is_header else "unmarked as"
                messages.append(f"Column {col + 1} {action} header")
            if data.get("cells", []):
                any_header = any(
                    self.table_model.get_cell(row, col) and self.table_model.get_cell(row, col).is_header
                    for row, col in data["cells"]
                )
                self.table_model.set_cells_as_header(data["cells"], not any_header)
                action = "marked as" if not any_header else "unmarked as"
                messages.append(f"{len(data['cells'])} cells {action} headers")
            self.statusbar.showMessage("; ".join(messages))
        
        self.table_editor.refresh_table()
        self.update_preview()
    
    def clear_all_headers(self):
        """Clear all header formatting from the table (DEPRECATED)"""
        self.table_model.clear_all_headers()
        self.table_editor.refresh_table()
        self.update_preview()
        self.statusbar.showMessage("All header selections cleared")
    
    def on_header_spec_changed(self):
        """Called when header specification text changes"""
        try:
            # Update the table model with new specifications
            rows_spec = self.header_rows_input.text().strip()
            cols_spec = self.header_cols_input.text().strip()
            
            self.table_model.set_header_rows_spec(rows_spec)
            self.table_model.set_header_cols_spec(cols_spec)
            
            # Validate specifications and provide feedback
            header_rows = self.table_model.get_header_rows()
            header_cols = self.table_model.get_header_cols()
            
            # Check for out-of-range values
            invalid_rows = [r for r in header_rows if r >= self.table_model.rows]
            invalid_cols = [c for c in header_cols if c >= self.table_model.cols]
            
            if invalid_rows or invalid_cols:
                status_parts = []
                if invalid_rows:
                    status_parts.append(f"Invalid rows: {[r+1 for r in invalid_rows]}")
                if invalid_cols:
                    status_parts.append(f"Invalid columns: {[c+1 for c in invalid_cols]}")
                self.statusbar.showMessage(f"Warning: {'; '.join(status_parts)}")
            else:
                # Valid specification
                status_parts = []
                if header_rows:
                    status_parts.append(f"Header rows: {[r+1 for r in header_rows]}")
                if header_cols:
                    status_parts.append(f"Header columns: {[c+1 for c in header_cols]}")
                
                if status_parts:
                    self.statusbar.showMessage("; ".join(status_parts))
                else:
                    self.statusbar.showMessage("No headers specified")
            
            # Refresh display
            self.table_editor.refresh_table()
            self.update_preview()
            
        except Exception as e:
            self.statusbar.showMessage(f"Header specification error: {str(e)}")
    
    def clear_header_specifications(self):
        """Clear header specifications and reset input boxes"""
        self.header_rows_input.clear()
        self.header_cols_input.clear()
        self.table_model.set_header_rows_spec("")
        self.table_model.set_header_cols_spec("")
        
        self.table_editor.refresh_table()
        self.update_preview()
        self.statusbar.showMessage("Header specifications cleared")
    
    def toggle_font_style(self, style: str):
        """Toggle font style for selected cells"""
        selected_ranges = self.table_editor.get_selected_ranges()
        if not selected_ranges:
            self.statusbar.showMessage("No cells selected")
            return
        
        # Determine current state for the first selected cell
        start_row, start_col, _, _ = selected_ranges[0]
        first_cell = self.table_model.get_cell(start_row, start_col)
        
        if style == "bold":
            # Toggle bold state
            new_state = not (first_cell and first_cell.is_bold)
            for start_row, start_col, end_row, end_col in selected_ranges:
                for row in range(start_row, end_row + 1):
                    for col in range(start_col, end_col + 1):
                        self.table_model.set_cell_font_style(row, col, "bold" if new_state else "normal")
            
        elif style == "italic":
            # Toggle italic state
            new_state = not (first_cell and first_cell.is_italic)
            for start_row, start_col, end_row, end_col in selected_ranges:
                for row in range(start_row, end_row + 1):
                    for col in range(start_col, end_col + 1):
                        self.table_model.set_cell_font_style(row, col, "italic" if new_state else "normal")
            
        elif style == "roman":
            # Set to normal/roman style
            for start_row, start_col, end_row, end_col in selected_ranges:
                for row in range(start_row, end_row + 1):
                    for col in range(start_col, end_col + 1):
                        self.table_model.set_cell_font_style(row, col, "normal")
        
        self.table_editor.refresh_table()
        self.update_preview()
        self.update_font_button_states()
        self.statusbar.showMessage(f"Applied {style} formatting to selected cells")
    
    def reset_font_formatting(self):
        """Reset font formatting for selected cells"""
        selected_ranges = self.table_editor.get_selected_ranges()
        if not selected_ranges:
            self.statusbar.showMessage("No cells selected")
            return
        
        for start_row, start_col, end_row, end_col in selected_ranges:
            for row in range(start_row, end_row + 1):
                for col in range(start_col, end_col + 1):
                    self.table_model.reset_cell_formatting(row, col)
        
        self.table_editor.refresh_table()
        self.update_preview()
        self.update_font_button_states()
        self.statusbar.showMessage("Reset font formatting for selected cells")
    
    def update_font_button_states(self):
        """Update font button states based on current selection"""
        selected_ranges = self.table_editor.get_selected_ranges()
        if not selected_ranges:
            # No selection, disable all buttons
            self.bold_btn.setChecked(False)
            self.italic_btn.setChecked(False)
            self.roman_btn.setChecked(False)
            return
        
        # Check if all selected cells have the same formatting
        has_bold = False
        has_italic = False
        has_normal = False
        
        for start_row, start_col, end_row, end_col in selected_ranges:
            for row in range(start_row, end_row + 1):
                for col in range(start_col, end_col + 1):
                    cell = self.table_model.get_cell(row, col)
                    if cell:
                        if cell.is_bold:
                            has_bold = True
                        if cell.is_italic:
                            has_italic = True
                        if cell.font_style == "normal":
                            has_normal = True
        
        # Update button states
        self.bold_btn.setChecked(has_bold)
        self.italic_btn.setChecked(has_italic)
        self.roman_btn.setChecked(has_normal)
    
    def apply_theme(self):
        """Apply the current theme to the entire application"""
        if self.dark_theme:
            # Dark theme
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QMenuBar {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border-bottom: 1px solid #555555;
                }
                QMenuBar::item {
                    background-color: transparent;
                    padding: 4px 8px;
                }
                QMenuBar::item:selected {
                    background-color: #555555;
                }
                QMenu {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555555;
                }
                QMenu::item:selected {
                    background-color: #555555;
                }
                QToolBar {
                    background-color: #3c3c3c;
                    border: 1px solid #555555;
                    color: #ffffff;
                }
                QStatusBar {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border-top: 1px solid #555555;
                }
                QPushButton {
                    background-color: #404040;
                    color: #ffffff;
                    border: 1px solid #666666;
                    padding: 5px 10px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #505050;
                }
                QPushButton:pressed {
                    background-color: #606060;
                }
                QSpinBox, QComboBox {
                    background-color: #404040;
                    color: #ffffff;
                    border: 1px solid #666666;
                    padding: 2px;
                }
                QSpinBox::up-button, QSpinBox::down-button {
                    background-color: #505050;
                    border: 1px solid #666666;
                }
                QComboBox::drop-down {
                    background-color: #505050;
                    border: 1px solid #666666;
                }
                QComboBox QAbstractItemView {
                    background-color: #404040;
                    color: #ffffff;
                    selection-background-color: #555555;
                }
                QLabel {
                    color: #ffffff;
                }
            """)
        else:
            # Light theme
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #ffffff;
                    color: #000000;
                }
                QWidget {
                    background-color: #ffffff;
                    color: #000000;
                }
                QMenuBar {
                    background-color: #f0f0f0;
                    color: #000000;
                    border-bottom: 1px solid #cccccc;
                }
                QMenuBar::item:selected {
                    background-color: #e0e0e0;
                }
                QMenu {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #cccccc;
                }
                QMenu::item:selected {
                    background-color: #e0e0e0;
                }
                QToolBar {
                    background-color: #f0f0f0;
                    border: 1px solid #cccccc;
                    color: #000000;
                }
                QStatusBar {
                    background-color: #f0f0f0;
                    color: #000000;
                    border-top: 1px solid #cccccc;
                }
                QPushButton {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #cccccc;
                    padding: 5px 10px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                }
                QPushButton:pressed {
                    background-color: #e0e0e0;
                }
                QSpinBox, QComboBox {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #cccccc;
                    padding: 2px;
                }
                QLabel {
                    color: #000000;
                }
            """)
        
        # Apply theme to table editor
        if hasattr(self, 'table_editor'):
            self.table_editor.set_theme(self.dark_theme)
    
    def load_theme_preference(self) -> bool:
        """Load saved theme preference"""
        try:
            from pathlib import Path
            import json
            
            config_file = Path.home() / ".latex_table_builder" / "settings.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    return settings.get("dark_theme", True)  # Default to dark
        except Exception as e:
            print(f"Error loading theme preference: {e}")
        
        return True  # Default to dark theme
    
    def save_theme_preference(self):
        """Save current theme preference"""
        try:
            from pathlib import Path
            import json
            
            config_dir = Path.home() / ".latex_table_builder"
            config_dir.mkdir(exist_ok=True)
            config_file = config_dir / "settings.json"
            
            # Load existing settings or create new
            settings = {}
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            
            # Update theme setting
            settings["dark_theme"] = self.dark_theme
            
            # Save settings
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
                
        except Exception as e:
            print(f"Error saving theme preference: {e}")
    
    def toggle_dark_theme(self):
        """Switch to dark theme"""
        self.dark_theme = True
        self.apply_theme()
        self.save_theme_preference()
        self.statusbar.showMessage("Switched to dark theme")
    
    def toggle_light_theme(self):
        """Switch to light theme"""
        self.dark_theme = False
        self.apply_theme()
        self.save_theme_preference()
        self.statusbar.showMessage("Switched to light theme")
    
    def open_style_dialog(self):
        """Open the table style configuration dialog"""
        from gui.style_dialog import StyleConfigDialog, TableStyle
        
        dialog = StyleConfigDialog(self, self.current_table_style)
        if dialog.exec() == QDialog.Accepted:
            self.current_table_style = dialog.get_result_style()
            self.update_style_label()
            self.update_preview()
            self.statusbar.showMessage(f"Applied style: {self.current_table_style.name}")
    
    def update_style_label(self):
        """Update the current style label"""
        if self.current_table_style:
            self.current_style_label.setText(f"Current: {self.current_table_style.name}")
        else:
            self.current_style_label.setText("Current: Default")
    
    def copy_to_clipboard(self):
        from utils.clipboard import copy_to_clipboard, save_to_temp_file, get_clipboard_status
        from core.latex_generator import LaTeXGenerator
        from PySide6.QtWidgets import QMessageBox
        
        # Use the same logic as preview
        if self.current_table_style:
            generator = LaTeXGenerator(self.table_model, self.current_table_style)
            latex_code = generator.generate("styled")
        else:
            generator = LaTeXGenerator(self.table_model)
            latex_code = generator.generate("tabular")
        
        result = copy_to_clipboard(latex_code)
        
        if result["success"]:
            method = result["method"]
            if result["fallback_used"]:
                self.statusbar.showMessage(f"LaTeX code copied using {method} (fallback method)")
            else:
                self.statusbar.showMessage("LaTeX code copied to clipboard")
        else:
            # Clipboard failed, offer alternatives
            temp_file = save_to_temp_file(latex_code)
            clipboard_status = get_clipboard_status()
            
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Clipboard Unavailable")
            
            if temp_file:
                msg.setText("Cannot copy to clipboard, but saved LaTeX code to temporary file.")
                msg.setDetailedText(f"File location: {temp_file}\n\n"
                                  f"Error: {result.get('error', 'Unknown error')}\n"
                                  f"Suggestion: {clipboard_status.get('suggestion', 'No suggestions available')}")
                msg.setInformativeText("You can open this file to copy the LaTeX code manually.")
            else:
                msg.setText("Cannot copy to clipboard and failed to save temporary file.")
                msg.setDetailedText(f"Error: {result.get('error', 'Unknown error')}\n"
                                  f"Suggestion: {clipboard_status.get('suggestion', 'No suggestions available')}")
                msg.setInformativeText("Please install clipboard support or manually copy from the preview panel.")
            
            msg.exec()
            self.statusbar.showMessage("Clipboard operation failed - see message for details")
    
    def paste_from_clipboard(self):
        """Handle paste operation - delegate to table editor"""
        self.table_editor.paste_from_clipboard()
    
    def new_table(self):
        self.table_model.clear()
        self.table_editor.refresh_table()
        self.update_preview()
        self.statusbar.showMessage("New table created")
    
    def open_file(self):
        pass
    
    def save_file(self):
        pass
    
    
    def show_system_info(self):
        from PySide6.QtWidgets import QMessageBox
        from utils.clipboard import get_clipboard_status
        import subprocess
        import sys
        
        # Check system capabilities
        info = []
        info.append(f"Python: {sys.version}")
        info.append(f"Platform: {sys.platform}")
        
        # Check LaTeX
        try:
            result = subprocess.run(['pdflatex', '--version'], 
                                  capture_output=True, timeout=5)
            if result.returncode == 0:
                latex_version = result.stdout.decode().split('\n')[0]
                info.append(f"LaTeX: {latex_version}")
            else:
                info.append("LaTeX: Not available")
        except:
            info.append("LaTeX: Not installed")
        
        # Check ImageMagick
        try:
            result = subprocess.run(['convert', '--version'], 
                                  capture_output=True, timeout=5)
            if result.returncode == 0:
                convert_version = result.stdout.decode().split('\n')[0]
                info.append(f"ImageMagick: {convert_version}")
            else:
                info.append("ImageMagick: Not available")
        except:
            info.append("ImageMagick: Not installed")
        
        # Check clipboard
        clipboard_status = get_clipboard_status()
        if clipboard_status["available"]:
            info.append(f"Clipboard: Available ({clipboard_status['method']})")
        else:
            info.append(f"Clipboard: Not available - {clipboard_status['suggestion']}")
        
        msg = QMessageBox()
        msg.setWindowTitle("System Information")
        msg.setText("LaTeX Table Builder - System Status")
        msg.setDetailedText('\n'.join(info))
        msg.exec()
    
    def show_installation_guide(self):
        from PySide6.QtWidgets import QMessageBox
        
        guide = """LaTeX Table Builder - Installation Guide

MINIMAL INSTALLATION (for preview only):
Download size: ~150-200MB

• Ubuntu/Debian: sudo apt-get install texlive-latex-base texlive-latex-recommended texlive-fonts-recommended imagemagick
• Fedora: sudo dnf install texlive-latex ImageMagick  
• Arch: sudo pacman -S texlive-core imagemagick
• macOS: brew install --cask basictex && brew install imagemagick

FULL INSTALLATION (for document creation):
• Ubuntu/Debian: sudo apt-get install texlive-latex-base texlive-latex-extra texlive-fonts-recommended
• Fedora: sudo dnf install texlive-latex texlive-latex-extra
• macOS: brew install --cask mactex
• Windows: Install MiKTeX or TeX Live

CLIPBOARD SUPPORT (Linux only):
• Install xclip: sudo apt-get install xclip
• Or install xsel: sudo apt-get install xsel
• Quick fix: ./fix_clipboard.sh

QUICK SETUP:
• LaTeX: ./install_minimal_latex.sh
• Clipboard: ./fix_clipboard.sh

What you get with minimal installation:
✓ LaTeX table preview in the application
✓ PDF generation for basic tables
✓ All standard table packages (tabular, booktabs, etc.)

You DON'T need the full LaTeX installation unless you plan to:
• Create complete LaTeX documents outside this application
• Use advanced LaTeX packages not related to tables

After installation, restart the application to detect new tools."""
        
        msg = QMessageBox()
        msg.setWindowTitle("Installation Guide")
        msg.setText("Installation Instructions")
        msg.setDetailedText(guide)
        msg.exec()
    
    def show_about(self):
        from PySide6.QtWidgets import QMessageBox
        
        about_text = """LaTeX Table Builder v0.1.0

A cross-platform LaTeX table builder with modern GUI interface.

Features:
• Spreadsheet-like table editor with merged cell support
• Multiple LaTeX formats (tabular, longtable, booktabs, array)
• Live LaTeX preview
• One-click clipboard export
• Table preset save/load functionality

Developed with Python and PySide6/Qt.

For more information, see the README file."""
        
        msg = QMessageBox()
        msg.setWindowTitle("About LaTeX Table Builder")
        msg.setText(about_text)
        msg.exec()