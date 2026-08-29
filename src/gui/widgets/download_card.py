"""
NightByte AI - Interactive Download Card Widget
Monochrome Dark theme styling, clean typography, progress bar and target toggle.
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QProgressBar, QFrame, QCheckBox
)
from PySide6.QtCore import Qt, Signal


class DownloadCard(QFrame):
    """Interactive card for active games/downloads with target selection checkbox."""

    selection_changed = Signal(str, bool)  # item_id, is_selected

    STYLE = """
        #DownloadCard {
            background-color: #141414;
            border: 1px solid #242424;
            border-radius: 10px;
        }
        #DownloadCard:hover {
            border-color: #444444;
        }
        #TitleLabel {
            color: #ffffff;
            font-weight: 700;
            font-size: 13px;
        }
        #PlatformBadge {
            background-color: #ffffff;
            color: #000000;
            border-radius: 4px;
            padding: 2px 7px;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 0.5px;
        }
        #StateBadge {
            color: #888888;
            font-size: 11px;
            font-weight: 600;
        }
        #SizeLabel {
            color: #666666;
            font-size: 11px;
            font-weight: 500;
        }
        #PercentLabel {
            color: #ffffff;
            font-weight: 700;
            font-size: 11px;
        }
        QProgressBar {
            background-color: #222222;
            border: none;
            border-radius: 3px;
            height: 5px;
        }
        QProgressBar::chunk {
            background-color: #ffffff;
            border-radius: 3px;
        }
        QCheckBox {
            spacing: 0px;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border: 1px solid #333333;
            border-radius: 4px;
            background-color: #1c1c1c;
        }
        QCheckBox::indicator:hover {
            border-color: #ffffff;
        }
        QCheckBox::indicator:checked {
            background-color: #ffffff;
            border-color: #ffffff;
        }
    """

    def __init__(self, item_data: dict, is_selected: bool = True, parent=None):
        super().__init__(parent)
        self.setObjectName("DownloadCard")
        self.setStyleSheet(self.STYLE)
        self.item_data = item_data
        self.item_id = item_data.get("id", item_data.get("item_id", ""))
        self.setup_ui(is_selected)
        self.update_data(item_data)

    def setup_ui(self, is_selected: bool):
        self.setFrameShape(QFrame.StyledPanel)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # Header Row: Checkbox + Platform + Title + State
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        self.check = QCheckBox()
        self.check.setChecked(is_selected)
        self.check.setToolTip("Toggle targeted monitoring for this item")
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
        self.percent_label.setObjectName("PercentLabel")
        footer_layout.addWidget(self.percent_label)

        layout.addLayout(footer_layout)

    def _on_check_toggled(self, checked: bool):
        self.selection_changed.emit(self.item_id, checked)

    def update_data(self, item: dict):
        self.item_data = item
        self.item_id = item.get("id", item.get("item_id", ""))
        self.title_label.setText(item.get("name", "Unknown Download"))
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
            self.size_label.setText(f"{self._format_bytes(dl_bytes)} received" if dl_bytes > 0 else "Active Process")

    def update_item(self, item: dict):
        self.update_data(item)

    def _format_bytes(self, b: int) -> str:
        if b >= 1024**3:
            return f"{b / (1024**3):.2f} GB"
        elif b >= 1024**2:
            return f"{b / (1024**2):.1f} MB"
        elif b >= 1024:
            return f"{b / 1024:.0f} KB"
        return f"{b} B"
