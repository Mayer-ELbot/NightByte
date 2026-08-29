"""
NightByte AI - PyInstaller Build Script
Builds the standalone, single-file Windows executable with embedded assets and icon.
"""

import os
import sys
import subprocess
import shutil

def build_exe():
    print("=" * 60)
    print("Starting NightByte AI Build Process...")
    print("=" * 60)

    # 1. Clean previous build artifacts
    for d in ["build", "dist"]:
        if os.path.exists(d):
            print(f"Cleaning {d}/ directory...")
            shutil.rmtree(d, ignore_errors=True)

    # 2. PyInstaller command arguments
    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        "--name", "NightByte",
        "--icon", "assets/app_icon.ico",
        "--add-data", "assets;assets",
        "--add-data", "src;src",
        "--paths", "src",
        "--hidden-import", "PySide6.QtCore",
        "--hidden-import", "PySide6.QtGui",
        "--hidden-import", "PySide6.QtWidgets",
        "--hidden-import", "psutil",
        "--hidden-import", "requests",
        "--hidden-import", "winsound",
        "--clean",
        "src/main.py"
    ]

    print("Running command:", " ".join(cmd))
    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("BUILD SUCCESSFUL!")
        dist_exe = os.path.join("dist", "NightByte.exe")
        target_exe = "NightByte.exe"
        steam_exe = "SteamDown.exe"
        if os.path.exists(dist_exe):
            shutil.copy2(dist_exe, target_exe)
            shutil.copy2(dist_exe, steam_exe)
            size_mb = os.path.getsize(target_exe) / (1024 * 1024)
            print(f"Output executable 1: {os.path.abspath(target_exe)} ({size_mb:.2f} MB)")
            print(f"Output executable 2: {os.path.abspath(steam_exe)} ({size_mb:.2f} MB)")
        print("=" * 60)
    else:
        print("\nBUILD FAILED with return code:", result.returncode)
        sys.exit(result.returncode)


if __name__ == "__main__":
    build_exe()
