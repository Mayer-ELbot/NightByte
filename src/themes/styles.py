"""
NightByte AI — Inverted Monochrome Dark Theme
Near-black dominant. White accents. Zero color. Zero noise.
Raycast / Linear / Things 3 dark mode aesthetic.
"""

MONO_DARK = """

/* ─── Global ────────────────────────────────────────────────── */
QWidget {
    background-color: #0f0f0f;
    color: #ffffff;
    font-family: 'Segoe UI', -apple-system, system-ui, sans-serif;
    font-size: 13px;
    selection-background-color: #ffffff;
    selection-color: #000000;
    border: none;
    outline: none;
}

/* ─── Title Bar ─────────────────────────────────────────────── */
#TitleBar {
    background-color: #0f0f0f;
    border-bottom: 1px solid #222222;
    min-height: 44px;
    max-height: 44px;
}

#AppTitle {
    color: #ffffff;
    font-size: 15px;
    font-weight: 800;
    letter-spacing: -0.3px;
}

#VersionLabel {
    color: #555555;
    font-size: 11px;
    font-weight: 500;
}

#TitleButton {
    background: transparent;
    border: 1px solid #2a2a2a;
    color: #666666;
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
    min-height: 28px;
}

#TitleButton:hover {
    background-color: #1c1c1c;
    color: #ffffff;
    border-color: #444444;
}

#CloseTitleButton {
    background: transparent;
    border: none;
    color: #555555;
    font-size: 14px;
    padding: 6px 12px;
    border-radius: 6px;
    min-height: 32px;
    min-width: 32px;
}

#CloseTitleButton:hover {
    background-color: #ffffff;
    color: #000000;
}

/* ─── Update Banner ─────────────────────────────────────────── */
#UpdateBanner {
    background-color: #ffffff;
    color: #000000;
    border: none;
    border-radius: 0;
    padding: 9px 16px;
    font-weight: 800;
    font-size: 12px;
    text-align: left;
}

#UpdateBanner:hover {
    background-color: #eeeeee;
}

/* ─── Tab Navigation ────────────────────────────────────────── */
QTabWidget::pane {
    border: none;
    background-color: #0f0f0f;
}

QTabBar {
    background-color: #0f0f0f;
    qproperty-drawBase: 0;
}

QTabBar::tab {
    background-color: #1c1c1c;
    color: #888888;
    border: 1px solid #2a2a2a;
    border-radius: 20px;
    padding: 7px 18px;
    margin-right: 6px;
    font-weight: 600;
    font-size: 12px;
    min-height: 32px;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    color: #000000;
    border-color: #ffffff;
    font-weight: 800;
}

QTabBar::tab:hover:!selected {
    background-color: #252525;
    color: #cccccc;
}

/* ─── Hero Speed ────────────────────────────────────────────── */
#HeroSpeed {
    color: #ffffff;
    font-size: 52px;
    font-weight: 900;
    letter-spacing: -2px;
    line-height: 1;
}

#HeroSpeedUnit {
    color: #666666;
    font-size: 16px;
    font-weight: 600;
    padding-bottom: 6px;
}

/* ─── Net Badge ─────────────────────────────────────────────── */
#NetBadgeOnline {
    background-color: #ffffff;
    color: #000000;
    border: none;
    border-radius: 20px;
    padding: 5px 14px;
    font-weight: 800;
    font-size: 12px;
}

#NetBadgeOffline {
    background-color: transparent;
    color: #ffffff;
    border: 1.5px solid #ffffff;
    border-radius: 20px;
    padding: 5px 14px;
    font-weight: 700;
    font-size: 12px;
}

/* ─── Master Power Button ───────────────────────────────────── */
#MasterPowerBtn {
    background-color: #ffffff;
    color: #000000;
    border: none;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 800;
    padding: 14px 20px;
    min-height: 48px;
    letter-spacing: 0.2px;
}

#MasterPowerBtn:hover {
    background-color: #e8e8e8;
}

#MasterPowerBtn:pressed {
    background-color: #cccccc;
}

#MasterPowerBtn[active="true"] {
    background-color: #1c1c1c;
    color: #ffffff;
    border: 1.5px solid #444444;
}

#MasterPowerBtn[active="true"]:hover {
    background-color: #252525;
    border-color: #666666;
}

/* ─── Platform Row Frame ────────────────────────────────────── */
#PlatformFrame {
    background-color: #0f0f0f;
    border: 1px solid #1e1e1e;
    border-radius: 10px;
}

#PlatformLabel {
    color: #555555;
    font-weight: 700;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* ─── Action Row ────────────────────────────────────────────── */
#ActionLabel {
    color: #ffffff;
    font-weight: 800;
    font-size: 13px;
}

QComboBox {
    background-color: #1c1c1c;
    border: 1px solid #333333;
    border-radius: 8px;
    padding: 7px 14px;
    color: #ffffff;
    font-weight: 700;
    font-size: 13px;
    min-height: 36px;
}

QComboBox:hover {
    border-color: #555555;
    background-color: #252525;
}

QComboBox::drop-down {
    border: none;
    width: 28px;
}

QComboBox QAbstractItemView {
    background-color: #1c1c1c;
    border: 1px solid #333333;
    border-radius: 8px;
    color: #ffffff;
    selection-background-color: #ffffff;
    selection-color: #000000;
    padding: 4px;
    font-weight: 600;
}

/* ─── Status Bar ────────────────────────────────────────────── */
#StatusBar {
    background-color: #0f0f0f;
    border-top: 1px solid #1e1e1e;
    min-height: 34px;
    max-height: 34px;
}

#StatusText {
    color: #555555;
    font-size: 12px;
    font-weight: 500;
}

#StatusTextActive {
    color: #ffffff;
    font-size: 12px;
    font-weight: 700;
}

#StatusTextWarning {
    color: #ffffff;
    font-size: 12px;
    font-weight: 800;
}

/* ─── Download Cards ────────────────────────────────────────── */
#DownloadCard {
    background-color: #141414;
    border: 1px solid #222222;
    border-radius: 10px;
}

#DownloadCard:hover {
    border-color: #444444;
}

#CardTitle {
    color: #ffffff;
    font-weight: 700;
    font-size: 13px;
}

#CardPlatform {
    background-color: #ffffff;
    color: #000000;
    border-radius: 4px;
    padding: 2px 7px;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.5px;
}

#CardState {
    color: #666666;
    font-size: 11px;
    font-weight: 600;
}

QProgressBar {
    background-color: #222222;
    border: none;
    border-radius: 3px;
    height: 5px;
}

QProgressBar::chunk {
    background-color: #ffffff;
    border-radius: 3px;
}

/* ─── Log List ──────────────────────────────────────────────── */
#LogList {
    background-color: #111111;
    border: 1px solid #1e1e1e;
    border-radius: 10px;
    color: #888888;
    font-size: 12px;
    padding: 8px;
    font-family: 'Cascadia Code', 'Consolas', monospace;
}

QListWidget::item {
    padding: 5px 6px;
    border-radius: 5px;
}

QListWidget::item:hover {
    background-color: #1a1a1a;
}

/* ─── Scroll Bars ───────────────────────────────────────────── */
QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    background: transparent;
    width: 5px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #2a2a2a;
    border-radius: 3px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #444444;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

/* ─── Form Controls ─────────────────────────────────────────── */
QSpinBox, QLineEdit {
    background-color: #1c1c1c;
    border: 1px solid #2a2a2a;
    border-radius: 7px;
    padding: 6px 10px;
    color: #ffffff;
    font-weight: 600;
    min-height: 32px;
}

QSpinBox:focus, QLineEdit:focus {
    border-color: #ffffff;
}

QCheckBox {
    color: #cccccc;
    font-weight: 600;
    spacing: 10px;
    font-size: 13px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #333333;
    border-radius: 5px;
    background-color: #1c1c1c;
}

QCheckBox::indicator:hover {
    border-color: #ffffff;
}

QCheckBox::indicator:checked {
    background-color: #ffffff;
    border-color: #ffffff;
}

QRadioButton {
    color: #cccccc;
    font-weight: 600;
    spacing: 10px;
}

QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #333333;
    border-radius: 8px;
    background-color: #1c1c1c;
}

QRadioButton::indicator:checked {
    background-color: #ffffff;
    border-color: #ffffff;
}

/* ─── Buttons ───────────────────────────────────────────────── */
#SecondaryButton {
    background-color: #1c1c1c;
    color: #cccccc;
    border: 1px solid #2a2a2a;
    border-radius: 8px;
    padding: 7px 16px;
    font-weight: 700;
    font-size: 12px;
    min-height: 32px;
}

#SecondaryButton:hover {
    background-color: #252525;
    color: #ffffff;
    border-color: #444444;
}

#PrimaryButton {
    background-color: #ffffff;
    color: #000000;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: 800;
    font-size: 13px;
    min-height: 36px;
}

#PrimaryButton:hover {
    background-color: #e8e8e8;
}

/* ─── Group Box ─────────────────────────────────────────────── */
QGroupBox {
    background-color: #111111;
    border: 1px solid #1e1e1e;
    border-radius: 10px;
    margin-top: 10px;
    padding: 14px 14px 10px 14px;
    color: #ffffff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
    background-color: #0f0f0f;
    color: #555555;
    font-weight: 800;
    font-size: 10px;
    letter-spacing: 1px;
    text-transform: uppercase;
}

/* ─── Mode Frame ────────────────────────────────────────────── */
#ModeFrame {
    background-color: #111111;
    border: 1px solid #1e1e1e;
    border-radius: 10px;
}

/* ─── Countdown Dialog ──────────────────────────────────────── */
#CountdownDialog {
    background-color: #0f0f0f;
    border: 1px solid #222222;
    border-radius: 16px;
}
"""
