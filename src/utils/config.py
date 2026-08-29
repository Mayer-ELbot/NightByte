"""
NightByte AI - Configuration Management
Handles persistent user settings, presets, and platform monitoring toggles.
"""

import os
import sys
import json
import logging

logger = logging.getLogger("NightByte.Config")

DEFAULT_CONFIG = {
    # General & Localization
    "language": "ar",                   # "ar" or "en"
    "theme": "cyberpunk_dark",          # "cyberpunk_dark", "oled_black", "steam_blue"
    "minimize_to_tray": True,
    "close_to_tray": True,
    "start_with_windows": False,
    "auto_check_updates": True,         # Automatically check GitHub for updates on launch
    
    # Download & Inactivity Monitoring
    "threshold_speed_kb": 50,           # Minimum speed in KB/s to consider "active download"
    "inactivity_timeout_sec": 180,      # Wait time (sec) with speed < threshold before action
    "countdown_duration_sec": 60,       # On-screen warning countdown before action (sec)
    "default_action": "shutdown",       # "shutdown", "sleep", "hibernate", "restart", "lock", "close_launchers", "monitors_off"
    "force_action": True,               # Force close hanging apps
    
    # Smart Internet Guardian
    "network_guardian_enabled": True,   # Monitor internet connectivity
    "pause_on_disconnect": True,        # FREEZE shutdown timer if internet disconnects
    "max_offline_wait_sec": 1800,       # Max seconds to wait for reconnection (0 = indefinite)
    "auto_resume_on_reconnect": True,   # Automatically resume monitoring once back online
    "ping_interval_sec": 3,             # Ping check interval
    
    # Smart Protection & Anti-AFK
    "anti_afk_enabled": True,           # Pause action if user is actively using mouse/keyboard
    "afk_threshold_sec": 300,           # User idle threshold in seconds (5 minutes)
    "gaming_mode_protection": True,     # Don't shutdown if full-screen 3D game is active
    "prevent_sleep_during_download": True, # Keep Windows awake during active downloads
    
    # Audio & Notifications
    "sound_alerts_enabled": True,       # Beep / voice alerts
    "sound_countdown_ticks": True,      # Beep during final 10 seconds of countdown
    "system_tray_notifications": True,  # Windows toast/balloon notifications
    "webhook_url": "",                  # Discord / Telegram / custom webhook URL
    "webhook_notify_on_complete": False,
    "webhook_notify_on_net_drop": False,
    
    # Platforms & Applications Monitored
    "monitor_steam": True,
    "monitor_epic": True,
    "monitor_ea": True,
    "monitor_battlenet": True,
    "monitor_xbox": True,
    "monitor_ubisoft": True,
    "monitor_torrents": True,
    "monitor_idm_browsers": True,
    "monitor_entire_system_io": True,   # Universal network I/O fallback
}


def get_config_path() -> str:
    """Get path to config file in user AppData directory."""
    appdata = os.getenv("APPDATA") or os.path.expanduser("~")
    config_dir = os.path.join(appdata, "NightByte")
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, "config.json")


class ConfigManager:
    """Manages reading, modifying, and saving app configuration."""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        self.config_path = get_config_path()
        self.settings = dict(DEFAULT_CONFIG)
        self.load()
        
    def load(self):
        """Load settings from JSON file with fallback to defaults."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    if isinstance(saved, dict):
                        for k, v in saved.items():
                            if k in self.settings:
                                self.settings[k] = v
                logger.info(f"Loaded config from {self.config_path}")
            except Exception as e:
                logger.error(f"Error loading config file: {e}. Using defaults.")
        else:
            self.save()

    def save(self):
        """Save current settings to JSON file."""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            logger.info("Configuration saved successfully.")
        except Exception as e:
            logger.error(f"Error saving config file: {e}")

    def get(self, key, default=None):
        """Get a setting value."""
        return self.settings.get(key, default if default is not None else DEFAULT_CONFIG.get(key))

    def set(self, key, value, auto_save=True):
        """Set a setting value."""
        self.settings[key] = value
        if auto_save:
            self.save()

    def update(self, new_settings: dict, auto_save=True):
        """Update multiple settings."""
        self.settings.update(new_settings)
        if auto_save:
            self.save()

    def reset_to_defaults(self):
        """Reset all settings to default values."""
        self.settings = dict(DEFAULT_CONFIG)
        self.save()
