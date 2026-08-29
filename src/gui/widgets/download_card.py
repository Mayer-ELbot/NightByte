"""
NightByte AI - Interactive Download Card Widget
Clean game card with selectable checkmark to target specific games for shutdown.
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QProgressBar, QFrame, QCheckBox
)
from PySide6.QtCore import Qt, Signal


class DownloadCard(QFrame):
    """Interactive card for active games with target selection checkbox."""

    selection_changed = Signal(str, bool)  # item_id, is_selected

    def __init__(self, item_data: dict, is_selected: bool = True, parent=None):
        super().__init__(parent)
        self.setObjectName("DownloadCard")
        self.item_data = item_data
        self.item_id = item_data.get("id", "")
        self.setup_ui(is_selected)
        self.update_data(item_data)

    def setup_ui(self, is_selected: bool):
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            #DownloadCard {
                background-color: #111827;
                border: 1px solid #1f2937;
                border-radius: 10px;
                padding: 8px;
            }
            #DownloadCard:hover {
                border-color: #0284c7;
            }
            #TitleLabel {
                color: #f8fafc;
                font-weight: bold;
                font-size: 13px;
            }
            #PlatformBadge {
                background-color: #0f172a;
                color: #38bdf8;
                border: 1px solid #0284c7;
                border-radius: 4px;
                padding: 2px 6px;
                font-size: 10px;
                font-weight: bold;
            }
            #StateBadge {
                color: #10b981;
                font-size: 11px;
                font-weight: 600;
            }
            #SizeLabel {
                color: #94a3b8;
                font-size: 11px;
            }
            QProgressBar {
                background-color: #0f172a;
                border: 1px solid #1e293b;
                border-radius: 3px;
                height: 6px;
                text-align: right;
            }
            QProgressBar::chunk {
                background-color: #0284c7;
                border-radius: 2px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(6)

        # Header Row: Checkbox + Platform + Title + State
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        self.check = QCheckBox()
        self.check.setChecked(is_selected)
        self.check.setToolTip("Check to target this specific download / اختر للمراقبة المخصصة")
        self.check.toggled.connect(self._on_check_toggled)
        header_layout.addWidget(self.check)

        self.platform_badge = QLabel("STEAM")
        self.platform_badge.setObjectName("PlatformBadge")
        header_layout.addWidget(self.platform_badge)

        self.title_label = QLabel("Game Title")
        self.title_label.setObjectName("TitleLabel")
        header_layout.addWidget(self.title_label, stretch=1)

        self.state_label = QLabel("Downloading")
        self.state_label.setObjectName("StateBadge")
        header_layout.addWidget(self.state_label)

        layout.addLayout(header_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

        # Footer Row: Bytes + Percent
        footer_layout = QHBoxLayout()
        self.size_label = QLabel("0 MB / 0 MB")
        self.size_label.setObjectName("SizeLabel")
        footer_layout.addWidget(self.size_label)

        footer_layout.addStretch()

        self.percent_label = QLabel("0%")
        self.percent_label.setStyleSheet("color: #38bdf8; font-weight: bold; font-size: 11px;")
        footer_layout.addWidget(self.percent_label)

        layout.addLayout(footer_layout)

    def _on_check_toggled(self, checked: bool):
        self.selection_changed.emit(self.item_id, checked)

    def update_data(self, item: dict):
        self.item_data = item
        self.item_id = item.get("id", "")
        self.title_label.setText(item.get("name", "Unknown Game"))
        self.platform_badge.setText(item.get("platform", "APP").upper())

        state_str = item.get("state", "Active")
        self.state_label.setText(state_str)

        dl_bytes = item.get("bytes_downloaded", 0)
        tot_bytes = item.get("bytes_total", 0)

        if tot_bytes > 0:
            pct = min(100.0, max(0.0, (dl_bytes / tot_bytes) * 100.0))
            self.progress_bar.setValue(int(pct))
            self.percent_label.setText(f"{pct:.1f}%")
            self.size_label.setText(f"{self._format_bytes(dl_bytes)} / {self._format_bytes(tot_bytes)}")
        else:
            self.progress_bar.setRange(0, 0)
            self.percent_label.setText("Active")
            self.size_label.setText(f"{self._format_bytes(dl_bytes)} transferred" if dl_bytes > 0 else "Active Process")

    def _format_bytes(self, b: int) -> str:
        if b >= 1024**3:
            return f"{b / (1024**3):.2f} GB"
        elif b >= 1024**2:
            return f"{b / (1024**2):.1f} MB"
        elif b >= 1024:
            return f"{b / 1024:.0f} KB"
        return f"{b} B"
