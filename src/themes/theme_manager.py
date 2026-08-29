"""
SteamDown Ultra AI - Theme Manager
Manages application stylesheets and dynamic widget polishing.
"""

from PySide6.QtWidgets import QWidget, QApplication
from themes.styles import CYBERPUNK_DARK


class ThemeManager:
    """Singleton managing application visual appearance and styling."""

    @staticmethod
    def apply_theme(app_or_widget, theme_name: str = "cyberpunk_dark"):
        """Apply selected stylesheet."""
        stylesheet = CYBERPUNK_DARK
        app_or_widget.setStyleSheet(stylesheet)
