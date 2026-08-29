"""
NightByte AI - Theme Manager
"""
from PySide6.QtWidgets import QApplication
from themes.styles import MONO_DARK


class ThemeManager:
    @staticmethod
    def apply_theme(app: QApplication, _name: str = "mono_dark"):
        app.setStyleSheet(MONO_DARK)
