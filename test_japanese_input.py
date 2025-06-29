#!/usr/bin/env python3
"""
Test script for Japanese IME input in table cells

This script creates a simple table widget to test Japanese input functionality.
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt, QLocale
from gui.table_editor import TableEditor
from core.table_model import TableModel

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Japanese IME Test - LaTeX Table Builder")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Add instructions
        instructions = QLabel("""
Japanese IME Input Test

Instructions:
1. Double-click on any table cell to edit
2. Try typing Japanese characters using your IME (mozc)
3. Press Enter to confirm the input
4. Check if Japanese characters appear correctly

Test examples:
- ひらがな (hiragana)
- カタカナ (katakana)  
- 漢字 (kanji)
- こんにちは (konnichiwa)
- ありがとう (arigatou)
        """)
        instructions.setStyleSheet("font-size: 12px; padding: 10px; background-color: #f0f0f0;")
        layout.addWidget(instructions)
        
        # Create test table
        table_model = TableModel(rows=5, cols=3)
        table_model.set_cell_content(0, 0, "Test Cell")
        table_model.set_cell_content(0, 1, "日本語テスト")
        table_model.set_cell_content(0, 2, "Japanese Test")
        
        self.table_editor = TableEditor(table_model)
        layout.addWidget(self.table_editor)
        
        # Set status message
        self.statusBar().showMessage("Ready for Japanese input testing")

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Japanese IME Test")
    
    # Configure for Japanese input
    import locale
    import os
    
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
    
    # Enable IME support
    app.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings, False)
    
    # Set locale
    try:
        locale.setlocale(locale.LC_ALL, '')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        except locale.Error:
            pass
    
    QLocale.setDefault(QLocale.system())
    
    window = TestWindow()
    window.show()
    
    print("Japanese IME Test Window opened")
    print("Try typing Japanese characters in the table cells")
    print("Close the window to exit")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()