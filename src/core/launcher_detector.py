"""
NightByte AI - Multi-Platform Launcher & Torrent Detector
Scans Epic Games, EA, Battle.net, Torrent clients, IDM, and active processes.
"""

import os
import json
import psutil
from utils.logger import logger


class LauncherDetector:
    """Detects active downloads from Epic Games, Torrent clients, EA, Battle.net, and IDM."""

    TORRENT_PROCS = ["qbittorrent.exe", "utorrent.exe", "bittorrent.exe", "deluge.exe", "transmission-qt.exe"]
    IDM_PROCS = ["idman.exe", "fdm.exe", "motrix.exe", "chrome.exe", "msedge.exe", "firefox.exe", "brave.exe"]
    EA_PROCS = ["eadesktop.exe", "eabackgroundservice.exe", "origin.exe"]
    BNET_PROCS = ["battle.net.exe", "agent.exe"]

    @classmethod
    def get_epic_active_downloads(cls) -> list[dict]:
        """Check Epic Games Launcher manifests for in-progress downloads."""
        downloads = []
        epic_manifests_dir = os.path.expandvars(r"%ProgramData%\Epic\EpicGamesLauncher\Data\Manifests")
        if os.path.isdir(epic_manifests_dir):
            try:
                for fname in os.listdir(epic_manifests_dir):
                    if fname.endswith(".item"):
                        item_path = os.path.join(epic_manifests_dir, fname)
                        try:
                            with open(item_path, "r", encoding="utf-8", errors="ignore") as f:
                                data = json.load(f)
                            # Check if actively downloading / updating
                            is_updating = data.get("bIsIncompleteInstall", False) or data.get("bIsQueuedForUpdate", False)
                            app_title = data.get("DisplayName") or data.get("AppName") or "Epic Game"
                            app_id = data.get("AppName") or fname
                            
                            if is_updating:
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
        """Detect running torrent client processes and their network activity."""
        downloads = []
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                pname = proc.info["name"]
                if pname and pname.lower() in cls.TORRENT_PROCS:
                    p_io = proc.io_counters() if hasattr(proc, 'io_counters') else None
                    r_bytes = p_io.read_bytes if p_io else 0
                    downloads.append({
                        "id": f"torrent_{proc.info['pid']}",
                        "name": f"Torrent Client ({pname.split('.')[0]})",
                        "platform": "Torrent",
                        "bytes_downloaded": r_bytes,
                        "bytes_total": 0,
                        "state": "Transferring Data",
                        "is_active": True,
                        "progress_percent": 0.0
                    })
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return downloads

    @classmethod
    def get_idm_browsers_active(cls) -> list[dict]:
        """Detect active IDM or Browser downloader processes."""
        downloads = []
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                pname = proc.info["name"]
                if pname and pname.lower() in cls.IDM_PROCS:
                    downloads.append({
                        "id": f"downloader_{proc.info['pid']}",
                        "name": f"Downloader ({pname})",
                        "platform": "Downloader",
                        "bytes_downloaded": 0,
                        "bytes_total": 0,
                        "state": "Active Process",
                        "is_active": True,
                        "progress_percent": 0.0
                    })
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return downloads

    @classmethod
    def get_ea_bnet_active(cls) -> list[dict]:
        """Detect EA App or Battle.net downloads."""
        downloads = []
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                pname = proc.info["name"]
                if pname:
                    pl = pname.lower()
                    if pl in cls.EA_PROCS:
                        downloads.append({
                            "id": f"ea_{proc.info['pid']}",
                            "name": "EA App Download Service",
                            "platform": "EA App",
                            "bytes_downloaded": 0,
                            "bytes_total": 0,
                            "state": "Active",
                            "is_active": True,
                            "progress_percent": 0.0
                        })
                        break
                    elif pl in cls.BNET_PROCS:
                        downloads.append({
                            "id": f"bnet_{proc.info['pid']}",
                            "name": "Battle.net Agent",
                            "platform": "Battle.net",
                            "bytes_downloaded": 0,
                            "bytes_total": 0,
                            "state": "Active",
                            "is_active": True,
                            "progress_percent": 0.0
                        })
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return downloads
