"""
NightByte AI - Master GUI Main Window
Clean, modern, minimalist interface with platform selector and granular game targeting.
"""

import os
import sys
import webbrowser
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget,
    QComboBox, QFrame, QScrollArea, QListWidget, QListWidgetItem, QTabWidget,
    QCheckBox, QRadioButton, QButtonGroup, QApplication
)
from PySide6.QtCore import Qt, QPoint, Signal, QTimer
from PySide6.QtGui import QIcon, QColor, QFont, QPixmap

from i18n.translations import tr
from utils.config import ConfigManager
from utils.logger import logger
from utils.updater import UpdateChecker, CURRENT_VERSION
from core.monitor_engine import MonitorEngine, MonitorState
from gui.widgets.speed_graph import LiveSpeedGraph
from gui.widgets.download_card import DownloadCard
from gui.countdown_dialog import CountdownWarningDialog
from gui.settings_dialog import SettingsScreen
from gui.tray_manager import TrayManager
from themes.theme_manager import ThemeManager


class MainWindow(QWidget):
    """The master application window."""

    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.engine = MonitorEngine(self)
        self.updater = UpdateChecker(self)
        self.countdown_dialog = None
        self.latest_update_url = ""
        self.active_cards = {}  # item_id -> DownloadCard

        # Window properties
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.resize(740, 640)
        self.setMinimumSize(640, 520)

        self.dragging = False
        self.drag_position = QPoint()

        # Build UI
        self.setup_ui()
        self.apply_language_and_direction()

        # System Tray
        app_icon = self._get_app_icon()
        self.setWindowIcon(app_icon)
        self.tray = TrayManager(app_icon, self)
        self._connect_tray_signals()
        self.tray.show()

        # Connect Engine Signals
        self.engine.stats_updated.connect(self._on_stats_updated)
        self.engine.countdown_started.connect(self._on_countdown_started)
        self.engine.countdown_tick.connect(self._on_countdown_tick)
        self.engine.countdown_aborted.connect(self._on_countdown_aborted)
        self.engine.action_executed.connect(self._on_action_executed)

        # Connect Updater
        self.updater.update_available.connect(self._on_update_available)
        if self.config.get("auto_check_updates", True):
            QTimer.singleShot(2500, self.updater.check_for_updates_async)

        # Connect Logger
        logger.log_added.connect(self._on_log_added)
        for t, lvl, msg in logger.history:
            self._on_log_added(t, lvl, msg)

    def _get_app_icon(self) -> QIcon:
        base_dir = getattr(sys, "_MEIPASS", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
        icon_path = os.path.join(base_dir, "assets", "app_icon.png")
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        ico_path = os.path.join(base_dir, "assets", "app_icon.ico")
        if os.path.exists(ico_path):
            return QIcon(ico_path)
        pix = QPixmap(64, 64)
        pix.fill(QColor("#0284c7"))
        return QIcon(pix)

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Title Bar
        self.title_bar = self._create_title_bar()
        main_layout.addWidget(self.title_bar)

        # 2. Update Banner (Hidden by default)
        self.update_banner = QPushButton()
        self.update_banner.setObjectName("UpdateBanner")
        self.update_banner.setCursor(Qt.PointingHandCursor)
        self.update_banner.clicked.connect(self._open_update_link)
        self.update_banner.hide()
        main_layout.addWidget(self.update_banner)

        # 3. Main Content Container
        self.content_container = QWidget()
        content_layout = QVBoxLayout(self.content_container)
        content_layout.setContentsMargins(12, 10, 12, 12)
        content_layout.setSpacing(8)

        self.nav_tabs = QTabWidget()
        self.nav_tabs.setObjectName("MainTabs")

        # Tabs
        self.dashboard_tab = self._create_dashboard_tab()
        self.nav_tabs.addTab(self.dashboard_tab, "📊 Dashboard")

        self.downloads_tab = self._create_downloads_tab()
        self.nav_tabs.addTab(self.downloads_tab, "🎮 Downloads")

        self.logs_tab = self._create_logs_tab()
        self.nav_tabs.addTab(self.logs_tab, "📜 Log & Guide")

        self.settings_screen = SettingsScreen()
        self.settings_screen.settings_saved.connect(self._on_settings_saved)
        self.nav_tabs.addTab(self.settings_screen, "⚙️ Settings")

        content_layout.addWidget(self.nav_tabs)
        main_layout.addWidget(self.content_container)

    def _create_title_bar(self) -> QWidget:
        title_bar = QWidget()
        title_bar.setObjectName("TitleBar")
        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(14, 0, 8, 0)
        layout.setSpacing(8)

        self.title_label = QLabel("⚡ NightByte")
        self.title_label.setObjectName("AppTitle")
        layout.addWidget(self.title_label)

        self.version_tag = QLabel(f"v{CURRENT_VERSION}")
        self.version_tag.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 600;")
        layout.addWidget(self.version_tag)

        layout.addStretch()

        self.lang_btn = QPushButton("🌐 العربية")
        self.lang_btn.setObjectName("TitleButton")
        self.lang_btn.setCursor(Qt.PointingHandCursor)
        self.lang_btn.clicked.connect(self._toggle_language)
        layout.addWidget(self.lang_btn)

        min_btn = QPushButton("─")
        min_btn.setObjectName("TitleButton")
        min_btn.setCursor(Qt.PointingHandCursor)
        min_btn.clicked.connect(self.showMinimized)
        layout.addWidget(min_btn)

        close_btn = QPushButton("✕")
        close_btn.setObjectName("CloseTitleButton")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self._handle_close_button)
        layout.addWidget(close_btn)

        return title_bar

    def _create_dashboard_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)

        # 1. Minimalist Hero Card
        hero_card = QFrame()
        hero_card.setObjectName("HeroCard")
        hero_layout = QVBoxLayout(hero_card)
        hero_layout.setContentsMargins(16, 12, 16, 12)
        hero_layout.setSpacing(10)

        top_row = QHBoxLayout()
        self.hero_speed_val = QLabel("0.0")
        self.hero_speed_val.setObjectName("HeroSpeed")
        top_row.addWidget(self.hero_speed_val)

        self.hero_speed_unit = QLabel("KB/s")
        self.hero_speed_unit.setObjectName("HeroSpeedUnit")
        top_row.addWidget(self.hero_speed_unit)

        top_row.addStretch()

        self.net_badge = QLabel("🟢 متصل")
        self.net_badge.setStyleSheet("background: #0f172a; color: #10b981; border: 1px solid #1e293b; border-radius: 6px; padding: 4px 10px; font-weight: bold; font-size: 11px;")
        top_row.addWidget(self.net_badge)
        hero_layout.addLayout(top_row)

        # Master Start/Stop Button
        self.power_btn = QPushButton("▶️ بدء المراقبة الذكية")
        self.power_btn.setObjectName("MasterPowerBtn")
        self.power_btn.setCursor(Qt.PointingHandCursor)
        self.power_btn.clicked.connect(self._toggle_monitoring)
        hero_layout.addWidget(self.power_btn)

        layout.addWidget(hero_card)

        # 2. Platform Chips Row (Interactive Checkboxes for platforms!)
        platform_frame = QFrame()
        platform_frame.setStyleSheet("background-color: #111827; border: 1px solid #1f2937; border-radius: 8px; padding: 6px;")
        platform_layout = QHBoxLayout(platform_frame)
        platform_layout.setContentsMargins(8, 4, 8, 4)
        platform_layout.setSpacing(10)

        plat_title = QLabel("المنصات:")
        plat_title.setStyleSheet("color: #94a3b8; font-weight: bold; font-size: 11px;")
        platform_layout.addWidget(plat_title)

        self.chip_steam = QCheckBox("Steam")
        self.chip_steam.setChecked(True)
        self.chip_steam.toggled.connect(lambda c: self.engine.set_platform_enabled("steam", c))
        platform_layout.addWidget(self.chip_steam)

        self.chip_epic = QCheckBox("Epic Games")
        self.chip_epic.setChecked(True)
        self.chip_epic.toggled.connect(lambda c: self.engine.set_platform_enabled("epic", c))
        platform_layout.addWidget(self.chip_epic)

        self.chip_torrent = QCheckBox("Torrent")
        self.chip_torrent.setChecked(True)
        self.chip_torrent.toggled.connect(lambda c: self.engine.set_platform_enabled("torrent", c))
        platform_layout.addWidget(self.chip_torrent)

        self.chip_ea = QCheckBox("EA / Battle.net")
        self.chip_ea.setChecked(True)
        self.chip_ea.toggled.connect(lambda c: self.engine.set_platform_enabled("ea_bnet", c))
        platform_layout.addWidget(self.chip_ea)

        self.chip_idm = QCheckBox("IDM / متصفح")
        self.chip_idm.setChecked(True)
        self.chip_idm.toggled.connect(lambda c: self.engine.set_platform_enabled("idm", c))
        platform_layout.addWidget(self.chip_idm)

        layout.addWidget(platform_frame)

        # 3. Vector Speed Graph
        self.speed_graph = LiveSpeedGraph()
        layout.addWidget(self.speed_graph)

        # 4. Action Selector Row
        action_bar = QHBoxLayout()
        action_bar.setSpacing(8)

        self.action_label = QLabel("عند انتهاء التحميل:")
        self.action_label.setStyleSheet("color: #cbd5e1; font-weight: bold; font-size: 12px;")
        action_bar.addWidget(self.action_label)

        self.action_combo = QComboBox()
        self.action_combo.setObjectName("ActionCombo")
        self._populate_actions_combo()
        self.action_combo.currentIndexChanged.connect(self._on_action_changed)
        action_bar.addWidget(self.action_combo, stretch=1)

        layout.addLayout(action_bar)

        # 5. Status Banner
        self.status_banner = QFrame()
        self.status_banner.setObjectName("StatusBanner")
        banner_layout = QHBoxLayout(self.status_banner)
        banner_layout.setContentsMargins(12, 6, 12, 6)

        self.status_icon = QLabel("💡")
        banner_layout.addWidget(self.status_icon)

        self.status_text = QLabel("جاهز - اضغط على الزر للبدء")
        self.status_text.setObjectName("StatusText")
        banner_layout.addWidget(self.status_text, stretch=1)

        layout.addWidget(self.status_banner)
        return widget

    def _create_downloads_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(8)

        # Target Mode Switch Header
        mode_frame = QFrame()
        mode_frame.setStyleSheet("background-color: #111827; border: 1px solid #1f2937; border-radius: 8px; padding: 6px;")
        mode_layout = QHBoxLayout(mode_frame)
        mode_layout.setContentsMargins(8, 4, 8, 4)

        mode_lbl = QLabel("🎯 وضع الهدف:")
        mode_lbl.setStyleSheet("color: #38bdf8; font-weight: bold; font-size: 11px;")
        mode_layout.addWidget(mode_lbl)

        self.radio_mode_all = QRadioButton("كل التحميلات في المنصات المحددة")
        self.radio_mode_all.setChecked(True)
        self.radio_mode_all.toggled.connect(self._on_target_mode_toggled)
        mode_layout.addWidget(self.radio_mode_all)

        self.radio_mode_selected = QRadioButton("فقط الألعاب / الملفات المحددة بالصح (✓)")
        self.radio_mode_selected.toggled.connect(self._on_target_mode_toggled)
        mode_layout.addWidget(self.radio_mode_selected)

        mode_layout.addStretch()
        layout.addWidget(mode_frame)

        # Scroll Area for active cards
        self.downloads_scroll = QScrollArea()
        self.downloads_scroll.setWidgetResizable(True)

        self.downloads_container = QWidget()
        self.downloads_layout = QVBoxLayout(self.downloads_container)
        self.downloads_layout.setContentsMargins(4, 4, 4, 4)
        self.downloads_layout.setSpacing(6)
        self.downloads_layout.setAlignment(Qt.AlignTop)

        self.empty_label = QLabel("لا توجد ألعاب أو تنزيلات نشطة حالياً.\n(بمجرد بدء أي تحميل في ستيم أو إيبك أو التورنت، ستظهر هنا فوراً)")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("color: #64748b; font-size: 13px; margin-top: 40px;")
        self.downloads_layout.addWidget(self.empty_label)

        self.downloads_scroll.setWidget(self.downloads_container)
        layout.addWidget(self.downloads_scroll)
        return widget

    def _create_logs_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(8)

        guide_banner = QFrame()
        guide_banner.setStyleSheet("background-color: #111827; border: 1px solid #1e293b; border-radius: 8px; padding: 8px 12px;")
        guide_layout = QHBoxLayout(guide_banner)
        guide_lbl = QLabel("📖 <b>سجل النشاط المباشر:</b> يشرح باللغة البسيطة ما يفعله البرنامج لحظة بلحظة (فحص النت، كشف الألعاب، مؤقتات الإيقاف، وحماية تفاعل المستخدم).")
        guide_lbl.setWordWrap(True)
        guide_lbl.setStyleSheet("color: #94a3b8; font-size: 11px;")
        guide_layout.addWidget(guide_lbl)
        layout.addWidget(guide_banner)

        self.log_list = QListWidget()
        self.log_list.setObjectName("LogList")
        layout.addWidget(self.log_list)

        btn_bar = QHBoxLayout()
        btn_bar.addStretch()
        self.clear_logs_btn = QPushButton("🗑️ مسح السجل")
        self.clear_logs_btn.setObjectName("SecondaryButton")
        self.clear_logs_btn.clicked.connect(self.log_list.clear)
        btn_bar.addWidget(self.clear_logs_btn)
        layout.addLayout(btn_bar)

        return widget

    def _on_target_mode_toggled(self):
        if self.radio_mode_selected.isChecked():
            self.engine.set_target_mode("selected")
        else:
            self.engine.set_target_mode("all")

    def _populate_actions_combo(self):
        lang = self.config.get("language", "ar")
        self.action_combo.blockSignals(True)
        self.action_combo.clear()

        actions = [
            ("action_shutdown", "shutdown"),
            ("action_sleep", "sleep"),
            ("action_hibernate", "hibernate"),
            ("action_restart", "restart"),
            ("action_lock", "lock"),
            ("action_logoff", "logoff"),
            ("action_close_launchers", "close_launchers"),
            ("action_monitors_off", "monitors_off"),
        ]

        curr_act = self.config.get("default_action", "shutdown")
        select_idx = 0
        for i, (key, val) in enumerate(actions):
            self.action_combo.addItem(tr(key, lang), val)
            if val == curr_act:
                select_idx = i

        self.action_combo.setCurrentIndex(select_idx)
        self.action_combo.blockSignals(False)

    def _on_action_changed(self, index: int):
        action_val = self.action_combo.currentData()
        if action_val:
            self.config.set("default_action", action_val)
            logger.info(f"Scheduled action set to: {action_val}")

    def _toggle_monitoring(self):
        if self.engine.is_enabled:
            self.engine.stop_monitoring()
        else:
            self.engine.start_monitoring()
        self._update_power_button_ui()

    def _update_power_button_ui(self):
        lang = self.config.get("language", "ar")
        if self.engine.is_enabled:
            self.power_btn.setText(f"⏸️ {tr('btn_disable', lang)}")
            self.power_btn.setProperty("active", "true")
        else:
            self.power_btn.setText(f"▶️ {tr('btn_enable', lang)}")
            self.power_btn.setProperty("active", "false")
        self.power_btn.style().unpolish(self.power_btn)
        self.power_btn.style().polish(self.power_btn)

    def _toggle_language(self):
        cur = self.config.get("language", "ar")
        new_lang = "en" if cur == "ar" else "ar"
        self.config.set("language", new_lang)
        self.apply_language_and_direction()

    def apply_language_and_direction(self):
        lang = self.config.get("language", "ar")
        is_rtl = (lang == "ar")
        self.setLayoutDirection(Qt.RightToLeft if is_rtl else Qt.LeftToRight)

        self.lang_btn.setText("English" if lang == "ar" else "العربية")
        self.title_label.setText(tr("app_name", lang))

        self.nav_tabs.setTabText(0, f"📊 {tr('tab_dashboard', lang)}")
        self.nav_tabs.setTabText(1, f"🎮 {tr('tab_downloads', lang)}")
        self.nav_tabs.setTabText(2, f"📜 {tr('tab_logs', lang)}")
        self.nav_tabs.setTabText(3, f"⚙️ {tr('tab_settings', lang)}")

        self._update_power_button_ui()
        self.action_label.setText(tr("label_select_action", lang))
        self._populate_actions_combo()
        self.clear_logs_btn.setText(f"🗑️ {tr('btn_clear_logs', lang)}")
        self.empty_label.setText(tr("no_active_downloads", lang))

        self.settings_screen.setup_ui()
        self.settings_screen.load_values()

    def _on_stats_updated(self, snapshot: dict):
        lang = self.config.get("language", "ar")
        speed_kb = snapshot["download_speed_kb"]
        is_online = snapshot["is_online"]
        ping = snapshot["ping_ms"]
        active_items = snapshot["active_items"]

        # Hero Speed
        if speed_kb >= 1024.0:
            self.hero_speed_val.setText(f"{speed_kb / 1024.0:.1f}")
            self.hero_speed_unit.setText("MB/s")
        else:
            self.hero_speed_val.setText(f"{speed_kb:.0f}")
            self.hero_speed_unit.setText("KB/s")

        # Net status badge
        if is_online:
            self.net_badge.setText(f"🟢 {tr('net_online', lang)} ({ping:.0f}ms)")
            self.net_badge.setStyleSheet("background: #0f172a; color: #10b981; border: 1px solid #1e293b; border-radius: 6px; padding: 4px 10px; font-weight: bold; font-size: 11px;")
        else:
            off_sec = snapshot["offline_duration_sec"]
            self.net_badge.setText(f"🔴 {tr('net_offline', lang)} ({off_sec}s)")
            self.net_badge.setStyleSheet("background: #450a0a; color: #ef4444; border: 1px solid #ef4444; border-radius: 6px; padding: 4px 10px; font-weight: bold; font-size: 11px;")

        # Vector Graph
        self.speed_graph.update_history(snapshot["speed_history"], speed_kb, snapshot["peak_speed_kb"])

        # Status Banner
        self._update_status_banner(snapshot["state"], snapshot["status_message"], lang)

        # Interactive Download Cards with Selection
        self._update_download_cards(active_items)

        # Tray
        self.tray.update_status(snapshot["is_enabled"], speed_kb, is_online, snapshot["status_message"])

    def _update_status_banner(self, state: str, message: str, lang: str):
        if state == MonitorState.IDLE:
            self.status_icon.setText("⏸️")
            self.status_text.setText(tr("status_idle", lang))
            self.status_text.setStyleSheet("color: #94a3b8;")
        elif state == MonitorState.ACTIVE_DOWNLOADING:
            self.status_icon.setText("🚀")
            self.status_text.setText(f"{tr('status_downloading', lang)} ({message})")
            self.status_text.setStyleSheet("color: #38bdf8;")
        elif state == MonitorState.BELOW_THRESHOLD:
            self.status_icon.setText("⏳")
            self.status_text.setText(f"{tr('status_below_threshold', lang)} - {message}")
            self.status_text.setStyleSheet("color: #f59e0b;")
        elif state == MonitorState.PAUSED_NET_DROP:
            self.status_icon.setText("⚠️")
            self.status_text.setText(f"{tr('status_paused_network', lang)}")
            self.status_text.setStyleSheet("color: #ef4444; font-weight: bold;")
        elif state == MonitorState.PAUSED_AFK:
            self.status_icon.setText("🛡️")
            self.status_text.setText(tr("status_paused_afk", lang))
            self.status_text.setStyleSheet("color: #a855f7;")
        elif state == MonitorState.COUNTDOWN:
            self.status_icon.setText("🚨")
            self.status_text.setText(tr("status_countdown", lang))
            self.status_text.setStyleSheet("color: #ef4444; font-weight: bold;")

    def _update_download_cards(self, active_items: list):
        current_ids = {item.get("id") for item in active_items if item.get("id")}
        
        # Remove old cards no longer present
        for old_id in list(self.active_cards.keys()):
            if old_id not in current_ids:
                card = self.active_cards.pop(old_id)
                self.downloads_layout.removeWidget(card)
                card.deleteLater()

        if not active_items:
            self.empty_label.show()
        else:
            self.empty_label.hide()
            for item in active_items:
                iid = item.get("id")
                if not iid:
                    continue
                if iid in self.active_cards:
                    self.active_cards[iid].update_data(item)
                else:
                    # New item detected -> default selected
                    is_sel = iid in self.engine.selected_item_ids or not self.engine.selected_item_ids
                    if is_sel:
                        self.engine.selected_item_ids.add(iid)
                    card = DownloadCard(item, is_selected=is_sel)
                    card.selection_changed.connect(self._on_card_selection_changed)
                    self.active_cards[iid] = card
                    self.downloads_layout.insertWidget(self.downloads_layout.count() - 1, card)

    def _on_card_selection_changed(self, item_id: str, is_selected: bool):
        self.engine.toggle_item_selection(item_id, is_selected)
        logger.info(f"Toggled item selection: {item_id} -> {is_selected}")

    def _on_update_available(self, version: str, notes: str, url: str):
        lang = self.config.get("language", "ar")
        self.latest_update_url = url
        self.update_banner.setText(tr("update_available_banner", lang, version=f"v{version}"))
        self.update_banner.show()

    def _open_update_link(self):
        if self.latest_update_url:
            webbrowser.open(self.latest_update_url)

    def _on_countdown_started(self, duration: int, action: str):
        if self.countdown_dialog:
            self.countdown_dialog.close()
        self.countdown_dialog = CountdownWarningDialog(duration, action, self.engine, self)
        self.countdown_dialog.show()
        lang = self.config.get("language", "ar")
        self.tray.show_notification(tr("countdown_title", lang), tr("countdown_desc", lang))

    def _on_countdown_tick(self, remaining: int):
        if self.countdown_dialog and self.countdown_dialog.isVisible():
            self.countdown_dialog.update_tick(remaining)

    def _on_countdown_aborted(self, reason: str):
        if self.countdown_dialog:
            self.countdown_dialog.close()
            self.countdown_dialog = None
        self.tray.show_notification("NightByte", f"Countdown Cancelled: {reason}")

    def _on_action_executed(self, action: str):
        if self.countdown_dialog:
            self.countdown_dialog.close()
            self.countdown_dialog = None

    def _on_log_added(self, timestamp: str, level: str, msg: str):
        item = QListWidgetItem(f"[{timestamp}]  {msg}")
        if level == "SUCCESS":
            item.setForeground(QColor("#10b981"))
        elif level == "WARNING":
            item.setForeground(QColor("#f59e0b"))
        elif level == "ERROR":
            item.setForeground(QColor("#ef4444"))
        else:
            item.setForeground(QColor("#94a3b8"))
        self.log_list.addItem(item)
        self.log_list.scrollToBottom()

    def _on_settings_saved(self):
        self.apply_language_and_direction()

    def _connect_tray_signals(self):
        self.tray.show_window_requested.connect(self._show_and_activate)
        self.tray.toggle_monitoring_requested.connect(self._toggle_monitoring)
        self.tray.cancel_shutdown_requested.connect(lambda: self.engine.cancel_countdown("Tray Cancel"))
        self.tray.quit_requested.connect(QApplication.instance().quit)

    def _show_and_activate(self):
        self.showNormal()
        self.activateWindow()

    def _handle_close_button(self):
        if self.config.get("close_to_tray", True):
            self.hide()
            self.tray.show_notification(
                "NightByte",
                "Application minimized to System Tray / تم تصغير البرنامج لشريط المهام"
            )
        else:
            QApplication.instance().quit()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and event.position().y() <= 40:
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
