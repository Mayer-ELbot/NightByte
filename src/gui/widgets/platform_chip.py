"""
NightByte AI - Modern Platform Toggle Chip
Sleek, pill-shaped interactive toggle button for platform filtering.
"""

from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor


class PlatformChip(QPushButton):
    """Modern pill toggle button representing a game platform."""

    toggled_platform = Signal(str, bool)

    def __init__(self, platform_key: str, label_text: str, is_active: bool = True, parent=None):
        super().__init__(label_text, parent)
        self.platform_key = platform_key
        self.setCheckable(True)
        self.setChecked(is_active)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(32)
        self.setObjectName("PlatformChip")
        self._update_style()
        self.toggled.connect(self._on_toggled)

    def _on_toggled(self, checked: bool):
        self._update_style()
        self.toggled_platform.emit(self.platform_key, checked)

    def _update_style(self):
        if self.isChecked():
            self.setStyleSheet("""
                QPushButton#PlatformChip {
                    background-color: rgba(59, 130, 246, 0.18);
                    color: #60a5fa;
                    border: 1px solid #3b82f6;
                    border-radius: 8px;
                    padding: 5px 14px;
                    font-weight: 700;
                    font-size: 12px;
                }
                QPushButton#PlatformChip:hover {
                    background-color: rgba(59, 130, 246, 0.28);
                    border-color: #60a5fa;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton#PlatformChip {
                    background-color: rgba(255, 255, 255, 0.03);
                    color: #64748b;
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    border-radius: 8px;
                    padding: 5px 14px;
                    font-weight: 500;
                    font-size: 12px;
                }
                QPushButton#PlatformChip:hover {
                    background-color: rgba(255, 255, 255, 0.06);
                    color: #94a3b8;
                    border-color: rgba(255, 255, 255, 0.15);
                }
            """)
