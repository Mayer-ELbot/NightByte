"""
SteamDown Ultra AI - Deep Steam Detection Engine
Deeply inspects Steam libraries, appmanifest VDFs, downloading directories, and process I/O.
"""

import os
import sys
import re
import time
import winreg
import psutil
from utils.logger import logger


class SteamDetector:
    """Provides deep detection of Steam active downloads and patching tasks."""
    
    # State flags in appmanifest_*.acf
    FLAG_UNINSTALLED = 1
    FLAG_UPDATE_REQUIRED = 4
    FLAG_FULLY_INSTALLED = 6
    FLAG_ENCRYPTED = 8
    FLAG_LOCKED = 16
    FLAG_FILES_MISSING = 32
    FLAG_APP_RUNNING = 64
    FLAG_FILES_CORRUPT = 128
    FLAG_UPDATE_RUNNING = 256
    FLAG_UPDATE_PAUSED = 512
    FLAG_UPDATE_STARTED = 1024
    FLAG_UNINSTALLING = 2048
    FLAG_BACKUP_RUNNING = 4096

    def __init__(self):
        self.steam_path = self._find_steam_path()
        self.cached_libraries = []
        self._last_library_scan = 0
        
    def _find_steam_path(self) -> str:
        """Find Steam installation path from Registry or standard locations."""
        # 1. Check Registry HKLM / HKCU
        keys_to_check = [
            (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam"),
        ]
        for root_key, subkey in keys_to_check:
            try:
                hkey = winreg.OpenKey(root_key, subkey)
                for val_name in ["SteamPath", "InstallPath"]:
                    try:
                        path, _ = winreg.QueryValueEx(hkey, val_name)
                        if path and os.path.exists(path):
                            winreg.CloseKey(hkey)
                            return os.path.normpath(path)
                    except Exception:
                        pass
                winreg.CloseKey(hkey)
            except Exception:
                continue

        # 2. Check default drive paths
        for drive in ["C", "D", "E", "F", "G"]:
            candidate = f"{drive}:\\Program Files (x86)\\Steam"
            if os.path.exists(candidate):
                return candidate
            candidate = f"{drive}:\\Steam"
            if os.path.exists(candidate):
                return candidate
                
        return ""

    def get_library_folders(self) -> list[str]:
        """Discover all Steam library folders across all storage drives."""
        # Cache for 60 seconds
        if self.cached_libraries and (time.time() - self._last_library_scan < 60):
            return self.cached_libraries
            
        libraries = []
        if self.steam_path and os.path.exists(self.steam_path):
            libraries.append(self.steam_path)
            vdf_path = os.path.join(self.steam_path, "steamapps", "libraryfolders.vdf")
            if os.path.exists(vdf_path):
                try:
                    with open(vdf_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        paths = re.findall(r'"path"\s+"([^"]+)"', content)
                        for p in paths:
                            clean_p = p.replace(r"\\", "\\")
                            if os.path.exists(clean_p) and clean_p not in libraries:
                                libraries.append(clean_p)
                except Exception as e:
                    logger.error(f"Error parsing libraryfolders.vdf: {e}")
                    
        self.cached_libraries = libraries
        self._last_library_scan = time.time()
        return libraries

    def is_steam_running(self) -> bool:
        """Check if any Steam processes are currently active."""
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                name = proc.info["name"]
                if name and name.lower() in ("steam.exe", "steamservice.exe", "steamwebhelper.exe"):
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False

    def get_active_downloads(self) -> list[dict]:
        """
        Scan all libraries for active manifests and downloading folders.
        Returns detailed list of active games and progress.
        """
        downloads = []
        libraries = self.get_library_folders()
        
        for lib in libraries:
            steamapps_dir = os.path.join(lib, "steamapps")
            if not os.path.isdir(steamapps_dir):
                continue
                
            # 1. Inspect appmanifest_*.acf
            try:
                for fname in os.listdir(steamapps_dir):
                    if fname.startswith("appmanifest_") and fname.endswith(".acf"):
                        acf_path = os.path.join(steamapps_dir, fname)
                        game_data = self._parse_acf(acf_path)
                        if game_data and game_data.get("is_active"):
                            downloads.append(game_data)
            except Exception as e:
                logger.error(f"Error scanning manifests in {steamapps_dir}: {e}")
                
            # 2. Inspect downloading directory for in-progress items
            downloading_dir = os.path.join(steamapps_dir, "downloading")
            if os.path.isdir(downloading_dir):
                try:
                    for appid in os.listdir(downloading_dir):
                        if appid.isdigit():
                            # Check if already added
                            if not any(d["app_id"] == appid for d in downloads):
                                app_folder = os.path.join(downloading_dir, appid)
                                size = self._get_folder_size(app_folder)
                                downloads.append({
                                    "app_id": appid,
                                    "name": f"Steam App {appid}",
                                    "platform": "Steam",
                                    "bytes_downloaded": size,
                                    "bytes_total": size,
                                    "state": "Downloading / Staging",
                                    "is_active": True,
                                    "progress_percent": 0.0
                                })
                except Exception as e:
                    logger.error(f"Error scanning downloading dir in {downloading_dir}: {e}")

        return downloads

    def _parse_acf(self, path: str) -> dict | None:
        """Parse an appmanifest_*.acf file to determine download state."""
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                
            appid_m = re.search(r'"appid"\s+"(\d+)"', content)
            name_m = re.search(r'"name"\s+"([^"]+)"', content)
            state_m = re.search(r'"StateFlags"\s+"(\d+)"', content)
            bytes_dl_m = re.search(r'"BytesDownloaded"\s+"(\d+)"', content)
            bytes_tot_m = re.search(r'"BytesToDownload"\s+"(\d+)"', content)
            bytes_stage_m = re.search(r'"BytesToStage"\s+"(\d+)"', content)
            
            if not appid_m or not state_m:
                return None
                
            appid = appid_m.group(1)
            name = name_m.group(1) if name_m else f"Steam App {appid}"
            state_flags = int(state_m.group(1))
            bytes_dl = int(bytes_dl_m.group(1)) if bytes_dl_m else 0
            bytes_tot = int(bytes_tot_m.group(1)) if bytes_tot_m else 0
            bytes_stage = int(bytes_stage_m.group(1)) if bytes_stage_m else 0
            
            # Check if active downloading or staging
            is_active = False
            state_str = "Idle"
            
            # If StateFlags has update running (1024 or 256) or update required with bytes
            if (state_flags & 1024) or (state_flags & 256) or (state_flags & 4) or (state_flags & 8):
                if bytes_tot > 0 and bytes_dl < bytes_tot:
                    is_active = True
                    state_str = "Downloading"
                elif bytes_stage > 0:
                    is_active = True
                    state_str = "Patching / Staging"
                elif state_flags & 1024:
                    is_active = True
                    state_str = "Updating"
                    
            if state_flags & 512:
                state_str = "Paused"
                is_active = False

            prog = 0.0
            if bytes_tot > 0:
                prog = min(100.0, (bytes_dl / bytes_tot) * 100.0)
                
            return {
                "app_id": appid,
                "name": name,
                "platform": "Steam",
                "bytes_downloaded": bytes_dl,
                "bytes_total": bytes_tot,
                "state": state_str,
                "is_active": is_active,
                "progress_percent": prog
            }
        except Exception:
            return None

    def _get_folder_size(self, path: str) -> int:
        """Calculate total bytes in a directory."""
        total = 0
        try:
            for root, _, files in os.walk(path):
                for f in files:
                    fp = os.path.join(root, f)
                    try:
                        total += os.path.getsize(fp)
                    except Exception:
                        pass
        except Exception:
            pass
        return total
