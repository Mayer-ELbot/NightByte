"""
NightByte AI - Completed Download History Card Widget
Displays detailed metrics for items downloaded during this session:
duration, average speed, peak speed, total transferred, and finish time.
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
)
from PySide6.QtCore import Qt


class HistoryCard(QFrame):
    """Card displaying analytics for a download completed during this session."""

    STYLE = """
        #HistoryCard {
            background-color: #121212;
            border: 1px solid #202020;
            border-radius: 10px;
        }
        #HistoryCard:hover {
            border-color: #383838;
        }
        #HNameLabel {
            color: #ffffff;
            font-weight: 700;
            font-size: 13px;
        }
        #HPlatformBadge {
            background-color: #ffffff;
            color: #000000;
            border-radius: 4px;
            padding: 2px 7px;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 0.5px;
        }
        #HCompletedBadge {
            color: #888888;
            font-size: 11px;
            font-weight: 600;
        }
        #HStatPill {
            background-color: #181818;
            border: 1px solid #282828;
            border-radius: 6px;
            padding: 4px 8px;
            color: #aaaaaa;
            font-size: 11px;
            font-weight: 600;
        }
    """

    def __init__(self, item_data: dict, parent=None):
        super().__init__(parent)
        self.setObjectName("HistoryCard")
        self.setStyleSheet(self.STYLE)
        self.item_data = item_data
        self.setup_ui()

    def setup_ui(self):
        self.setFrameShape(QFrame.StyledPanel)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        # Header Row: Platform + Name + Completed time
        header = QHBoxLayout()
        header.setSpacing(8)

        badge = QLabel(self.item_data.get("platform", "APP").upper())
        badge.setObjectName("HPlatformBadge")
        header.addWidget(badge)

        name_lbl = QLabel(self.item_data.get("name", "Unknown Download"))
        name_lbl.setObjectName("HNameLabel")
        header.addWidget(name_lbl, stretch=1)

        time_str = self.item_data.get("completed_at", "")
        comp_lbl = QLabel(f"✓ Finished {time_str}")
        comp_lbl.setObjectName("HCompletedBadge")
        header.addWidget(comp_lbl)

        layout.addLayout(header)

        # Metrics Row: Duration, Avg Speed, Peak Speed, Total Size
        metrics = QHBoxLayout()
        metrics.setSpacing(6)

        duration = self.item_data.get("duration_str", "")
        if duration:
            m1 = QLabel(f"⏱  {duration}")
            m1.setObjectName("HStatPill")
            metrics.addWidget(m1)

        avg_spd = self.item_data.get("avg_speed_str", "")
        if avg_spd:
            m2 = QLabel(f"⚡  Avg {avg_spd}")
            m2.setObjectName("HStatPill")
            metrics.addWidget(m2)

        peak_spd = self.item_data.get("peak_speed_str", "")
        if peak_spd:
            m3 = QLabel(f"▲  Peak {peak_spd}")
            m3.setObjectName("HStatPill")
            metrics.addWidget(m3)

        size_str = self.item_data.get("total_size_str", "")
        if size_str:
            m4 = QLabel(f"📦  {size_str}")
            m4.setObjectName("HStatPill")
            metrics.addWidget(m4)

        metrics.addStretch()
        layout.addLayout(metrics)
