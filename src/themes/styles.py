"""
NightByte AI - Minimalist Clean Modern Dark Stylesheet
Designed for maximum simplicity, visual clarity, WCAG AA contrast, and zero visual clutter.
"""

CYBERPUNK_DARK = """
/* Global Application Base */
QWidget {
    background-color: #0b0f19;
    color: #f1f5f9;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
    selection-background-color: #0284c7;
    selection-color: #ffffff;
}

/* Frameless Clean Title Bar */
#TitleBar {
    background-color: #0f172a;
    border-bottom: 1px solid #1e293b;
    min-height: 38px;
    max-height: 38px;
}

#AppTitle {
    color: #38bdf8;
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 0.5px;
}

#TitleButton {
    background: transparent;
    border: none;
    color: #94a3b8;
    padding: 6px 10px;
    min-height: 26px;
    border-radius: 6px;
    font-size: 12px;
    font-weight: 600;
}

#TitleButton:hover {
    background-color: #1e293b;
    color: #f8fafc;
}

#CloseTitleButton {
    background: transparent;
    border: none;
    color: #94a3b8;
    padding: 6px;
    min-width: 32px;
    border-radius: 6px;
    font-size: 14px;
}

#CloseTitleButton:hover {
    background-color: #ef4444;
    color: #ffffff;
}

/* Update Notification Banner */
#UpdateBanner {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #854d0e, stop:1 #ca8a04);
    color: #ffffff;
    border-radius: 8px;
    padding: 8px 14px;
    font-weight: bold;
    font-size: 12px;
    margin: 4px 10px 0px 10px;
}

#UpdateBanner:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #a16207, stop:1 #eab308);
}

/* Minimalist Master Hero Card */
#HeroCard {
    background-color: #111827;
    border: 1px solid #1f2937;
    border-radius: 14px;
    padding: 20px;
}

#HeroSpeed {
    color: #38bdf8;
    font-size: 42px;
    font-weight: 900;
    font-family: 'Segoe UI', Arial, sans-serif;
}

#HeroSpeedUnit {
    color: #94a3b8;
    font-size: 14px;
    font-weight: 600;
}

/* Master Power Button */
#MasterPowerBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #10b981);
    color: #ffffff;
    border: none;
    border-radius: 12px;
    font-size: 15px;
    font-weight: 800;
    padding: 12px 24px;
    min-height: 46px;
}

#MasterPowerBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #34d399);
}

#MasterPowerBtn[active="true"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #dc2626, stop:1 #ef4444);
}

#MasterPowerBtn[active="true"]:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ef4444, stop:1 #f87171);
}

/* Compact Metrics */
#MetricPill {
    background-color: #161e2e;
    border: 1px solid #243044;
    border-radius: 8px;
    padding: 8px 12px;
}

#MetricPillTitle {
    color: #94a3b8;
    font-size: 11px;
    font-weight: 600;
}

#MetricPillVal {
    color: #f8fafc;
    font-size: 14px;
    font-weight: 700;
}

/* Navigation Tabs */
QTabWidget::pane {
    border: 1px solid #1e293b;
    background-color: #0b0f19;
    border-radius: 10px;
    padding: 10px;
}

QTabBar::tab {
    background-color: #111827;
    color: #94a3b8;
    border: 1px solid #1e293b;
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 9px 18px;
    margin-right: 4px;
    font-weight: 600;
    font-size: 13px;
}

QTabBar::tab:selected {
    background-color: #1e293b;
    color: #38bdf8;
    border-bottom: 2px solid #0284c7;
}

QTabBar::tab:hover:!selected {
    background-color: #161e2e;
    color: #cbd5e1;
}

/* Buttons */
#PrimaryButton {
    background-color: #0284c7;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: bold;
    font-size: 12px;
    min-height: 34px;
}

#PrimaryButton:hover {
    background-color: #0369a1;
}

#SecondaryButton {
    background-color: #1e293b;
    color: #cbd5e1;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 500;
    font-size: 12px;
    min-height: 34px;
}

#SecondaryButton:hover {
    background-color: #334155;
    color: #f8fafc;
}

/* Status Banner */
#StatusBanner {
    background-color: #111827;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 10px 14px;
}

#StatusText {
    font-size: 13px;
    font-weight: 600;
    color: #38bdf8;
}

/* Form Controls */
QComboBox {
    background-color: #111827;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 6px 12px;
    color: #f8fafc;
    min-height: 32px;
}

QComboBox:hover {
    border-color: #0284c7;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #111827;
    border: 1px solid #334155;
    border-radius: 8px;
    color: #f8fafc;
    selection-background-color: #0284c7;
}

QSpinBox, QLineEdit {
    background-color: #111827;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 6px 10px;
    color: #f8fafc;
    min-height: 30px;
}

QSpinBox:hover, QLineEdit:hover {
    border-color: #0284c7;
}

QSpinBox:focus, QLineEdit:focus {
    border-color: #38bdf8;
}

QCheckBox {
    color: #cbd5e1;
    spacing: 8px;
    font-size: 12px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #334155;
    border-radius: 4px;
    background-color: #111827;
}

QCheckBox::indicator:hover {
    border-color: #0284c7;
}

QCheckBox::indicator:checked {
    background-color: #0284c7;
    border-color: #38bdf8;
}

/* Scroll Area */
QScrollArea {
    border: none;
    background-color: transparent;
}

QScrollBar:vertical {
    background-color: #0b0f19;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #1e293b;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #334155;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Event Log List */
#LogList {
    background-color: #0b0f19;
    border: 1px solid #1e293b;
    border-radius: 8px;
    color: #94a3b8;
    font-family: 'Segoe UI', 'Consolas', monospace;
    font-size: 12px;
    padding: 8px;
}

QListWidget::item {
    padding: 6px 8px;
    border-radius: 6px;
    margin-bottom: 2px;
}

QListWidget::item:hover {
    background-color: #111827;
}
"""
