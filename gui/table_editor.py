from PySide6.QtWidgets import (QTableWidget, QTableWidgetItem, QHeaderView, 
                               QAbstractItemView, QApplication, QMessageBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor, QPalette
from core.table_model import TableModel


class TableEditor(QTableWidget):
    cell_changed = Signal(int, int, str)
    toggle_headers_requested = Signal()
    
    def __init__(self, table_model: TableModel):
        super().__init__()
        self.table_model = table_model
        self.dark_theme = True  # Track current theme
        self.setup_table()
        self.connect_signals()
        self.apply_theme()
        
    def setup_table(self):
        self.setRowCount(self.table_model.rows)
        self.setColumnCount(self.table_model.cols)
        
        self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.verticalHeader().setSectionResizeMode(QHeaderView.Interactive)
        
        self.horizontalHeader().setDefaultSectionSize(100)
        self.verticalHeader().setDefaultSectionSize(30)
        
        font = QFont()
        font.setPointSize(10)
        self.setFont(font)
        
        self.setAlternatingRowColors(True)
        
        self.populate_table()
        
    def apply_theme(self):
        """Apply the current theme to the table"""
        if self.dark_theme:
            # Dark theme
            self.setStyleSheet("""
                QTableWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                    gridline-color: #555555;
                    selection-background-color: #505050;
                    selection-color: #ffffff;
                }
                QTableWidget::item {
                    background-color: #2b2b2b;
                    color: #ffffff;
                    border: 1px solid #555555;
                }
                QTableWidget::item:selected {
                    background-color: #505050;
                    color: #ffffff;
                }
                QTableWidget::item:hover {
                    background-color: #404040;
                }
                QHeaderView::section {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555555;
                    padding: 4px;
                }
            """)
        else:
            # Light theme
            self.setStyleSheet("""
                QTableWidget {
                    background-color: #ffffff;
                    color: #000000;
                    gridline-color: #cccccc;
                    selection-background-color: #316AC5;
                    selection-color: #ffffff;
                }
                QTableWidget::item {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #cccccc;
                }
                QTableWidget::item:selected {
                    background-color: #316AC5;
                    color: #ffffff;
                }
                QTableWidget::item:hover {
                    background-color: #e6f3ff;
                }
                QHeaderView::section {
                    background-color: #f0f0f0;
                    color: #000000;
                    border: 1px solid #cccccc;
                    padding: 4px;
                }
            """)
    
    def set_theme(self, dark_theme: bool):
        """Switch between dark and light theme"""
        self.dark_theme = dark_theme
        self.apply_theme()
        self.refresh_table()  # Refresh to update cell colors
        
    def connect_signals(self):
        self.cellChanged.connect(self.on_cell_changed)
        
    def populate_table(self):
        for row in range(self.table_model.rows):
            for col in range(self.table_model.cols):
                cell = self.table_model.get_cell(row, col)
                if cell and not cell.is_merged_part:
                    item = QTableWidgetItem(cell.content)
                    
                    if cell.alignment == 'l':
                        item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    elif cell.alignment == 'c':
                        item.setTextAlignment(Qt.AlignCenter)
                    elif cell.alignment == 'r':
                        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    
                    # Style header cells
                    if cell.is_header or cell.is_bold:
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)
                        if self.dark_theme:
                            item.setBackground(QColor(70, 80, 100))  # Dark blue for headers
                            item.setForeground(QColor(255, 255, 255))  # White text
                        else:
                            item.setBackground(QColor(230, 240, 250))  # Light blue for headers
                            item.setForeground(QColor(0, 0, 0))  # Black text
                    else:
                        # Set default colors for non-header cells
                        if self.dark_theme:
                            item.setForeground(QColor(255, 255, 255))  # White text
                        else:
                            item.setForeground(QColor(0, 0, 0))  # Black text
                    
                    self.setItem(row, col, item)
                    
                    if cell.span.row_span > 1 or cell.span.col_span > 1:
                        self.setSpan(row, col, cell.span.row_span, cell.span.col_span)
                        if self.dark_theme:
                            item.setBackground(QColor(60, 70, 90))  # Dark merged cell color
                        else:
                            item.setBackground(QColor(240, 248, 255))  # Light merged cell color
                elif cell and cell.is_merged_part:
                    item = QTableWidgetItem("")
                    item.setFlags(Qt.NoItemFlags)
                    if self.dark_theme:
                        item.setBackground(QColor(45, 45, 45))  # Dark gray for merged parts
                    else:
                        item.setBackground(QColor(245, 245, 245))  # Light gray for merged parts
                    self.setItem(row, col, item)
    
    def refresh_table(self):
        self.clearSpans()
        self.setRowCount(self.table_model.rows)
        self.setColumnCount(self.table_model.cols)
        
        self.blockSignals(True)
        self.clear()
        self.populate_table()
        self.blockSignals(False)
        
    def on_cell_changed(self, row: int, col: int):
        item = self.item(row, col)
        if item:
            content = item.text()
            self.table_model.set_cell_content(row, col, content)
            self.cell_changed.emit(row, col, content)
    
    def get_selected_ranges(self):
        ranges = []
        selected_ranges = self.selectedRanges()
        
        for selected_range in selected_ranges:
            start_row = selected_range.topRow()
            start_col = selected_range.leftColumn()
            end_row = selected_range.bottomRow()
            end_col = selected_range.rightColumn()
            ranges.append((start_row, start_col, end_row, end_col))
        
        return ranges
    
    def get_selection_type(self):
        """Determine if selection is rows, columns, or mixed"""
        ranges = self.get_selected_ranges()
        if not ranges:
            return "none", []
        
        # Analyze the selection pattern
        all_rows = set()
        all_cols = set()
        all_cells = []
        
        for start_row, start_col, end_row, end_col in ranges:
            # Check if this range spans entire rows
            if start_col == 0 and end_col == self.columnCount() - 1:
                for row in range(start_row, end_row + 1):
                    all_rows.add(row)
            # Check if this range spans entire columns  
            elif start_row == 0 and end_row == self.rowCount() - 1:
                for col in range(start_col, end_col + 1):
                    all_cols.add(col)
            else:
                # Individual cells or partial ranges
                for row in range(start_row, end_row + 1):
                    for col in range(start_col, end_col + 1):
                        all_cells.append((row, col))
        
        # Determine selection type
        if all_rows and not all_cols and not all_cells:
            return "rows", list(all_rows)
        elif all_cols and not all_rows and not all_cells:
            return "columns", list(all_cols)
        elif all_cells and not all_rows and not all_cols:
            return "cells", all_cells
        else:
            return "mixed", {"rows": list(all_rows), "columns": list(all_cols), "cells": all_cells}
    
    def get_selected_rows(self):
        """Get list of fully selected rows"""
        selection_type, data = self.get_selection_type()
        if selection_type == "rows":
            return data
        elif selection_type == "mixed":
            return data.get("rows", [])
        return []
    
    def get_selected_columns(self):
        """Get list of fully selected columns"""
        selection_type, data = self.get_selection_type()
        if selection_type == "columns":
            return data
        elif selection_type == "mixed":
            return data.get("columns", [])
        return []
    
    def select_range(self, start_row: int, start_col: int, end_row: int, end_col: int):
        self.setRangeSelected(
            self.model().createIndex(start_row, start_col),
            self.model().createIndex(end_row, end_col),
            True
        )
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.delete_selected_cells()
        elif event.key() == Qt.Key_Tab:
            self.move_to_next_cell()
        elif event.key() == Qt.Key_Backtab:
            self.move_to_previous_cell()
        elif (event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_V):
            self.paste_from_clipboard()
        else:
            super().keyPressEvent(event)
    
    def delete_selected_cells(self):
        selected_ranges = self.get_selected_ranges()
        for start_row, start_col, end_row, end_col in selected_ranges:
            for row in range(start_row, end_row + 1):
                for col in range(start_col, end_col + 1):
                    self.table_model.set_cell_content(row, col, "")
                    item = self.item(row, col)
                    if item:
                        item.setText("")
    
    def move_to_next_cell(self):
        current_row = self.currentRow()
        current_col = self.currentColumn()
        
        next_col = current_col + 1
        next_row = current_row
        
        if next_col >= self.columnCount():
            next_col = 0
            next_row += 1
            
        if next_row >= self.rowCount():
            next_row = 0
            
        self.setCurrentCell(next_row, next_col)
    
    def move_to_previous_cell(self):
        current_row = self.currentRow()
        current_col = self.currentColumn()
        
        prev_col = current_col - 1
        prev_row = current_row
        
        if prev_col < 0:
            prev_col = self.columnCount() - 1
            prev_row -= 1
            
        if prev_row < 0:
            prev_row = self.rowCount() - 1
            
        self.setCurrentCell(prev_row, prev_col)
    
    def paste_from_clipboard(self):
        """Handle paste operation from clipboard"""
        from utils.clipboard import get_from_clipboard
        from utils.paste_parser import PasteParser
        
        # Get clipboard data
        clipboard_data = get_from_clipboard()
        if not clipboard_data:
            QMessageBox.information(self, "Paste", "No data found in clipboard")
            return
        
        # Parse clipboard data
        table_data, metadata = PasteParser.parse_clipboard_data(clipboard_data)
        
        if not metadata.get("success", False):
            QMessageBox.warning(self, "Paste Error", 
                              f"Failed to parse clipboard data:\n{metadata.get('error', 'Unknown error')}")
            return
        
        if not table_data:
            QMessageBox.information(self, "Paste", "No table data found in clipboard")
            return
        
        # Get current selection or cursor position
        current_row = self.currentRow()
        current_col = self.currentColumn()
        
        # If no valid position, start at (0,0)
        if current_row < 0:
            current_row = 0
        if current_col < 0:
            current_col = 0
        
        # Check if we need to resize the table
        required_rows = current_row + metadata["rows"]
        required_cols = current_col + metadata["cols"]
        
        needs_resize = (required_rows > self.table_model.rows or 
                       required_cols > self.table_model.cols)
        
        if needs_resize:
            # Ask user for confirmation
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Question)
            msg.setWindowTitle("Resize Table")
            msg.setText("The pasted data is larger than the current table.")
            msg.setInformativeText(f"Current table: {self.table_model.rows}×{self.table_model.cols}\n"
                                 f"Required size: {required_rows}×{required_cols}\n\n"
                                 f"Resize table to accommodate pasted data?")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.Yes)
            
            if msg.exec() == QMessageBox.Yes:
                # Resize the table
                new_rows = max(self.table_model.rows, required_rows)
                new_cols = max(self.table_model.cols, required_cols)
                
                if not self.table_model.resize(new_rows, new_cols):
                    QMessageBox.warning(self, "Resize Error", "Failed to resize table")
                    return
                
                # Update spinboxes in main window if available
                main_window = self.window()
                if hasattr(main_window, 'rows_spinbox'):
                    main_window.rows_spinbox.setValue(new_rows)
                if hasattr(main_window, 'cols_spinbox'):
                    main_window.cols_spinbox.setValue(new_cols)
            else:
                # User declined resize, ask how to handle
                msg2 = QMessageBox()
                msg2.setIcon(QMessageBox.Question)
                msg2.setWindowTitle("Paste Options")
                msg2.setText("How would you like to handle the oversized data?")
                msg2.addButton("Paste what fits", QMessageBox.AcceptRole)
                msg2.addButton("Cancel", QMessageBox.RejectRole)
                
                if msg2.exec() != QMessageBox.AcceptRole:
                    return
        
        # Perform the paste operation
        pasted_cells = 0
        skipped_cells = 0
        
        for row_idx, row_data in enumerate(table_data):
            target_row = current_row + row_idx
            if target_row >= self.table_model.rows:
                break
                
            for col_idx, cell_content in enumerate(row_data):
                target_col = current_col + col_idx
                if target_col >= self.table_model.cols:
                    break
                
                # Check if cell is part of a merged region
                cell = self.table_model.get_cell(target_row, target_col)
                if cell and cell.is_merged_part:
                    skipped_cells += 1
                    continue
                
                # Set cell content
                self.table_model.set_cell_content(target_row, target_col, cell_content)
                pasted_cells += 1
        
        # Refresh the table display
        self.refresh_table()
        
        # Show status message
        main_window = self.window()
        if hasattr(main_window, 'statusbar'):
            if skipped_cells > 0:
                main_window.statusbar.showMessage(
                    f"Pasted {pasted_cells} cells, skipped {skipped_cells} merged cells")
            else:
                main_window.statusbar.showMessage(f"Pasted {pasted_cells} cells")
        
        # Emit signal to update preview
        self.cell_changed.emit(current_row, current_col, "")
    
    def contextMenuEvent(self, event):
        from PySide6.QtWidgets import QMenu
        from PySide6.QtGui import QAction
        
        menu = QMenu(self)
        
        # Header actions
        selection_type, data = self.get_selection_type()
        
        if selection_type == "rows":
            header_action = QAction(f"Toggle Row Header(s)", self)
        elif selection_type == "columns":
            header_action = QAction(f"Toggle Column Header(s)", self)
        else:
            header_action = QAction("Toggle Header", self)
        
        header_action.triggered.connect(self.toggle_headers_context)
        menu.addAction(header_action)
        
        menu.addSeparator()
        
        paste_action = QAction("Paste", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.paste_from_clipboard)
        menu.addAction(paste_action)
        
        menu.addSeparator()
        
        merge_action = QAction("Merge Cells", self)
        merge_action.triggered.connect(self.merge_selected_cells)
        menu.addAction(merge_action)
        
        unmerge_action = QAction("Unmerge Cells", self)
        unmerge_action.triggered.connect(self.unmerge_selected_cells)
        menu.addAction(unmerge_action)
        
        menu.addSeparator()
        
        align_left_action = QAction("Align Left", self)
        align_left_action.triggered.connect(lambda: self.set_alignment("l"))
        menu.addAction(align_left_action)
        
        align_center_action = QAction("Align Center", self)
        align_center_action.triggered.connect(lambda: self.set_alignment("c"))
        menu.addAction(align_center_action)
        
        align_right_action = QAction("Align Right", self)
        align_right_action.triggered.connect(lambda: self.set_alignment("r"))
        menu.addAction(align_right_action)
        
        menu.exec(event.globalPos())
    
    def toggle_headers_context(self):
        """Toggle headers from context menu"""
        self.toggle_headers_requested.emit()
    
    def merge_selected_cells(self):
        selected_ranges = self.get_selected_ranges()
        if not selected_ranges:
            return
        
        start_row, start_col, end_row, end_col = selected_ranges[0]
        
        if self.table_model.merge_cells(start_row, start_col, end_row, end_col):
            self.refresh_table()
    
    def unmerge_selected_cells(self):
        selected_ranges = self.get_selected_ranges()
        if not selected_ranges:
            return
        
        start_row, start_col, _, _ = selected_ranges[0]
        
        if self.table_model.unmerge_cells(start_row, start_col):
            self.refresh_table()
    
    def set_alignment(self, alignment: str):
        selected_ranges = self.get_selected_ranges()
        for start_row, start_col, end_row, end_col in selected_ranges:
            for row in range(start_row, end_row + 1):
                for col in range(start_col, end_col + 1):
                    self.table_model.set_cell_alignment(row, col, alignment)
                    item = self.item(row, col)
                    if item:
                        if alignment == 'l':
                            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                        elif alignment == 'c':
                            item.setTextAlignment(Qt.AlignCenter)
                        elif alignment == 'r':
                            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)