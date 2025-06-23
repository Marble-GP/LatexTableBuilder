"""
Paste Parser Module

Handles parsing of clipboard data from various spreadsheet applications including:
- Excel (Windows/Mac)
- LibreOffice Calc
- Google Sheets
- Other CSV/TSV formatted data
"""

import re
from typing import List, Tuple, Optional, Dict, Any
from io import StringIO
import csv


class PasteParser:
    """Parser for spreadsheet clipboard data"""
    
    @staticmethod
    def detect_format(clipboard_data: str) -> str:
        """
        Detect the format of clipboard data
        Returns: 'tsv', 'csv', 'excel', 'text', 'empty'
        """
        if not clipboard_data or not clipboard_data.strip():
            return 'empty'
        
        lines = clipboard_data.strip().split('\n')
        
        # Check for Excel/LibreOffice tab-separated format (most common)
        if len(lines) > 0:
            first_line = lines[0]
            if '\t' in first_line:
                return 'tsv'  # Tab-separated values (Excel default)
            elif ',' in first_line and len(first_line.split(',')) > 1:
                return 'csv'  # Comma-separated values
        
        # Single cell or plain text
        return 'text'
    
    @staticmethod
    def parse_tsv(data: str) -> List[List[str]]:
        """Parse tab-separated values (Excel/LibreOffice default)"""
        rows = []
        lines = data.strip().split('\n')
        
        for line in lines:
            # Split on tabs and clean up each cell
            cells = line.split('\t')
            cleaned_cells = []
            
            for cell in cells:
                # Remove quotes if present and clean whitespace
                cell = cell.strip()
                if cell.startswith('"') and cell.endswith('"') and len(cell) > 1:
                    cell = cell[1:-1]
                # Handle escaped quotes
                cell = cell.replace('""', '"')
                cleaned_cells.append(cell)
            
            rows.append(cleaned_cells)
        
        return rows
    
    @staticmethod
    def parse_csv(data: str) -> List[List[str]]:
        """Parse comma-separated values"""
        rows = []
        
        try:
            # Use Python's CSV parser for proper handling of quotes and escapes
            csv_reader = csv.reader(StringIO(data))
            for row in csv_reader:
                # Clean up cells
                cleaned_row = [cell.strip() for cell in row]
                rows.append(cleaned_row)
        except Exception:
            # Fallback to simple split if CSV parsing fails
            lines = data.strip().split('\n')
            for line in lines:
                cells = [cell.strip() for cell in line.split(',')]
                rows.append(cells)
        
        return rows
    
    @staticmethod
    def parse_text(data: str) -> List[List[str]]:
        """Parse plain text - treat as single cell or simple row"""
        lines = data.strip().split('\n')
        
        # If multiple lines, treat each as a single-cell row
        if len(lines) > 1:
            return [[line.strip()] for line in lines if line.strip()]
        else:
            # Single line - could be space or other delimiter separated
            line = lines[0].strip()
            
            # Try to detect if it's multiple values
            if ' ' in line and not line.count(' ') > 10:  # Reasonable heuristic
                # Split on multiple spaces (likely column-aligned text)
                cells = re.split(r'\s{2,}', line)
                if len(cells) > 1:
                    return [[cell.strip() for cell in cells]]
            
            # Treat as single cell
            return [[line]]
    
    @staticmethod
    def parse_clipboard_data(clipboard_data: str) -> Tuple[List[List[str]], Dict[str, Any]]:
        """
        Parse clipboard data and return table data with metadata
        
        Returns:
            tuple: (table_data, metadata)
            - table_data: List of rows, each row is a list of cell contents
            - metadata: Dict containing parsing info like format, dimensions, etc.
        """
        if not clipboard_data:
            return [], {"format": "empty", "rows": 0, "cols": 0, "error": "No data"}
        
        format_type = PasteParser.detect_format(clipboard_data)
        metadata = {"format": format_type, "rows": 0, "cols": 0, "original_size": len(clipboard_data)}
        
        try:
            if format_type == 'tsv':
                table_data = PasteParser.parse_tsv(clipboard_data)
            elif format_type == 'csv':
                table_data = PasteParser.parse_csv(clipboard_data)
            elif format_type == 'text':
                table_data = PasteParser.parse_text(clipboard_data)
            else:  # empty
                table_data = []
            
            # Calculate dimensions
            if table_data:
                metadata["rows"] = len(table_data)
                metadata["cols"] = max(len(row) for row in table_data) if table_data else 0
                
                # Normalize row lengths (pad shorter rows with empty strings)
                max_cols = metadata["cols"]
                for row in table_data:
                    while len(row) < max_cols:
                        row.append("")
            
            metadata["success"] = True
            
        except Exception as e:
            metadata["error"] = str(e)
            metadata["success"] = False
            table_data = []
        
        return table_data, metadata
    
    @staticmethod
    def normalize_table_data(table_data: List[List[str]], min_rows: int = 1, min_cols: int = 1) -> List[List[str]]:
        """
        Normalize table data to ensure minimum dimensions and consistent row lengths
        """
        if not table_data:
            table_data = []
        
        # Ensure minimum dimensions
        rows_needed = max(min_rows, len(table_data))
        cols_needed = min_cols
        
        if table_data:
            cols_needed = max(cols_needed, max(len(row) for row in table_data))
        
        # Normalize existing rows
        for row in table_data:
            while len(row) < cols_needed:
                row.append("")
        
        # Add missing rows
        while len(table_data) < rows_needed:
            table_data.append([""] * cols_needed)
        
        return table_data
    
    @staticmethod
    def preview_paste_data(clipboard_data: str, max_preview_size: int = 500) -> str:
        """
        Generate a preview string of what will be pasted
        """
        if not clipboard_data:
            return "No data to paste"
        
        table_data, metadata = PasteParser.parse_clipboard_data(clipboard_data)
        
        if not metadata.get("success", False):
            return f"Parse error: {metadata.get('error', 'Unknown error')}"
        
        if not table_data:
            return "No table data found"
        
        # Create preview
        preview_lines = [
            f"Format: {metadata['format'].upper()}",
            f"Dimensions: {metadata['rows']} rows × {metadata['cols']} columns",
            "",
            "Preview (first few cells):"
        ]
        
        # Show first few rows and columns
        max_rows = min(5, len(table_data))
        max_cols = min(4, metadata['cols'])
        
        for i in range(max_rows):
            row = table_data[i]
            preview_row = []
            for j in range(min(max_cols, len(row))):
                cell = row[j]
                # Truncate long cell content
                if len(cell) > 20:
                    cell = cell[:17] + "..."
                preview_row.append(f'"{cell}"')
            
            if len(row) > max_cols:
                preview_row.append("...")
            
            preview_lines.append("  " + " | ".join(preview_row))
        
        if len(table_data) > max_rows:
            preview_lines.append("  ...")
        
        preview_text = "\n".join(preview_lines)
        
        # Truncate if too long
        if len(preview_text) > max_preview_size:
            preview_text = preview_text[:max_preview_size] + "..."
        
        return preview_text


def test_parser():
    """Test function for the parser"""
    # Test data samples
    test_data = {
        "excel_tsv": "Name\tAge\tCity\nJohn\t25\tNew York\nJane\t30\tLos Angeles",
        "csv": "Name,Age,City\nJohn,25,New York\nJane,30,Los Angeles",
        "single_cell": "Hello World",
        "multiline_text": "Line 1\nLine 2\nLine 3",
        "empty": ""
    }
    
    for name, data in test_data.items():
        print(f"\n=== Testing {name} ===")
        print(f"Input: {repr(data)}")
        
        table_data, metadata = PasteParser.parse_clipboard_data(data)
        print(f"Metadata: {metadata}")
        print(f"Table data: {table_data}")
        print(f"Preview:\n{PasteParser.preview_paste_data(data)}")


if __name__ == "__main__":
    test_parser()