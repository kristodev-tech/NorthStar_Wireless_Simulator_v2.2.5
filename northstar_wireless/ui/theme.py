from pathlib import Path
from ..services.paths import resource_path

DARK_QSS = """
QWidget {
    background: #0f1116;
    color: #e8e8e8;
    font-size: 12px;
}

/* ── Scroll Areas / Scrollbars ───────────────────────────────────────────── */
QScrollArea { border: none; background: transparent; }
QScrollArea > QWidget > QWidget { background: transparent; } /* viewport chain */

QFrame#HeatLegendBar {
    border: 1px solid #2a3550;
    border-radius: 3px;
}

QScrollBar:vertical {
    background: #0f1116;
    width: 10px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background: #2a3550;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #3a4a70; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }

/* (Optional) horizontal scrollbar hidden, but keep consistent if it appears */
QScrollBar:horizontal {
    background: #0f1116;
    height: 10px;
    margin: 2px;
}
QScrollBar::handle:horizontal {
    background: #2a3550;
    border-radius: 5px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover { background: #3a4a70; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; }
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: none; }

/* ── Main Window / Layout ───────────────────────────────────────────────── */
QMainWindow::separator { background: #1b1f2a; width: 1px; height: 1px; }

QFrame#Card {
    background: #151923;
    border: 1px solid #232a3a;
    border-radius: 10px;
}

/* ── Group Boxes ────────────────────────────────────────────────────────── */
QGroupBox {
    border: 1px solid #232a3a;
    border-radius: 10px;
    margin-top: 10px;
    padding: 10px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 6px;
    color: #b9c2d3;
}

/* ── Buttons ───────────────────────────────────────────────────────────── */
QPushButton {
    background: #1b2333;
    border: 1px solid #2a3550;
    border-radius: 8px;
    padding: 7px 10px;
}
QPushButton:hover { background: #222d42; }
QPushButton:pressed { background: #182235; }
QPushButton:disabled {
    color: #6a7283;
    border: 1px solid #242b3a;
    background: #141824;
}

/* ── Inputs ────────────────────────────────────────────────────────────── */
QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit {
    background: #121622;
    border: 1px solid #2a3550;
    border-radius: 7px;
    padding: 4px 8px;
}

QComboBox::drop-down { border: 0px; }
QComboBox QAbstractItemView {
    background: #121622;
    border: 1px solid #2a3550;
    selection-background-color: #222d42;
    selection-color: #e8e8e8;
}

/* ── SpinBox arrow buttons (prevents tiny/unusable chevrons) ─────────────── */
QSpinBox::up-button, QSpinBox::down-button {
    subcontrol-origin: border;
    width: 18px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background: #222d42;
}

/* ── Dock Widgets (if you use them later) ───────────────────────────────── */
QDockWidget {
    titlebar-close-icon: none;
    titlebar-normal-icon: none;
}
QDockWidget::title {
    background: #121622;
    border-bottom: 1px solid #232a3a;
    padding: 6px;
}

/* ── Labels ─────────────────────────────────────────────────────────────── */
QLabel#Dim { color: #9aa3b5; }
"""


def app_stylesheet():
    checked = Path(resource_path("assets/ui/check_checked.png")).as_posix()
    disabled = Path(resource_path("assets/ui/check_disabled.png")).as_posix()
    return (
        DARK_QSS
        + """
QLabel { background: transparent; }
QCheckBox { spacing: 9px; padding: 3px 0; }
QCheckBox::indicator { width: 20px; height: 20px; border: 1px solid #8795ac; border-radius: 4px; background: #101621; }
QCheckBox::indicator:unchecked { image: none; }
QCheckBox::indicator:hover { border: 2px solid #70d8ec; }
QCheckBox::indicator:checked { border: none; image: url("__CHECKED__"); }
QCheckBox::indicator:checked:disabled { border: none; image: url("__DISABLED__"); }
QCheckBox::indicator:unchecked:disabled { border-color: #4c5665; background: #1c222c; }
QCheckBox:focus { color: #86e1f2; }
QPushButton:checked { background: #18566c; border: 2px solid #70d8ec; color: white; }
QPushButton:focus { border-color: #8ee0f1; }
QMenu::indicator { width: 18px; height: 18px; }
QMenu::indicator:checked { image: url("__CHECKED__"); }
QFrame#GuideCard { background: #151923; border: 1px solid #293b54; border-radius: 10px; }
QLabel#StepHint { color: #bbcbdc; }
""".replace("__CHECKED__", checked).replace("__DISABLED__", disabled)
    )
