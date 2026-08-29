# ⚡ NightByte AI

<p align="center">
  <img src="assets/app_icon.png" width="128" height="128" alt="NightByte AI Logo" />
</p>

<p align="center">
  <b>The Smartest Open-Source Auto-Shutdown & Download Guardian for Windows</b><br>
  <i>المساعد الذكي مفتوح المصدر لإيقاف التشغيل وإدارة التحميلات وحماية انقطاع الإنترنت</i>
</p>

<p align="center">
  <a href="https://github.com/Mayer-ELbot/NightByte/releases"><img src="https://img.shields.io/github/v/release/Mayer-ELbot/NightByte?color=0284c7&style=for-the-badge" alt="Latest Release"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-emerald?style=for-the-badge" alt="MIT License"></a>
  <img src="https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python" alt="Python 3.12+">
  <img src="https://img.shields.io/badge/GUI-PySide6%20%2F%20Qt-green?style=for-the-badge&logo=qt" alt="PySide6">
  <img src="https://img.shields.io/badge/Platform-Windows%2010%20%2F%2011-0078d7?style=for-the-badge&logo=windows" alt="Windows">
</p>

---

## 🌟 Overview / نظرة عامة

**NightByte AI** is a lightweight, ultra-intelligent desktop application designed to monitor your game downloads across **Steam, Epic Games, EA App, Battle.net, Xbox, Torrent clients, and IDM**, and automatically perform system actions (**Shutdown, Sleep, Hibernate, Restart, Lock, Turn off Displays**) when downloads complete.

Unlike traditional shutdown timers, **NightByte AI is intelligent**:
- 🛡️ **Internet Drop Protection (Network Guardian):** If your internet disconnects in the middle of the night, **NightByte freezes the shutdown timer** so your PC stays awake and finishes the download when the connection resumes!
- 🎮 **Deep Steam & Launcher Parsing:** Reads `libraryfolders.vdf`, `appmanifest_*.acf` state flags, and staging directories so it never shuts down during game file allocation, patching, or verifying.
- 🧠 **Anti-AFK & Gaming Mode:** If you are actively using your PC or playing a full-screen game, NightByte defers shutdown automatically.
- 🚨 **Floating Countdown HUD:** Sleek on-screen warning window with instant 1-click **Cancel** button and snooze quick-actions (`+5m`, `+15m`, `+30m`, `+1h`).
- 🔄 **Built-in GitHub Update Checker:** Automatically notifies you when a new release is available on GitHub.
- 🌐 **100% Bilingual:** Instant toggle between **العربية** and **English** with native RTL/LTR layout.

---

## 🚀 Key Features / المميزات الرئيسية

| Feature | Description |
| :--- | :--- |
| **🛡️ Network Guardian** | Continuous async health ping. Automatically freezes shutdown countdown when internet drops to prevent corrupted/unfinished downloads. |
| **🎮 Multi-Platform Engine** | Deep detection for Steam, Epic Games, EA App, Battle.net, Xbox, Ubisoft Connect, qBittorrent, IDM, and Web Browsers. |
| **📊 Minimalist Live Dashboard** | Real-time vector speed graph, large hero speed display, disk write rate, session data received, and active items list. |
| **🧠 Anti-AFK & Awake Lock** | Keeps Windows awake during downloads (`SetThreadExecutionState`) and pauses action if user input is detected. |
| **🚨 Countdown Warning HUD** | Translucent floating circular countdown dialog with loud alert and snooze controls. |
| **🔔 Discord / Telegram Webhook** | Optional webhook notifications sent directly to your phone when downloads finish. |
| **📥 GitHub Release Updater** | Asynchronous version check with direct 1-click update download link. |
| **⚙️ System Tray Integration** | Minimize to tray, dynamic tooltip with live speed, and quick right-click menu. |

---

## 📥 Download & Quick Start / التحميل والتشغيل

### Option 1: Standalone Portable Executable (No Python Required)
1. Download the latest **`NightByte.exe`** from [GitHub Releases](https://github.com/Mayer-ELbot/NightByte/releases).
2. Double click **`NightByte.exe`** and start using it immediately!

### Option 2: Run from Source Code
```bash
# 1. Clone the repository
git clone https://github.com/Mayer-ELbot/NightByte.git
cd NightByte

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the application
python src/main.py
```

---

## 🛠️ Building the Standalone `.exe` / بناء الملف التنفيذي

To compile the single-file Windows executable with embedded icons and assets:

```bash
python build.py
```
The compiled binary will be generated in `./NightByte.exe`.

---

## 📁 Project Architecture / هيكلية المشروع

```
NightByte/
├── assets/                 # App icons and graphics
│   ├── app_icon.ico
│   └── app_icon.png
├── src/
│   ├── core/               # Core intelligence & platform detectors
│   │   ├── monitor_engine.py
│   │   ├── network_guardian.py
│   │   ├── steam_detector.py
│   │   └── system_power.py
│   ├── gui/                # PySide6 GUI views & dialogs
│   │   ├── countdown_dialog.py
│   │   ├── main_window.py
│   │   ├── settings_dialog.py
│   │   ├── tray_manager.py
│   │   └── widgets/
│   │       ├── download_card.py
│   │       └── speed_graph.py
│   ├── i18n/               # Arabic & English localization
│   │   └── translations.py
│   ├── themes/             # Minimalist Dark Stylesheets
│   │   ├── styles.py
│   │   └── theme_manager.py
│   ├── utils/              # Config, logger, sound, updater
│   │   ├── config.py
│   │   ├── logger.py
│   │   ├── sound_effects.py
│   │   └── updater.py
│   └── main.py             # Entry point
├── .github/workflows/      # Automated CI/CD GitHub Action
│   └── build.yml
├── build.py                # Standalone PyInstaller builder
├── CONTRIBUTING.md         # Open-source contribution guidelines
├── LICENSE                 # MIT License
└── README.md               # Documentation
```

---

## 🤝 Contributing / المساهمة والتطوير

Contributions, issues, and feature requests are welcome!
Feel free to check the [issues page](https://github.com/Mayer-ELbot/NightByte/issues).

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 🙏 Acknowledgements & Credits / شكر وتقدير

- Inspired by the concept of [SteamDown](https://github.com/Avaneesh13/SteamDown) by [@Avaneesh13](https://github.com/Avaneesh13).
- Built independently from scratch with a completely new architecture, multi-platform engine, network guardian, and modern interface under the MIT License.

---

## 📄 License / الترخيص

Distributed under the **MIT License**. See `LICENSE` for more information.

---

<p align="center">
  Made with ❤️ for gamers & night downloaders worldwide.
</p>

