"""
SteamDown Ultra AI - Master Monitoring & Intelligence Engine
Coordinates Steam detection, multi-platform launchers, I/O rates, Network Guardian, and Anti-AFK.
"""

import time
import psutil
from PySide6.QtCore import QObject, Signal, QTimer

from utils.config import ConfigManager
from utils.logger import logger
from utils.sound_effects import SoundManager
from core.network_guardian import NetworkGuardian
from core.system_power import SystemPowerController
from core.steam_detector import SteamDetector


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
    Core intelligent engine managing download monitoring, network drop protection,
    smart inactivity timers, on-screen warnings, and automated system actions.
    """
    
    stats_updated = Signal(dict)
    countdown_started = Signal(int, str)  # duration_sec, action
    countdown_tick = Signal(int)          # remaining_sec
    countdown_aborted = Signal(str)       # reason
    action_executed = Signal(str)         # action
    
    # Process definitions for supported platforms
    PLATFORM_PROCESSES = {
        "epic": ["epicgameslauncher.exe"],
        "ea": ["eadesktop.exe", "eabackgroundservice.exe", "origin.exe"],
        "battlenet": ["battle.net.exe", "agent.exe"],
        "xbox": ["xboxapp.exe", "gamingservices.exe"],
        "ubisoft": ["upc.exe", "ubisoftconnect.exe"],
        "torrents": ["qbittorrent.exe", "utorrent.exe", "bittorrent.exe", "transmission-qt.exe", "deluge.exe"],
        "idm_browsers": ["idman.exe", "fdm.exe", "motrix.exe", "chrome.exe", "msedge.exe", "firefox.exe", "brave.exe"],
    }

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
        self.status_message = "Idle"
        
        # Performance & IO Metrics
        self.prev_net_bytes = 0
        self.prev_disk_bytes = 0
        self.prev_time = time.time()
        
        self.current_speed_kb = 0.0
        self.current_disk_kb = 0.0
        self.peak_speed_kb = 0.0
        self.total_session_bytes = 0
        self.speed_history = [0.0] * 60  # Last 60 seconds history for UI graphs
        
        # Inactivity & Countdown Timers
        self.below_threshold_start = None
        self.countdown_start = None
        self.countdown_remaining = 0
        self.snooze_until = None
        
        # Connect Network Guardian
        self.network_guardian.status_changed.connect(self._on_network_status_changed)
        
        # Main Engine Timer (1 Hz tick)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._engine_tick)
        self.timer.start(1000)

    def start_monitoring(self):
        """Enable smart monitoring mode."""
        self.is_enabled = True
        self.below_threshold_start = None
        self.countdown_start = None
        self.snooze_until = None
        self.current_state = MonitorState.ACTIVE_DOWNLOADING
        self.network_guardian.start()
        
        if self.config.get("prevent_sleep_during_download", True):
            SystemPowerController.set_awake_lock(True)
            
        logger.info("Smart Monitoring ENABLED.")

    def stop_monitoring(self):
        """Disable smart monitoring mode."""
        self.is_enabled = False
        self.below_threshold_start = None
        self.countdown_start = None
        self.snooze_until = None
        self.current_state = MonitorState.IDLE
        self.network_guardian.stop()
        SystemPowerController.set_awake_lock(False)
        logger.info("Smart Monitoring DISABLED.")

    def cancel_countdown(self, reason: str = "User cancelled"):
        """Cancel an active countdown and reset timer."""
        self.countdown_start = None
        self.countdown_remaining = 0
        self.below_threshold_start = None
        self.current_state = MonitorState.ACTIVE_DOWNLOADING if self.is_enabled else MonitorState.IDLE
        self.countdown_aborted.emit(reason)
        logger.info(f"Countdown aborted: {reason}")

    def snooze(self, seconds: int):
        """Snooze the countdown for specified seconds."""
        self.snooze_until = time.time() + seconds
        self.cancel_countdown(f"Snoozed for {seconds // 60} minutes")
        logger.info(f"Snoozed monitoring for {seconds // 60} minutes.")

    def _on_network_status_changed(self, is_online: bool, ping_ms: float, offline_duration: int):
        """Handle network status changes from Network Guardian."""
        if not self.is_enabled:
            return
            
        if not is_online:
            if self.config.get("pause_on_disconnect", True):
                if self.current_state in (MonitorState.BELOW_THRESHOLD, MonitorState.COUNTDOWN):
                    logger.warning("Internet disconnected! Freezing shutdown timers.")
                    self.current_state = MonitorState.PAUSED_NET_DROP
                    self.below_threshold_start = None
                    self.countdown_start = None
        else:
            if self.current_state == MonitorState.PAUSED_NET_DROP:
                logger.info("Internet restored! Resuming download monitor.")
                self.current_state = MonitorState.ACTIVE_DOWNLOADING

    def _calculate_io_speeds(self) -> tuple[float, float]:
        """Compute network download rate and disk write rate across system/launchers."""
        now = time.time()
        dt = max(0.1, now - self.prev_time)
        
        # 1. Network I/O
        net_io = psutil.net_io_counters()
        cur_net_bytes = net_io.bytes_recv
        if self.prev_net_bytes > 0:
            net_delta = max(0, cur_net_bytes - self.prev_net_bytes)
            speed_kb = (net_delta / 1024.0) / dt
            self.total_session_bytes += net_delta
        else:
            speed_kb = 0.0
            
        # 2. Disk I/O
        disk_io = psutil.disk_io_counters()
        cur_disk_bytes = disk_io.write_bytes if disk_io else 0
        if self.prev_disk_bytes > 0:
            disk_delta = max(0, cur_disk_bytes - self.prev_disk_bytes)
            disk_kb = (disk_delta / 1024.0) / dt
        else:
            disk_kb = 0.0

        self.prev_net_bytes = cur_net_bytes
        self.prev_disk_bytes = cur_disk_bytes
        self.prev_time = now

        # Update speed history
        self.current_speed_kb = speed_kb
        self.current_disk_kb = disk_kb
        self.peak_speed_kb = max(self.peak_speed_kb, speed_kb)
        self.speed_history.append(speed_kb)
        if len(self.speed_history) > 60:
            self.speed_history.pop(0)

        return speed_kb, disk_kb

    def _scan_active_launchers(self) -> list[dict]:
        """Check active games and launcher processes."""
        active_items = []
        
        # 1. Steam deep detector
        if self.config.get("monitor_steam", True):
            steam_downloads = self.steam_detector.get_active_downloads()
            active_items.extend(steam_downloads)
            
        # 2. Other platform processes
        for platform_key, process_names in self.PLATFORM_PROCESSES.items():
            if not self.config.get(f"monitor_{platform_key}", True):
                continue
            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    pname = proc.info["name"]
                    if pname and pname.lower() in process_names:
                        # Check if process is actively doing IO
                        p_io = proc.io_counters() if hasattr(proc, 'io_counters') else None
                        active_items.append({
                            "app_id": str(proc.info["pid"]),
                            "name": pname,
                            "platform": platform_key.upper(),
                            "bytes_downloaded": p_io.read_bytes if p_io else 0,
                            "bytes_total": 0,
                            "state": "Active Process",
                            "is_active": True,
                            "progress_percent": 0.0
                        })
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        return active_items

    def _engine_tick(self):
        """Master 1-second tick loop."""
        speed_kb, disk_kb = self._calculate_io_speeds()
        net_status = self.network_guardian.get_status()
        active_items = self._scan_active_launchers()
        
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
            self.status_message = "Monitoring disabled"
            self._broadcast_stats(speed_kb, disk_kb, active_items, net_status, 0, 0)
            return

        # Check Internet Disconnection Guardian
        if not net_status["online"] and self.config.get("pause_on_disconnect", True):
            self.current_state = MonitorState.PAUSED_NET_DROP
            self.status_message = "Internet disconnected - Timers paused"
            self.below_threshold_start = None
            self.countdown_start = None
            
            # Check max offline timeout
            max_offline = self.config.get("max_offline_wait_sec", 1800)
            if 0 < max_offline <= net_status["offline_duration_sec"]:
                logger.warning(f"Max offline wait of {max_offline}s reached!")
                
            self._broadcast_stats(speed_kb, disk_kb, active_items, net_status, 0, 0)
            return

        # Check Anti-AFK User Activity
        if self.config.get("anti_afk_enabled", True):
            user_idle = SystemPowerController.get_user_idle_seconds()
            afk_limit = self.config.get("afk_threshold_sec", 300)
            if user_idle < afk_limit:
                # User is active!
                if self.current_state == MonitorState.COUNTDOWN:
                    self.cancel_countdown("User activity detected (Anti-AFK)")
                self.current_state = MonitorState.PAUSED_AFK
                self.status_message = "User is active - Action deferred"
                self.below_threshold_start = None
                self._broadcast_stats(speed_kb, disk_kb, active_items, net_status, 0, 0)
                return

        # Check Gaming Mode (full-screen app)
        if self.config.get("gaming_mode_protection", True):
            if SystemPowerController.is_fullscreen_app_running():
                if self.current_state == MonitorState.COUNTDOWN:
                    self.cancel_countdown("Full-screen game detected")
                self.status_message = "Gaming mode active"
                self.below_threshold_start = None
                self._broadcast_stats(speed_kb, disk_kb, active_items, net_status, 0, 0)
                return

        # Determine download activity
        has_active_manifest_dl = any(d.get("is_active") and d.get("state") == "Downloading" for d in active_items)
        is_speed_active = speed_kb >= threshold_kb

        if is_speed_active or has_active_manifest_dl:
            # Active downloading happening!
            self.current_state = MonitorState.ACTIVE_DOWNLOADING
            self.status_message = f"Downloading active ({speed_kb:.1f} KB/s)"
            self.below_threshold_start = None
            if self.countdown_start:
                self.cancel_countdown("Download resumed")
        else:
            # Speed is below threshold!
            if self.countdown_start is not None:
                # We are in COUNTDOWN state!
                elapsed = now - self.countdown_start
                remaining = int(max(0, countdown_sec - elapsed))
                self.countdown_remaining = remaining
                self.current_state = MonitorState.COUNTDOWN
                self.status_message = f"Countdown in progress: {remaining}s remaining"
                self.countdown_tick.emit(remaining)
                
                if self.config.get("sound_countdown_ticks", True) and remaining <= 10 and remaining > 0:
                    SoundManager.alert_countdown_tick()
                    
                if remaining <= 0:
                    self._trigger_final_action()
                    
            elif self.below_threshold_start is None:
                # Start below threshold wait
                self.below_threshold_start = now
                self.current_state = MonitorState.BELOW_THRESHOLD
                self.status_message = f"Speed < {threshold_kb} KB/s. Inactivity timer started."
            else:
                # Below threshold timer running
                time_below = now - self.below_threshold_start
                if time_below >= inactivity_sec:
                    # Inactivity threshold reached -> Start Countdown HUD!
                    self._start_countdown()
                else:
                    rem_inactivity = int(inactivity_sec - time_below)
                    self.current_state = MonitorState.BELOW_THRESHOLD
                    self.status_message = f"Inactivity wait: {rem_inactivity}s until countdown"

        timer_rem = 0
        if self.below_threshold_start:
            timer_rem = max(0, int(inactivity_sec - (now - self.below_threshold_start)))
            
        self._broadcast_stats(speed_kb, disk_kb, active_items, net_status, timer_rem, self.countdown_remaining)

    def _start_countdown(self):
        """Initiate the on-screen countdown warning dialog."""
        duration = self.config.get("countdown_duration_sec", 60)
        action = self.config.get("default_action", "shutdown")
        self.countdown_start = time.time()
        self.countdown_remaining = duration
        self.current_state = MonitorState.COUNTDOWN
        self.status_message = f"Warning: Action scheduled in {duration}s"
        
        logger.warning(f"Countdown started! {duration}s until '{action}'.")
        if self.config.get("sound_alerts_enabled", True):
            SoundManager.alert_warning()
            
        self.countdown_started.emit(duration, action)

    def _trigger_final_action(self):
        """Execute the configured system action."""
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
        """Emit comprehensive stats package to GUI views."""
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
            "is_online": net_status.get("online", True),
            "ping_ms": net_status.get("ping_ms", 0.0),
            "offline_duration_sec": net_status.get("offline_duration_sec", 0),
            "timer_remaining_sec": timer_remaining,
            "countdown_remaining_sec": countdown_remaining,
        }
        self.stats_updated.emit(snapshot)
