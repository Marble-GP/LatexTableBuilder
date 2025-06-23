from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                               QPushButton, QLabel, QScrollArea, QSplitter, QSlider, QSpinBox)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QPixmap, QPainter
import tempfile
import os
import subprocess
from pathlib import Path


class LaTeXRenderThread(QThread):
    render_finished = Signal(str, bool)  # image_path, success
    
    def __init__(self, latex_code: str):
        super().__init__()
        self.latex_code = latex_code
    
    def run(self):
        try:
            success, image_path = self._render_latex()
            self.render_finished.emit(image_path, success)
        except Exception as e:
            print(f"LaTeX rendering error: {e}")
            self.render_finished.emit("", False)
    
    def _render_latex(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            tex_file = temp_path / "table.tex"
            pdf_file = temp_path / "table.pdf"
            png_file = temp_path / "table.png"
            
            # Use smart package detection to only include available packages
            from utils.latex_packages import get_safe_latex_document
            complete_latex = get_safe_latex_document(self.latex_code)
            
            with open(tex_file, 'w', encoding='utf-8') as f:
                f.write(complete_latex)
            
            try:
                result = subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', str(tex_file)],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0 or not pdf_file.exists():
                    return False, ""
                
                # Use higher density for better quality and auto-crop to table content
                convert_result = subprocess.run(
                    ['convert', '-density', '300', '-quality', '100', '-trim', '+repage', str(pdf_file), str(png_file)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if convert_result.returncode != 0 or not png_file.exists():
                    return False, ""
                
                final_png = Path.home() / ".latex_table_builder" / "preview.png"
                final_png.parent.mkdir(exist_ok=True)
                
                import shutil
                shutil.copy2(png_file, final_png)
                
                return True, str(final_png)
                
            except (subprocess.TimeoutExpired, FileNotFoundError) as e:
                print(f"LaTeX compilation error: {e}")
                return False, ""


class PreviewWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.current_latex = ""
        self.render_thread = None
        self.zoom_factor = 1.0  # Current zoom level
        self.original_pixmap = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header with controls
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("LaTeX Preview"))
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_preview)
        header_layout.addWidget(self.refresh_btn)
        
        self.toggle_btn = QPushButton("Show Code")
        self.toggle_btn.clicked.connect(self.toggle_view)
        header_layout.addWidget(self.toggle_btn)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Zoom controls
        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(QLabel("Zoom:"))
        
        # Zoom out button
        self.zoom_out_btn = QPushButton("-")
        self.zoom_out_btn.setMaximumWidth(30)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        zoom_layout.addWidget(self.zoom_out_btn)
        
        # Zoom slider
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(25)  # 25%
        self.zoom_slider.setMaximum(500)  # 500%
        self.zoom_slider.setValue(100)   # 100%
        self.zoom_slider.setTickPosition(QSlider.TicksBelow)
        self.zoom_slider.setTickInterval(50)
        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)
        zoom_layout.addWidget(self.zoom_slider)
        
        # Zoom in button
        self.zoom_in_btn = QPushButton("+")
        self.zoom_in_btn.setMaximumWidth(30)
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        zoom_layout.addWidget(self.zoom_in_btn)
        
        # Zoom percentage display
        self.zoom_label = QLabel("100%")
        self.zoom_label.setMinimumWidth(50)
        zoom_layout.addWidget(self.zoom_label)
        
        # Reset zoom button
        self.reset_zoom_btn = QPushButton("Reset")
        self.reset_zoom_btn.clicked.connect(self.reset_zoom)
        zoom_layout.addWidget(self.reset_zoom_btn)
        
        # Fit to window button
        self.fit_btn = QPushButton("Fit")
        self.fit_btn.clicked.connect(self.fit_to_window)
        zoom_layout.addWidget(self.fit_btn)
        
        zoom_layout.addStretch()
        layout.addLayout(zoom_layout)
        
        self.splitter = QSplitter(Qt.Vertical)
        layout.addWidget(self.splitter)
        
        self.setup_preview_area()
        self.setup_code_area()
        
        self.splitter.setSizes([400, 200])
        self.code_widget.hide()
        
        # Set initial zoom to fit window
        self.setFocusPolicy(Qt.StrongFocus)
    
    def setup_preview_area(self):
        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setMinimumHeight(300)
        
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: white; border: 1px solid gray;")
        self.preview_label.setText("LaTeX preview will appear here")
        
        self.preview_scroll.setWidget(self.preview_label)
        self.splitter.addWidget(self.preview_scroll)
    
    def setup_code_area(self):
        self.code_widget = QWidget()
        code_layout = QVBoxLayout(self.code_widget)
        
        code_layout.addWidget(QLabel("Generated LaTeX Code:"))
        
        self.code_edit = QTextEdit()
        self.code_edit.setReadOnly(True)
        self.code_edit.setMaximumHeight(200)
        
        font = QFont("Courier New", 9)
        self.code_edit.setFont(font)
        
        code_layout.addWidget(self.code_edit)
        
        code_buttons = QHBoxLayout()
        
        copy_code_btn = QPushButton("Copy Code")
        copy_code_btn.clicked.connect(self.copy_code)
        code_buttons.addWidget(copy_code_btn)
        
        save_code_btn = QPushButton("Save as File")
        save_code_btn.clicked.connect(self.save_code)
        code_buttons.addWidget(save_code_btn)
        
        code_buttons.addStretch()
        code_layout.addLayout(code_buttons)
        
        self.splitter.addWidget(self.code_widget)
    
    def update_preview(self, latex_code: str):
        self.current_latex = latex_code
        self.code_edit.setPlainText(latex_code)
        
        latex_status = self._check_latex_availability()
        
        if latex_status["available"]:
            self._render_latex(latex_code)
        else:
            missing_tools = latex_status["missing"]
            error_msg = "LaTeX Preview Unavailable\n\n"
            error_msg += "Missing required tools:\n"
            for tool in missing_tools:
                error_msg += f"• {tool}\n"
            error_msg += "\nInstall instructions:\n"
            error_msg += "• LaTeX: sudo apt-get install texlive-latex-base\n"
            error_msg += "• ImageMagick: sudo apt-get install imagemagick"
            
            self.preview_label.setText(error_msg)
            self.preview_label.setWordWrap(True)
            self.preview_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
            self.preview_label.setStyleSheet("""
                background-color: #fff3cd; 
                border: 1px solid #ffeaa7; 
                color: #856404;
                padding: 20px;
                font-family: Arial;
                font-size: 12px;
            """)
    
    def _check_latex_availability(self):
        missing = []
        
        try:
            subprocess.run(['pdflatex', '--version'], 
                         capture_output=True, timeout=5)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            missing.append("pdflatex (LaTeX)")
        
        try:
            subprocess.run(['convert', '--version'], 
                         capture_output=True, timeout=5)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            missing.append("convert (ImageMagick)")
        
        return {
            "available": len(missing) == 0,
            "missing": missing
        }
    
    def _is_latex_available(self):
        return self._check_latex_availability()["available"]
    
    def _render_latex(self, latex_code: str):
        if self.render_thread and self.render_thread.isRunning():
            self.render_thread.terminate()
            self.render_thread.wait()
        
        self.preview_label.setText("Rendering LaTeX...")
        self.refresh_btn.setEnabled(False)
        
        self.render_thread = LaTeXRenderThread(latex_code)
        self.render_thread.render_finished.connect(self._on_render_finished)
        self.render_thread.start()
    
    def _on_render_finished(self, image_path: str, success: bool):
        self.refresh_btn.setEnabled(True)
        
        if success and image_path and os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # Store original pixmap for resizing
                self.original_pixmap = pixmap
                
                # Set a reasonable initial zoom (try to fit, but minimum 75%)
                self._set_initial_zoom()
                self._scale_pixmap_to_fit()
            else:
                self.preview_label.setText("Failed to load rendered image")
        else:
            self.preview_label.setText("LaTeX rendering failed\nCheck your LaTeX installation")
    
    def _set_initial_zoom(self):
        """Set a reasonable initial zoom level for new images"""
        if not hasattr(self, 'original_pixmap') or self.original_pixmap.isNull():
            return
        
        # Calculate fit zoom for table content
        available_size = self.preview_scroll.viewport().size()
        available_width = available_size.width() - 60  # More margin for better fit
        available_height = available_size.height() - 60
        
        original_size = self.original_pixmap.size()
        
        scale_x = available_width / original_size.width()
        scale_y = available_height / original_size.height()
        fit_scale = min(scale_x, scale_y)
        
        # Use 90% of optimal fit for better visibility, with good range
        initial_scale = fit_scale * 0.9
        initial_scale = max(0.75, min(initial_scale, 2.0))
        initial_zoom = int(initial_scale * 100)
        
        # Set zoom slider without triggering preserve/restore (since it's a new image)
        self.zoom_slider.blockSignals(True)
        self.zoom_slider.setValue(initial_zoom)
        self.zoom_slider.blockSignals(False)
        
        # Update zoom factor and label
        self.zoom_factor = initial_scale
        self.zoom_label.setText(f"{initial_zoom}%")
        
        # Center the content after initial load
        from PySide6.QtCore import QTimer
        QTimer.singleShot(100, self._center_content)
    
    def _scale_pixmap_to_fit(self):
        """Scale the pixmap based on current zoom level"""
        if not hasattr(self, 'original_pixmap') or self.original_pixmap.isNull():
            return
        
        # Calculate target size based on zoom factor
        original_size = self.original_pixmap.size()
        target_width = int(original_size.width() * self.zoom_factor)
        target_height = int(original_size.height() * self.zoom_factor)
        
        # Scale with high quality
        scaled_pixmap = self.original_pixmap.scaled(
            target_width, target_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        self.preview_label.setPixmap(scaled_pixmap)
        
        # Adjust label size to pixmap
        self.preview_label.resize(scaled_pixmap.size())
    
    def on_zoom_changed(self, value):
        """Handle zoom slider changes while preserving view position"""
        # Store current center point before zoom
        self._preserve_center_point()
        
        # Update zoom
        old_zoom = self.zoom_factor
        self.zoom_factor = value / 100.0
        self.zoom_label.setText(f"{value}%")
        self._scale_pixmap_to_fit()
        
        # Restore center point after zoom
        self._restore_center_point(old_zoom)
    
    def _preserve_center_point(self):
        """Store the current center point of the view"""
        if not hasattr(self, 'preview_scroll'):
            return
        
        # Get current scroll position
        h_scrollbar = self.preview_scroll.horizontalScrollBar()
        v_scrollbar = self.preview_scroll.verticalScrollBar()
        
        # Calculate center point as percentage of total scrollable area
        if h_scrollbar.maximum() > 0:
            self._center_x_ratio = (h_scrollbar.value() + h_scrollbar.pageStep() / 2) / h_scrollbar.maximum()
        else:
            self._center_x_ratio = 0.5
            
        if v_scrollbar.maximum() > 0:
            self._center_y_ratio = (v_scrollbar.value() + v_scrollbar.pageStep() / 2) / v_scrollbar.maximum()
        else:
            self._center_y_ratio = 0.5
    
    def _restore_center_point(self, old_zoom=None):
        """Restore the center point after zoom change"""
        if not hasattr(self, '_center_x_ratio') or not hasattr(self, 'preview_scroll'):
            return
        
        # Wait for the widget to update its size
        from PySide6.QtCore import QTimer
        QTimer.singleShot(10, self._do_restore_center_point)
    
    def _do_restore_center_point(self):
        """Actually perform the center point restoration"""
        if not hasattr(self, '_center_x_ratio'):
            return
            
        h_scrollbar = self.preview_scroll.horizontalScrollBar()
        v_scrollbar = self.preview_scroll.verticalScrollBar()
        
        # Calculate new scroll position to maintain center point
        if h_scrollbar.maximum() > 0:
            new_h_pos = int(self._center_x_ratio * h_scrollbar.maximum() - h_scrollbar.pageStep() / 2)
            new_h_pos = max(0, min(new_h_pos, h_scrollbar.maximum()))
            h_scrollbar.setValue(new_h_pos)
        
        if v_scrollbar.maximum() > 0:
            new_v_pos = int(self._center_y_ratio * v_scrollbar.maximum() - v_scrollbar.pageStep() / 2)
            new_v_pos = max(0, min(new_v_pos, v_scrollbar.maximum()))
            v_scrollbar.setValue(new_v_pos)
    
    def zoom_in(self):
        """Zoom in by 25%"""
        current_value = self.zoom_slider.value()
        new_value = min(current_value + 25, self.zoom_slider.maximum())
        self.zoom_slider.setValue(new_value)
    
    def zoom_out(self):
        """Zoom out by 25%"""
        current_value = self.zoom_slider.value()
        new_value = max(current_value - 25, self.zoom_slider.minimum())
        self.zoom_slider.setValue(new_value)
    
    def reset_zoom(self):
        """Reset zoom to 100%"""
        self.zoom_slider.setValue(100)
    
    def fit_to_window(self):
        """Fit the image to the available window space and center the table content"""
        if not hasattr(self, 'original_pixmap') or self.original_pixmap.isNull():
            return
        
        # Get available size (subtract scrollbar space and margins)
        available_size = self.preview_scroll.viewport().size()
        # Reserve space for scrollbars and margins
        available_width = available_size.width() - 60  # More margin for better fit
        available_height = available_size.height() - 60
        
        original_size = self.original_pixmap.size()
        
        # Calculate scale factor to fit comfortably with padding
        scale_x = available_width / original_size.width()
        scale_y = available_height / original_size.height()
        scale_factor = min(scale_x, scale_y)
        
        # Use a slightly smaller scale for better visibility (90% of optimal fit)
        scale_factor = scale_factor * 0.9
        
        # Set reasonable bounds: minimum 75% for readability, maximum 300% for very small tables
        scale_factor = max(0.75, min(scale_factor, 3.0))
        
        # Convert to percentage and set slider
        zoom_percentage = int(scale_factor * 100)
        zoom_percentage = max(self.zoom_slider.minimum(), 
                            min(zoom_percentage, self.zoom_slider.maximum()))
        
        # First set the zoom
        self.zoom_slider.setValue(zoom_percentage)
        
        # Center the content after a brief delay to ensure scaling is complete
        from PySide6.QtCore import QTimer
        QTimer.singleShot(50, self._center_content)
    
    def _center_content(self):
        """Center the table content in the scroll area"""
        if not hasattr(self, 'original_pixmap') or self.original_pixmap.isNull():
            return
        
        # Get the scroll area and content sizes
        scroll_area = self.preview_scroll
        content_size = self.preview_label.size()
        viewport_size = scroll_area.viewport().size()
        
        # Calculate center position
        center_x = max(0, (content_size.width() - viewport_size.width()) // 2)
        center_y = max(0, (content_size.height() - viewport_size.height()) // 2)
        
        # Set scroll position to center
        scroll_area.horizontalScrollBar().setValue(center_x)
        scroll_area.verticalScrollBar().setValue(center_y)
    
    def refresh_preview(self):
        if self.current_latex:
            self.update_preview(self.current_latex)
    
    def toggle_view(self):
        if self.code_widget.isVisible():
            self.code_widget.hide()
            self.toggle_btn.setText("Show Code")
        else:
            self.code_widget.show()
            self.toggle_btn.setText("Hide Code")
    
    def copy_code(self):
        from utils.clipboard import copy_to_clipboard, save_to_temp_file, get_clipboard_status
        from PySide6.QtWidgets import QMessageBox
        
        result = copy_to_clipboard(self.current_latex)
        
        if result["success"]:
            method = result["method"]
            if result["fallback_used"]:
                print(f"LaTeX code copied using {method} (fallback method)")
            else:
                print("LaTeX code copied to clipboard")
        else:
            # Show message box for clipboard failure
            temp_file = save_to_temp_file(self.current_latex)
            clipboard_status = get_clipboard_status()
            
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Clipboard Unavailable")
            
            if temp_file:
                msg.setText("Cannot copy to clipboard, but saved LaTeX code to temporary file.")
                msg.setDetailedText(f"File location: {temp_file}\n\n"
                                  f"Error: {result.get('error', 'Unknown error')}\n"
                                  f"Suggestion: {clipboard_status.get('suggestion', 'No suggestions available')}")
            else:
                msg.setText("Cannot copy to clipboard and failed to save temporary file.")
                msg.setDetailedText(f"Error: {result.get('error', 'Unknown error')}\n"
                                  f"Suggestion: {clipboard_status.get('suggestion', 'No suggestions available')}")
            
            msg.exec()
    
    def save_code(self):
        from PySide6.QtWidgets import QFileDialog
        
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save LaTeX Code",
            "table.tex",
            "LaTeX Files (*.tex);;All Files (*)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.current_latex)
                print(f"LaTeX code saved to {filename}")
            except Exception as e:
                print(f"Failed to save file: {e}")
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts for zoom"""
        if event.key() == Qt.Key_Plus or (event.key() == Qt.Key_Equal and event.modifiers() & Qt.ControlModifier):
            self.zoom_in()
        elif event.key() == Qt.Key_Minus and event.modifiers() & Qt.ControlModifier:
            self.zoom_out()
        elif event.key() == Qt.Key_0 and event.modifiers() & Qt.ControlModifier:
            self.reset_zoom()
        else:
            super().keyPressEvent(event)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Don't auto-scale on resize - let user control zoom manually
        # Users can use "Fit" button if they want to fit to window