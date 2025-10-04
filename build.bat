@echo off
echo ========================================
echo    My Notes - Clean Build
echo ========================================
echo.

set PYTHON=C:\Users\futur\AppData\Local\Programs\Python\Python313\python.exe

echo Step 1: Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "MyNotes.spec" del MyNotes.spec

echo.
echo Step 2: Waiting for any locked files to release...
timeout /t 3 /nobreak >nul

echo.
echo Step 3: Compiling src/main.py...
%PYTHON% -m PyInstaller --onefile --windowed --name="MyNotes" --add-data="assets;assets" --add-data="data;data" --hidden-import=PIL._tkinter_finder --hidden-import=pymupdf src/main.py

echo.
if exist "dist\MyNotes.exe" (
    echo ========================================
    echo    SUCCESS! 🎉
    echo ========================================
    echo.
    echo ✅ Executable created: dist\MyNotes.exe
    echo.
    echo 🧪 Testing the executable...
    start "" "dist\MyNotes.exe"
    echo.
    echo 💝 Ready to send to your girlfriend!
    echo 🖥️  Runs on ANY Windows laptop
    echo 📦 File size:
    for %%F in ("dist\MyNotes.exe") do echo      %%~zF bytes
) else (
    echo ========================================
    echo    BUILD FAILED
    echo ========================================
)

echo.
pause