"""
NightByte AI - Multi-Platform Launcher & Process Throughput Detector
Measures active real-time I/O throughput to eliminate false positives from idle
browsers, dormant torrent clients, and background Windows system processes.
"""

import os
import json
import time
import psutil
from utils.logger import logger


class LauncherDetector:
    """Detects active downloads with throughput threshold verification."""

    TORRENT_PROCS = ["qbittorrent.exe", "utorrent.exe", "bittorrent.exe", "deluge.exe", "transmission-qt.exe"]
    IDM_PROCS = ["idman.exe", "fdm.exe", "motrix.exe"]
    BROWSER_PROCS = ["chrome.exe", "msedge.exe", "firefox.exe", "brave.exe", "opera.exe"]
    EA_PROCS = ["eadesktop.exe", "eabackgroundservice.exe", "origin.exe"]
    BNET_PROCS = ["agent.exe", "battle.net.exe"]

    # Windows noise filter
    SYSTEM_NOISE_PROCS = {
        "svchost.exe", "system", "searchindexer.exe", "msmpeng.exe",
        "onedrive.exe", "explorer.exe", "dwm.exe", "audiodg.exe", "spoolsv.exe"
    }

    # Per-process IO cache: {pid: (bytes_read, bytes_write, timestamp)}
    _io_cache = {}

    @classmethod
    def _get_process_speed_kb(cls, proc) -> float:
        """Calculate real-time I/O transfer speed (KB/s) for a given process."""
        try:
            pid = proc.pid
            io = proc.io_counters()
            now = time.time()
            total_bytes = io.read_bytes + io.write_bytes

            if pid in cls._io_cache:
                prev_bytes, prev_time = cls._io_cache[pid]
                dt = max(0.1, now - prev_time)
                delta = max(0, total_bytes - prev_bytes)
                speed_kb = (delta / 1024.0) / dt
                cls._io_cache[pid] = (total_bytes, now)
                return speed_kb
            else:
                cls._io_cache[pid] = (total_bytes, now)
                return 0.0
        except (psutil.NoSuchProcess, psutil.AccessDenied, Exception):
            return 0.0

    @classmethod
    def get_epic_active_downloads(cls) -> list[dict]:
        """Check Epic Games Launcher manifests for verified in-progress downloads."""
        downloads = []
        epic_manifests_dir = os.path.expandvars(r"%ProgramData%\Epic\EpicGamesLauncher\Data\Manifests")
        if not os.path.isdir(epic_manifests_dir):
            return downloads

        # Check if Epic launcher or UnrealCEFSubProcess is running
        epic_running = False
        for proc in psutil.process_iter(["name"]):
            try:
                pname = (proc.info["name"] or "").lower()
                if pname in ("epicgameslauncher.exe", "unrealcefsubprocess.exe"):
                    epic_running = True
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if not epic_running:
            return downloads

        try:
            for fname in os.listdir(epic_manifests_dir):
                if fname.endswith(".item"):
                    item_path = os.path.join(epic_manifests_dir, fname)
                    try:
                        with open(item_path, "r", encoding="utf-8", errors="ignore") as f:
                            data = json.load(f)

                        is_incomplete = data.get("bIsIncompleteInstall", False)
                        is_updating = data.get("bIsQueuedForUpdate", False)
                        app_title = data.get("DisplayName") or data.get("AppName") or "Epic Game"
                        app_id = data.get("AppName") or fname

                        if is_incomplete or is_updating:
                            downloads.append({
                                "id": f"epic_{app_id}",
                                "name": app_title,
                                "platform": "Epic Games",
                                "bytes_downloaded": 0,
                                "bytes_total": 0,
                                "state": "Downloading / Installing",
                                "is_active": True,
                                "progress_percent": 0.0
                            })
                    except Exception:
                        pass
        except Exception:
            pass

        return downloads

    @classmethod
    def get_torrent_active_downloads(cls) -> list[dict]:
        """Detect torrent clients that have active network/disk transfer (> 10 KB/s)."""
        downloads = []
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                pname = (proc.info["name"] or "").lower()
                if pname in cls.TORRENT_PROCS:
                    speed_kb = cls._get_process_speed_kb(proc)
                    if speed_kb >= 10.0:  # Genuinely transferring
                        downloads.append({
                            "id": f"torrent_{proc.pid}",
                            "name": f"Torrent Client ({pname.split('.')[0]})",
                            "platform": "Torrent",
                            "bytes_downloaded": 0,
                            "bytes_total": 0,
                            "state": f"Downloading ({speed_kb:.0f} KB/s)",
                            "is_active": True,
                            "progress_percent": 0.0
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return downloads

    @classmethod
    def get_idm_browsers_active(cls) -> list[dict]:
        """Detect IDM and Browser downloaders with active transfer (> 50 KB/s)."""
        downloads = []
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                pname = (proc.info["name"] or "").lower()
                if pname in cls.SYSTEM_NOISE_PROCS:
                    continue

                if pname in cls.IDM_PROCS:
                    speed_kb = cls._get_process_speed_kb(proc)
                    if speed_kb >= 10.0:
                        downloads.append({
                            "id": f"downloader_{proc.pid}",
                            "name": f"Download Manager ({pname})",
                            "platform": "IDM",
                            "bytes_downloaded": 0,
                            "bytes_total": 0,
                            "state": f"Active ({speed_kb:.0f} KB/s)",
                            "is_active": True,
                            "progress_percent": 0.0
                        })
                elif pname in cls.BROWSER_PROCS:
                    speed_kb = cls._get_process_speed_kb(proc)
                    # Only flag browser if actively downloading a file at substantial speed
                    if speed_kb >= 100.0:
                        downloads.append({
                            "id": f"browser_{proc.pid}",
                            "name": f"Browser Download ({pname})",
                            "platform": "Browser",
                            "bytes_downloaded": 0,
                            "bytes_total": 0,
                            "state": f"Downloading ({speed_kb:.0f} KB/s)",
                            "is_active": True,
                            "progress_percent": 0.0
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return downloads

    @classmethod
    def get_ea_bnet_active(cls) -> list[dict]:
        """Detect active downloads from EA App or Battle.net agent (> 10 KB/s)."""
        downloads = []
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                pname = (proc.info["name"] or "").lower()
                if pname in cls.EA_PROCS:
                    speed_kb = cls._get_process_speed_kb(proc)
                    if speed_kb >= 15.0:
                        downloads.append({
                            "id": f"ea_{proc.pid}",
                            "name": "EA App Download Service",
                            "platform": "EA App",
                            "bytes_downloaded": 0,
                            "bytes_total": 0,
                            "state": f"Downloading ({speed_kb:.0f} KB/s)",
                            "is_active": True,
                            "progress_percent": 0.0
                        })
                elif pname in cls.BNET_PROCS:
                    speed_kb = cls._get_process_speed_kb(proc)
                    if speed_kb >= 15.0:
                        downloads.append({
                            "id": f"bnet_{proc.pid}",
                            "name": "Battle.net Agent",
                            "platform": "Battle.net",
                            "bytes_downloaded": 0,
                            "bytes_total": 0,
                            "state": f"Updating ({speed_kb:.0f} KB/s)",
                            "is_active": True,
                            "progress_percent": 0.0
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return downloads
