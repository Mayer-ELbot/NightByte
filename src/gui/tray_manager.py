"""
SteamDown Ultra AI - System Tray Manager
Provides system tray icon, live tooltip, quick action context menu, and balloon alerts.
"""

from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import QObject, Signal
from i18n.translations import tr
from utils.config import ConfigManager


class TrayManager(QObject):
    """Manages the Windows System Tray lifecycle and menu."""

    show_window_requested = Signal()
    toggle_monitoring_requested = Signal()
    cancel_shutdown_requested = Signal()
    quit_requested = Signal()

    def __init__(self, icon: QIcon, parent=None):
        super().__init__(parent)
        self.config = ConfigManager()
        self.tray_icon = QSystemTrayIcon(icon, parent)
        self.tray_icon.setToolTip("SteamDown Ultra AI")
        self.tray_icon.activated.connect(self._on_tray_activated)
        
        self.menu = QMenu()
        self.setup_menu()
        self.tray_icon.setContextMenu(self.menu)

    def show(self):
        self.tray_icon.show()

    def hide(self):
        self.tray_icon.hide()

    def setup_menu(self):
        lang = self.config.get("language", "ar")
        self.menu.clear()

        # Open
        self.open_act = QAction(f"🖥️ {tr('tray_open', lang)}", self.menu)
        self.open_act.triggered.connect(self.show_window_requested.emit)
        self.menu.addAction(self.open_act)

        self.menu.addSeparator()

        # Toggle monitor
        self.toggle_act = QAction(f"▶️ {tr('tray_enable', lang)}", self.menu)
        self.toggle_act.triggered.connect(self.toggle_monitoring_requested.emit)
        self.menu.addAction(self.toggle_act)

        # Cancel shutdown
        self.cancel_act = QAction(f"🛑 {tr('tray_cancel_shutdown', lang)}", self.menu)
        self.cancel_act.triggered.connect(self.cancel_shutdown_requested.emit)
        self.menu.addAction(self.cancel_act)

        self.menu.addSeparator()

        # Exit
        self.exit_act = QAction(f"❌ {tr('tray_exit', lang)}", self.menu)
        self.exit_act.triggered.connect(self.quit_requested.emit)
        self.menu.addAction(self.exit_act)

    def update_status(self, is_enabled: bool, speed_kb: float, is_online: bool, state_str: str):
        """Update tray tooltip and toggle action text."""
        lang = self.config.get("language", "ar")
        speed_text = f"{speed_kb / 1024.0:.1f} MB/s" if speed_kb >= 1024 else f"{speed_kb:.0f} KB/s"
        online_text = "🟢 Online" if is_online else "🔴 Offline"
        
        tip = f"SteamDown Ultra AI\n{online_text} | {speed_text}\n{state_str}"
        self.tray_icon.setToolTip(tip)

        if is_enabled:
            self.toggle_act.setText(f"⏸️ {tr('tray_disable', lang)}")
        else:
            self.toggle_act.setText(f"▶️ {tr('tray_enable', lang)}")

    def show_notification(self, title: str, message: str, icon_type=QSystemTrayIcon.Information):
        """Show native Windows notification balloon."""
        if self.config.get("system_tray_notifications", True):
            self.tray_icon.showMessage(title, message, icon_type, 3000)

    def _on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.show_window_requested.emit()
