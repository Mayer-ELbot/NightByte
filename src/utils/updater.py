"""
NightByte AI - GitHub Update Checker
Asynchronously checks GitHub Releases API for new updates and downloads.
"""

import sys
import json
import threading
import requests
from PySide6.QtCore import QObject, Signal
from utils.logger import logger

CURRENT_VERSION = "2.0.0"
GITHUB_REPO = "Mayer-ELbot/NightByte"
RELEASES_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
RELEASES_PAGE_URL = f"https://github.com/{GITHUB_REPO}/releases/latest"


class UpdateChecker(QObject):
    """Checks for new versions on GitHub in a background thread."""

    update_available = Signal(str, str, str)  # latest_ver, release_notes, download_url
    up_to_date = Signal(str)                  # current_ver
    check_failed = Signal(str)                # error_msg

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_version = CURRENT_VERSION
        self.repo = GITHUB_REPO

    def check_for_updates_async(self):
        """Run update check in background thread."""
        thread = threading.Thread(target=self._check_worker, daemon=True)
        thread.start()

    def _check_worker(self):
        """Worker making GitHub API request."""
        try:
            logger.info(f"Checking for updates on GitHub ({GITHUB_REPO})...")
            headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "NightByte-UpdateChecker"}
            resp = requests.get(RELEASES_API_URL, headers=headers, timeout=6)
            
            if resp.status_code == 200:
                data = resp.json()
                tag_name = data.get("tag_name", "").lstrip("v")
                body = data.get("body", "Bug fixes and performance improvements.")
                html_url = data.get("html_url", RELEASES_PAGE_URL)

                # Check if there is a direct .exe asset
                assets = data.get("assets", [])
                exe_url = html_url
                for asset in assets:
                    if asset.get("name", "").endswith(".exe"):
                        exe_url = asset.get("browser_download_url", html_url)
                        break

                if self._is_newer(tag_name, self.current_version):
                    logger.success(f"✨ New update found: v{tag_name} (Current: v{self.current_version})")
                    self.update_available.emit(tag_name, body, exe_url)
                else:
                    logger.info(f"NightByte is up to date (v{self.current_version}).")
                    self.up_to_date.emit(self.current_version)
            elif resp.status_code == 404:
                # No releases yet
                logger.info(f"No releases found on GitHub repository yet. (v{self.current_version})")
                self.up_to_date.emit(self.current_version)
            else:
                msg = f"GitHub API responded with code {resp.status_code}"
                logger.warning(msg)
                self.check_failed.emit(msg)
        except Exception as e:
            logger.warning(f"Could not connect to GitHub to check updates: {e}")
            self.check_failed.emit(str(e))

    def _is_newer(self, latest_str: str, current_str: str) -> bool:
        """Compare semver strings like 2.1.0 vs 2.0.0."""
        try:
            latest_parts = [int(p) for p in latest_str.split(".") if p.isdigit()]
            current_parts = [int(p) for p in current_str.split(".") if p.isdigit()]
            return latest_parts > current_parts
        except Exception:
            return False
