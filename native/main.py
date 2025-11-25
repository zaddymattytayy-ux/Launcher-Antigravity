import sys
import os
import logging
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSharedMemory, Qt

# Disable Qt's automatic high-DPI scaling
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0"
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
os.environ["QT_SCALE_FACTOR"] = "1"

# Add current directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from launcher_app import LauncherApp
from error_logger import setup_logging

def main():
    # Setup logging
    setup_logging()
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("MU Online Launcher")
    
    # Single instance check using QSharedMemory
    shared_memory = QSharedMemory("MUOnlineLauncherInstance")
    if not shared_memory.create(1):
        print("Launcher is already running!")
        # In a real app, you might want to bring the existing window to front here
        # For now, we just exit
        sys.exit(0)
        
    # Initialize and show main window
    window = LauncherApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
