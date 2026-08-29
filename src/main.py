"""
NightByte AI - Application Entry Point
High DPI aware initialization, single-instance handling, theme application, and main loop.
"""

import sys
import os

# Add src to sys.path so relative and absolute imports work cleanly in dev & PyInstaller
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

from themes.theme_manager import ThemeManager
from gui.main_window import MainWindow
from utils.logger import logger


def main():
    # 1. Enable High-DPI Scaling for crisp displays
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("NightByte AI")
    app.setOrganizationName("NightByte")

    # 2. Apply Monochrome Dark Theme
    ThemeManager.apply_theme(app, "mono_dark")

    # 3. Create Main Dashboard
    window = MainWindow()

    # Check CLI arguments (e.g. startup minimized)
    if "--minimized" in sys.argv:
        logger.info("Launched in minimized mode.")
        window.hide()
    else:
        window.show()

    logger.success("NightByte AI initialized successfully.")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
