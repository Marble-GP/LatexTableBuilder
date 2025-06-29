#!/usr/bin/env python3

import sys
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("LaTeX Table Builder")
    app.setApplicationVersion("1.1.0")
    
    # Configure for international text support including Japanese
    import locale
    from PySide6.QtCore import QLocale, QTranslator
    
    # Set UTF-8 encoding for text handling
    import os
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
    
    # Enable input method support for Japanese and other languages
    from PySide6.QtCore import Qt
    app.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings, False)
    
    # Set locale to system default (supports Japanese locale if system is configured)
    try:
        locale.setlocale(locale.LC_ALL, '')
    except locale.Error:
        # Fallback to UTF-8 if system locale is not available
        try:
            locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
        except locale.Error:
            pass  # Use default locale
    
    # Set Qt locale for proper text rendering and input methods
    QLocale.setDefault(QLocale.system())
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()