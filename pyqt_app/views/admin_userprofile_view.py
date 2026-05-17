"""
pyqt_app/views/admin_userprofile_view.py
Admin — User Profile management page.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor, QPixmap
import os

from pyqt_app.styles.theme import FONT_FAMILY, palette
from controllers.admin_controller import get_all_users, delete_user


class AdminUserProfileView(QWidget):
    def __init__(self, mode="light", parent=None):
        super().__init__(parent)
        self._mode = mode
        self._init_layout()

    def _init_layout(self):
        """Create outer layout once — never deleted."""
        self._outer = QVBoxLayout(self)
        self._outer.setContentsMargins(0, 0, 0, 0)
        self._outer.setSpacing(0)
        self._container = QWidget()
        self._outer.addWidget(self._container)
        self._populate()

    def _populate(self):
        c = palette(self._mode)
        root = QVBoxLayout(self._container)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        section = QLabel("User Data")
        section.setFont(QFont(FONT_FAMILY, 16, QFont.Weight.Bold))
        root.addWidget(section)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        sw = QWidget()
        sl = QVBoxLayout(sw)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.setSpacing(8)

        users = get_all_users()
        if not users:
            empty = QLabel("No users found.")
            empty.setStyleSheet(f"color: {c['text_muted']}; font-size: 13px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sl.addWidget(empty)
        else:
            for user in users:
                sl.addWidget(self._make_user_card(user, c))

        sl.addStretch()
        scroll.setWidget(sw)
        root.addWidget(scroll, 1)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        save_btn = QPushButton("Save  Changes")
        save_btn.setFixedHeight(40)
        save_btn.setFixedWidth(160)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {c['btn_primary']};
                color: {c['text_dark']};
                border: none; border-radius: 10px;
                font-weight: bold; font-size: 13px;
            }}
            QPushButton:hover {{ background: {c['btn_primary_hover']}; }}
        """)
        save_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        save_btn.clicked.connect(lambda: QMessageBox.information(self, "Info", "Changes saved!"))
        btn_row.addWidget(save_btn)
        root.addLayout(btn_row)

    def _make_user_card(self, user: dict, c: dict) -> QFrame:
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: #F5FAF6;
                border: 1.5px solid #D6EAD8;
                border-radius: 12px;
            }
        """)
        card.setFixedHeight(80)
        lay = QHBoxLayout(card)
        lay.setContentsMargins(16, 10, 10, 10)
        lay.setSpacing(14)

        # Avatar
        ava_lbl = QLabel()
        ava_lbl.setFixedSize(52, 52)
        ava_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ava_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), "..", "..", "assets", "default_avatar.png"))
        if os.path.exists(ava_path):
            pix = QPixmap(ava_path).scaled(
                48, 48, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            ava_lbl.setPixmap(pix)
            ava_lbl.setStyleSheet("background: #F0D8C8; border-radius: 26px; border: none;")
        else:
            ava_lbl.setText("\U0001f464")
            ava_lbl.setStyleSheet("background: #F0D8C8; border-radius: 26px; border: none; font-size: 22px;")
        lay.addWidget(ava_lbl)

        # Info
        info = QFrame()
        info.setStyleSheet("border: none; background: transparent;")
        il = QVBoxLayout(info)
        il.setContentsMargins(0, 0, 0, 0)
        il.setSpacing(2)
        n = QLabel(user.get("nama_lengkap", "Unknown"))
        n.setFont(QFont(FONT_FAMILY, 13, QFont.Weight.Bold))
        n.setStyleSheet(f"color: {c['text_dark']}; border: none; background: transparent;")
        il.addWidget(n)
        e = QLabel(user.get("email", ""))
        e.setStyleSheet(f"color: {c['text_muted']}; font-size: 11px; border: none; background: transparent;")
        il.addWidget(e)
        lay.addWidget(info, 1)

        # Buttons
        bc = QVBoxLayout()
        bc.setSpacing(4)
        bc.setContentsMargins(0, 0, 0, 0)
        eb = QPushButton("\U0001f4cb")
        eb.setFixedSize(36, 30)
        eb.setStyleSheet(f"QPushButton {{ background: {c['btn_primary']}; border: none; border-radius: 6px; font-size: 15px; }} QPushButton:hover {{ background: {c['btn_primary_hover']}; }}")
        eb.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        bc.addWidget(eb)
        db = QPushButton("\U0001f5d1")
        db.setFixedSize(36, 30)
        db.setStyleSheet(f"QPushButton {{ background: {c['danger_bg']}; border: none; border-radius: 6px; font-size: 15px; }} QPushButton:hover {{ background: #F5D0D0; }}")
        db.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        uid = user.get("id")
        db.clicked.connect(lambda _, u=uid: self._del(u))
        bc.addWidget(db)
        lay.addLayout(bc)
        return card

    def _del(self, uid):
        r = QMessageBox.question(self, "Delete", "Delete this user?")
        if r == QMessageBox.StandardButton.Yes:
            ok, msg = delete_user(uid)
            if ok:
                QMessageBox.information(self, "Success", msg)
                self._rebuild()
            else:
                QMessageBox.critical(self, "Error", msg)

    def _rebuild(self):
        """Replace container with fresh one."""
        old = self._container
        self._outer.removeWidget(old)
        old.deleteLater()
        self._container = QWidget()
        self._outer.addWidget(self._container)
        self._populate()
