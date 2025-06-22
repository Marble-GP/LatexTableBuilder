from typing import Dict, Tuple, Any, Optional
from dataclasses import dataclass


@dataclass
class CellSpan:
    row_span: int = 1
    col_span: int = 1


@dataclass
class Cell:
    content: str = ""
    span: CellSpan = None
    is_merged_part: bool = False
    alignment: str = "l"  # l, c, r for left, center, right
    is_bold: bool = False  # Independent font formatting
    is_italic: bool = False  # Independent font formatting
    font_style: str = ""  # empty = use defaults, "normal", "bold", "italic"
    is_header: bool = False  # Deprecated - will be replaced by explicit header ranges
    
    def __post_init__(self):
        if self.span is None:
            self.span = CellSpan()


class TableModel:
    def __init__(self, rows: int = 5, cols: int = 5):
        self.rows = rows
        self.cols = cols
        self._cells: Dict[Tuple[int, int], Cell] = {}
        self._merged_regions: list = []
        
        # New explicit header specifications (1-based as per user input)
        self.header_rows_spec: str = ""  # e.g., "1", "1,2", "1-3"
        self.header_cols_spec: str = ""  # e.g., "1", "1,2", "1-3"
        
        for i in range(rows):
            for j in range(cols):
                cell = Cell()
                cell.alignment = "c"  # Default to center alignment
                self._cells[(i, j)] = cell
    
    def get_cell(self, row: int, col: int) -> Optional[Cell]:
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self._cells.get((row, col))
        return None
    
    def set_cell_content(self, row: int, col: int, content: str):
        cell = self.get_cell(row, col)
        if cell and not cell.is_merged_part:
            cell.content = content
    
    def set_cell_alignment(self, row: int, col: int, alignment: str):
        cell = self.get_cell(row, col)
        if cell and alignment in ['l', 'c', 'r']:
            cell.alignment = alignment
    
    def set_cell_bold(self, row: int, col: int, is_bold: bool):
        cell = self.get_cell(row, col)
        if cell:
            cell.is_bold = is_bold
    
    def set_cell_italic(self, row: int, col: int, is_italic: bool):
        cell = self.get_cell(row, col)
        if cell:
            cell.is_italic = is_italic
    
    def set_cell_font_style(self, row: int, col: int, font_style: str):
        """Set font style: normal, bold, italic, roman"""
        cell = self.get_cell(row, col)
        if cell and font_style in ['normal', 'bold', 'italic', 'roman']:
            cell.font_style = font_style
            # Update individual flags for backward compatibility
            cell.is_bold = (font_style == 'bold')
            cell.is_italic = (font_style == 'italic')
    
    def reset_cell_formatting(self, row: int, col: int):
        """Reset cell formatting to use defaults"""
        cell = self.get_cell(row, col)
        if cell:
            cell.is_bold = False
            cell.is_italic = False
            cell.font_style = ""  # Empty = use defaults
    
    def set_row_as_header(self, row: int, is_header: bool = True):
        """Mark an entire row as header (DEPRECATED - use header_rows_spec instead)"""
        for col in range(self.cols):
            cell = self.get_cell(row, col)
            if cell:
                cell.is_header = is_header
                # No longer automatically sets bold formatting
    
    def set_column_as_header(self, col: int, is_header: bool = True):
        """Mark an entire column as header (DEPRECATED - use header_cols_spec instead)"""
        for row in range(self.rows):
            cell = self.get_cell(row, col)
            if cell:
                cell.is_header = is_header
                # No longer automatically sets bold formatting
    
    def toggle_row_header(self, row: int):
        """Toggle header status for an entire row"""
        # Check if any cell in the row is currently a header
        is_currently_header = any(
            self.get_cell(row, col) and self.get_cell(row, col).is_header 
            for col in range(self.cols)
        )
        # Toggle to opposite state
        self.set_row_as_header(row, not is_currently_header)
        return not is_currently_header
    
    def toggle_column_header(self, col: int):
        """Toggle header status for an entire column"""
        # Check if any cell in the column is currently a header
        is_currently_header = any(
            self.get_cell(row, col) and self.get_cell(row, col).is_header 
            for row in range(self.rows)
        )
        # Toggle to opposite state
        self.set_column_as_header(col, not is_currently_header)
        return not is_currently_header
    
    def set_cells_as_header(self, cells: list, is_header: bool = True):
        """Mark a list of (row, col) cells as headers (DEPRECATED)"""
        for row, col in cells:
            cell = self.get_cell(row, col)
            if cell:
                cell.is_header = is_header
                # No longer automatically sets bold formatting
    
    def clear_all_headers(self):
        """Remove header formatting from all cells in the table"""
        for row in range(self.rows):
            for col in range(self.cols):
                cell = self.get_cell(row, col)
                if cell:
                    cell.is_header = False
                    # Bold formatting is now independent
    
    # NEW: Header range specification methods
    def set_header_rows_spec(self, spec: str):
        """Set header rows specification (1-based, e.g., '1', '1,2', '1-3')"""
        self.header_rows_spec = spec.strip()
    
    def set_header_cols_spec(self, spec: str):
        """Set header columns specification (1-based, e.g., '1', '1,2', '1-3')"""
        self.header_cols_spec = spec.strip()
    
    def parse_range_spec(self, spec: str) -> list:
        """Parse a range specification string into a list of 0-based indices
        
        Examples:
        - '1' -> [0]
        - '1,2' -> [0, 1]
        - '1-3' -> [0, 1, 2]
        - '1,3-5' -> [0, 2, 3, 4]
        - '1,' -> [0]
        - '' -> []
        """
        if not spec.strip():
            return []
        
        indices = []
        parts = [part.strip() for part in spec.split(',') if part.strip()]
        
        for part in parts:
            if '-' in part:
                # Range specification
                try:
                    start, end = part.split('-', 1)
                    start_idx = int(start.strip()) - 1  # Convert to 0-based
                    end_idx = int(end.strip()) - 1      # Convert to 0-based
                    if start_idx >= 0 and end_idx >= start_idx:
                        indices.extend(range(start_idx, end_idx + 1))
                except ValueError:
                    # Invalid range, skip
                    continue
            else:
                # Single value
                try:
                    idx = int(part.strip()) - 1  # Convert to 0-based
                    if idx >= 0:
                        indices.append(idx)
                except ValueError:
                    # Invalid number, skip
                    continue
        
        # Remove duplicates and sort
        return sorted(list(set(indices)))
    
    def get_header_rows(self) -> list:
        """Get list of 0-based header row indices from specification"""
        return self.parse_range_spec(self.header_rows_spec)
    
    def get_header_cols(self) -> list:
        """Get list of 0-based header column indices from specification"""
        return self.parse_range_spec(self.header_cols_spec)
    
    def is_header_row(self, row: int) -> bool:
        """Check if a row is a header row based on explicit specification"""
        return row in self.get_header_rows()
    
    def is_header_col(self, col: int) -> bool:
        """Check if a column is a header column based on explicit specification"""
        return col in self.get_header_cols()
    
    def is_header_cell(self, row: int, col: int) -> bool:
        """Check if a cell is in header area based on explicit specification"""
        return self.is_header_row(row) or self.is_header_col(col)
    
    def merge_cells(self, start_row: int, start_col: int, end_row: int, end_col: int):
        if not (0 <= start_row <= end_row < self.rows and 
                0 <= start_col <= end_col < self.cols):
            return False
        
        if start_row == end_row and start_col == end_col:
            return False
        
        main_cell = self.get_cell(start_row, start_col)
        if not main_cell:
            return False
        
        row_span = end_row - start_row + 1
        col_span = end_col - start_col + 1
        
        main_cell.span = CellSpan(row_span, col_span)
        
        for i in range(start_row, end_row + 1):
            for j in range(start_col, end_col + 1):
                if i == start_row and j == start_col:
                    continue
                cell = self.get_cell(i, j)
                if cell:
                    cell.is_merged_part = True
                    cell.content = ""
        
        self._merged_regions.append((start_row, start_col, end_row, end_col))
        return True
    
    def unmerge_cells(self, row: int, col: int):
        cell = self.get_cell(row, col)
        if not cell or cell.span.row_span == 1 and cell.span.col_span == 1:
            return False
        
        end_row = row + cell.span.row_span - 1
        end_col = col + cell.span.col_span - 1
        
        for i in range(row, end_row + 1):
            for j in range(col, end_col + 1):
                target_cell = self.get_cell(i, j)
                if target_cell:
                    target_cell.is_merged_part = False
                    target_cell.span = CellSpan()
        
        self._merged_regions = [region for region in self._merged_regions 
                               if region != (row, col, end_row, end_col)]
        return True
    
    def is_cell_merged(self, row: int, col: int) -> bool:
        cell = self.get_cell(row, col)
        return cell and (cell.is_merged_part or 
                        cell.span.row_span > 1 or cell.span.col_span > 1)
    
    def get_merge_info(self, row: int, col: int) -> Optional[Tuple[int, int, int, int]]:
        for region in self._merged_regions:
            start_row, start_col, end_row, end_col = region
            if start_row <= row <= end_row and start_col <= col <= end_col:
                return region
        return None
    
    def resize(self, new_rows: int, new_cols: int):
        if new_rows <= 0 or new_cols <= 0:
            return False
        
        new_cells = {}
        
        for i in range(new_rows):
            for j in range(new_cols):
                if i < self.rows and j < self.cols:
                    new_cells[(i, j)] = self._cells.get((i, j), Cell())
                else:
                    cell = Cell()
                    cell.alignment = "c"  # Default to center alignment
                    new_cells[(i, j)] = cell
        
        self._cells = new_cells
        self.rows = new_rows
        self.cols = new_cols
        
        self._merged_regions = [
            region for region in self._merged_regions 
            if region[2] < new_rows and region[3] < new_cols
        ]
        
        return True
    
    def clear(self):
        for cell in self._cells.values():
            cell.content = ""
            cell.span = CellSpan()
            cell.is_merged_part = False
            cell.alignment = "l"
        self._merged_regions.clear()
    
    def to_dict(self) -> dict:
        return {
            'rows': self.rows,
            'cols': self.cols,
            'cells': {
                f"{row},{col}": {
                    'content': cell.content,
                    'alignment': cell.alignment,
                    'row_span': cell.span.row_span,
                    'col_span': cell.span.col_span,
                    'is_merged_part': cell.is_merged_part
                }
                for (row, col), cell in self._cells.items()
                if cell.content or cell.is_merged_part or 
                   cell.span.row_span > 1 or cell.span.col_span > 1
            },
            'merged_regions': self._merged_regions
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TableModel':
        model = cls(data['rows'], data['cols'])
        
        for pos_str, cell_data in data.get('cells', {}).items():
            row, col = map(int, pos_str.split(','))
            cell = model.get_cell(row, col)
            if cell:
                cell.content = cell_data.get('content', '')
                cell.alignment = cell_data.get('alignment', 'l')
                cell.span = CellSpan(
                    cell_data.get('row_span', 1),
                    cell_data.get('col_span', 1)
                )
                cell.is_merged_part = cell_data.get('is_merged_part', False)
        
        model._merged_regions = data.get('merged_regions', [])
        return model