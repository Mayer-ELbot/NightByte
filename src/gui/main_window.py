"""
NightByte AI - Master GUI Main Window
Inverted monochrome dark. English-only. Zero clutter. Bold minimalist design.
Displays live downloads, session completed history, and system action schedules.
"""

import os
import sys
import webbrowser
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QFrame, QScrollArea, QListWidget, QListWidgetItem,
    QTabWidget, QRadioButton, QApplication
)
from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtGui import QIcon, QFont

from i18n.translations import t
from utils.config import ConfigManager
from utils.logger import logger
from utils.updater import UpdateChecker, CURRENT_VERSION
from core.monitor_engine import MonitorEngine, MonitorState
from gui.widgets.speed_graph import SpeedGraph
from gui.widgets.download_card import DownloadCard
from gui.widgets.history_card import HistoryCard
from gui.widgets.platform_chip import PlatformChip
from gui.countdown_dialog import CountdownWarningDialog
from gui.settings_dialog import SettingsScreen
from gui.tray_manager import TrayManager


def _h(spacing: int = 0, margins=(0, 0, 0, 0)) -> QHBoxLayout:
    lay = QHBoxLayout()
    lay.setSpacing(spacing)
    lay.setContentsMargins(*margins)
    return lay


def _v(spacing: int = 0, margins=(0, 0, 0, 0)) -> QVBoxLayout:
    lay = QVBoxLayout()
    lay.setSpacing(spacing)
    lay.setContentsMargins(*margins)
    return lay


