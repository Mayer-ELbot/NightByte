"""
NightByte AI - Configuration Management
"""

import os
import json
import logging

logger = logging.getLogger("NightByte.Config")

DEFAULT_CONFIG = {
    "theme": "mono_light",
    "minimize_to_tray": True,
    "close_to_tray": True,
    "start_with_windows": False,
    "auto_check_updates": True,

    "threshold_speed_kb": 50,
    "inactivity_timeout_sec": 180,
    "countdown_duration_sec": 60,
    "default_action": "shutdown",
    "force_action": True,

    "network_guardian_enabled": True,
    "pause_on_disconnect": True,
    "max_offline_wait_sec": 1800,
    "auto_resume_on_reconnect": True,
    "ping_interval_sec": 3,

    "anti_afk_enabled": True,
    "afk_threshold_sec": 300,
    "gaming_mode_protection": True,
    "prevent_sleep_during_download": True,

    "sound_alerts_enabled": True,
    "sound_countdown_ticks": True,
    "system_tray_notifications": True,
    "webhook_url": "",

    "monitor_steam": True,
    "monitor_epic": True,
    "monitor_ea": True,
    "monitor_battlenet": True,
    "monitor_torrents": True,
    "monitor_idm_browsers": True,
}


def get_config_path() -> str:
    appdata = os.getenv("APPDATA") or os.path.expanduser("~")
    config_dir = os.path.join(appdata, "NightByte")
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, "config.json")


class ConfigManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self.config_path = get_config_path()
        self.settings = dict(DEFAULT_CONFIG)
        self.load()

    def load(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    if isinstance(saved, dict):
                        for k, v in saved.items():
                            if k in self.settings:
                                self.settings[k] = v
            except Exception as e:
                logger.error(f"Config load error: {e}")
        else:
            self.save()

    def save(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            logger.error(f"Config save error: {e}")

    def get(self, key, default=None):
        return self.settings.get(key, default if default is not None else DEFAULT_CONFIG.get(key))

    def set(self, key, value, auto_save=True):
        self.settings[key] = value
        if auto_save:
            self.save()

    def update(self, new_settings: dict, auto_save=True):
        self.settings.update(new_settings)
        if auto_save:
            self.save()

    def reset_to_defaults(self):
        self.settings = dict(DEFAULT_CONFIG)
        self.save()
