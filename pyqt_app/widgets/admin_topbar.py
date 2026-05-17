"""
pyqt_app/widgets/admin_topbar.py
Admin top bar — page title + Anonymous/Admin avatar (right side).
"""
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont, QPixmap, QCursor
import os

from pyqt_app.styles.theme import FONT_FAMILY


class AdminTopbarWidget(QFrame):
    """Top bar for admin panel: page title (left), bell (optional), user info (right)."""

    bell_clicked = pyqtSignal()

    def __init__(self, user_name: str = "Anonymous", show_bell: bool = False, parent=None):
        super().__init__(parent)
        self.setObjectName("topbar")
        self.setFixedHeight(60)
        self._user_name = user_name
        self._show_bell = show_bell
        self._build()

    def _build(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        # Page title (left side)
        self._title_frame = QFrame()
        title_lay = QVBoxLayout(self._title_frame)
        title_lay.setContentsMargins(0, 0, 0, 0)
        title_lay.setSpacing(0)

        self.title_label = QLabel("Scholarship Data")
        self.title_label.setObjectName("title")
        self.title_label.setFont(QFont(FONT_FAMILY, 20, QFont.Weight.Bold))
        title_lay.addWidget(self.title_label)

        self.subtitle_label = QLabel("")
        self.subtitle_label.setObjectName("muted")
        self.subtitle_label.setVisible(False)
        title_lay.addWidget(self.subtitle_label)

        lay.addWidget(self._title_frame)
        lay.addStretch(1)

        # Bell (optional, shown only on Help Center)
        if self._show_bell:
            bell = QPushButton("\U0001f514")
            bell.setFixedSize(36, 36)
            bell.setStyleSheet("""
                QPushButton {
                    background: transparent; border: none; font-size: 18px;
                    border-radius: 18px;
                }
                QPushButton:hover { background: #E2EBE5; }
            """)
            bell.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            bell.clicked.connect(self.bell_clicked.emit)
            lay.addWidget(bell)

        # Avatar + name
        ava_frame = QFrame()
        ava_lay = QHBoxLayout(ava_frame)
        ava_lay.setContentsMargins(8, 0, 0, 0)
        ava_lay.setSpacing(8)

        # Circle avatar placeholder
        ava_lbl = QLabel()
        ava_lbl.setFixedSize(40, 40)
        ava_lbl.setStyleSheet("""
            background: #D9D9D9;
            border-radius: 20px;
        """)
        ava_lay.addWidget(ava_lbl)

        text_frame = QFrame()
        text_lay = QVBoxLayout(text_frame)
        text_lay.setContentsMargins(0, 0, 0, 0)
        text_lay.setSpacing(0)
        name_lbl = QLabel(self._user_name)
        name_lbl.setFont(QFont(FONT_FAMILY, 12, QFont.Weight.Bold))
        text_lay.addWidget(name_lbl)
        role_lbl = QLabel("Admin")
        role_lbl.setObjectName("muted")
        text_lay.addWidget(role_lbl)
        ava_lay.addWidget(text_frame)

        # Dropdown arrow
        arrow = QLabel("⌄")
        arrow.setStyleSheet("color: #888; font-size: 14px;")
        ava_lay.addWidget(arrow)

        lay.addWidget(ava_frame)

    def set_title(self, title: str, subtitle: str = ""):
        self.title_label.setText(title)
        if subtitle:
            self.subtitle_label.setText(subtitle)
            self.subtitle_label.setVisible(True)
        else:
            self.subtitle_label.setVisible(False)

    def set_bell_visible(self, visible: bool):
        """Show/hide bell. Rebuilds if needed."""
        pass  # Bell visibility is set at construction time
