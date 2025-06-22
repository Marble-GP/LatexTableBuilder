import pyperclip
import subprocess
import tempfile
import os
from typing import Optional, Dict


def get_clipboard_status() -> Dict[str, any]:
    """Check clipboard availability and provide detailed status"""
    status = {
        "available": False,
        "method": None,
        "error": None,
        "suggestion": None
    }
    
    try:
        pyperclip.copy("")
        status["available"] = True
        status["method"] = "pyperclip"
        return status
    except Exception as e:
        status["error"] = str(e)
        
        # Check for Linux-specific solutions
        if "linux" in os.name.lower() or "posix" in os.name.lower():
            # Check if we're in a graphical session
            if not os.environ.get('DISPLAY') and not os.environ.get('WAYLAND_DISPLAY'):
                status["suggestion"] = "No graphical session detected. Clipboard requires a desktop environment."
            elif _check_command("xclip"):
                status["suggestion"] = "xclip is available but pyperclip cannot use it. Try: ./fix_clipboard.sh"
            elif _check_command("xsel"):
                status["suggestion"] = "xsel is available but pyperclip cannot use it. Try: ./fix_clipboard.sh"
            else:
                status["suggestion"] = "Install clipboard support: sudo apt-get install xclip (or run ./fix_clipboard.sh)"
        else:
            status["suggestion"] = "Clipboard functionality not available on this system"
    
    return status


def _check_command(command: str) -> bool:
    """Check if a command is available in the system PATH"""
    try:
        subprocess.run([command, "--version"], capture_output=True, timeout=2)
        return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def copy_to_clipboard(text: str) -> Dict[str, any]:
    """
    Copy text to clipboard with detailed result information
    Returns dict with success status and details
    """
    result = {
        "success": False,
        "method": None,
        "error": None,
        "fallback_used": False
    }
    
    # Try primary method (pyperclip)
    try:
        pyperclip.copy(text)
        result["success"] = True
        result["method"] = "pyperclip"
        return result
    except Exception as e:
        result["error"] = str(e)
    
    # Try Linux fallbacks
    if not result["success"]:
        fallback_result = _try_linux_fallbacks(text)
        if fallback_result["success"]:
            result.update(fallback_result)
            result["fallback_used"] = True
    
    return result


def _try_linux_fallbacks(text: str) -> Dict[str, any]:
    """Try Linux-specific clipboard methods"""
    result = {"success": False, "method": None, "error": None}
    
    # Try xclip
    if _check_command("xclip"):
        try:
            process = subprocess.run(
                ["xclip", "-selection", "clipboard"],
                input=text,
                text=True,
                capture_output=True,
                timeout=5
            )
            if process.returncode == 0:
                result["success"] = True
                result["method"] = "xclip"
                return result
        except Exception as e:
            result["error"] = f"xclip failed: {e}"
    
    # Try xsel
    if _check_command("xsel"):
        try:
            process = subprocess.run(
                ["xsel", "--clipboard", "--input"],
                input=text,
                text=True,
                capture_output=True,
                timeout=5
            )
            if process.returncode == 0:
                result["success"] = True
                result["method"] = "xsel"
                return result
        except Exception as e:
            result["error"] = f"xsel failed: {e}"
    
    return result


def save_to_temp_file(text: str, filename: str = "latex_table.tex") -> Optional[str]:
    """Save text to a temporary file as fallback"""
    try:
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        
        return filepath
    except Exception as e:
        print(f"Failed to save temp file: {e}")
        return None


def get_from_clipboard() -> Optional[str]:
    """Get text from clipboard"""
    try:
        return pyperclip.paste()
    except Exception:
        # Try Linux fallbacks
        if _check_command("xclip"):
            try:
                result = subprocess.run(
                    ["xclip", "-selection", "clipboard", "-o"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return result.stdout
            except Exception:
                pass
        
        if _check_command("xsel"):
            try:
                result = subprocess.run(
                    ["xsel", "--clipboard", "--output"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return result.stdout
            except Exception:
                pass
        
        return None


def is_clipboard_available() -> bool:
    """Check if clipboard functionality is available"""
    return get_clipboard_status()["available"]