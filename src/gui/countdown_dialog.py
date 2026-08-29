"""
SteamDown Ultra AI - On-Screen Countdown HUD Dialog
Sleek floating warning dialog with instant abort and snooze buttons.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QColor, QFont
from i18n.translations import tr
from utils.config import ConfigManager


class CountdownWarningDialog(QDialog):
    """Floating on-screen warning window showing circular countdown and abort controls."""

    def __init__(self, duration_sec: int, action_name: str, engine=None, parent=None):
        super().__init__(parent)
        self.duration_sec = duration_sec
        self.remaining_sec = duration_sec
        self.action_name = action_name
        self.engine = engine
        self.config = ConfigManager()
        
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(460, 320)
        
        self.dragging = False
        self.drag_position = QPoint()
        
        self.setup_ui()
        self.update_tick(duration_sec)

    def setup_ui(self):
        lang = self.config.get("language", "ar")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Container Frame with Glass styling
        self.card = QFrame()
        self.card.setObjectName("CountdownCard")
        self.card.setStyleSheet("""
            #CountdownCard {
                background-color: #0f172a;
                border: 2px solid #ef4444;
                border-radius: 16px;
            }
            #Title {
                color: #f87171;
                font-size: 16px;
                font-weight: bold;
            }
            #Description {
                color: #cbd5e1;
                font-size: 12px;
            }
            #Digits {
                color: #ef4444;
                font-size: 56px;
                font-weight: 900;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            #ActionTag {
                background-color: #1e293b;
                color: #38bdf8;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 12px;
                font-weight: bold;
            }
            #AbortButton {
                background-color: #ef4444;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
            }
            #AbortButton:hover {
                background-color: #dc2626;
            }
            #SnoozeButton {
                background-color: #1e293b;
                color: #94a3b8;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 11px;
                font-weight: 500;
            }
            #SnoozeButton:hover {
                background-color: #334155;
                color: #f8fafc;
            }
        """)

        # Drop shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(239, 68, 68, 120))
        shadow.setOffset(0, 4)
        self.card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(24, 20, 24, 20)
        card_layout.setSpacing(10)
        card_layout.setAlignment(Qt.AlignCenter)

        # Title
        title_label = QLabel(tr("countdown_title", lang))
        title_label.setObjectName("Title")
        title_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title_label)

        # Action tag
        action_tr = tr(f"action_{self.action_name}", lang) if self.action_name else self.action_name
        self.action_tag = QLabel(f"⚡ {action_tr}")
        self.action_tag.setObjectName("ActionTag")
        self.action_tag.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.action_tag)

        # Big Countdown Digits
        self.digits_label = QLabel(str(self.duration_sec))
        self.digits_label.setObjectName("Digits")
        self.digits_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.digits_label)

        # Description
        desc_label = QLabel(tr("countdown_desc", lang))
        desc_label.setObjectName("Description")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        card_layout.addWidget(desc_label)

        # Big Cancel Button
        self.abort_btn = QPushButton(f"🛑 {tr('btn_cancel_countdown', lang)}")
        self.abort_btn.setObjectName("AbortButton")
        self.abort_btn.setCursor(Qt.PointingHandCursor)
        self.abort_btn.clicked.connect(self._on_abort_clicked)
        card_layout.addWidget(self.abort_btn)

        # Snooze buttons row
        snooze_layout = QHBoxLayout()
        snooze_layout.setSpacing(8)

        for text_key, secs in [
            ("btn_snooze_5m", 300),
            ("btn_snooze_15m", 900),
            ("btn_snooze_30m", 1800),
            ("btn_snooze_1h", 3600)
        ]:
            btn = QPushButton(tr(text_key, lang))
            btn.setObjectName("SnoozeButton")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, s=secs: self._on_snooze_clicked(s))
            snooze_layout.addWidget(btn)

        card_layout.addLayout(snooze_layout)
        main_layout.addWidget(self.card)

    def update_tick(self, remaining_sec: int):
        """Update digits on countdown tick."""
        self.remaining_sec = remaining_sec
        self.digits_label.setText(str(remaining_sec))
        if remaining_sec <= 0:
            self.accept()

    def _on_abort_clicked(self):
        """Cancel the countdown and close dialog."""
        if self.engine:
            self.engine.cancel_countdown("User pressed Abort button in Warning Dialog")
        self.reject()

    def _on_snooze_clicked(self, seconds: int):
        """Snooze countdown."""
        if self.engine:
            self.engine.snooze(seconds)
        self.reject()

    # Window dragging
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
