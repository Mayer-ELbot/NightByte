"""
NightByte AI - Master Monitoring & Intelligence Engine
Coordinates platform detection, session download lifecycle tracking,
completed item analytics, internet drop protection, and scheduled system actions.
"""

import time
import psutil
from datetime import datetime
from PySide6.QtCore import QObject, Signal, QTimer

from utils.config import ConfigManager
from utils.logger import logger
from utils.sound_effects import SoundManager
from core.network_guardian import NetworkGuardian
from core.system_power import SystemPowerController
from core.steam_detector import SteamDetector
from core.launcher_detector import LauncherDetector


class MonitorState:
    IDLE = "IDLE"
    ACTIVE_DOWNLOADING = "ACTIVE_DOWNLOADING"
    BELOW_THRESHOLD = "BELOW_THRESHOLD"
    PAUSED_NET_DROP = "PAUSED_NET_DROP"
    PAUSED_AFK = "PAUSED_AFK"
    COUNTDOWN = "COUNTDOWN"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"


class MonitorEngine(QObject):
    """
    Intelligent engine supporting platform filtering, targeted game monitoring,
    session lifecycle tracking, completed downloads history, and automatic power management.
    """

    stats_updated = Signal(dict)
    countdown_started = Signal(int, str)
    countdown_tick = Signal(int)
    countdown_aborted = Signal(str)
    action_executed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = ConfigManager()
        self.steam_detector = SteamDetector()
        self.network_guardian = NetworkGuardian(
            check_interval_sec=self.config.get("ping_interval_sec", 3)
        )

        # State tracking
        self.is_enabled = False
        self.current_state = MonitorState.IDLE
        self.status_message = "Ready"

        # Platform filter toggles
        self.monitored_platforms = {
            "steam": True,
            "epic": True,
            "torrent": True,
            "ea_bnet": True,
            "idm": True
        }

        # Specific Targeted Items Monitoring
        self.target_mode = "all"        # "all" or "selected"
        self.selected_item_ids = set()

        # IO Metrics
        self.prev_net_bytes = 0
        self.prev_disk_bytes = 0
        self.prev_time = time.time()

        self.current_speed_kb = 0.0
        self.current_disk_kb = 0.0
        self.peak_speed_kb = 0.0
        self.total_session_bytes = 0
        self.speed_history = [0.0] * 60

        # Session History & Analytics (Only for downloads during this active session)
        self.session_start_time = None
        self.session_active_items = {}  # {item_id: {data, start_time, samples, peak_speed, last_bytes}}
        self.completed_downloads = []   # List of completed item dicts
        self.scheduled_action_time_str = ""

        # Timers
        self.below_threshold_start = None
        self.countdown_start = None
        self.countdown_remaining = 0
        self.snooze_until = None

        self.network_guardian.status_changed.connect(self._on_network_status_changed)

        # Main Engine 1-sec Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._engine_tick)
        self.timer.start(1000)

    def set_platform_enabled(self, platform_key: str, enabled: bool):
        """Toggle monitoring for a specific platform (steam, epic, torrent, etc.)."""
        self.monitored_platforms[platform_key] = enabled
        logger.info(f"Platform filter '{platform_key}' set to {enabled}")

    def set_target_mode(self, mode: str, item_ids: set = None):
        """Set whether to wait for ALL downloads or ONLY specific selected games/files."""
        self.target_mode = mode
        if item_ids is not None:
            self.selected_item_ids = set(item_ids)
        logger.info(f"Target mode set to '{mode}' with {len(self.selected_item_ids)} selected items.")

    def toggle_item_selection(self, item_id: str, selected: bool):
        """Add or remove an item from targeted monitoring."""
        if selected:
            self.selected_item_ids.add(item_id)
        else:
            self.selected_item_ids.discard(item_id)

    def start_monitoring(self):
        """Start smart download monitoring and initialize session analytics."""
        self.is_enabled = True
        self.session_start_time = time.time()
        self.below_threshold_start = None
        self.countdown_start = None
        self.snooze_until = None
        self.scheduled_action_time_str = ""
        self.current_state = MonitorState.ACTIVE_DOWNLOADING
        self.network_guardian.start()

        if self.config.get("prevent_sleep_during_download", True):
            SystemPowerController.set_awake_lock(True)

        logger.info("Smart Download Monitoring STARTED.")

    def stop_monitoring(self):
        """Stop smart download monitoring."""
        self.is_enabled = False
        self.below_threshold_start = None
        self.countdown_start = None
        self.snooze_until = None
        self.current_state = MonitorState.IDLE
        self.network_guardian.stop()
        SystemPowerController.set_awake_lock(False)
        logger.info("Smart Download Monitoring STOPPED.")

    def cancel_countdown(self, reason: str = "User cancelled"):
        """Cancel an ongoing shutdown countdown."""
        self.countdown_start = None
        self.countdown_remaining = 0
        self.below_threshold_start = None
        self.scheduled_action_time_str = ""
        self.current_state = MonitorState.ACTIVE_DOWNLOADING if self.is_enabled else MonitorState.IDLE
        self.countdown_aborted.emit(reason)
        logger.info(f"Countdown cancelled: {reason}")

    def snooze(self, seconds: int):
        """Snooze monitoring."""
        self.snooze_until = time.time() + seconds
        self.cancel_countdown(f"Snoozed for {seconds // 60}m")
        logger.info(f"Monitoring snoozed for {seconds // 60} minutes.")

    def _on_network_status_changed(self, is_online: bool, _ping_ms: float, _offline_duration: int):
        if not self.is_enabled:
            return
        if not is_online and self.config.get("pause_on_disconnect", True):
            if self.current_state in (MonitorState.BELOW_THRESHOLD, MonitorState.COUNTDOWN):
                logger.warning("Internet disconnected! Freezing countdown timer to protect download.")
                self.current_state = MonitorState.PAUSED_NET_DROP
                self.below_threshold_start = None
                self.countdown_start = None
        elif is_online and self.current_state == MonitorState.PAUSED_NET_DROP:
            logger.success("Internet reconnected! Resuming download monitor.")
            self.current_state = MonitorState.ACTIVE_DOWNLOADING

    def _calculate_io_speeds(self) -> tuple[float, float]:
        now = time.time()
        dt = max(0.1, now - self.prev_time)

        net_io = psutil.net_io_counters()
        cur_net = net_io.bytes_recv
        if self.prev_net_bytes > 0:
            net_delta = max(0, cur_net - self.prev_net_bytes)
            speed_kb = (net_delta / 1024.0) / dt
            if self.is_enabled:
                self.total_session_bytes += net_delta
        else:
            speed_kb = 0.0

        disk_io = psutil.disk_io_counters()
        cur_disk = disk_io.write_bytes if disk_io else 0
        if self.prev_disk_bytes > 0:
            disk_delta = max(0, cur_disk - self.prev_disk_bytes)
            disk_kb = (disk_delta / 1024.0) / dt
        else:
            disk_kb = 0.0

        self.prev_net_bytes = cur_net
        self.prev_disk_bytes = cur_disk
        self.prev_time = now

        self.current_speed_kb = speed_kb
        self.current_disk_kb = disk_kb
        self.peak_speed_kb = max(self.peak_speed_kb, speed_kb)
        self.speed_history.append(speed_kb)
        if len(self.speed_history) > 60:
            self.speed_history.pop(0)

        return speed_kb, disk_kb

    def _scan_all_platforms(self) -> list[dict]:
        """Collect active items across all enabled platforms."""
        items = []
        if self.monitored_platforms.get("steam", True):
            items.extend(self.steam_detector.get_active_downloads())
        if self.monitored_platforms.get("epic", True):
            items.extend(LauncherDetector.get_epic_active_downloads())
        if self.monitored_platforms.get("torrent", True):
            items.extend(LauncherDetector.get_torrent_active_downloads())
        if self.monitored_platforms.get("ea_bnet", True):
            items.extend(LauncherDetector.get_ea_bnet_active())
        if self.monitored_platforms.get("idm", True):
            items.extend(LauncherDetector.get_idm_browsers_active())
        return items

    def _update_session_tracker(self, active_items: list, speed_kb: float):
        """Track lifecycle, duration, speeds, and completion of session downloads."""
        now = time.time()
        current_active_ids = set()

        for item in active_items:
            iid = item.get("id", "")
            if not iid:
                continue
            current_active_ids.add(iid)

            if iid not in self.session_active_items:
                # Newly detected active download during this session
                self.session_active_items[iid] = {
                    "id": iid,
                    "name": item.get("name", "Download"),
                    "platform": item.get("platform", "App"),
                    "start_time": now,
                    "samples": [speed_kb] if speed_kb > 0 else [],
                    "peak_speed_kb": speed_kb,
                    "bytes_downloaded": item.get("bytes_downloaded", 0),
                    "bytes_total": item.get("bytes_total", 0)
                }
            else:
                # Update existing tracked item
                record = self.session_active_items[iid]
                if speed_kb > 0:
                    record["samples"].append(speed_kb)
                    record["peak_speed_kb"] = max(record["peak_speed_kb"], speed_kb)
                if item.get("bytes_downloaded", 0) > 0:
                    record["bytes_downloaded"] = item.get("bytes_downloaded")
                if item.get("bytes_total", 0) > 0:
                    record["bytes_total"] = item.get("bytes_total")

        # Check for completed downloads (items previously tracked that are no longer active)
        finished_ids = []
        for iid, record in self.session_active_items.items():
            if iid not in current_active_ids:
                # Item has finished downloading
                duration_sec = int(max(1, now - record["start_time"]))
                samples = record["samples"]
                avg_speed_kb = sum(samples) / len(samples) if samples else 0.0
                peak_speed_kb = record["peak_speed_kb"]
                total_bytes = record["bytes_downloaded"] if record["bytes_downloaded"] > 0 else record["bytes_total"]

                finished_entry = {
                    "id": iid,
                    "name": record["name"],
                    "platform": record["platform"],
                    "duration_str": self._format_duration(duration_sec),
                    "duration_sec": duration_sec,
                    "avg_speed_str": self._format_speed(avg_speed_kb),
                    "peak_speed_str": self._format_speed(peak_speed_kb),
                    "total_size_str": self._format_bytes(total_bytes) if total_bytes > 0 else "Completed",
                    "completed_at": datetime.now().strftime("%I:%M %p")
                }
                self.completed_downloads.insert(0, finished_entry)
                finished_ids.append(iid)
                logger.success(f"Download COMPLETED in this session: {record['name']} (took {finished_entry['duration_str']})")

        for fid in finished_ids:
            self.session_active_items.pop(fid, None)

    def _engine_tick(self):
        speed_kb, disk_kb = self._calculate_io_speeds()
        net_status = self.network_guardian.get_status()
        active_items = self._scan_all_platforms()

        if self.is_enabled:
            self._update_session_tracker(active_items, speed_kb)

        threshold_kb = self.config.get("threshold_speed_kb", 50)
        inactivity_sec = self.config.get("inactivity_timeout_sec", 180)
        countdown_sec = self.config.get("countdown_duration_sec", 60)

        now = time.time()

        # Handle Snooze
        if self.snooze_until:
            if now < self.snooze_until:
                rem = int(self.snooze_until - now)
                self.status_message = f"Snoozed ({rem}s remaining)"
                self._broadcast_stats(speed_kb, disk_kb, active_items, net_status, 0, 0)
                return
            else:
                self.snooze_until = None

        if not self.is_enabled:
            self.current_state = MonitorState.IDLE
            self.status_message = "Ready"
            self._broadcast_stats(speed_kb, disk_kb, active_items, net_status, 0, 0)
            return

        # 1. Check Internet Guardian
        if not net_status["online"] and self.config.get("pause_on_disconnect", True):
            self.current_state = MonitorState.PAUSED_NET_DROP
            self.status_message = "Internet disconnected - Timer frozen"
            self.below_threshold_start = None
            self.countdown_start = None
            self._broadcast_stats(speed_kb, disk_kb, active_items, net_status, 0, 0)
            return

        # 2. Check Anti-AFK
        if self.config.get("anti_afk_enabled", True):
            user_idle = SystemPowerController.get_user_idle_seconds()
            afk_limit = self.config.get("afk_threshold_sec", 300)
            if user_idle < afk_limit:
                if self.current_state == MonitorState.COUNTDOWN:
                    self.cancel_countdown("User activity detected")
                self.current_state = MonitorState.PAUSED_AFK
                self.status_message = "User is active"
                self.below_threshold_start = None
                self._broadcast_stats(speed_kb, disk_kb, active_items, net_status, 0, 0)
                return

        # 3. Check Gaming Mode
        if self.config.get("gaming_mode_protection", True):
            if SystemPowerController.is_fullscreen_app_running():
                if self.current_state == MonitorState.COUNTDOWN:
                    self.cancel_countdown("Full-screen game running")
                self.status_message = "Gaming mode active"
                self.below_threshold_start = None
                self._broadcast_stats(speed_kb, disk_kb, active_items, net_status, 0, 0)
                return

        # 4. Check Download Activity based on Target Mode
        is_target_active = False

        if self.target_mode == "selected" and self.selected_item_ids:
            for item in active_items:
                if item.get("id") in self.selected_item_ids and item.get("is_active"):
                    is_target_active = True
                    break
        else:
            has_manifest_dl = any(d.get("is_active") for d in active_items)
            is_target_active = (speed_kb >= threshold_kb) or has_manifest_dl

        if is_target_active:
            self.current_state = MonitorState.ACTIVE_DOWNLOADING
            self.status_message = f"Downloading ({speed_kb:.0f} KB/s)"
            self.below_threshold_start = None
            if self.countdown_start:
                self.cancel_countdown("Download resumed")
        else:
            if self.countdown_start is not None:
                elapsed = now - self.countdown_start
                remaining = int(max(0, countdown_sec - elapsed))
                self.countdown_remaining = remaining
                self.current_state = MonitorState.COUNTDOWN
                self.status_message = f"Action in {remaining}s"
                self.countdown_tick.emit(remaining)

                if self.config.get("sound_countdown_ticks", True) and 0 < remaining <= 10:
                    SoundManager.alert_countdown_tick()

                if remaining <= 0:
                    self._trigger_final_action()

            elif self.below_threshold_start is None:
                self.below_threshold_start = now
                self.current_state = MonitorState.BELOW_THRESHOLD
                self.status_message = "Downloads finished — waiting"
            else:
                time_below = now - self.below_threshold_start
                if time_below >= inactivity_sec:
                    self._start_countdown()
                else:
                    rem_inact = int(inactivity_sec - time_below)
                    self.current_state = MonitorState.BELOW_THRESHOLD
                    self.status_message = f"Inactivity wait: {rem_inact}s"

        timer_rem = 0
        if self.below_threshold_start:
            timer_rem = max(0, int(inactivity_sec - (now - self.below_threshold_start)))

        self._broadcast_stats(speed_kb, disk_kb, active_items, net_status, timer_rem, self.countdown_remaining)

    def _start_countdown(self):
        duration = self.config.get("countdown_duration_sec", 60)
        action = self.config.get("default_action", "shutdown")
        self.countdown_start = time.time()
        self.countdown_remaining = duration
        self.current_state = MonitorState.COUNTDOWN
        self.status_message = f"Action scheduled in {duration}s"

        scheduled_time = time.time() + duration
        self.scheduled_action_time_str = datetime.fromtimestamp(scheduled_time).strftime("%I:%M:%S %p")

        logger.warning(f"Download completed! Countdown started: {duration}s until '{action}' ({self.scheduled_action_time_str}).")
        if self.config.get("sound_alerts_enabled", True):
            SoundManager.alert_warning()

        self.countdown_started.emit(duration, action)

    def _trigger_final_action(self):
        self.current_state = MonitorState.EXECUTING
        action = self.config.get("default_action", "shutdown")
        force = self.config.get("force_action", True)
        self.status_message = f"Executing '{action}'..."
        logger.info(f"Executing scheduled action: {action}")

        if self.config.get("sound_alerts_enabled", True):
            SoundManager.alert_completed()

        self.action_executed.emit(action)
        SystemPowerController.execute_action(action, force)
        self.current_state = MonitorState.COMPLETED
        self.is_enabled = False

    def _broadcast_stats(self, speed_kb: float, disk_kb: float, active_items: list,
                         net_status: dict, timer_remaining: int, countdown_remaining: int):
        snapshot = {
            "is_enabled": self.is_enabled,
            "state": self.current_state,
            "status_message": self.status_message,
            "download_speed_kb": speed_kb,
            "disk_write_kb": disk_kb,
            "peak_speed_kb": self.peak_speed_kb,
            "total_session_bytes": self.total_session_bytes,
            "speed_history": list(self.speed_history),
            "active_items": active_items,
            "completed_items": list(self.completed_downloads),
            "scheduled_action_time": self.scheduled_action_time_str,
            "is_online": net_status.get("online", True),
            "ping_ms": net_status.get("ping_ms", 0.0),
            "timer_remaining_sec": timer_remaining,
            "countdown_remaining_sec": countdown_remaining,
            "target_mode": self.target_mode,
            "selected_item_ids": list(self.selected_item_ids)
        }
        self.stats_updated.emit(snapshot)

    def _format_duration(self, sec: int) -> str:
        if sec >= 3600:
            h = sec // 3600
            m = (sec % 3600) // 60
            s = sec % 60
            return f"{h}h {m}m {s}s"
        elif sec >= 60:
            m = sec // 60
            s = sec % 60
            return f"{m}m {s}s"
        return f"{sec}s"

    def _format_speed(self, speed_kb: float) -> str:
        if speed_kb >= 1024.0:
            return f"{speed_kb / 1024.0:.1f} MB/s"
        return f"{speed_kb:.0f} KB/s"

    def _format_bytes(self, b: int) -> str:
        if b >= 1024**3:
            return f"{b / (1024**3):.2f} GB"
        elif b >= 1024**2:
            return f"{b / (1024**2):.1f} MB"
        elif b >= 1024:
            return f"{b / 1024:.0f} KB"
        return f"{b} B"
