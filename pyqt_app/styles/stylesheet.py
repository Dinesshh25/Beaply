"""
pyqt_app/styles/stylesheet.py
Beaply – Global QSS stylesheet builder for PyQt6.
"""
from .theme import palette, FONT_FAMILY


def build_stylesheet(mode: str = "light") -> str:
    """Return full QSS string for the given *mode*."""
    c = palette(mode)
    return f"""
/* ══════════════════════════════════════════════
   GLOBAL
   ══════════════════════════════════════════════ */
* {{
    font-family: "{FONT_FAMILY}";
    outline: none;
}}
QMainWindow, QWidget#central {{
    background-color: {c['bg']};
}}

/* ── Scrollbars ─────────────────────────────── */
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {c['border']};
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{
    background: {c['text_muted']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
    height: 0;
}}
QScrollBar:horizontal {{
    height: 0;
}}

/* ── Cards ──────────────────────────────────── */
QFrame[frameClass="card"] {{
    background-color: {c['card']};
    border: 1px solid {c['border']};
    border-radius: 14px;
}}
QFrame[frameClass="card"]:hover {{
    border-color: {c['btn_primary']};
}}

/* ── Sidebar ────────────────────────────────── */
QFrame#sidebar {{
    background-color: {c['sidebar_bg']};
    border-right: 1px solid {c['border']};
}}
QPushButton.nav-btn {{
    background-color: transparent;
    color: {c['text_dark']};
    border: none;
    border-radius: 10px;
    padding: 8px 14px;
    text-align: left;
    font-size: 12px;
}}
QPushButton.nav-btn:hover {{
    background-color: {c['btn_pale']};
}}
QPushButton.nav-btn[active="true"] {{
    background-color: {c['sidebar_active_bg']};
    color: {c['sidebar_active_tx']};
    font-weight: bold;
}}
QPushButton.nav-btn-bottom {{
    background-color: transparent;
    color: {c['text_muted']};
    border: none;
    border-radius: 8px;
    padding: 6px 14px;
    text-align: left;
    font-size: 12px;
}}
QPushButton.nav-btn-bottom:hover {{
    background-color: {c['btn_pale']};
}}
QPushButton.nav-btn-bottom[active="true"] {{
    background-color: {c['sidebar_active_bg']};
    color: {c['sidebar_active_tx']};
    font-weight: bold;
}}

/* ── Buttons ────────────────────────────────── */
QPushButton#btn_primary {{
    background-color: {c['btn_primary']};
    color: {c['text_dark']};
    border: none;
    border-radius: 12px;
    padding: 10px 24px;
    font-weight: bold;
    font-size: 13px;
}}
QPushButton#btn_primary:hover {{
    background-color: {c['btn_primary_hover']};
}}
QPushButton#btn_outline {{
    background-color: transparent;
    color: {c['text_dark']};
    border: 1px solid {c['border']};
    border-radius: 12px;
    padding: 10px 24px;
    font-size: 13px;
}}
QPushButton#btn_outline:hover {{
    background-color: {c['btn_pale']};
}}
QPushButton#btn_danger {{
    background-color: transparent;
    color: {c['danger']};
    border: 2px solid {c['danger']};
    border-radius: 12px;
    padding: 10px 24px;
    font-weight: bold;
    font-size: 13px;
}}
QPushButton#btn_danger:hover {{
    background-color: {c['danger_bg']};
}}
QPushButton#btn_link {{
    background: transparent;
    color: {c['text_accent']};
    border: none;
    font-size: 11px;
    padding: 4px;
}}
QPushButton#btn_link:hover {{
    text-decoration: underline;
}}
QPushButton#btn_small_primary {{
    background-color: {c['btn_primary']};
    color: {c['text_dark']};
    border: none;
    border-radius: 8px;
    padding: 5px 14px;
    font-size: 11px;
    font-weight: bold;
}}
QPushButton#btn_small_primary:hover {{
    background-color: {c['btn_primary_hover']};
}}

/* ── Inputs ─────────────────────────────────── */
QLineEdit {{
    background-color: {c['input_bg']};
    color: {c['text_dark']};
    border: none;
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 13px;
}}
QLineEdit:focus {{
    border: 2px solid {c['btn_primary']};
}}
QTextEdit {{
    background-color: {c['card']};
    color: {c['text_dark']};
    border: 1px solid {c['border']};
    border-radius: 10px;
    padding: 8px;
    font-size: 12px;
}}
QComboBox {{
    background-color: {c['card']};
    color: {c['text_dark']};
    border: 1px solid {c['border']};
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 12px;
    min-height: 28px;
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox QAbstractItemView {{
    background-color: {c['card']};
    color: {c['text_dark']};
    border: 1px solid {c['border']};
    selection-background-color: {c['btn_pale']};
    selection-color: {c['text_dark']};
}}

/* ── Labels ─────────────────────────────────── */
QLabel {{
    color: {c['text_dark']};
    background: transparent;
}}
QLabel#title {{
    font-size: 22px;
    font-weight: bold;
}}
QLabel#subtitle {{
    font-size: 12px;
    color: {c['text_muted']};
}}
QLabel#section_title {{
    font-size: 16px;
    font-weight: bold;
}}
QLabel#accent {{
    color: {c['text_accent']};
    font-weight: bold;
}}
QLabel#muted {{
    color: {c['text_muted']};
    font-size: 11px;
}}
QLabel#error {{
    color: #FF3B30;
    font-size: 11px;
}}

/* ── Topbar ─────────────────────────────────── */
QFrame#topbar {{
    background: transparent;
}}

/* ── Scroll Area ────────────────────────────── */
QScrollArea {{
    background: transparent;
    border: none;
}}
QScrollArea > QWidget > QWidget {{
    background: transparent;
}}

/* ── Checkbox / Switch ──────────────────────── */
QCheckBox {{
    color: {c['text_dark']};
    font-size: 12px;
    spacing: 8px;
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {c['border']};
    border-radius: 4px;
    background: {c['card']};
}}
QCheckBox::indicator:checked {{
    background: {c['btn_primary']};
    border-color: {c['btn_primary']};
}}

/* ── Radio ──────────────────────────────────── */
QRadioButton {{
    color: {c['text_dark']};
    font-size: 12px;
    spacing: 8px;
}}
QRadioButton::indicator {{
    width: 16px;
    height: 16px;
    border: 2px solid {c['border']};
    border-radius: 8px;
    background: {c['card']};
}}
QRadioButton::indicator:checked {{
    background: {c['btn_primary']};
    border-color: {c['btn_primary']};
}}

/* ── ToolTip ────────────────────────────────── */
QToolTip {{
    background-color: {c['card']};
    color: {c['text_dark']};
    border: 1px solid {c['border']};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 11px;
}}
"""
