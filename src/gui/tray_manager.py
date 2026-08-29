"""
NightByte AI — System Tray Manager
English-only. Clean minimal tray menu.
"""

from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import QObject, Signal

from utils.config import ConfigManager


class TrayManager(QObject):

    show_requested   = Signal()
    toggle_requested = Signal()
    cancel_requested = Signal()
    exit_requested   = Signal()

    def __init__(self, icon: QIcon, parent=None):
        super().__init__(parent)
        self.config = ConfigManager()
        self._running = False

        self.tray = QSystemTrayIcon(icon, parent)
        self.tray.setToolTip("NightByte AI")
        self.tray.activated.connect(self._activated)

        self.menu = QMenu()
        self._build_menu()
        self.tray.setContextMenu(self.menu)
        self.tray.show()

    def _build_menu(self):
        self.menu.clear()

        open_act = QAction("Open NightByte", self.menu)
        open_act.triggered.connect(self.show_requested.emit)
        self.menu.addAction(open_act)

        self.menu.addSeparator()

        self.toggle_act = QAction("▶  Start Monitoring", self.menu)
        self.toggle_act.triggered.connect(self.toggle_requested.emit)
        self.menu.addAction(self.toggle_act)

        self.cancel_act = QAction("🛑  Cancel Shutdown", self.menu)
        self.cancel_act.triggered.connect(self.cancel_requested.emit)
        self.cancel_act.setEnabled(False)
        self.menu.addAction(self.cancel_act)

        self.menu.addSeparator()

        exit_act = QAction("Exit", self.menu)
        exit_act.triggered.connect(self.exit_requested.emit)
        self.menu.addAction(exit_act)

    def update_status(self, status_text: str, running: bool = None):
        if running is not None:
            self._running = running
        self.toggle_act.setText(
            "■  Stop Monitoring" if self._running else "▶  Start Monitoring"
        )
        tip = f"NightByte AI — {status_text}"
        self.tray.setToolTip(tip)

    def set_countdown_active(self, active: bool):
        self.cancel_act.setEnabled(active)

    def show_tray_message(self, title: str, message: str):
        if self.config.get("system_tray_notifications", True):
            self.tray.showMessage(title, message, QSystemTrayIcon.Information, 3000)

    def _activated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.show_requested.emit()
