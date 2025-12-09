@echo off
setlocal enabledelayedexpansion

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

REM Calculate the project root (go up 3 levels from scripts/deployment)
for %%A in ("%SCRIPT_DIR%\..\..") do set PROJECT_ROOT=%%~fA

REM Set the entry point and output paths
set ENTRY_POINT=%PROJECT_ROOT%\flicker\__main__.py
set OUTPUT_DIR=%SCRIPT_DIR%\dist
set BUILD_DIR=%SCRIPT_DIR%\build

REM Verify entry point exists
if not exist "%ENTRY_POINT%" (
    echo Error: Entry point not found at %ENTRY_POINT%
    exit /b 1
)

REM Re-generate PyQt resources

pyside6-rcc -o %PROJECT_ROOT%\flicker\assets\resources_rc.py ^
    %PROJECT_ROOT%\flicker\assets\resources.qrc

REM Run pyinstaller
pyinstaller ^
    --onedir --clean ^
    --distpath "%OUTPUT_DIR%" ^
    --workpath "%BUILD_DIR%" ^
    --specpath "%OUTPUT_DIR%" ^
    --name "Flicker" ^
    --icon %PROJECT_ROOT%\flicker\assets\icons\flicker.ico ^
    --noconfirm ^
    "%ENTRY_POINT%"

if %errorlevel% equ 0 (
    echo Build completed successfully. Output: %OUTPUT_DIR%
) else (
    echo Build failed with error code %errorlevel%
    exit /b %errorlevel%
)

endlocal
