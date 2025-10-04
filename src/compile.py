import PyInstaller.__main__
import os
import shutil

# Define the root directory (one level up from /src)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    # 1. Clean up previous builds (optional)
    print("Cleaning previous build and dist folders...")
    shutil.rmtree(os.path.join(ROOT_DIR, "build"), ignore_errors=True)
    shutil.rmtree(os.path.join(ROOT_DIR, "dist"), ignore_errors=True)

    # 2. Define the path to your main script
    # Using run.py in the project root as the entry point
    main_script = os.path.join(ROOT_DIR, "run.py")

    # 3. Define the path to your assets and data folders
    assets_dir = os.path.join(ROOT_DIR, "assets")
    data_dir = os.path.join(ROOT_DIR, "data")

    # 4. Build the PyInstaller command
    pyinstaller_cmd = [
        main_script,
        '--name=MyNotes',
        '--onefile',
        '--windowed',
        # '--icon=' + os.path.join(assets_dir, 'icon.ico'),  # Commented out - icon file doesn't exist
        '--add-data=' + assets_dir + ';assets',
        '--add-data=' + data_dir + ';data',
        '--clean',
        '--hidden-import=PIL._tkinter_finder',
        '--hidden-import=pymupdf',
    ]

    # 5. Print the command for debugging
    print("Running PyInstaller with the following command:")
    print(" ".join(pyinstaller_cmd))

    # 6. Run PyInstaller
    PyInstaller.__main__.run(pyinstaller_cmd)

    print("Build completed! Check the 'dist' folder for MyNotes.exe")

if __name__ == '__main__':
    main()