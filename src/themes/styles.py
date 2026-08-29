"""
NightByte AI - Professional Modern Dark Theme
Designed for maximum elegance, simplicity, visual harmony, and zero visual clutter.
"""

CYBERPUNK_DARK = """
/* Global Application Base */
QWidget {
    background-color: #0b0f17;
    color: #e2e8f0;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Arial, sans-serif;
    font-size: 13px;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
}

/* Title Bar */
#TitleBar {
    background-color: #111827;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    min-height: 40px;
    max-height: 40px;
}

#AppTitle {
    color: #38bdf8;
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 0.3px;
}

#TitleButton {
    background: transparent;
    border: 1px solid transparent;
    color: #94a3b8;
    padding: 5px 10px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
}

#TitleButton:hover {
    background-color: rgba(255, 255, 255, 0.06);
    color: #f8fafc;
}

#CloseTitleButton {
    background: transparent;
    border: none;
    color: #94a3b8;
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 14px;
}

#CloseTitleButton:hover {
    background-color: #ef4444;
    color: #ffffff;
}

/* Update Banner */
#UpdateBanner {
    background-color: #1e3a8a;
    color: #93c5fd;
    border: 1px solid #3b82f6;
    border-radius: 8px;
    padding: 8px 14px;
    font-weight: 700;
    font-size: 12px;
    margin: 4px 12px 0px 12px;
}

#UpdateBanner:hover {
    background-color: #1d4ed8;
    color: #ffffff;
}

/* Navigation Segmented Tab Bar */
QTabWidget::pane {
    border: 1px solid rgba(255, 255, 255, 0.06);
    background-color: #0b0f17;
    border-radius: 12px;
    padding: 10px;
}

QTabBar {
    background-color: transparent;
    qproperty-drawBase: 0;
}

QTabBar::tab {
    background-color: #111827;
    color: #94a3b8;
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 8px;
    padding: 8px 16px;
    margin-right: 6px;
    margin-bottom: 8px;
    font-weight: 600;
    font-size: 12px;
}

QTabBar::tab:selected {
    background-color: #2563eb;
    color: #ffffff;
    border: 1px solid #3b82f6;
}

QTabBar::tab:hover:!selected {
    background-color: rgba(255, 255, 255, 0.05);
    color: #f1f5f9;
}

/* Surface Cards */
#HeroCard {
    background-color: #111827;
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    padding: 16px;
}

#HeroSpeed {
    color: #ffffff;
    font-size: 38px;
    font-weight: 900;
    letter-spacing: -0.5px;
}

#HeroSpeedUnit {
    color: #64748b;
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 6px;
}

/* Master Power Button */
#MasterPowerBtn {
    background-color: #2563eb;
    color: #ffffff;
    border: none;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 800;
    padding: 12px 20px;
    min-height: 44px;
}

#MasterPowerBtn:hover {
    background-color: #1d4ed8;
}

#MasterPowerBtn[active="true"] {
    background-color: #dc2626;
}

#MasterPowerBtn[active="true"]:hover {
    background-color: #b91c1c;
}

/* Action Selector & Form Controls */
QComboBox {
    background-color: #161f30;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 6px 14px;
    color: #f8fafc;
    font-weight: 600;
    font-size: 12px;
    min-height: 32px;
}

QComboBox:hover {
    border-color: #3b82f6;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #161f30;
    border: 1px solid #334155;
    border-radius: 8px;
    color: #f8fafc;
    selection-background-color: #2563eb;
    padding: 4px;
}

QSpinBox, QLineEdit {
    background-color: #161f30;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 6px 10px;
    color: #f8fafc;
    min-height: 30px;
}

QSpinBox:hover, QLineEdit:hover {
    border-color: #3b82f6;
}

QSpinBox:focus, QLineEdit:focus {
    border-color: #60a5fa;
}

/* Checkboxes */
QCheckBox {
    color: #cbd5e1;
    spacing: 8px;
    font-size: 12px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #334155;
    border-radius: 5px;
    background-color: #161f30;
}

QCheckBox::indicator:hover {
    border-color: #3b82f6;
}

QCheckBox::indicator:checked {
    background-color: #2563eb;
    border-color: #3b82f6;
}

QRadioButton {
    color: #cbd5e1;
    spacing: 8px;
    font-size: 12px;
}

QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #334155;
    border-radius: 8px;
    background-color: #161f30;
}

QRadioButton::indicator:checked {
    background-color: #2563eb;
    border-color: #60a5fa;
}

/* Secondary Button */
#SecondaryButton {
    background-color: #161f30;
    color: #cbd5e1;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 12px;
    min-height: 32px;
}

#SecondaryButton:hover {
    background-color: rgba(255, 255, 255, 0.08);
    color: #f8fafc;
    border-color: rgba(255, 255, 255, 0.15);
}

#PrimaryButton {
    background-color: #2563eb;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: bold;
    font-size: 12px;
    min-height: 32px;
}

#PrimaryButton:hover {
    background-color: #1d4ed8;
}

/* Status Banner */
#StatusBanner {
    background-color: #111827;
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 10px;
    padding: 10px 14px;
}

#StatusText {
    font-size: 12px;
    font-weight: 600;
    color: #94a3b8;
}

/* Scrollbars */
QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    background-color: transparent;
    width: 6px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #1f2937;
    border-radius: 3px;
    min-height: 24px;
}

QScrollBar::handle:vertical:hover {
    background-color: #374151;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Event Log */
#LogList {
    background-color: #111827;
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 10px;
    color: #94a3b8;
    font-size: 12px;
    padding: 8px;
}

QListWidget::item {
    padding: 6px 8px;
    border-radius: 6px;
    margin-bottom: 2px;
}

QListWidget::item:hover {
    background-color: rgba(255, 255, 255, 0.04);
}
"""
