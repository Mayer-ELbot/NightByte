"""
NightByte AI — Settings Screen (English-only)
Inline settings panel embedded in the Settings tab.
"""

import webbrowser
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox,
    QCheckBox, QLineEdit, QPushButton, QGroupBox, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from i18n.translations import t
from utils.config import ConfigManager
from utils.updater import UpdateChecker, CURRENT_VERSION
from utils.logger import logger


def _group(title: str) -> QGroupBox:
    g = QGroupBox(title.upper())
    return g


def _lbl(text: str) -> QLabel:
    lb = QLabel(text)
    lb.setWordWrap(True)
    return lb


class SettingsScreen(QWidget):
    settings_saved = Signal()

    def __init__(self, config: ConfigManager = None, parent=None):
        super().__init__(parent)
        self.config = config or ConfigManager()
        self.updater = UpdateChecker(self)
        self.updater.update_available.connect(
            lambda v, url: self._set_update_label(f"✦ New version {v} — click to download", url)
        )
        self.updater.up_to_date.connect(
            lambda v: self._set_update_label(f"✓ Up to date (v{v})", "")
        )
        self.updater.check_failed.connect(
            lambda e: self._set_update_label(f"Could not check: {e}", "")
        )
        self._update_url = ""
        self._build()
        self._load()

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.NoFrame)

        inner = QWidget()
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(14)

        # ── General ──────────────────────────────────────────────
        g = _group("General")
        gl = QVBoxLayout(g)
        gl.setSpacing(10)

        self.autostart_cb   = QCheckBox(t("s_autostart"))
        self.close_tray_cb  = QCheckBox(t("s_close_tray"))
        self.auto_update_cb = QCheckBox(t("s_auto_updates"))
        for cb in [self.autostart_cb, self.close_tray_cb, self.auto_update_cb]:
            gl.addWidget(cb)
        lay.addWidget(g)

        # ── Network Guardian ─────────────────────────────────────
        g2 = _group("Network Guardian")
        gl2 = QVBoxLayout(g2)
        gl2.setSpacing(10)
        self.guardian_cb = QCheckBox(t("s_guardian"))
        gl2.addWidget(self.guardian_cb)
        lay.addWidget(g2)

        # ── Speed & Timers ───────────────────────────────────────
        g3 = _group("Speed & Timers")
        gl3 = QVBoxLayout(g3)
        gl3.setSpacing(10)

        for attr, label, lo, hi, suffix in [
            ("threshold_spin", t("s_threshold"),  1,    5000, " KB/s"),
            ("inactivity_spin", t("s_inactivity"), 10, 3600,  " sec"),
            ("countdown_spin", t("s_countdown"),  5,    300,  " sec"),
        ]:
            row = QHBoxLayout()
            row.addWidget(_lbl(label), 1)
            spin = QSpinBox()
            spin.setRange(lo, hi)
            spin.setSuffix(suffix)
            spin.setFixedWidth(110)
            setattr(self, attr, spin)
            row.addWidget(spin)
            gl3.addLayout(row)

        lay.addWidget(g3)

        # ── Protection ───────────────────────────────────────────
        g4 = _group("Protection")
        gl4 = QVBoxLayout(g4)
        gl4.setSpacing(10)
        self.anti_afk_cb  = QCheckBox(t("s_anti_afk"))
        self.gaming_cb    = QCheckBox(t("s_gaming"))
        self.no_sleep_cb  = QCheckBox(t("s_prevent_sleep"))
        for cb in [self.anti_afk_cb, self.gaming_cb, self.no_sleep_cb]:
            gl4.addWidget(cb)
        lay.addWidget(g4)

        # ── Notifications ────────────────────────────────────────
        g5 = _group("Notifications")
        gl5 = QVBoxLayout(g5)
        gl5.setSpacing(10)
        self.sound_cb  = QCheckBox(t("s_sound"))
        self.notif_cb  = QCheckBox(t("s_notifications"))
        for cb in [self.sound_cb, self.notif_cb]:
            gl5.addWidget(cb)

        wh_row = QHBoxLayout()
        wh_row.addWidget(_lbl(t("s_webhook")), 1)
        self.webhook_edit = QLineEdit()
        self.webhook_edit.setPlaceholderText("https://discord.com/api/webhooks/...")
        wh_row.addWidget(self.webhook_edit, 2)
        gl5.addLayout(wh_row)
        lay.addWidget(g5)

        # ── Update Checker ───────────────────────────────────────
        g6 = _group("Updates")
        gl6 = QVBoxLayout(g6)
        gl6.setSpacing(8)

        upd_row = QHBoxLayout()
        self.update_lbl = QLabel(f"Current version: v{CURRENT_VERSION}")
        self.update_lbl.setObjectName("StatusText")
        self.update_lbl.setCursor(Qt.PointingHandCursor)
        self.update_lbl.mousePressEvent = lambda _: (
            webbrowser.open(self._update_url) if self._update_url else None
        )

        check_btn = QPushButton(t("btn_check_updates"))
        check_btn.setObjectName("SecondaryButton")
        check_btn.setCursor(Qt.PointingHandCursor)
        check_btn.clicked.connect(lambda: self.updater.check_async())

        upd_row.addWidget(self.update_lbl, 1)
        upd_row.addWidget(check_btn)
        gl6.addLayout(upd_row)
        lay.addWidget(g6)

        # ── Action Buttons ───────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setObjectName("SecondaryButton")
        reset_btn.setCursor(Qt.PointingHandCursor)
        reset_btn.clicked.connect(self._reset)
        btn_row.addWidget(reset_btn)

        save_btn = QPushButton("Save Settings")
        save_btn.setObjectName("PrimaryButton")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(save_btn)

        lay.addLayout(btn_row)
        lay.addStretch()

        inner.setLayout(lay)
        scroll.setWidget(inner)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(scroll)

    # ── Load / Save ───────────────────────────────────────────────────────────

    def _load(self):
        c = self.config
        self.autostart_cb.setChecked(c.get("start_with_windows", False))
        self.close_tray_cb.setChecked(c.get("close_to_tray", True))
        self.auto_update_cb.setChecked(c.get("auto_check_updates", True))
        self.guardian_cb.setChecked(c.get("network_guardian_enabled", True))
        self.threshold_spin.setValue(c.get("threshold_speed_kb", 50))
        self.inactivity_spin.setValue(c.get("inactivity_timeout_sec", 180))
        self.countdown_spin.setValue(c.get("countdown_duration_sec", 60))
        self.anti_afk_cb.setChecked(c.get("anti_afk_enabled", True))
        self.gaming_cb.setChecked(c.get("gaming_mode_protection", True))
        self.no_sleep_cb.setChecked(c.get("prevent_sleep_during_download", True))
        self.sound_cb.setChecked(c.get("sound_alerts_enabled", True))
        self.notif_cb.setChecked(c.get("system_tray_notifications", True))
        self.webhook_edit.setText(c.get("webhook_url", ""))

    def _save(self):
        self.config.update({
            "start_with_windows":       self.autostart_cb.isChecked(),
            "close_to_tray":            self.close_tray_cb.isChecked(),
            "auto_check_updates":       self.auto_update_cb.isChecked(),
            "network_guardian_enabled": self.guardian_cb.isChecked(),
            "threshold_speed_kb":       self.threshold_spin.value(),
            "inactivity_timeout_sec":   self.inactivity_spin.value(),
            "countdown_duration_sec":   self.countdown_spin.value(),
            "anti_afk_enabled":         self.anti_afk_cb.isChecked(),
            "gaming_mode_protection":   self.gaming_cb.isChecked(),
            "prevent_sleep_during_download": self.no_sleep_cb.isChecked(),
            "sound_alerts_enabled":     self.sound_cb.isChecked(),
            "system_tray_notifications": self.notif_cb.isChecked(),
            "webhook_url":              self.webhook_edit.text().strip(),
        })
        self.settings_saved.emit()
        logger.info("Settings saved.")

    def _reset(self):
        self.config.reset_to_defaults()
        self._load()
        logger.info("Settings reset to defaults.")

    def _set_update_label(self, text: str, url: str):
        self._update_url = url
        self.update_lbl.setText(text)
