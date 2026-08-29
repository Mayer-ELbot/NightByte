"""
NightByte AI — Countdown Warning Dialog
Minimal dark floating HUD. English-only.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtGui import QFont


class CountdownWarningDialog(QDialog):
    """Floating always-on-top countdown HUD."""

    cancelled = Signal()
    snoozed   = Signal(int)   # seconds to snooze

    STYLE = """
        QDialog { background: transparent; }
        #CountdownCard {
            background-color: #111111;
            border: 1.5px solid #333333;
            border-radius: 16px;
        }
        #CDTitle {
            color: #ffffff;
            font-size: 15px;
            font-weight: 800;
        }
        #CDAction {
            color: #888888;
            font-size: 12px;
            font-weight: 600;
            background: #1c1c1c;
            border-radius: 6px;
            padding: 4px 12px;
        }
        #CDDigits {
            color: #ffffff;
            font-size: 64px;
            font-weight: 900;
        }
        #CDDesc {
            color: #555555;
            font-size: 12px;
        }
        #AbortBtn {
            background-color: #ffffff;
            color: #000000;
            border: none;
            border-radius: 9px;
            font-size: 13px;
            font-weight: 800;
            padding: 11px 20px;
            min-height: 42px;
        }
        #AbortBtn:hover { background-color: #e0e0e0; }
        #SnoozeBtn {
            background-color: #1c1c1c;
            color: #888888;
            border: 1px solid #2a2a2a;
            border-radius: 7px;
            padding: 7px 12px;
            font-size: 12px;
            font-weight: 700;
        }
        #SnoozeBtn:hover { background-color: #252525; color: #cccccc; border-color: #444; }
    """

    def __init__(self, duration_sec: int, action_label: str, parent=None):
        super().__init__(parent)
        self.duration_sec  = duration_sec
        self.action_label  = action_label

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet(self.STYLE)
        self.setFixedSize(440, 300)

        self.dragging = False
        self.drag_position = QPoint()

        self._build()
        self.digits_label.setText(str(duration_sec))

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)

        card = QFrame()
        card.setObjectName("CountdownCard")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(24, 22, 24, 20)
        lay.setSpacing(10)
        lay.setAlignment(Qt.AlignCenter)

        title = QLabel("⚠  Downloads Completed")
        title.setObjectName("CDTitle")
        title.setAlignment(Qt.AlignCenter)
        lay.addWidget(title)

        action_lbl = QLabel(f"⚡  {self.action_label}")
        action_lbl.setObjectName("CDAction")
        action_lbl.setAlignment(Qt.AlignCenter)
        lay.addWidget(action_lbl, 0, Qt.AlignCenter)

        self.digits_label = QLabel("60")
        self.digits_label.setObjectName("CDDigits")
        self.digits_label.setAlignment(Qt.AlignCenter)
        lay.addWidget(self.digits_label)

        desc = QLabel("Shutdown executes at zero.  Cancel or snooze anytime.")
        desc.setObjectName("CDDesc")
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        lay.addWidget(desc)

        abort = QPushButton("🛑  Cancel Shutdown")
        abort.setObjectName("AbortBtn")
        abort.setCursor(Qt.PointingHandCursor)
        abort.clicked.connect(self._abort)
        lay.addWidget(abort)

        snooze_row = QHBoxLayout()
        snooze_row.setSpacing(8)
        for label, secs in [("+5m", 300), ("+15m", 900), ("+30m", 1800), ("+1h", 3600)]:
            b = QPushButton(label)
            b.setObjectName("SnoozeBtn")
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda _, s=secs: self._snooze(s))
            snooze_row.addWidget(b)
        lay.addLayout(snooze_row)

        outer.addWidget(card)

    def update_tick(self, remaining: int):
        self.digits_label.setText(str(remaining))
        if remaining <= 0:
            self.accept()

    def _abort(self):
        self.cancelled.emit()
        self.reject()

    def _snooze(self, secs: int):
        self.snoozed.emit(secs)
        self.reject()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseReleaseEvent(self, _):
        self.dragging = False

    def mouseMoveEvent(self, e):
        if self.dragging and e.buttons() & Qt.LeftButton:
            self.move(e.globalPosition().toPoint() - self.drag_position)
