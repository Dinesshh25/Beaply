"""
pyqt_app/widgets/topbar.py
Top bar widget — page title, bell icon, user avatar + name.
"""
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont, QPixmap, QCursor
import os

from pyqt_app.styles.theme import FONT_FAMILY


class TopbarWidget(QFrame):
    """Top bar with page title (left), bell icon + user info (right)."""

    bell_clicked = pyqtSignal()
    avatar_clicked = pyqtSignal()

    def __init__(self, user_name: str = "Guest", parent=None):
        super().__init__(parent)
        self.setObjectName("topbar")
        self.setFixedHeight(60)
        self._user_name = user_name
        self._build()

    def _build(self):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        # Page title
        self.title_label = QLabel("Dashboard")
        self.title_label.setObjectName("title")
        self.title_label.setFont(QFont(FONT_FAMILY, 20, QFont.Weight.Bold))
        lay.addWidget(self.title_label)

        lay.addStretch(1)

        # Bell
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

        # Avatar
        ava_frame = QFrame()
        ava_frame.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        ava_lay = QHBoxLayout(ava_frame)
        ava_lay.setContentsMargins(8, 0, 0, 0)
        ava_lay.setSpacing(8)
        try:
            ava_path = os.path.abspath(os.path.join(
                os.path.dirname(__file__), "..", "..", "assets", "default_avatar.png"))
            pix = QPixmap(ava_path).scaled(
                40, 40, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            ava_lbl = QLabel()
            ava_lbl.setPixmap(pix)
            ava_lbl.setFixedSize(40, 40)
        except Exception:
            ava_lbl = QLabel("O")
            ava_lbl.setFont(QFont(FONT_FAMILY, 20))
            ava_lbl.setFixedSize(40, 40)
            ava_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ava_lay.addWidget(ava_lbl)

        text_frame = QFrame()
        text_lay = QVBoxLayout(text_frame)
        text_lay.setContentsMargins(0, 0, 0, 0)
        text_lay.setSpacing(0)
        name_lbl = QLabel(self._user_name)
        name_lbl.setFont(QFont(FONT_FAMILY, 12, QFont.Weight.Bold))
        text_lay.addWidget(name_lbl)
        role_lbl = QLabel("Student")
        role_lbl.setObjectName("muted")
        text_lay.addWidget(role_lbl)
        ava_lay.addWidget(text_frame)

        ava_frame.mousePressEvent = lambda e: self.avatar_clicked.emit()
        lay.addWidget(ava_frame)

    def set_title(self, title: str):
        self.title_label.setText(title)

    def set_user_name(self, name: str):
        self._user_name = name
