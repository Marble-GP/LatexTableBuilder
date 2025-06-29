"""
ImageMagick Version Detection and Command Pattern Selection

This module provides smart detection of ImageMagick installation and
automatically selects the appropriate command patterns based on version.

Supported patterns:
- ImageMagick 7.x: Uses 'magick convert' command
- ImageMagick 6.x: Uses 'convert' command  
- GraphicsMagick: Uses 'gm convert' command (fallback)
"""

import subprocess
import re
from typing import Optional, List, Dict, Any
from dataclasses import dataclass


@dataclass
class ImageMagickInfo:
    """Information about detected ImageMagick installation"""
    command_pattern: List[str]  # Base command to use (e.g., ['magick', 'convert'] or ['convert'])
    version: str
    major_version: int
    minor_version: int
    is_imagemagick: bool  # True for ImageMagick, False for GraphicsMagick
    display_name: str  # Human-readable name


class ImageMagickDetector:
    """Detects ImageMagick installation and provides appropriate command patterns"""
    
    def __init__(self):
        self._cached_info: Optional[ImageMagickInfo] = None
    
    def detect(self) -> Optional[ImageMagickInfo]:
        """Detect ImageMagick installation and return configuration info"""
        if self._cached_info is not None:
            return self._cached_info
        
        # Try detection patterns in order of preference
        detection_patterns = [
            self._try_imagemagick7_magick,
            self._try_imagemagick7_convert,
            self._try_imagemagick6_convert,
            self._try_graphicsmagick
        ]
        
        for detector in detection_patterns:
            info = detector()
            if info:
                self._cached_info = info
                return info
        
        return None
    
    def _try_imagemagick7_magick(self) -> Optional[ImageMagickInfo]:
        """Try ImageMagick 7.x with 'magick' command"""
        try:
            result = subprocess.run(['magick', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version_info = self._parse_imagemagick_version(result.stdout)
                if version_info and version_info['major'] >= 7:
                    return ImageMagickInfo(
                        command_pattern=['magick'],
                        version=version_info['version'],
                        major_version=version_info['major'],
                        minor_version=version_info['minor'],
                        is_imagemagick=True,
                        display_name=f"ImageMagick {version_info['version']} (modern)"
                    )
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass
        return None
    
    def _try_imagemagick7_convert(self) -> Optional[ImageMagickInfo]:
        """Try ImageMagick 7.x with 'convert' command (some installations)"""
        try:
            result = subprocess.run(['convert', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and 'ImageMagick' in result.stdout:
                version_info = self._parse_imagemagick_version(result.stdout)
                if version_info and version_info['major'] >= 7:
                    return ImageMagickInfo(
                        command_pattern=['convert'],
                        version=version_info['version'],
                        major_version=version_info['major'],
                        minor_version=version_info['minor'],
                        is_imagemagick=True,
                        display_name=f"ImageMagick {version_info['version']} (legacy mode)"
                    )
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass
        return None
    
    def _try_imagemagick6_convert(self) -> Optional[ImageMagickInfo]:
        """Try ImageMagick 6.x with 'convert' command"""
        try:
            result = subprocess.run(['convert', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and 'ImageMagick' in result.stdout:
                version_info = self._parse_imagemagick_version(result.stdout)
                if version_info and version_info['major'] == 6:
                    return ImageMagickInfo(
                        command_pattern=['convert'],
                        version=version_info['version'],
                        major_version=version_info['major'],
                        minor_version=version_info['minor'],
                        is_imagemagick=True,
                        display_name=f"ImageMagick {version_info['version']} (legacy)"
                    )
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass
        return None
    
    def _try_graphicsmagick(self) -> Optional[ImageMagickInfo]:
        """Try GraphicsMagick as fallback"""
        try:
            result = subprocess.run(['gm', 'version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version_info = self._parse_graphicsmagick_version(result.stdout)
                if version_info:
                    return ImageMagickInfo(
                        command_pattern=['gm', 'convert'],
                        version=version_info['version'],
                        major_version=version_info['major'],
                        minor_version=version_info['minor'],
                        is_imagemagick=False,
                        display_name=f"GraphicsMagick {version_info['version']} (fallback)"
                    )
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass
        return None
    
    def _parse_imagemagick_version(self, version_output: str) -> Optional[Dict[str, Any]]:
        """Parse ImageMagick version from command output"""
        # Look for version pattern like "Version: ImageMagick 6.9.12-98" or "ImageMagick 7.1.1-47"
        patterns = [
            r'Version:\s*ImageMagick\s+(\d+)\.(\d+)\.(\d+)-(\d+)',
            r'ImageMagick\s+(\d+)\.(\d+)\.(\d+)-(\d+)',
            r'Version:\s*ImageMagick\s+(\d+)\.(\d+)\.(\d+)',
            r'ImageMagick\s+(\d+)\.(\d+)\.(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, version_output)
            if match:
                groups = match.groups()
                major = int(groups[0])
                minor = int(groups[1])
                patch = int(groups[2])
                build = int(groups[3]) if len(groups) > 3 else 0
                
                if build > 0:
                    version = f"{major}.{minor}.{patch}-{build}"
                else:
                    version = f"{major}.{minor}.{patch}"
                
                return {
                    'version': version,
                    'major': major,
                    'minor': minor,
                    'patch': patch,
                    'build': build
                }
        return None
    
    def _parse_graphicsmagick_version(self, version_output: str) -> Optional[Dict[str, Any]]:
        """Parse GraphicsMagick version from command output"""
        # Look for version pattern like "GraphicsMagick 1.3.42"
        pattern = r'GraphicsMagick\s+(\d+)\.(\d+)\.(\d+)'
        match = re.search(pattern, version_output)
        if match:
            major = int(match.group(1))
            minor = int(match.group(2))
            patch = int(match.group(3))
            version = f"{major}.{minor}.{patch}"
            
            return {
                'version': version,
                'major': major,
                'minor': minor,
                'patch': patch,
                'build': 0
            }
        return None
    
    def get_convert_command(self, input_file: str, output_file: str, 
                          options: List[str] = None) -> Optional[List[str]]:
        """Get the complete convert command for the detected ImageMagick installation"""
        info = self.detect()
        if not info:
            return None
        
        if options is None:
            options = ['-density', '300', '-quality', '100', '-trim', '+repage']
        
        if info.major_version >= 7 and info.command_pattern == ['magick']:
            # ImageMagick 7.x with modern 'magick' command
            return ['magick', 'convert'] + options + [input_file, output_file]
        else:
            # ImageMagick 6.x or GraphicsMagick with 'convert' or 'gm convert'
            return info.command_pattern + options + [input_file, output_file]
    
    def get_version_command(self) -> Optional[List[str]]:
        """Get the version check command for the detected installation"""
        info = self.detect()
        if not info:
            return None
        
        if info.is_imagemagick:
            if info.command_pattern == ['magick']:
                return ['magick', '--version']
            else:
                return ['convert', '--version']
        else:
            # GraphicsMagick
            return ['gm', 'version']
    
    def is_available(self) -> bool:
        """Check if any compatible ImageMagick installation is available"""
        return self.detect() is not None
    
    def get_info(self) -> Optional[ImageMagickInfo]:
        """Get information about the detected installation"""
        return self.detect()


# Global instance for easy access
_detector = ImageMagickDetector()


def get_imagemagick_info() -> Optional[ImageMagickInfo]:
    """Get information about the detected ImageMagick installation"""
    return _detector.get_info()


def get_convert_command(input_file: str, output_file: str, 
                       options: List[str] = None) -> Optional[List[str]]:
    """Get the appropriate convert command for the system"""
    return _detector.get_convert_command(input_file, output_file, options)


def get_version_command() -> Optional[List[str]]:
    """Get the appropriate version check command for the system"""
    return _detector.get_version_command()


def is_imagemagick_available() -> bool:
    """Check if ImageMagick is available on the system"""
    return _detector.is_available()