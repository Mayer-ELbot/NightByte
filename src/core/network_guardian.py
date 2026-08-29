"""
SteamDown Ultra AI - Smart Network Guardian
Monitors internet connectivity in real time to prevent false shutdowns when network drops.
"""

import socket
import time
import threading
from PySide6.QtCore import QObject, Signal, QTimer
from utils.logger import logger
from utils.sound_effects import SoundManager


class NetworkGuardian(QObject):
    """
    Monitors internet connection health and emits signals on status transitions.
    Freezes countdowns when internet is lost to protect active downloads.
    """
    
    status_changed = Signal(bool, float, int)  # is_online, ping_ms, offline_duration_sec
    
    # Fast reliable probe endpoints (IP, Port)
    PROBE_TARGETS = [
        ("1.1.1.1", 53),            # Cloudflare DNS
        ("8.8.8.8", 53),            # Google DNS
        ("1.0.0.1", 53),            # Cloudflare Alt
        ("162.254.195.3", 443),     # Valve/Steam CDN
    ]
    
    def __init__(self, check_interval_sec: float = 3.0, parent=None):
        super().__init__(parent)
        self.check_interval_sec = max(1.0, check_interval_sec)
        self.is_online = True
        self.last_ping_ms = 0.0
        self.offline_start_time = None
        self.offline_duration_sec = 0
        self._running = False
        self._lock = threading.Lock()
        
        # Background worker thread
        self._worker_thread = None
        self._stop_event = threading.Event()
        
    def start(self):
        """Start the background connectivity monitoring thread."""
        if self._running:
            return
        self._running = True
        self._stop_event.clear()
        self._worker_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._worker_thread.start()
        logger.info("Network Guardian started - Internet drop protection active.")

    def stop(self):
        """Stop the background monitoring thread."""
        self._running = False
        self._stop_event.set()
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=1.0)
        logger.info("Network Guardian stopped.")

    def _check_socket(self, host: str, port: int, timeout: float = 1.2) -> tuple[bool, float]:
        """Attempt socket connection and measure latency."""
        t0 = time.time()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, port))
            sock.close()
            latency = (time.time() - t0) * 1000.0
            return True, latency
        except Exception:
            return False, 0.0

    def check_connection(self) -> tuple[bool, float]:
        """Test multiple endpoints to reliably determine internet status."""
        for host, port in self.PROBE_TARGETS:
            ok, lat = self._check_socket(host, port)
            if ok:
                return True, lat
        return False, 0.0

    def _monitor_loop(self):
        """Continuous background check loop."""
        while not self._stop_event.is_set():
            online, ping = self.check_connection()
            with self._lock:
                prev_online = self.is_online
                self.is_online = online
                self.last_ping_ms = ping
                
                if not online:
                    if self.offline_start_time is None:
                        self.offline_start_time = time.time()
                        self.offline_duration_sec = 0
                        logger.warning("⚠️ Internet disconnected! Network Guardian activated.")
                        SoundManager.alert_network_lost()
                    else:
                        self.offline_duration_sec = int(time.time() - self.offline_start_time)
                else:
                    if not prev_online:
                        logger.success("🟢 Internet connection restored! Resuming normal monitoring.")
                        SoundManager.alert_network_restored()
                    self.offline_start_time = None
                    self.offline_duration_sec = 0
                    
                cur_online = self.is_online
                cur_ping = self.last_ping_ms
                cur_duration = self.offline_duration_sec

            self.status_changed.emit(cur_online, cur_ping, cur_duration)
            self._stop_event.wait(self.check_interval_sec)

    def get_status(self) -> dict:
        """Get current network snapshot."""
        with self._lock:
            return {
                "online": self.is_online,
                "ping_ms": self.last_ping_ms,
                "offline_duration_sec": self.offline_duration_sec
            }
