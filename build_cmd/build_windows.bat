@echo off
echo === LaTeX Table Builder - Windows Build Script ===
echo.

REM Check if we're in the right directory
if not exist "main.py" (
    echo Error: main.py not found. Please run this script from the project root directory.
    pause
    exit /b 1
)

REM Check if PyInstaller is installed
python -m pyinstaller --version >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
)

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del *.spec

REM Create the Windows binary
echo Building Windows binary...
python -m pyinstaller ^
    --onefile ^
    --windowed ^
    --name "LatexTableBuilder" ^
    --add-data "CLAUDE.md;." ^
    --add-data "README.md;." ^
    --distpath "dist/windows" ^
    main.py

REM Check if build was successful
if exist "dist\windows\LatexTableBuilder.exe" (
    echo.
    echo ✅ Windows binary built successfully!
    echo 📁 Location: dist\windows\LatexTableBuilder.exe
    for %%A in ("dist\windows\LatexTableBuilder.exe") do echo 📊 Size: %%~zA bytes
    echo.
    echo To run the application:
    echo   cd dist\windows
    echo   LatexTableBuilder.exe
    echo.
) else (
    echo ❌ Build failed! Check the output above for errors.
    pause
    exit /b 1
)

pause