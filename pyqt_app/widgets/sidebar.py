"""
pyqt_app/widgets/sidebar.py
Sidebar navigation widget — matches the Figma mockup.
"""
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QSizePolicy, QSpacerItem, QWidget
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap, QFont, QCursor
import os

from pyqt_app.styles.theme import palette, FONT_FAMILY


class SidebarWidget(QFrame):
    """Left sidebar with logo, nav items, pro card, and bottom links."""

    navigate = pyqtSignal(str)  # emitted with nav key

    NAV_ITEMS = [
        ("dashboard",   "\U0001f3e0", "menu_dashboard"),
        ("eksplorasi",  "\U0001f4da", "menu_scholarships"),
        ("rekomendasi", "\u2728",     "menu_recom"),
        ("bookmarks",   "\U0001f516", "menu_bookmarks"),
        ("kalender",    "\U0001f4c5", "menu_calendar"),
        ("notifikasi",  "\U0001f514", "menu_notif"),
        ("profil",      "\U0001f464", "menu_profile"),
    ]

    BOTTOM_ITEMS = [
        ("settings", "\u2699", "menu_settings"),
        ("bantuan",  "\u2753", "menu_help"),
    ]

    def __init__(self, t_func, bhs="id", parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(210)
        self._t = t_func
        self._bhs = bhs
        self._buttons: dict[str, QPushButton] = {}
        self._active_key = ""
        self._build()

    # ── Build ────────────────────────────────────────────────
    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Logo
        logo_frame = QFrame()
        logo_lay = QHBoxLayout(logo_frame)
        logo_lay.setContentsMargins(16, 18, 16, 12)
        try:
            logo_path = os.path.abspath(os.path.join(
                os.path.dirname(__file__), "..", "..", "assets", "logo_beaply.png"))
            pix = QPixmap(logo_path).scaled(
                200, 100, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            logo_lbl = QLabel()
            logo_lbl.setPixmap(pix)
            logo_lay.addWidget(logo_lbl)
        except Exception:
            logo_lbl = QLabel("beaply")
            logo_lbl.setFont(QFont(FONT_FAMILY, 28, QFont.Weight.Bold))
            logo_lbl.setStyleSheet("color: #D4917B;")
            logo_lay.addWidget(logo_lbl)
        layout.addWidget(logo_frame)

        # Nav items
        nav_frame = QFrame()
        nav_lay = QVBoxLayout(nav_frame)
        nav_lay.setContentsMargins(10, 0, 10, 0)
        nav_lay.setSpacing(2)
        for key, icon, lbl_key in self.NAV_ITEMS:
            btn = self._make_nav_btn(key, icon, lbl_key, "nav-btn")
            nav_lay.addWidget(btn)
        layout.addWidget(nav_frame)

        layout.addStretch(1)

        # Bottom items
        bot_frame = QFrame()
        bot_lay = QVBoxLayout(bot_frame)
        bot_lay.setContentsMargins(10, 4, 10, 10)
        bot_lay.setSpacing(2)
        for key, icon, lbl_key in self.BOTTOM_ITEMS:
            btn = self._make_nav_btn(key, icon, lbl_key, "nav-btn-bottom")
            bot_lay.addWidget(btn)
        layout.addWidget(bot_frame)

    def _make_nav_btn(self, key, icon, lbl_key, css_class):
        label = self._t(lbl_key, self._bhs)
        btn = QPushButton(f"  {icon}  {label}")
        btn.setProperty("class", css_class)
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn.setFixedHeight(36)
        btn.clicked.connect(lambda _, k=key: self._on_click(k))
        self._buttons[key] = btn
        return btn

    def _build_pro_card(self):
        card = QFrame()
        card.setStyleSheet("""
            QFrame { background: #E8F0EA; border-radius: 14px; }
        """)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(2)
        lbl1 = QLabel("Upgrade to")
        lbl1.setStyleSheet("font-size: 9px; color: #888;")
        lbl1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(lbl1)
        lbl2 = QLabel("Beaply Pro")
        lbl2.setFont(QFont(FONT_FAMILY, 13, QFont.Weight.Bold))
        lbl2.setStyleSheet("color: #2D6A4F;")
        lbl2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(lbl2)
        lbl3 = QLabel("Unlock premium features\nand scholarship matches\ntailored just for you.")
        lbl3.setStyleSheet("font-size: 8px; color: #888;")
        lbl3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl3.setWordWrap(True)
        lay.addWidget(lbl3)
        btn = QPushButton("Upgrade Now >")
        btn.setObjectName("btn_small_primary")
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn.setFixedHeight(28)
        lay.addWidget(btn)
        wrapper = QFrame()
        wl = QVBoxLayout(wrapper)
        wl.setContentsMargins(10, 0, 10, 8)
        wl.addWidget(card)
        return wrapper

    # ── Public ───────────────────────────────────────────────
    def set_active(self, key: str):
        self._active_key = key
        for k, btn in self._buttons.items():
            btn.setProperty("active", "true" if k == key else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def set_language(self, bhs: str):
        self._bhs = bhs
        for key, icon, lbl_key in self.NAV_ITEMS + self.BOTTOM_ITEMS:
            btn = self._buttons.get(key)
            if btn:
                btn.setText(f"  {icon}  {self._t(lbl_key, bhs)}")

    def _on_click(self, key: str):
        self.navigate.emit(key)
