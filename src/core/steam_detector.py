"""
NightByte AI - Deep Steam Platform & Game Detector
Accurately detects active Steam downloads, updates, and staging files while
strictly excluding already-installed games and dormant manifests.
"""

import os
import re
import time
import winreg
import psutil
from utils.logger import logger


class SteamDetector:
    """Deep detection of Steam games, active downloads, and patching stages."""

    def __init__(self):
        self.steam_path = self._find_steam_path()
        self.cached_libraries = []
        self._last_library_scan = 0
        self._previous_item_bytes = {}  # {appid: (bytes_dl, timestamp)}

    def _find_steam_path(self) -> str:
        """Locate Steam installation directory from Registry or standard paths."""
        for root_key, subkey in [
            (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam"),
        ]:
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

        for drive in ["C", "D", "E", "F", "G", "H", "Z"]:
            for folder in ["Program Files (x86)\\Steam", "Program Files\\Steam", "Steam"]:
                candidate = f"{drive}:\\{folder}"
                if os.path.exists(candidate):
                    return candidate
        return ""

    def get_library_folders(self) -> list[str]:
        """Discover all Steam library folders across all drives."""
        now = time.time()
        if self.cached_libraries and (now - self._last_library_scan < 30):
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
        self._last_library_scan = now
        return libraries

    def is_steam_running(self) -> bool:
        """Check if Steam process is active."""
        for proc in psutil.process_iter(["name"]):
            try:
                name = proc.info["name"]
                if name and name.lower() in ("steam.exe", "steamservice.exe", "steamwebhelper.exe"):
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False

    def get_active_downloads(self) -> list[dict]:
        """Scan all libraries for genuinely active manifests and in-progress downloads."""
        downloads = []
        libraries = self.get_library_folders()

        for lib in libraries:
            steamapps_dir = os.path.join(lib, "steamapps")
            if not os.path.isdir(steamapps_dir):
                continue

            # 1. Scan appmanifest_*.acf
            try:
                for fname in os.listdir(steamapps_dir):
                    if fname.startswith("appmanifest_") and fname.endswith(".acf"):
                        acf_path = os.path.join(steamapps_dir, fname)
                        game_data = self._parse_acf(acf_path)
                        if game_data and game_data.get("is_active"):
                            downloads.append(game_data)
            except Exception as e:
                logger.error(f"Error scanning manifests in {steamapps_dir}: {e}")

            # 2. Check downloading folder for active recent writes (< 60s)
            downloading_dir = os.path.join(steamapps_dir, "downloading")
            if os.path.isdir(downloading_dir):
                try:
                    for appid in os.listdir(downloading_dir):
                        if appid.isdigit() and not any(d["id"] == f"steam_{appid}" for d in downloads):
                            app_folder = os.path.join(downloading_dir, appid)
                            if self._is_folder_recently_modified(app_folder, max_age_sec=60):
                                size = self._get_folder_size(app_folder)
                                if size > 0:
                                    downloads.append({
                                        "id": f"steam_{appid}",
                                        "app_id": appid,
                                        "name": f"Steam App ({appid})",
                                        "platform": "Steam",
                                        "bytes_downloaded": size,
                                        "bytes_total": size,
                                        "state": "Downloading",
                                        "is_active": True,
                                        "progress_percent": 50.0
                                    })
                except Exception:
                    pass

        return downloads

    def _parse_acf(self, path: str) -> dict | None:
        """
        Parse Steam ACF manifest file.
        Strictly verify active state flags without false positives for installed games.
        """
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            appid_m = re.search(r'"appid"\s+"(\d+)"', content)
            name_m = re.search(r'"name"\s+"([^"]+)"', content)
            state_m = re.search(r'"StateFlags"\s+"(\d+)"', content)
            bytes_dl_m = re.search(r'"BytesDownloaded"\s+"(\d+)"', content)
            bytes_tot_m = re.search(r'"BytesToDownload"\s+"(\d+)"', content)
            bytes_stage_m = re.search(r'"BytesToStage"\s+"(\d+)"', content)
            bytes_staged_m = re.search(r'"BytesStaged"\s+"(\d+)"', content)

            if not appid_m or not state_m:
                return None

            appid = appid_m.group(1)
            name = name_m.group(1) if name_m else f"Steam App {appid}"
            state_flags = int(state_m.group(1))
            bytes_dl = int(bytes_dl_m.group(1)) if bytes_dl_m else 0
            bytes_tot = int(bytes_tot_m.group(1)) if bytes_tot_m else 0
            bytes_stage = int(bytes_stage_m.group(1)) if bytes_stage_m else 0
            bytes_staged = int(bytes_staged_m.group(1)) if bytes_staged_m else 0

            # StateFlags Interpretation:
            # 4: StateFullyInstalled (IDLE - NOT active!)
            # 512 / 128: Paused / UpdatePaused (NOT active)
            # 1024: StateDownloading
            # 2048: StateStaging
            # 4096: StateCommitting
            # 8192: StateValidating
            # 16: StateUpdateRunning
            # 64: StatePreallocating

            # Immediate exclusion for idle fully installed games
            if state_flags == 4:
                return None

            # Immediate exclusion for paused states
            if (state_flags & 512) or (state_flags & 128):
                return None

            is_active = False
            state_str = "Idle"

            # Check downloading state
            if state_flags & 1024:
                if bytes_tot > 0 and bytes_dl < bytes_tot:
                    is_active = True
                    state_str = "Downloading"
                elif bytes_tot > 0 and bytes_dl >= bytes_tot:
                    # Download completed, may be committing or finishing
                    if bytes_stage > bytes_staged:
                        is_active = True
                        state_str = "Patching"
                    else:
                        is_active = False
                        state_str = "Completed"

            elif state_flags & 2048:
                is_active = True
                state_str = "Staging Files"

            elif state_flags & 4096:
                is_active = True
                state_str = "Committing Files"

            elif state_flags & 8192:
                is_active = True
                state_str = "Validating Files"

            elif state_flags & 16:
                is_active = True
                state_str = "Updating"

            # If not active according to state flags, reject it
            if not is_active:
                return None

            prog = 0.0
            if bytes_tot > 0:
                prog = min(100.0, max(0.0, (bytes_dl / bytes_tot) * 100.0))

            return {
                "id": f"steam_{appid}",
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

    def _is_folder_recently_modified(self, path: str, max_age_sec: int = 60) -> bool:
        """Check if any file in the folder was modified within max_age_sec."""
        now = time.time()
        try:
            for root, _, files in os.walk(path):
                for f in files:
                    try:
                        mtime = os.path.getmtime(os.path.join(root, f))
                        if (now - mtime) < max_age_sec:
                            return True
                    except Exception:
                        pass
        except Exception:
            pass
        return False

    def _get_folder_size(self, path: str) -> int:
        total = 0
        try:
            for root, _, files in os.walk(path):
                for f in files:
                    try:
                        total += os.path.getsize(os.path.join(root, f))
                    except Exception:
                        pass
        except Exception:
            pass
        return total
