"""
SteamDown Ultra AI - System Power & Native Windows Controller
Provides native power control, awake-locks, anti-AFK idle detection, and autostart.
"""

import os
import sys
import time
import subprocess
import winreg
import ctypes
from ctypes import wintypes
import psutil
from utils.logger import logger


# Windows API Constants & Structures
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_AWAYMODE_REQUIRED = 0x00000040

HWND_BROADCAST = 0xFFFF
WM_SYSCOMMAND = 0x0112
SC_MONITORPOWER = 0xF170

class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.UINT),
        ("dwTime", wintypes.DWORD)
    ]


class SystemPowerController:
    """Controls Windows power actions, idle detection, and system state."""
    
    _awake_locked = False
    
    @classmethod
    def set_awake_lock(cls, enable: bool):
        """
        Prevent or allow Windows from sleeping while downloading.
        Uses SetThreadExecutionState Win32 API.
        """
        try:
            kernel32 = ctypes.windll.kernel32
            if enable:
                kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_AWAYMODE_REQUIRED)
                if not cls._awake_locked:
                    logger.info("System Awake-Lock engaged (preventing PC sleep during downloads).")
                cls._awake_locked = True
            else:
                kernel32.SetThreadExecutionState(ES_CONTINUOUS)
                if cls._awake_locked:
                    logger.info("System Awake-Lock released.")
                cls._awake_locked = False
        except Exception as e:
            logger.error(f"Failed to set execution state: {e}")

    @classmethod
    def get_user_idle_seconds(cls) -> float:
        """
        Get the number of seconds since the user last moved mouse or pressed key.
        Uses GetLastInputInfo Win32 API.
        """
        try:
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32
            
            lii = LASTINPUTINFO()
            lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
            if user32.GetLastInputInfo(ctypes.byref(lii)):
                millis = kernel32.GetTickCount() - lii.dwTime
                return max(0.0, millis / 1000.0)
        except Exception as e:
            logger.error(f"Error checking user idle time: {e}")
        return 999999.0

    @classmethod
    def is_fullscreen_app_running(cls) -> bool:
        """Check if the currently focused window is in full-screen mode (e.g. game)."""
        try:
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            if not hwnd:
                return False
                
            # Get window rect
            rect = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            
            # Get screen resolution
            screen_w = user32.GetSystemMetrics(0)
            screen_h = user32.GetSystemMetrics(1)
            
            w = rect.right - rect.left
            h = rect.bottom - rect.top
            
            # If foreground window covers the entire screen, it's likely a full-screen game or video
            if w >= screen_w and h >= screen_h and rect.left <= 0 and rect.top <= 0:
                return True
        except Exception as e:
            logger.error(f"Error checking full-screen state: {e}")
        return False

    @classmethod
    def execute_action(cls, action: str, force: bool = True) -> bool:
        """Execute the chosen system action."""
        logger.info(f"Executing system action: '{action}' (force={force})...")
        action = action.lower().strip()
        
        # Release awake lock before shutdown/sleep
        cls.set_awake_lock(False)
        
        try:
            if action == "shutdown":
                f_flag = " /f" if force else ""
                subprocess.Popen(f"shutdown /s /t 0{f_flag}", shell=True)
                return True
                
            elif action == "restart":
                f_flag = " /f" if force else ""
                subprocess.Popen(f"shutdown /r /t 0{f_flag}", shell=True)
                return True
                
            elif action == "sleep":
                # Rundll32 SetSuspendState: sleep (0,1,0)
                subprocess.Popen("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
                return True
                
            elif action == "hibernate":
                subprocess.Popen("shutdown /h", shell=True)
                return True
                
            elif action == "lock":
                subprocess.Popen("rundll32.exe user32.dll,LockWorkStation", shell=True)
                return True
                
            elif action == "logoff":
                f_flag = " /f" if force else ""
                subprocess.Popen(f"shutdown /l{f_flag}", shell=True)
                return True
                
            elif action == "monitors_off":
                # Send SC_MONITORPOWER 2 (turn off)
                user32 = ctypes.windll.user32
                user32.SendMessageW(HWND_BROADCAST, WM_SYSCOMMAND, SC_MONITORPOWER, 2)
                return True
                
            elif action == "close_launchers" or action == "close_steam":
                cls.close_launchers_gracefully()
                return True
                
            else:
                logger.warning(f"Unknown action: {action}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing action {action}: {e}")
            return False

    @classmethod
    def close_launchers_gracefully(cls):
        """Gracefully request Steam and other launchers to exit to save progress."""
        try:
            # 1. Graceful Steam shutdown command
            steam_path = cls.get_steam_install_path()
            if steam_path:
                steam_exe = os.path.join(steam_path, "Steam.exe")
                if os.path.exists(steam_exe):
                    try:
                        subprocess.run([steam_exe, "-shutdown"], timeout=5)
                        logger.info("Sent graceful -shutdown signal to Steam.")
                    except Exception:
                        pass
            
            # 2. Terminate any remaining launcher processes safely
            launcher_names = ["steam.exe", "steamservice.exe", "epicgameslauncher.exe", 
                              "eadesktop.exe", "battle.net.exe", "upc.exe"]
            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    pname = proc.info["name"]
                    if pname and pname.lower() in launcher_names:
                        proc.terminate()
                        logger.info(f"Terminated process {pname} (PID: {proc.info['pid']})")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            logger.error(f"Error closing launchers: {e}")

    @classmethod
    def get_steam_install_path(cls) -> str:
        """Get Steam directory from Windows Registry."""
        for subkey in [r"SOFTWARE\WOW6432Node\Valve\Steam", r"SOFTWARE\Valve\Steam"]:
            try:
                hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, subkey)
                path, _ = winreg.QueryValueEx(hkey, "InstallPath")
                winreg.CloseKey(hkey)
                if path and os.path.exists(path):
                    return path
            except Exception:
                continue
        return ""

    @classmethod
    def set_autostart_registry(cls, enable: bool) -> bool:
        """Add or remove SteamDown from Windows Startup Registry."""
        reg_key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "SteamDownUltraAI"
        try:
            hkey = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_key_path, 0, winreg.KEY_SET_VALUE)
            if enable:
                exe_path = sys.executable if getattr(sys, "frozen", False) else os.path.abspath(sys.argv[0])
                winreg.SetValueEx(hkey, app_name, 0, winreg.REG_SZ, f'"{exe_path}" --minimized')
                logger.info("Added SteamDown to Windows startup.")
            else:
                try:
                    winreg.DeleteValue(hkey, app_name)
                    logger.info("Removed SteamDown from Windows startup.")
                except FileNotFoundError:
                    pass
            winreg.CloseKey(hkey)
            return True
        except Exception as e:
            logger.error(f"Failed to update startup registry: {e}")
            return False
