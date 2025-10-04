#!/usr/bin/env python3
"""
My Notes - Professional PDF Reader and a Note Taking Application
"""

import tkinter as tk
import os
import sys

# Add current directory to path for PyInstaller
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from app import BookNoteTakingApp
except ImportError as e:
    print(f"Import error: {e}")
    print("Available files in directory:")
    for file in os.listdir(current_dir):
        print(f"  - {file}")
    input("Press Enter to exit...")
    sys.exit(1)

def main():
    """Main entry point for the application"""
    try:
        # Create data directory if it doesn't exist
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        # Create notes directory if it doesn't exist
        notes_dir = os.path.join(data_dir, "notes")
        if not os.path.exists(notes_dir):
            os.makedirs(notes_dir)

        print("Starting My Notes Application...")
        print("Data directory:", os.path.abspath(data_dir))

        root = tk.Tk()
        app = BookNoteTakingApp(root)

        # Handle window close event properly
        root.protocol("WM_DELETE_WINDOW", app.cleanup_and_exit)

        print("Application started successfully!")
        root.mainloop()

    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()