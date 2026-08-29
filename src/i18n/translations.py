"""
NightByte AI - English-only string constants.
Arabic support removed. English is the sole interface language.
"""

STRINGS = {
    # App
    "app_name": "NightByte",
    "app_version_prefix": "v",

    # Tabs
    "tab_dashboard": "Dashboard",
    "tab_downloads": "Downloads",
    "tab_logs": "Live Log",
    "tab_settings": "Settings",

    # Status messages
    "status_idle": "Ready — click Start to begin",
    "status_downloading": "Downloading",
    "status_below_threshold": "Download finished — waiting",
    "status_countdown": "Shutdown countdown in progress!",
    "status_paused_network": "Paused — internet disconnected (download protected)",
    "status_paused_afk": "Paused — user activity detected",
    "status_completed": "Done!",

    # Net badge
    "net_online": "Online",
    "net_offline": "Offline",

    # Buttons
    "btn_start": "▶  Start Monitoring",
    "btn_stop": "■  Stop Monitoring",
    "btn_clear_logs": "Clear Log",
    "btn_save": "Save Settings",
    "btn_reset": "Reset to Defaults",
    "btn_check_updates": "Check for Updates",
    "btn_cancel_countdown": "Cancel Shutdown",

    # Action combo label & items
    "label_when_done": "When done:",
    "action_shutdown": "Shutdown PC",
    "action_sleep": "Sleep PC",
    "action_hibernate": "Hibernate PC",
    "action_restart": "Restart PC",
    "action_lock": "Lock Workstation",
    "action_logoff": "Log Off",
    "action_close_launchers": "Close Steam & Launchers",
    "action_monitors_off": "Turn Off Displays",

    # Platform chips
    "plat_steam": "Steam",
    "plat_epic": "Epic Games",
    "plat_torrent": "Torrent",
    "plat_ea": "EA / Battle.net",
    "plat_idm": "IDM / Browsers",

    # Target mode
    "target_all": "All active downloads",
    "target_selected": "Only checked items (✓)",
    "target_mode_label": "Wait for:",

    # Update banner
    "update_banner": "✦  New version {version} available — click to download",

    # Countdown
    "countdown_title": "Downloads Completed",
    "countdown_desc": "Shutdown will execute when the countdown reaches zero. Cancel or snooze anytime.",

    # Downloads tab empty state
    "no_downloads": "No active downloads detected.\nStart a download in Steam, Epic, or your torrent client and it will appear here.",

    # Live log guide
    "log_guide": "Live activity feed — every engine step explained in plain English.",

    # Settings groups
    "sg_general": "General",
    "sg_guardian": "Network Guardian",
    "sg_timers": "Speed & Timers",
    "sg_protection": "Protection",
    "sg_notifications": "Notifications",

    # Settings fields
    "s_autostart": "Start automatically with Windows",
    "s_close_tray": "Close window → minimize to system tray",
    "s_guardian": "Freeze shutdown timer when internet disconnects",
    "s_threshold": "Minimum download speed to stay active (KB/s):",
    "s_inactivity": "Idle wait before starting countdown (seconds):",
    "s_countdown": "Warning countdown duration (seconds):",
    "s_anti_afk": "Pause if user is using mouse or keyboard",
    "s_gaming": "Pause if a full-screen game is running",
    "s_prevent_sleep": "Prevent Windows sleep during active downloads",
    "s_sound": "Enable audio alerts",
    "s_notifications": "Windows toast notifications",
    "s_auto_updates": "Check GitHub for updates on startup",
    "s_webhook": "Webhook URL (Discord / Telegram):",

    # Tray
    "tray_open": "Open NightByte",
    "tray_start": "Start Monitoring",
    "tray_stop": "Stop Monitoring",
    "tray_cancel": "Cancel Shutdown",
    "tray_exit": "Exit",
}


def t(key: str, **kwargs) -> str:
    """Return the English string for the given key."""
    text = STRINGS.get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except Exception:
            pass
    return text
