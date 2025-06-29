import subprocess
import tempfile
import os
from typing import Set, Dict


class LaTeXPackageDetector:
    """Detect which LaTeX packages are available on the system"""
    
    def __init__(self):
        self._available_packages = None
        self._tested_packages = set()
    
    def is_package_available(self, package_name: str) -> bool:
        """Check if a specific LaTeX package is available"""
        if package_name in self._tested_packages:
            return package_name in (self._available_packages or set())
        
        return self._test_package(package_name)
    
    def _test_package(self, package_name: str) -> bool:
        """Test if a package can be loaded by trying to compile a minimal document"""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                test_file = os.path.join(temp_dir, "test.tex")
                
                test_content = f"""
\\documentclass{{article}}
\\usepackage{{{package_name}}}
\\begin{{document}}
Test
\\end{{document}}
"""
                
                with open(test_file, 'w') as f:
                    f.write(test_content)
                
                result = subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', test_file],
                    cwd=temp_dir,
                    capture_output=True,
                    timeout=10
                )
                
                available = result.returncode == 0
                self._tested_packages.add(package_name)
                
                if self._available_packages is None:
                    self._available_packages = set()
                
                if available:
                    self._available_packages.add(package_name)
                
                return available
                
        except Exception:
            return False
    
    def get_available_packages(self, package_list: list) -> Set[str]:
        """Get a set of available packages from a given list"""
        available = set()
        for package in package_list:
            if self.is_package_available(package):
                available.add(package)
        return available
    
    def get_safe_latex_template(self, latex_content: str) -> str:
        """Generate a LaTeX document template with only available packages"""
        # Start with only the most basic packages
        essential_packages = ['array']
        optional_packages = ['booktabs', 'longtable', 'multirow']
        japanese_packages = ['xeCJK', 'luatexja', 'CJKutf8', 'CJK']
        
        # Always include array (it's in latex-base)
        package_includes = ["\\usepackage{array}"]
        
        # Check if Japanese text is present and add appropriate packages
        if self._contains_japanese_text(latex_content):
            japanese_package_added = False
            # Try Japanese packages in order of preference
            for package in japanese_packages:
                if self.is_package_available(package):
                    if package == 'xeCJK':
                        package_includes.append("\\usepackage{xeCJK}")
                        package_includes.append("\\setCJKmainfont{NotoSansCJK-Regular}")
                    elif package == 'luatexja':
                        package_includes.append("\\usepackage{luatexja}")
                    elif package == 'CJKutf8':
                        package_includes.append("\\usepackage{CJKutf8}")
                    elif package == 'CJK':
                        package_includes.append("\\usepackage{CJK}")
                    japanese_package_added = True
                    break
            
            # If no Japanese packages are available, add UTF-8 input encoding
            if not japanese_package_added:
                package_includes.append("\\usepackage[utf8]{inputenc}")
                package_includes.append("\\usepackage[T1]{fontenc}")
        
        # Test optional packages
        for package in optional_packages:
            if self.is_package_available(package):
                package_includes.append(f"\\usepackage{{{package}}}")
        
        # Create document with appropriate wrapper for CJK if needed
        if self._contains_japanese_text(latex_content) and any('CJK' in inc for inc in package_includes):
            template = f"""\\documentclass{{article}}
{chr(10).join(package_includes)}
\\begin{{document}}
\\pagestyle{{empty}}
\\begin{{CJK}}{{UTF8}}{{min}}
{latex_content}
\\end{{CJK}}
\\end{{document}}
"""
        else:
            template = f"""\\documentclass{{article}}
{chr(10).join(package_includes)}
\\begin{{document}}
\\pagestyle{{empty}}
{latex_content}
\\end{{document}}
"""
        return template
    
    def _contains_japanese_text(self, text: str) -> bool:
        """Check if text contains Japanese characters (Hiragana, Katakana, Kanji)"""
        import re
        # Unicode ranges for Japanese characters
        hiragana = r'[\u3040-\u309F]'  # Hiragana
        katakana = r'[\u30A0-\u30FF]'  # Katakana
        kanji = r'[\u4E00-\u9FAF]'     # Kanji (CJK Unified Ideographs)
        japanese_pattern = f'({hiragana}|{katakana}|{kanji})'
        return bool(re.search(japanese_pattern, text))


# Global instance
_detector = LaTeXPackageDetector()


def is_latex_package_available(package_name: str) -> bool:
    """Check if a LaTeX package is available"""
    return _detector.is_package_available(package_name)


def get_safe_latex_document(latex_content: str) -> str:
    """Get a complete LaTeX document with only available packages"""
    return _detector.get_safe_latex_template(latex_content)


def get_package_recommendations() -> Dict[str, str]:
    """Get package installation recommendations"""
    return {
        'booktabs': 'texlive-latex-recommended',
        'longtable': 'texlive-latex-recommended', 
        'multirow': 'texlive-latex-recommended',
        'array': 'texlive-latex-base',
        'amsmath': 'texlive-latex-recommended',
        'xeCJK': 'texlive-xetex (for Japanese with XeLaTeX)',
        'luatexja': 'texlive-luatex (for Japanese with LuaLaTeX)',
        'CJKutf8': 'texlive-latex-cjk (for Japanese with pdfLaTeX)',
        'CJK': 'texlive-latex-cjk (for Japanese with pdfLaTeX)'
    }