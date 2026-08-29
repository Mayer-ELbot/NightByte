# Changelog 📜

All notable changes to **NightByte AI** are documented in this file.

---

## [v2.0.0] - 2026-08-29

### 🚀 Major Transformation & Rebranding
- Rebranded application from `SteamDown` to **NightByte AI** with a fresh, monochrome minimalist dark interface.
- Complete open-source release on GitHub with MIT License.

### 🛡️ Smart Network Guardian
- Added asynchronous real-time internet connectivity monitor.
- **Auto-Freeze on Disconnect:** Automatically pauses and freezes shutdown countdown when internet drops to prevent corrupted/unfinished downloads.
- Auto-resumes monitoring seamlessly when connection is restored.

### 🎮 Deep Multi-Platform Download Engine
- Deep Steam integration: parses `libraryfolders.vdf`, `appmanifest_*.acf` state flags, and `steamapps/downloading/` directory.
- Detects staging, allocating, and patching tasks so the PC never turns off while updating files on disk.
- Multi-launcher support for Epic Games, EA App, Battle.net, Xbox / MS Store, Ubisoft Connect, qBittorrent, IDM, and Browsers.
- Specific game targeting mode: selectively wait for specific downloads instead of all.
- Universal system-wide and per-process network and disk I/O throughput fallback.

### 🧠 Anti-AFK & System Protection
- Added user activity detection (`GetLastInputInfo`): pauses shutdown if user is active with mouse/keyboard.
- Added full-screen 3D gaming mode protection.
- Native Awake-Lock (`SetThreadExecutionState`) to prevent Windows from sleeping during downloads.

### 🚨 Countdown Warning HUD & Audio
- Translucent on-screen circular warning countdown dialog.
- Instant 1-click **Cancel** button.
- Quick Snooze buttons (`+5m`, `+15m`, `+30m`, `+1h`).
- Native audio chimes and countdown tick beeps.

### 🔄 GitHub Update Checker
- Added asynchronous GitHub Releases API integration to notify users directly in-app when new versions are published.

### 🖤 Monochrome Dark UI
- Pure distraction-free minimalist dark aesthetic designed for high contrast and ergonomics.
