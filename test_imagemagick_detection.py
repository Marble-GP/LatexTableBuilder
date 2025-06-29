#!/usr/bin/env python3
"""
Test script for ImageMagick smart detection system

This script demonstrates the new ImageMagick version detection 
and command pattern selection functionality.
"""

from utils.imagemagick_detector import (
    get_imagemagick_info, 
    get_convert_command, 
    get_version_command,
    is_imagemagick_available
)

def main():
    print("🔍 ImageMagick Smart Detection Test")
    print("=" * 50)
    
    # Test availability
    available = is_imagemagick_available()
    print(f"✅ Available: {available}")
    
    if not available:
        print("❌ No compatible ImageMagick installation found")
        print("\nSupported installations:")
        print("- ImageMagick 7.x (magick command)")
        print("- ImageMagick 6.x (convert command)")
        print("- GraphicsMagick (gm convert command)")
        return
    
    # Get detailed info
    info = get_imagemagick_info()
    if info:
        print(f"\n📋 Installation Details:")
        print(f"   Name: {info.display_name}")
        print(f"   Version: {info.version}")
        print(f"   Major Version: {info.major_version}")
        print(f"   Minor Version: {info.minor_version}")
        print(f"   Command Pattern: {' '.join(info.command_pattern)}")
        print(f"   Is ImageMagick: {info.is_imagemagick}")
        
        # Show version command
        version_cmd = get_version_command()
        if version_cmd:
            print(f"\n🔧 Version Check Command:")
            print(f"   {' '.join(version_cmd)}")
        
        # Show convert command example
        convert_cmd = get_convert_command("input.pdf", "output.png")
        if convert_cmd:
            print(f"\n🖼️  PDF to PNG Convert Command:")
            print(f"   {' '.join(convert_cmd)}")
        
        # Show different option examples
        print(f"\n⚙️  Command Examples:")
        
        # High quality conversion
        hq_cmd = get_convert_command("table.pdf", "table.png", 
                                   ['-density', '300', '-quality', '100', '-trim', '+repage'])
        if hq_cmd:
            print(f"   High Quality: {' '.join(hq_cmd)}")
        
        # Simple conversion
        simple_cmd = get_convert_command("input.pdf", "output.png", [])
        if simple_cmd:
            print(f"   Simple: {' '.join(simple_cmd)}")
        
        # Custom options
        custom_cmd = get_convert_command("input.pdf", "output.jpg", 
                                       ['-density', '150', '-quality', '90'])
        if custom_cmd:
            print(f"   Custom: {' '.join(custom_cmd)}")
        
        print(f"\n✨ Benefits of Smart Detection:")
        print(f"   • Automatically uses the best available command")
        print(f"   • Supports multiple ImageMagick versions")
        print(f"   • Falls back to GraphicsMagick if needed")
        print(f"   • No manual configuration required")
        print(f"   • Future-proof for new ImageMagick versions")


if __name__ == "__main__":
    main()