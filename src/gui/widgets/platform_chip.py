"""
NightByte AI — Platform Chip Widget
Active = white bg / black text.  Inactive = dark outlined pill.
"""

from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Signal


class PlatformChip(QPushButton):
    toggled_platform = Signal(str, bool)

    _ACTIVE_STYLE = """
        QPushButton {
            background-color: #ffffff;
            color: #000000;
            border: none;
            border-radius: 20px;
            padding: 6px 14px;
            font-weight: 800;
            font-size: 12px;
            min-height: 32px;
        }
        QPushButton:hover {
            background-color: #e8e8e8;
        }
    """

    _INACTIVE_STYLE = """
        QPushButton {
            background-color: transparent;
            color: #666666;
            border: 1px solid #2a2a2a;
            border-radius: 20px;
            padding: 6px 14px;
            font-weight: 600;
            font-size: 12px;
            min-height: 32px;
        }
        QPushButton:hover {
            border-color: #555555;
            color: #aaaaaa;
        }
    """

    def __init__(self, label: str, key: str, active: bool = True, parent=None):
        super().__init__(label, parent)
        self.key = key
        self.setCheckable(True)
        self.setChecked(active)
        self._refresh()
        self.toggled.connect(self._on_toggle)

    def _refresh(self):
        self.setStyleSheet(self._ACTIVE_STYLE if self.isChecked() else self._INACTIVE_STYLE)

    def _on_toggle(self, checked: bool):
        self._refresh()
        self.toggled_platform.emit(self.key, checked)