def _lbl(text: str, obj_name: str = "", font_size: int = 0, bold: bool = False) -> QLabel:
    lb = QLabel(text)
    if obj_name:
        lb.setObjectName(obj_name)
    if font_size or bold:
        f = lb.font()
        if font_size:
            f.setPointSize(font_size)
        if bold:
            f.setWeight(QFont.ExtraBold)
        lb.setFont(f)
    return lb


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.engine = MonitorEngine(self)
        self.updater = UpdateChecker(self)
        self.countdown_dialog = None
        self.latest_update_url = ""
        self.active_cards: dict[str, DownloadCard] = {}
        self.history_cards_ids = set()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.resize(750, 640)
        self.setMinimumSize(660, 540)
        self.dragging = False
        self.drag_position = QPoint()

        self._build_ui()

        icon = self._get_app_icon()
        self.setWindowIcon(icon)
        self.tray = TrayManager(icon, self)
        self._connect_tray()
        self._connect_engine()

        # Update checker
        self.updater.update_available.connect(self._on_update_available)
        if self.config.get("auto_check_updates", True):
            QTimer.singleShot(3000, lambda: self.updater.check_async())

    def _get_app_icon(self) -> QIcon:
        for base in [
            os.path.dirname(os.path.abspath(sys.argv[0])),
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            os.path.dirname(os.path.abspath(__file__)),
            "."
        ]:
            ico = os.path.join(base, "assets", "app_icon.ico")
            if os.path.exists(ico):
                return QIcon(ico)
        return QIcon()

    def _build_ui(self):
        root = _v(0, (0, 0, 0, 0))
        root.addWidget(self._make_titlebar())
        root.addWidget(self._make_update_banner())
        root.addWidget(self._make_tabs(), 1)
        root.addWidget(self._make_statusbar())
        self.setLayout(root)

    # ── Title Bar ─────────────────────────────────────────────────────────────

    def _make_titlebar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("TitleBar")
        bar.setFixedHeight(44)
        lay = _h(0, (14, 0, 10, 0))

        title = _lbl("NightByte", "AppTitle")
        ver = _lbl(f"  v{CURRENT_VERSION}", "VersionLabel")

        lay.addWidget(title)
        lay.addWidget(ver)
        lay.addStretch()

        # Settings shortcut in titlebar
        self.settings_btn = QPushButton("Settings")
        self.settings_btn.setObjectName("TitleButton")
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.clicked.connect(self._open_settings)
        lay.addWidget(self.settings_btn)
        lay.addSpacing(6)

        # Window controls
        min_btn = QPushButton("—")
        min_btn.setObjectName("TitleButton")
        min_btn.setCursor(Qt.PointingHandCursor)
        min_btn.clicked.connect(self.showMinimized)
        lay.addWidget(min_btn)

        close_btn = QPushButton("✕")
        close_btn.setObjectName("CloseTitleButton")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self._close_or_tray)
        lay.addWidget(close_btn)

        bar.setLayout(lay)
        bar.setLayoutDirection(Qt.LeftToRight)
        return bar

    # ── Update Banner ─────────────────────────────────────────────────────────

    def _make_update_banner(self) -> QPushButton:
        self.update_banner = QPushButton("")
        self.update_banner.setObjectName("UpdateBanner")
        self.update_banner.setFixedHeight(36)
        self.update_banner.hide()
        self.update_banner.setCursor(Qt.PointingHandCursor)
        self.update_banner.clicked.connect(
            lambda: webbrowser.open(self.latest_update_url)
        )
        return self.update_banner

    # ── Tabs ──────────────────────────────────────────────────────────────────

    def _make_tabs(self) -> QTabWidget:
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.addTab(self._tab_dashboard(), "  Dashboard  ")
        self.tabs.addTab(self._tab_downloads(), "  Downloads & History  ")
        self.tabs.addTab(self._tab_log(), "  Live Log  ")
        self.tabs.addTab(self._make_settings_tab(), "  Settings  ")
        return self.tabs

    # ── Dashboard Tab ─────────────────────────────────────────────────────────

    def _tab_dashboard(self) -> QWidget:
        w = QWidget()
        lay = _v(12, (16, 16, 16, 16))

        # Speed Hero Row
        hero_row = _h(0)
        speed_col = _h(8)

        self.speed_value = _lbl("0", "HeroSpeed")
        self.speed_unit = _lbl("KB/s", "HeroSpeedUnit")

        f = self.speed_value.font()
        f.setPointSize(44)
        f.setWeight(QFont.Black)
        self.speed_value.setFont(f)

        speed_col.addWidget(self.speed_value)
        speed_col.setAlignment(self.speed_value, Qt.AlignBottom)
        speed_col.addWidget(self.speed_unit)
        speed_col.setAlignment(self.speed_unit, Qt.AlignBottom)
        speed_col.addStretch()

        hero_row.addLayout(speed_col)
        hero_row.addStretch()

        self.net_badge = QPushButton("● Online")
        self.net_badge.setObjectName("NetBadgeOnline")
        self.net_badge.setEnabled(False)
        hero_row.addWidget(self.net_badge)

        lay.addLayout(hero_row)

        # Start / Stop Button
        self.power_btn = QPushButton(t("btn_start"))
        self.power_btn.setObjectName("MasterPowerBtn")
        self.power_btn.setFixedHeight(48)
        self.power_btn.setCursor(Qt.PointingHandCursor)
        self.power_btn.clicked.connect(self._toggle_monitoring)
        lay.addWidget(self.power_btn)

        # Platform Chips Row
        plat_frame = QFrame()
        plat_frame.setObjectName("PlatformFrame")
        plat_lay = _h(8, (12, 10, 12, 10))

        plat_label = _lbl("Platforms:", "PlatformLabel")
        plat_lay.addWidget(plat_label)
        plat_lay.addSpacing(4)

        self.platform_chips: dict[str, PlatformChip] = {}
        chip_defs = [
            ("steam", "Steam", "monitor_steam"),
            ("epic", "Epic", "monitor_epic"),
            ("torrent", "Torrent", "monitor_torrents"),
            ("ea_bnet", "EA / BN", "monitor_ea"),
            ("idm", "IDM", "monitor_idm_browsers"),
        ]
        for key, label, cfg_key in chip_defs:
            active_val = self.config.get(cfg_key, True)
            chip = PlatformChip(label, key, active=active_val)
            chip.toggled_platform.connect(self._on_platform_toggle)
            self.platform_chips[key] = chip
            plat_lay.addWidget(chip)

        plat_lay.addStretch()
        plat_frame.setLayout(plat_lay)
        lay.addWidget(plat_frame)

        # Speed Graph
        self.graph = SpeedGraph()
        lay.addWidget(self.graph, 1)

        # Action Selector Row
        action_row = _h(12)
        action_label = _lbl(t("label_when_done"), "ActionLabel")
        action_row.addWidget(action_label)
        action_row.addStretch()

        self.action_combo = QComboBox()
        actions = [
            ("shutdown", t("action_shutdown")),
            ("sleep", t("action_sleep")),
            ("hibernate", t("action_hibernate")),
            ("restart", t("action_restart")),
            ("lock", t("action_lock")),
            ("logoff", t("action_logoff")),
            ("close_launchers", t("action_close_launchers")),
            ("monitors_off", t("action_monitors_off")),
        ]
        for key, lbl in actions:
            self.action_combo.addItem(lbl, key)

        saved_action = self.config.get("default_action", "shutdown")
        for i in range(self.action_combo.count()):
            if self.action_combo.itemData(i) == saved_action:
                self.action_combo.setCurrentIndex(i)
                break

        self.action_combo.setFixedWidth(210)
        self.action_combo.currentIndexChanged.connect(self._on_action_changed)
        action_row.addWidget(self.action_combo)
        lay.addLayout(action_row)

        w.setLayout(lay)
        return w

    # ── Downloads & History Tab ───────────────────────────────────────────────

    def _tab_downloads(self) -> QWidget:
        w = QWidget()
        lay = _v(12, (16, 16, 16, 16))

        # Target mode & Session summary banner
        mode_frame = QFrame()
        mode_frame.setObjectName("ModeFrame")
        ml = _h(14, (14, 10, 14, 10))

        lbl = _lbl(t("target_mode_label"), "ActionLabel")
        ml.addWidget(lbl)
        ml.addSpacing(6)

        self.mode_all_radio = QRadioButton(t("target_all"))
        self.mode_sel_radio = QRadioButton(t("target_selected"))
        self.mode_all_radio.setChecked(True)
        self.mode_all_radio.toggled.connect(
            lambda checked: self.engine.set_target_mode("all" if checked else "selected")
        )
        ml.addWidget(self.mode_all_radio)
        ml.addWidget(self.mode_sel_radio)
        ml.addStretch()

        # Session data pill
        self.session_data_pill = QLabel("Session: 0 MB")
        self.session_data_pill.setStyleSheet("""
            background-color: #1c1c1c;
            border: 1px solid #282828;
            border-radius: 6px;
            padding: 3px 8px;
            color: #888888;
            font-size: 11px;
            font-weight: 700;
        """)
        ml.addWidget(self.session_data_pill)

        mode_frame.setLayout(ml)
        lay.addWidget(mode_frame)

        # Scroll Area for Active & Completed Downloads
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.NoFrame)

        self.content_box = QWidget()
        self.content_box_layout = _v(14)
        self.content_box_layout.setAlignment(Qt.AlignTop)

        # Section 1: Active Downloads
        active_sec_header = _h(0)
        active_sec_header.addWidget(_lbl("Active Downloads", "ActionLabel"))
        self.content_box_layout.addLayout(active_sec_header)

        self.active_container = QWidget()
        self.cards_layout = _v(8)
        self.cards_layout.setAlignment(Qt.AlignTop)
        self.empty_lbl = _lbl("No active downloads detected.", "StatusText")
        self.empty_lbl.setAlignment(Qt.AlignCenter)
        self.cards_layout.addWidget(self.empty_lbl)
        self.active_container.setLayout(self.cards_layout)
        self.content_box_layout.addWidget(self.active_container)

        # Section 2: Session Completed History
        hist_sec_header = _h(0)
        hist_sec_header.addWidget(_lbl("Session Completed History", "ActionLabel"))
        self.content_box_layout.addLayout(hist_sec_header)

        self.history_container = QWidget()
        self.history_layout = _v(8)
        self.history_layout.setAlignment(Qt.AlignTop)
        self.empty_hist_lbl = _lbl("No completed downloads in this session yet.", "StatusText")
        self.empty_hist_lbl.setAlignment(Qt.AlignCenter)
        self.history_layout.addWidget(self.empty_hist_lbl)
        self.history_container.setLayout(self.history_layout)
        self.content_box_layout.addWidget(self.history_container)

        self.content_box.setLayout(self.content_box_layout)
        scroll.setWidget(self.content_box)
        lay.addWidget(scroll, 1)

        w.setLayout(lay)
        return w

    # ── Live Log Tab ──────────────────────────────────────────────────────────

    def _tab_log(self) -> QWidget:
        w = QWidget()
        lay = _v(10, (16, 16, 16, 16))

        header = _h(0)
        header.addWidget(_lbl("Live Activity Log", "ActionLabel"))
        header.addStretch()
        clr = QPushButton(t("btn_clear_logs"))
        clr.setObjectName("SecondaryButton")
        clr.setCursor(Qt.PointingHandCursor)
        clr.clicked.connect(lambda: self.log_list.clear())
        header.addWidget(clr)
        lay.addLayout(header)

        self.log_list = QListWidget()
        self.log_list.setObjectName("LogList")
        lay.addWidget(self.log_list, 1)
        w.setLayout(lay)
        return w

    # ── Settings Tab ──────────────────────────────────────────────────────────

    def _make_settings_tab(self) -> QWidget:
        container = QWidget()
        lay = _v(0, (0, 0, 0, 0))
        self._settings_screen = SettingsScreen(self.config, parent=container)
        lay.addWidget(self._settings_screen)
        container.setLayout(lay)
        return container

    # ── Status Bar ────────────────────────────────────────────────────────────

    def _make_statusbar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("StatusBar")
        lay = _h(0, (14, 0, 14, 0))
        self.status_lbl = _lbl("💡  " + t("status_idle"), "StatusText")
        lay.addWidget(self.status_lbl)
        lay.addStretch()
        bar.setLayout(lay)
        return bar

    # ── Connections ───────────────────────────────────────────────────────────

    def _connect_engine(self):
        e = self.engine
        e.stats_updated.connect(self._on_stats_updated)
        e.countdown_started.connect(self._on_countdown_start)
        e.countdown_tick.connect(self._on_countdown_tick)
        e.countdown_aborted.connect(self._on_countdown_aborted)
        e.action_executed.connect(self._on_action_executed)

    def _connect_tray(self):
        t_ = self.tray
        t_.show_requested.connect(self.show_window)
        t_.toggle_requested.connect(self._toggle_monitoring)
        t_.cancel_requested.connect(lambda: self.engine.cancel_countdown("Cancelled from tray"))
        t_.exit_requested.connect(self._exit_app)

    # ── Event Handlers ────────────────────────────────────────────────────────

    def _toggle_monitoring(self):
        if self.engine.is_enabled:
            self.engine.stop_monitoring()
        else:
            action = self.action_combo.currentData() or "shutdown"
            self.config.set("default_action", action)
            self.engine.start_monitoring()

    def _on_action_changed(self):
        action = self.action_combo.currentData() or "shutdown"
        self.config.set("default_action", action)

    def _on_stats_updated(self, snapshot: dict):
        is_running = snapshot.get("is_enabled", False)
        state = snapshot.get("state", MonitorState.IDLE)
        msg = snapshot.get("status_message", "Ready")
        speed_kb = snapshot.get("download_speed_kb", 0.0)
        is_online = snapshot.get("is_online", True)
        active_items = snapshot.get("active_items", [])
        completed_items = snapshot.get("completed_items", [])
        tot_session_bytes = snapshot.get("total_session_bytes", 0)

        # Update button state
        self.power_btn.setProperty("active", str(is_running).lower())
        self.power_btn.style().unpolish(self.power_btn)
        self.power_btn.style().polish(self.power_btn)
        self.power_btn.setText(t("btn_stop") if is_running else t("btn_start"))

        # Update speed metrics
        if speed_kb >= 1024.0:
            self.speed_value.setText(f"{speed_kb / 1024.0:.1f}")
            self.speed_unit.setText("MB/s")
        else:
            self.speed_value.setText(f"{speed_kb:.0f}")
            self.speed_unit.setText("KB/s")

        self.graph.add_point(speed_kb)

        # Update session data pill
        if tot_session_bytes >= 1024**3:
            self.session_data_pill.setText(f"Session: {tot_session_bytes / (1024**3):.2f} GB")
        elif tot_session_bytes >= 1024**2:
            self.session_data_pill.setText(f"Session: {tot_session_bytes / (1024**2):.1f} MB")
        else:
            self.session_data_pill.setText(f"Session: {tot_session_bytes / 1024:.0f} KB")

        # Update network status badge
        if is_online:
            self.net_badge.setText("● Online")
            self.net_badge.setObjectName("NetBadgeOnline")
        else:
            self.net_badge.setText("● Offline")
            self.net_badge.setObjectName("NetBadgeOffline")
        self.net_badge.style().unpolish(self.net_badge)
        self.net_badge.style().polish(self.net_badge)

        # Update status bar text
        if state == MonitorState.COUNTDOWN:
            self.status_lbl.setText(f"⚠️  {msg}")
            self.status_lbl.setObjectName("StatusTextWarning")
        elif is_running:
            self.status_lbl.setText(f"👁  {msg}")
            self.status_lbl.setObjectName("StatusTextActive")
        else:
            self.status_lbl.setText(f"💡  {msg}")
            self.status_lbl.setObjectName("StatusText")

        self.status_lbl.style().unpolish(self.status_lbl)
        self.status_lbl.style().polish(self.status_lbl)

        # Update tray status
        self.tray.update_status(msg, running=is_running)
        self.tray.set_countdown_active(state == MonitorState.COUNTDOWN)

        # Update active download cards & completed history cards
        self._update_download_cards(active_items)
        self._update_history_cards(completed_items)

        # Log significant state transitions
        if is_running and state in (MonitorState.COUNTDOWN, MonitorState.PAUSED_NET_DROP, MonitorState.PAUSED_AFK):
            self._log_feed(f"[{state}] {msg}")

    def _update_download_cards(self, items: list):
        current_ids = {item.get("id", item.get("item_id", "")) for item in items if item.get("id") or item.get("item_id")}

        # Remove finished/stale cards
        for iid in list(self.active_cards.keys()):
            if iid not in current_ids:
                card = self.active_cards.pop(iid)
                self.cards_layout.removeWidget(card)
                card.deleteLater()

        # Add or update existing cards
        for item in items:
            iid = item.get("id", item.get("item_id", ""))
            if not iid:
                continue
            if iid not in self.active_cards:
                is_selected = iid in self.engine.selected_item_ids if self.engine.selected_item_ids else True
                card = DownloadCard(item, is_selected=is_selected, parent=self.active_container)
                card.selection_changed.connect(self.engine.toggle_item_selection)
                self.cards_layout.insertWidget(0, card)
                self.active_cards[iid] = card
                self._log_feed(f"Detected active download: {item.get('name', 'App')} ({item.get('platform', 'App').upper()})")
            else:
                self.active_cards[iid].update_data(item)

        self.empty_lbl.setVisible(len(self.active_cards) == 0)

    def _update_history_cards(self, completed_items: list):
        for item in completed_items:
            iid = item.get("id", "")
            if iid and iid not in self.history_cards_ids:
                card = HistoryCard(item, parent=self.history_container)
                self.history_layout.insertWidget(0, card)
                self.history_cards_ids.add(iid)
                self._log_feed(f"Completed in this session: {item.get('name')} (Duration: {item.get('duration_str')}, Avg: {item.get('avg_speed_str')})")

        self.empty_hist_lbl.setVisible(len(self.history_cards_ids) == 0)

    def _log_feed(self, msg: str):
        item = QListWidgetItem(msg)
        self.log_list.insertItem(0, item)
        if self.log_list.count() > 300:
            self.log_list.takeItem(self.log_list.count() - 1)

    def _on_countdown_start(self, seconds: int, action: str):
        if not self.countdown_dialog:
            action_tr = t(f"action_{action}") if action else "Shutdown"
            self.countdown_dialog = CountdownWarningDialog(seconds, action_tr, self)
            self.countdown_dialog.cancelled.connect(lambda: self.engine.cancel_countdown("User cancelled"))
            self.countdown_dialog.snoozed.connect(self.engine.snooze)
            self.countdown_dialog.show()

    def _on_countdown_tick(self, remaining: int):
        if self.countdown_dialog:
            self.countdown_dialog.update_tick(remaining)

    def _on_countdown_aborted(self, reason: str):
        if self.countdown_dialog:
            self.countdown_dialog.close()
            self.countdown_dialog = None
        self._log_feed(f"Countdown cancelled: {reason}")

    def _on_action_executed(self, action: str):
        self._log_feed(f"Executed action: {action}")

    def _on_update_available(self, version: str, url: str):
        self.latest_update_url = url
        self.update_banner.setText(t("update_banner", version=version))
        self.update_banner.show()

    def _on_platform_toggle(self, key: str, enabled: bool):
        cfg_map = {
            "steam": "monitor_steam",
            "epic": "monitor_epic",
            "torrent": "monitor_torrents",
            "ea_bnet": "monitor_ea",
            "idm": "monitor_idm_browsers",
        }
        cfg_key = cfg_map.get(key)
        if cfg_key:
            self.config.set(cfg_key, enabled)
        self.engine.set_platform_enabled(key, enabled)
        self._log_feed(f"Platform '{key.upper()}' monitoring {'enabled' if enabled else 'disabled'}.")

    def _open_settings(self):
        self.tabs.setCurrentIndex(3)

    # ── Window Behavior & Dragging ────────────────────────────────────────────

    def _close_or_tray(self):
        if self.config.get("close_to_tray", True):
            self.hide()
            self.tray.show_tray_message("NightByte", "Running in background.")
        else:
            self._exit_app()

    def _exit_app(self):
        self.engine.stop_monitoring()
        QApplication.quit()

    def show_window(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton and e.position().y() < 44:
            self.dragging = True
            self.drag_position = e.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self.dragging and e.buttons() & Qt.LeftButton:
            self.move(e.globalPosition().toPoint() - self.drag_position)

    def mouseReleaseEvent(self, _):
        self.dragging = False

    def closeEvent(self, e):
        if self.config.get("close_to_tray", True):
            e.ignore()
            self.hide()
        else:
            self.engine.stop_monitoring()
            e.accept()
