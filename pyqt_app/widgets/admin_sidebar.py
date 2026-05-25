"""
pyqt_app/widgets/admin_sidebar.py
Admin sidebar — different nav items for admin panel.
"""
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QSizePolicy, QSpacerItem, QWidget
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap, QFont, QCursor
import os

from pyqt_app.styles.theme import palette, FONT_FAMILY


class AdminSidebarWidget(QFrame):
    """Left sidebar for admin panel with admin-specific navigation."""

    navigate = pyqtSignal(str)  # emitted with nav key

    NAV_ITEMS = [
        ("admin_scholarships", "\U0001f4da", "Scholarships"),
        ("admin_users",        "\U0001f464", "User Profile"),
        ("admin_helpcenter",   "\u2753",     "Help Center"),
        ("admin_settings",     "\u2699",     "Settings"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(210)
        self._buttons: dict[str, QPushButton] = {}
        self._active_key = ""
        self._build()

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
                110, 55, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            logo_lbl = QLabel()
            logo_lbl.setPixmap(pix)
            logo_lay.addWidget(logo_lbl)
        except Exception:
            logo_lbl = QLabel("beaply")
            logo_lbl.setFont(QFont(FONT_FAMILY, 22, QFont.Weight.Bold))
            logo_lbl.setStyleSheet("color: #D4917B;")
            logo_lay.addWidget(logo_lbl)
        layout.addWidget(logo_frame)

        # Nav items
        nav_frame = QFrame()
        nav_lay = QVBoxLayout(nav_frame)
        nav_lay.setContentsMargins(10, 0, 10, 0)
        nav_lay.setSpacing(2)
        for key, icon, label in self.NAV_ITEMS:
            btn = self._make_nav_btn(key, icon, label)
            nav_lay.addWidget(btn)
        layout.addWidget(nav_frame)

        layout.addStretch(1)

    def _make_nav_btn(self, key, icon, label):
        btn = QPushButton(f"  {icon}  {label}")
        btn.setProperty("class", "nav-btn")
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn.setFixedHeight(36)
        btn.clicked.connect(lambda _, k=key: self._on_click(k))
        self._buttons[key] = btn
        return btn

    def set_active(self, key: str):
        self._active_key = key
        for k, btn in self._buttons.items():
            btn.setProperty("active", "true" if k == key else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _on_click(self, key: str):
        self.navigate.emit(key)
