"""
NightByte AI - Settings Screen & Dialog
Full-featured configuration dialog with grouped tabs, controls, and GitHub update check.
"""

import webbrowser
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, QSpinBox, 
    QCheckBox, QComboBox, QLineEdit, QPushButton, QFormLayout, QGroupBox,
    QMessageBox, QScrollArea
)
from PySide6.QtCore import Qt, Signal
import requests

from i18n.translations import tr
from utils.config import ConfigManager
from utils.updater import UpdateChecker, CURRENT_VERSION
from core.system_power import SystemPowerController
from utils.logger import logger


class SettingsScreen(QWidget):
    """Full-screen or tabbed settings management view."""

    settings_saved = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = ConfigManager()
        self.updater = UpdateChecker(self)
        self._connect_updater()
        self.setup_ui()
        self.load_values()

    def _connect_updater(self):
        self.updater.update_available.connect(self._on_update_found)
        self.updater.up_to_date.connect(self._on_up_to_date)
        self.updater.check_failed.connect(self._on_update_failed)

    def setup_ui(self):
        lang = self.config.get("language", "ar")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setObjectName("SettingsTabs")

        # Tab 1: General & Localization
        self.tab_general = self._create_general_tab(lang)
        self.tabs.addTab(self.tab_general, f"⚙️ {tr('settings_group_general', lang)}")

        # Tab 2: Network Guardian
        self.tab_guardian = self._create_guardian_tab(lang)
        self.tabs.addTab(self.tab_guardian, f"🛡️ {tr('settings_group_guardian', lang)}")

        # Tab 3: Triggers & Timers
        self.tab_triggers = self._create_triggers_tab(lang)
        self.tabs.addTab(self.tab_triggers, f"⏱️ {tr('settings_group_triggers', lang)}")

        # Tab 4: Safety & Anti-AFK
        self.tab_safety = self._create_safety_tab(lang)
        self.tabs.addTab(self.tab_safety, f"🧠 {tr('settings_group_protection', lang)}")

        # Tab 5: Monitored Platforms
        self.tab_platforms = self._create_platforms_tab(lang)
        self.tabs.addTab(self.tab_platforms, f"🎮 {tr('settings_group_platforms', lang)}")

        # Tab 6: Notifications & Updates
        self.tab_notifs = self._create_notifs_tab(lang)
        self.tabs.addTab(self.tab_notifs, f"🔔 {tr('settings_group_notifications', lang)}")

        main_layout.addWidget(self.tabs)

        # Bottom Action Bar
        bottom_bar = QHBoxLayout()
        self.reset_btn = QPushButton(f"🔄 {tr('btn_reset', lang)}")
        self.reset_btn.setObjectName("SecondaryButton")
        self.reset_btn.clicked.connect(self._on_reset_clicked)
        bottom_bar.addWidget(self.reset_btn)

        bottom_bar.addStretch()

        self.save_btn = QPushButton(f"💾 {tr('btn_save', lang)}")
        self.save_btn.setObjectName("PrimaryButton")
        self.save_btn.clicked.connect(self._on_save_clicked)
        bottom_bar.addWidget(self.save_btn)

        main_layout.addLayout(bottom_bar)

    def _create_general_tab(self, lang: str) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(14)

        form = QFormLayout()
        form.setSpacing(12)

        # Language
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("العربية (Arabic)", "ar")
        self.lang_combo.addItem("English (US)", "en")
        form.addRow(tr("setting_lang", lang), self.lang_combo)

        # Autostart
        self.autostart_check = QCheckBox(tr("setting_autostart", lang))
        layout.addLayout(form)
        layout.addWidget(self.autostart_check)

        # Tray options
        self.min_tray_check = QCheckBox(tr("setting_min_tray", lang))
        self.close_tray_check = QCheckBox(tr("setting_close_tray", lang))
        layout.addWidget(self.min_tray_check)
        layout.addWidget(self.close_tray_check)

        layout.addStretch()
        return widget

    def _create_guardian_tab(self, lang: str) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)

        self.guardian_enable_check = QCheckBox(tr("setting_guardian_enable", lang))
        self.guardian_pause_check = QCheckBox(tr("setting_guardian_pause", lang))
        self.guardian_resume_check = QCheckBox(tr("setting_guardian_resume", lang))

        layout.addWidget(self.guardian_enable_check)
        layout.addWidget(self.guardian_pause_check)
        layout.addWidget(self.guardian_resume_check)

        form = QFormLayout()
        self.max_offline_spin = QSpinBox()
        self.max_offline_spin.setRange(0, 86400)
        self.max_offline_spin.setSuffix(" sec")
        form.addRow(tr("setting_guardian_max_wait", lang), self.max_offline_spin)
        layout.addLayout(form)

        layout.addStretch()
        return widget

    def _create_triggers_tab(self, lang: str) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(12)

        # Threshold speed
        self.threshold_spin = QSpinBox()
        self.threshold_spin.setRange(1, 100000)
        self.threshold_spin.setSuffix(" KB/s")
        form.addRow(tr("setting_threshold_speed", lang), self.threshold_spin)

        # Inactivity timeout
        self.inactivity_spin = QSpinBox()
        self.inactivity_spin.setRange(10, 7200)
        self.inactivity_spin.setSuffix(" sec")
        form.addRow(tr("setting_inactivity_time", lang), self.inactivity_spin)

        # Countdown duration
        self.countdown_spin = QSpinBox()
        self.countdown_spin.setRange(5, 600)
        self.countdown_spin.setSuffix(" sec")
        form.addRow(tr("setting_countdown_time", lang), self.countdown_spin)

        layout.addLayout(form)
        layout.addStretch()
        return widget

    def _create_safety_tab(self, lang: str) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)

        self.anti_afk_check = QCheckBox(tr("setting_anti_afk", lang))
        layout.addWidget(self.anti_afk_check)

        form = QFormLayout()
        self.afk_timeout_spin = QSpinBox()
        self.afk_timeout_spin.setRange(10, 3600)
        self.afk_timeout_spin.setSuffix(" sec")
        form.addRow(tr("setting_afk_timeout", lang), self.afk_timeout_spin)
        layout.addLayout(form)

        self.gaming_mode_check = QCheckBox(tr("setting_gaming_mode", lang))
        self.prevent_sleep_check = QCheckBox(tr("setting_prevent_sleep", lang))
        layout.addWidget(self.gaming_mode_check)
        layout.addWidget(self.prevent_sleep_check)

        layout.addStretch()
        return widget

    def _create_platforms_tab(self, lang: str) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)

        self.mon_steam_check = QCheckBox(tr("setting_mon_steam", lang))
        self.mon_epic_check = QCheckBox(tr("setting_mon_epic", lang))
        self.mon_ea_check = QCheckBox(tr("setting_mon_ea", lang))
        self.mon_battlenet_check = QCheckBox(tr("setting_mon_battlenet", lang))
        self.mon_xbox_check = QCheckBox(tr("setting_mon_xbox", lang))
        self.mon_ubisoft_check = QCheckBox(tr("setting_mon_ubisoft", lang))
        self.mon_torrents_check = QCheckBox(tr("setting_mon_torrents", lang))
        self.mon_idm_check = QCheckBox(tr("setting_mon_idm", lang))
        self.mon_system_check = QCheckBox(tr("setting_mon_system_io", lang))

        layout.addWidget(self.mon_steam_check)
        layout.addWidget(self.mon_epic_check)
        layout.addWidget(self.mon_ea_check)
        layout.addWidget(self.mon_battlenet_check)
        layout.addWidget(self.mon_xbox_check)
        layout.addWidget(self.mon_ubisoft_check)
        layout.addWidget(self.mon_torrents_check)
        layout.addWidget(self.mon_idm_check)
        layout.addWidget(self.mon_system_check)

        layout.addStretch()
        return widget

    def _create_notifs_tab(self, lang: str) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)

        self.sound_enable_check = QCheckBox(tr("setting_sound_enable", lang))
        self.sound_ticks_check = QCheckBox(tr("setting_sound_ticks", lang))
        self.tray_notifs_check = QCheckBox(tr("setting_tray_notif", lang))
        self.auto_check_updates_check = QCheckBox(tr("setting_auto_check_updates", lang))

        layout.addWidget(self.sound_enable_check)
        layout.addWidget(self.sound_ticks_check)
        layout.addWidget(self.tray_notifs_check)
        layout.addWidget(self.auto_check_updates_check)

        # Webhook section
        form = QFormLayout()
        self.webhook_edit = QLineEdit()
        self.webhook_edit.setPlaceholderText("https://discord.com/api/webhooks/...")
        form.addRow(tr("setting_webhook_url", lang), self.webhook_edit)
        layout.addLayout(form)

        btn_row = QHBoxLayout()
        self.test_webhook_btn = QPushButton(f"🚀 {tr('btn_test_webhook', lang)}")
        self.test_webhook_btn.setObjectName("SecondaryButton")
        self.test_webhook_btn.clicked.connect(self._on_test_webhook)
        btn_row.addWidget(self.test_webhook_btn)

        # Update check button
        self.check_updates_btn = QPushButton(f"🔄 {tr('update_btn_check', lang)}")
        self.check_updates_btn.setObjectName("SecondaryButton")
        self.check_updates_btn.clicked.connect(self._on_manual_check_update)
        btn_row.addWidget(self.check_updates_btn)

        layout.addLayout(btn_row)
        layout.addStretch()
        return widget

    def load_values(self):
        """Populate controls from ConfigManager."""
        cur_lang = self.config.get("language", "ar")
        idx = self.lang_combo.findData(cur_lang)
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)

        # General
        self.autostart_check.setChecked(bool(self.config.get("start_with_windows", False)))
        self.min_tray_check.setChecked(bool(self.config.get("minimize_to_tray", True)))
        self.close_tray_check.setChecked(bool(self.config.get("close_to_tray", True)))

        # Guardian
        self.guardian_enable_check.setChecked(bool(self.config.get("network_guardian_enabled", True)))
        self.guardian_pause_check.setChecked(bool(self.config.get("pause_on_disconnect", True)))
        self.guardian_resume_check.setChecked(bool(self.config.get("auto_resume_on_reconnect", True)))
        self.max_offline_spin.setValue(int(self.config.get("max_offline_wait_sec", 1800)))

        # Triggers
        self.threshold_spin.setValue(int(self.config.get("threshold_speed_kb", 50)))
        self.inactivity_spin.setValue(int(self.config.get("inactivity_timeout_sec", 180)))
        self.countdown_spin.setValue(int(self.config.get("countdown_duration_sec", 60)))

        # Safety
        self.anti_afk_check.setChecked(bool(self.config.get("anti_afk_enabled", True)))
        self.afk_timeout_spin.setValue(int(self.config.get("afk_threshold_sec", 300)))
        self.gaming_mode_check.setChecked(bool(self.config.get("gaming_mode_protection", True)))
        self.prevent_sleep_check.setChecked(bool(self.config.get("prevent_sleep_during_download", True)))

        # Platforms
        self.mon_steam_check.setChecked(bool(self.config.get("monitor_steam", True)))
        self.mon_epic_check.setChecked(bool(self.config.get("monitor_epic", True)))
        self.mon_ea_check.setChecked(bool(self.config.get("monitor_ea", True)))
        self.mon_battlenet_check.setChecked(bool(self.config.get("monitor_battlenet", True)))
        self.mon_xbox_check.setChecked(bool(self.config.get("monitor_xbox", True)))
        self.mon_ubisoft_check.setChecked(bool(self.config.get("monitor_ubisoft", True)))
        self.mon_torrents_check.setChecked(bool(self.config.get("monitor_torrents", True)))
        self.mon_idm_check.setChecked(bool(self.config.get("monitor_idm_browsers", True)))
        self.mon_system_check.setChecked(bool(self.config.get("monitor_entire_system_io", True)))

        # Notifs
        self.sound_enable_check.setChecked(bool(self.config.get("sound_alerts_enabled", True)))
        self.sound_ticks_check.setChecked(bool(self.config.get("sound_countdown_ticks", True)))
        self.tray_notifs_check.setChecked(bool(self.config.get("system_tray_notifications", True)))
        self.auto_check_updates_check.setChecked(bool(self.config.get("auto_check_updates", True)))
        self.webhook_edit.setText(self.config.get("webhook_url", ""))

    def _on_save_clicked(self):
        """Save settings to config file."""
        new_lang = self.lang_combo.currentData()
        autostart = self.autostart_check.isChecked()

        if autostart != self.config.get("start_with_windows"):
            SystemPowerController.set_autostart_registry(autostart)

        updates = {
            "language": new_lang,
            "start_with_windows": autostart,
            "minimize_to_tray": self.min_tray_check.isChecked(),
            "close_to_tray": self.close_tray_check.isChecked(),

            "network_guardian_enabled": self.guardian_enable_check.isChecked(),
            "pause_on_disconnect": self.guardian_pause_check.isChecked(),
            "auto_resume_on_reconnect": self.guardian_resume_check.isChecked(),
            "max_offline_wait_sec": self.max_offline_spin.value(),

            "threshold_speed_kb": self.threshold_spin.value(),
            "inactivity_timeout_sec": self.inactivity_spin.value(),
            "countdown_duration_sec": self.countdown_spin.value(),

            "anti_afk_enabled": self.anti_afk_check.isChecked(),
            "afk_threshold_sec": self.afk_timeout_spin.value(),
            "gaming_mode_protection": self.gaming_mode_check.isChecked(),
            "prevent_sleep_during_download": self.prevent_sleep_check.isChecked(),

            "monitor_steam": self.mon_steam_check.isChecked(),
            "monitor_epic": self.mon_epic_check.isChecked(),
            "monitor_ea": self.mon_ea_check.isChecked(),
            "monitor_battlenet": self.mon_battlenet_check.isChecked(),
            "monitor_xbox": self.mon_xbox_check.isChecked(),
            "monitor_ubisoft": self.mon_ubisoft_check.isChecked(),
            "monitor_torrents": self.mon_torrents_check.isChecked(),
            "monitor_idm_browsers": self.mon_idm_check.isChecked(),
            "monitor_entire_system_io": self.mon_system_check.isChecked(),

            "sound_alerts_enabled": self.sound_enable_check.isChecked(),
            "sound_countdown_ticks": self.sound_ticks_check.isChecked(),
            "system_tray_notifications": self.tray_notifs_check.isChecked(),
            "auto_check_updates": self.auto_check_updates_check.isChecked(),
            "webhook_url": self.webhook_edit.text().strip(),
        }

        self.config.update(updates)
        logger.success("Settings saved successfully.")
        self.settings_saved.emit()
        QMessageBox.information(self, "NightByte AI", "Settings saved successfully! / تم حفظ الإعدادات بنجاح")

    def _on_reset_clicked(self):
        """Reset all values to defaults."""
        self.config.reset_to_defaults()
        self.load_values()
        logger.info("Settings reset to defaults.")

    def _on_manual_check_update(self):
        """Trigger update check."""
        self.check_updates_btn.setText("⏳ Checking...")
        self.check_updates_btn.setEnabled(False)
        self.updater.check_for_updates_async()

    def _on_update_found(self, version: str, notes: str, url: str):
        self.check_updates_btn.setText("🔄 Check for Updates")
        self.check_updates_btn.setEnabled(True)
        ret = QMessageBox.information(
            self,
            "Update Available",
            f"A new version of NightByte is available: v{version}\n\nWould you like to view the release page to download it?",
            QMessageBox.Yes | QMessageBox.No
        )
        if ret == QMessageBox.Yes:
            webbrowser.open(url)

    def _on_up_to_date(self, version: str):
        self.check_updates_btn.setText("🔄 Check for Updates")
        self.check_updates_btn.setEnabled(True)
        QMessageBox.information(self, "NightByte AI", f"You are running the latest version (v{version})!")

    def _on_update_failed(self, error: str):
        self.check_updates_btn.setText("🔄 Check for Updates")
        self.check_updates_btn.setEnabled(True)
        QMessageBox.warning(self, "NightByte AI", f"Update check failed: {error}")

    def _on_test_webhook(self):
        """Send a test message to the configured webhook."""
        url = self.webhook_edit.text().strip()
        if not url:
            QMessageBox.warning(self, "Webhook", "Please enter a valid webhook URL first.")
            return
        try:
            payload = {"content": "🔔 **NightByte AI**: Webhook test successful! / تم اختبار الإشعار بنجاح."}
            resp = requests.post(url, json=payload, timeout=5)
            if resp.status_code in (200, 204):
                QMessageBox.information(self, "Webhook", "Notification sent successfully! / تم إرسال الإشعار بنجاح")
            else:
                QMessageBox.warning(self, "Webhook", f"Server responded with status code: {resp.status_code}")
        except Exception as e:
            QMessageBox.critical(self, "Webhook", f"Failed to send webhook: {e}")
