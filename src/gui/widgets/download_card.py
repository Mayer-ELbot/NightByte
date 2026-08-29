"""
SteamDown Ultra AI - Download Card Widget
Sleek game/download item card with progress bar, ETA, and platform badge.
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QProgressBar, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class DownloadCard(QFrame):
    """Card representing an active or recent download item."""

    def __init__(self, item_data: dict, parent=None):
        super().__init__(parent)
        self.setObjectName("DownloadCard")
        self.item_data = item_data
        self.setup_ui()
        self.update_data(item_data)

    def setup_ui(self):
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            #DownloadCard {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 10px;
                margin-bottom: 6px;
            }
            #DownloadCard:hover {
                border-color: #0ea5e9;
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
                font-weight: 500;
            }
            #SizeLabel {
                color: #94a3b8;
                font-size: 11px;
            }
            QProgressBar {
                background-color: #0f172a;
                border: 1px solid #334155;
                border-radius: 4px;
                height: 8px;
                text-align: right;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #38bdf8);
                border-radius: 3px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # Header row (Platform badge + Title + State)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        self.platform_badge = QLabel("STEAM")
        self.platform_badge.setObjectName("PlatformBadge")
        header_layout.addWidget(self.platform_badge)

        self.title_label = QLabel("Game Title")
        self.title_label.setObjectName("TitleLabel")
        self.title_label.setWordWrap(False)
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

        # Footer row (Bytes info & percentage)
        footer_layout = QHBoxLayout()
        self.size_label = QLabel("0 MB / 0 MB")
        self.size_label.setObjectName("SizeLabel")
        footer_layout.addWidget(self.size_label)

        footer_layout.addStretch()

        self.percent_label = QLabel("0%")
        self.percent_label.setObjectName("SizeLabel")
        self.percent_label.setStyleSheet("color: #38bdf8; font-weight: bold;")
        footer_layout.addWidget(self.percent_label)

        layout.addLayout(footer_layout)

    def update_data(self, item: dict):
        """Refresh card with latest item stats."""
        self.item_data = item
        self.title_label.setText(item.get("name", "Unknown App"))
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
            self.progress_bar.setRange(0, 0) # Indeterminate animation
            self.percent_label.setText("Active")
            self.size_label.setText(f"{self._format_bytes(dl_bytes)} transferred")

    def _format_bytes(self, b: int) -> str:
        """Format bytes to MB/GB."""
        if b >= 1024 * 1024 * 1024:
            return f"{b / (1024**3):.2f} GB"
        elif b >= 1024 * 1024:
            return f"{b / (1024**2):.1f} MB"
        elif b >= 1024:
            return f"{b / 1024:.0f} KB"
        return f"{b} B"
