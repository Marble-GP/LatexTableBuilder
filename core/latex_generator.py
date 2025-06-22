from core.table_model import TableModel
from typing import List, Tuple, Optional


class LaTeXGenerator:
    def __init__(self, table_model: TableModel, table_style=None):
        self.table_model = table_model
        self.table_style = table_style
    
    def generate(self, style: str = "tabular") -> str:
        if style == "tabular":
            return self._generate_tabular()
        elif style == "longtable":
            return self._generate_longtable()
        elif style == "booktabs":
            return self._generate_booktabs()
        elif style == "array":
            return self._generate_array()
        elif style == "styled":
            return self._generate_styled_table()
        else:
            return self._generate_tabular()
    
    def _generate_styled_table(self) -> str:
        """Generate a LaTeX table using the custom style settings"""
        if not self.table_style:
            return self._generate_tabular()
        
        lines = []
        
        # Add title if requested
        if self.table_style.include_title and self.table_style.title_text:
            lines.append("\\begin{table}[htbp]")
            lines.append("\\centering")
            lines.append(f"\\caption{{{self.table_style.title_text}}}")
        
        # Generate column specification with borders
        col_spec = self._get_styled_column_spec()
        lines.append(f"\\begin{{tabular}}{{{col_spec}}}")
        
        # Add top border
        if self.table_style.top_bottom_borders:
            lines.append(self._get_line_command("normal"))
        
        # Generate table rows
        for row_idx in range(self.table_model.rows):
            # Generate the row content first
            row_latex = self._generate_styled_row(row_idx)
            lines.append(row_latex)
            
            # Add line after the row (except for the last row) - Apply RH Logic
            if row_idx < self.table_model.rows - 1:
                # Check if this is after a header row
                is_after_header = self._is_header_row_boundary(row_idx + 1)
                
                if is_after_header and self.table_style.header_rows_thick:
                    # Case 4: Header thick ON + Headers set → Always double line (ignore RH)
                    lines.append(self._get_line_command(self.table_style.header_rows_style))
                elif self.table_style.all_rows_lines:
                    # Cases 1,2,3: Follow RH logic (1 hline when all_rows_lines is ON)
                    lines.append(self._get_line_command("normal"))
                # If all_rows_lines is OFF and not case 4, add no lines (RH = 0 hlines)
        
        # Add bottom border
        if self.table_style.top_bottom_borders:
            lines.append(self._get_line_command("normal"))
        
        lines.append("\\end{tabular}")
        
        # Close table environment if title was added
        if self.table_style.include_title and self.table_style.title_text:
            lines.append("\\end{table}")
        
        return "\n".join(lines)
    
    def _get_styled_column_spec(self) -> str:
        """Generate column specification with custom styling"""
        specs = []
        
        # Add left border if requested
        if self.table_style.left_right_borders:
            specs.append("|")
        
        for col in range(self.table_model.cols):
            # Get column alignment
            alignment = self._get_column_alignment(col)
            specs.append(alignment)
            
            # Add column separator - Apply RH Logic for vertical lines
            if col < self.table_model.cols - 1:
                # Check if this is after a header column
                is_after_header_col = self._is_header_column_boundary(col + 1)
                
                if is_after_header_col and self.table_style.header_columns_thick:
                    # Case 4: Header column thick ON + Headers set → Always double line (ignore RH)
                    specs.append(self._get_column_line_style(self.table_style.header_columns_style))
                elif self.table_style.all_columns_lines:
                    # Cases 1,2,3: Follow RH logic (1 vline when all_columns_lines is ON)
                    specs.append("|")
                # If all_columns_lines is OFF and not case 4, add no lines (RH = 0 vlines)
        
        # Add right border if requested
        if self.table_style.left_right_borders:
            specs.append("|")
        
        return "".join(specs)
    
    def _get_column_alignment(self, col: int) -> str:
        """Get the alignment for a specific column"""
        for row in range(self.table_model.rows):
            cell = self.table_model.get_cell(row, col)
            if cell and cell.content and not cell.is_merged_part:
                return cell.alignment
        return "c"  # Default to center
    
    def _get_line_command(self, line_style: str) -> str:
        """Get the appropriate LaTeX line command - RH' Logic"""
        if line_style == "double":
            return "\\hline\\hline"  # RH' = 2 hlines
        elif line_style == "single":
            return "\\hline"        # RH' = 1 hline
        else:
            return "\\hline"        # Default = 1 hline
    
    def _get_column_line_style(self, line_style: str) -> str:
        """Get column line separator for thick styles - RH' Logic"""
        if line_style == "double":
            return "||"  # RH' = 2 vlines
        elif line_style == "single":
            return "|"   # RH' = 1 vline
        else:
            return "|"   # Default = 1 vline
    
    def _generate_styled_row(self, row_idx: int) -> str:
        """Generate a single row with custom styling"""
        cells = []
        col_idx = 0
        
        while col_idx < self.table_model.cols:
            cell = self.table_model.get_cell(row_idx, col_idx)
            
            if not cell or cell.is_merged_part:
                col_idx += 1
                continue
            
            content = cell.content
            
            # Apply formatting based on explicit font style or default settings
            content = self._apply_font_formatting(content, cell, row_idx, col_idx)
            
            # Handle merged cells
            if cell.span.row_span > 1 or cell.span.col_span > 1:
                if cell.span.col_span > 1:
                    content = f"\\multicolumn{{{cell.span.col_span}}}{{{cell.alignment}}}{{{content}}}"
                if cell.span.row_span > 1:
                    content = f"\\multirow{{{cell.span.row_span}}}{{*}}{{{content}}}"
                
                col_idx += cell.span.col_span
            else:
                col_idx += 1
            
            cells.append(content)
        
        return " & ".join(cells) + " \\\\"
    
    def _count_header_cells_by_direction(self) -> tuple[int, int]:
        """Count total header cells in row direction vs column direction
        Returns: (row_direction_count, column_direction_count)
        """
        row_direction_count = 0
        column_direction_count = 0
        
        for row in range(self.table_model.rows):
            for col in range(self.table_model.cols):
                cell = self.table_model.get_cell(row, col)
                if cell and cell.is_header:
                    row_direction_count += 1
                    column_direction_count += 1
        
        # Count how many rows have headers vs how many columns have headers
        header_rows = set()
        header_cols = set()
        
        for row in range(self.table_model.rows):
            for col in range(self.table_model.cols):
                cell = self.table_model.get_cell(row, col)
                if cell and cell.is_header:
                    header_rows.add(row)
                    header_cols.add(col)
        
        return len(header_rows), len(header_cols)
    
    def _get_header_priority_direction(self) -> str:
        """Determine which direction should get header line priority
        Returns: 'row' if row headers have priority, 'column' if column headers have priority, 'none' if no headers
        """
        row_header_count, col_header_count = self._count_header_cells_by_direction()
        
        if row_header_count == 0 and col_header_count == 0:
            return 'none'
        elif row_header_count > col_header_count:
            return 'row'
        elif col_header_count > row_header_count:
            return 'column'
        else:
            # Equal count - default to row priority
            return 'row'
    
    def _is_header_row_boundary(self, row_idx: int) -> bool:
        """Check if this row is a boundary after header rows using explicit header specification"""
        if row_idx == 0:
            return False
        
        # Use explicit header specification instead of cell-by-cell detection
        prev_row_is_header = self.table_model.is_header_row(row_idx - 1)
        curr_row_is_header = self.table_model.is_header_row(row_idx)
        
        return prev_row_is_header and not curr_row_is_header
    
    def _is_header_column_boundary(self, col_idx: int) -> bool:
        """Check if this column is a boundary after header columns using explicit header specification"""
        if col_idx == 0:
            return False
        
        # Use explicit header specification instead of cell-by-cell detection
        prev_col_is_header = self.table_model.is_header_col(col_idx - 1)
        curr_col_is_header = self.table_model.is_header_col(col_idx)
        
        return prev_col_is_header and not curr_col_is_header
    
    def _apply_font_formatting(self, content: str, cell, row: int, col: int) -> str:
        """Apply font formatting based on explicit style or default settings"""
        # First check if cell has explicit formatting
        if cell.is_bold or cell.font_style == "bold":
            return f"\\textbf{{{content}}}"
        elif cell.is_italic or cell.font_style == "italic":
            return f"\\textit{{{content}}}"
        elif cell.font_style == "normal":
            # Explicitly set to normal, don't apply defaults
            return content
        
        # If no explicit formatting (empty font_style) and we have table style, apply defaults
        if cell.font_style == "" and self.table_style and hasattr(self.table_style, 'header_default_font'):
            is_header_cell = self.table_model.is_header_cell(row, col)
            
            if is_header_cell and self.table_style.header_default_font == "bold":
                return f"\\textbf{{{content}}}"
            elif is_header_cell and self.table_style.header_default_font == "italic":
                return f"\\textit{{{content}}}"
            elif not is_header_cell and self.table_style.data_default_font == "bold":
                return f"\\textbf{{{content}}}"
            elif not is_header_cell and self.table_style.data_default_font == "italic":
                return f"\\textit{{{content}}}"
        
        # No formatting applied
        return content
    
    def _get_column_spec(self) -> str:
        column_specs = []
        for col in range(self.table_model.cols):
            alignment = 'l'
            for row in range(self.table_model.rows):
                cell = self.table_model.get_cell(row, col)
                if cell and cell.content and not cell.is_merged_part:
                    alignment = cell.alignment
                    break
            column_specs.append(alignment)
        return ''.join(column_specs)
    
    def _generate_tabular(self) -> str:
        column_spec = self._get_column_spec()
        
        lines = [
            "\\begin{tabular}{" + column_spec + "}",
            "\\hline"
        ]
        
        for row in range(self.table_model.rows):
            row_content = self._generate_row(row)
            if row_content:
                lines.append(row_content + " \\\\")
                lines.append("\\hline")
        
        lines.append("\\end{tabular}")
        return '\n'.join(lines)
    
    def _generate_longtable(self) -> str:
        column_spec = self._get_column_spec()
        
        lines = [
            "\\begin{longtable}{" + column_spec + "}",
            "\\hline"
        ]
        
        if self.table_model.rows > 0:
            header_row = self._generate_row(0)
            if header_row:
                lines.extend([
                    header_row + " \\\\",
                    "\\hline",
                    "\\endfirsthead",
                    "",
                    "\\hline",
                    header_row + " \\\\",
                    "\\hline",
                    "\\endhead",
                    "",
                    "\\hline",
                    "\\endfoot",
                    "",
                    "\\hline",
                    "\\endlastfoot",
                    ""
                ])
                
                for row in range(1, self.table_model.rows):
                    row_content = self._generate_row(row)
                    if row_content:
                        lines.append(row_content + " \\\\")
                        lines.append("\\hline")
        
        lines.append("\\end{longtable}")
        return '\n'.join(lines)
    
    def _generate_booktabs(self) -> str:
        # Check if booktabs package is available, fallback to tabular if not
        try:
            from utils.latex_packages import is_latex_package_available
            if not is_latex_package_available('booktabs'):
                # Fallback to regular tabular with hlines
                return self._generate_tabular()
        except ImportError:
            # If package detection fails, use regular tabular
            return self._generate_tabular()
        
        column_spec = self._get_column_spec()
        
        lines = [
            "\\begin{tabular}{" + column_spec + "}",
            "\\toprule"
        ]
        
        for row in range(self.table_model.rows):
            row_content = self._generate_row(row)
            if row_content:
                lines.append(row_content + " \\\\")
                if row == 0 and self.table_model.rows > 1:
                    # After header row, use midrule
                    lines.append("\\midrule")
                # No lines between data rows in IEEE style
        
        lines.append("\\bottomrule")
        lines.append("\\end{tabular}")
        return '\n'.join(lines)
    
    def _generate_array(self) -> str:
        column_spec = self._get_column_spec()
        
        lines = [
            "\\begin{array}{" + column_spec + "}"
        ]
        
        for row in range(self.table_model.rows):
            row_content = self._generate_row(row)
            if row_content:
                if row < self.table_model.rows - 1:
                    lines.append(row_content + " \\\\")
                else:
                    lines.append(row_content)
        
        lines.append("\\end{array}")
        return '\n'.join(lines)
    
    def _generate_row(self, row: int) -> str:
        cells = []
        col = 0
        
        while col < self.table_model.cols:
            cell = self.table_model.get_cell(row, col)
            
            if not cell:
                cells.append("")
                col += 1
                continue
            
            if cell.is_merged_part:
                col += 1
                continue
            
            content = self._escape_latex(cell.content)
            
            # Apply formatting based on explicit font style or default settings
            content = self._apply_font_formatting(content, cell, row, col)
            
            if cell.span.col_span > 1:
                content = f"\\multicolumn{{{cell.span.col_span}}}{{{cell.alignment}}}{{{content}}}"
                
            if cell.span.row_span > 1:
                # Check if multirow package is available
                try:
                    from utils.latex_packages import is_latex_package_available
                    if is_latex_package_available('multirow'):
                        content = f"\\multirow{{{cell.span.row_span}}}{{*}}{{{content}}}"
                    # If multirow is not available, just use the content as-is
                    # (not perfect but better than failing to compile)
                except ImportError:
                    pass
            
            cells.append(content)
            col += cell.span.col_span
        
        # Don't pad with empty cells when we have multicolumn spans
        # The multicolumn command already accounts for the spanned columns
        return " & ".join(cells)
    
    def _escape_latex(self, text: str) -> str:
        if not text:
            return ""
        
        escape_chars = {
            '&': '\\&',
            '%': '\\%',
            '$': '\\$',
            '#': '\\#',
            '^': '\\textasciicircum{}',
            '_': '\\_',
            '{': '\\{',
            '}': '\\}',
            '~': '\\textasciitilde{}',
            '\\': '\\textbackslash{}'
        }
        
        result = text
        for char, escaped in escape_chars.items():
            result = result.replace(char, escaped)
        
        return result
    
    def generate_complete_document(self, style: str = "tabular", 
                                 document_class: str = "article",
                                 packages: List[str] = None) -> str:
        if packages is None:
            packages = []
        
        if style == "longtable" and "longtable" not in packages:
            packages.append("longtable")
        if style == "booktabs" and "booktabs" not in packages:
            packages.append("booktabs")
        if style == "array" and "array" not in packages:
            packages.append("array")
        
        has_multirow = self._has_multirow()
        if has_multirow and "multirow" not in packages:
            packages.append("multirow")
        
        lines = [
            f"\\documentclass{{{document_class}}}",
            ""
        ]
        
        for package in packages:
            lines.append(f"\\usepackage{{{package}}}")
        
        if packages:
            lines.append("")
        
        lines.extend([
            "\\begin{document}",
            "",
            self.generate(style),
            "",
            "\\end{document}"
        ])
        
        return '\n'.join(lines)
    
    def _has_multirow(self) -> bool:
        for row in range(self.table_model.rows):
            for col in range(self.table_model.cols):
                cell = self.table_model.get_cell(row, col)
                if cell and cell.span.row_span > 1:
                    return True
        return False
    
    def generate_with_caption(self, style: str = "tabular", 
                            caption: str = "", 
                            label: str = "",
                            position: str = "htbp") -> str:
        table_content = self.generate(style)
        
        lines = [
            f"\\begin{{table}}[{position}]",
            "\\caption{" + caption + "}" if caption else "\\caption{Performance Comparison}",
            "\\label{" + label + "}" if label else "\\label{tab:comparison}",
            "\\centering",
            table_content,
            "\\end{table}"
        ]
        
        return '\n'.join(lines)
    
    def generate_ieee_style(self, caption: str = "", label: str = "") -> str:
        """Generate IEEE-style table with booktabs formatting"""
        # Mark first row as header
        self.table_model.set_row_as_header(0, True)
        
        # Use booktabs style
        table_content = self.generate("booktabs")
        
        # Wrap in table environment
        return self.generate_with_caption("booktabs", caption, label, "htbp")