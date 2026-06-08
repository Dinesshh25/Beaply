"""
pyqt_app/views/admin_userprofile_view.py
Admin — User Profile management page.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QMessageBox, QDialog, QLineEdit, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor, QPixmap, QColor, QPainter, QLinearGradient
import os

from pyqt_app.styles.theme import FONT_FAMILY, palette
from controllers.admin_controller import get_all_users, delete_user, update_user

def show_custom_msgbox(parent, title, text, c, icon=QMessageBox.Icon.Information, is_question=False):
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.setIcon(icon)
    if is_question:
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    msg.setStyleSheet(f"QMessageBox {{ background-color: {c['card']}; }} QLabel {{ color: {c['text_dark']}; }} QPushButton {{ background: {c['btn_pale']}; color: {c['text_dark']}; border-radius: 4px; padding: 4px 12px; min-width: 60px; }}")
    return msg.exec()

class EditUserDialog(QDialog):
    def __init__(self, user, mode, parent=None):
        super().__init__(parent)
        self.user = user
        self.mode = mode
        self._c = palette(mode)
        
        self.setWindowTitle("Edit User")
        self.setFixedSize(400, 320)
        self.setStyleSheet("QDialog { background: transparent; }")
        
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(20, 20, 20, 20)
        
        self.content_frame = QFrame()
        _content_bg = 'rgba(255, 255, 255, 0.85)' if self.mode == 'light' else f'rgba(41, 42, 45, 0.95)'
        self.content_frame.setStyleSheet(f"QFrame {{ background-color: {_content_bg}; border-radius: 20px; }} QLabel {{ background: transparent; color: {self._c['text_dark']}; }}")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        self.content_frame.setGraphicsEffect(shadow)
        
        dl = QVBoxLayout(self.content_frame)
        dl.setContentsMargins(24, 20, 24, 20)
        dl.setSpacing(12)
        
        title = QLabel("Edit User")
        title.setFont(QFont(FONT_FAMILY, 15, QFont.Weight.Bold))
        dl.addWidget(title)
        
        self.fields = {}
        for label, key, val in [
            ("Name", "nama_lengkap", user.get("nama_lengkap", "")),
            ("Email", "email", user.get("email", "")),
        ]:
            lbl = QLabel(label)
            lbl.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Bold))
            dl.addWidget(lbl)
            inp = QLineEdit(str(val) if val else "")
            inp.setFixedHeight(38)
            inp.setStyleSheet(f"""
                QLineEdit {{
                    padding: 8px 14px;
                    font-size: 13px;
                    background: {self._c['input_bg']};
                    color: {self._c['text_dark']};
                    border: none;
                    border-radius: 10px;
                }}
                QLineEdit:focus {{
                    border: 2px solid {self._c['btn_primary']};
                }}
            """)
            dl.addWidget(inp)
            self.fields[key] = inp
            
        dl.addStretch()
        
        save = QPushButton("Save Changes")
        save.setFixedHeight(40)
        save.setStyleSheet(f"""
            QPushButton {{
                background: {self._c['btn_primary']};
                color: {self._c['text_dark']};
                border: none; border-radius: 10px;
                font-weight: bold; font-size: 13px;
            }}
            QPushButton:hover {{ background: {self._c['btn_primary_hover']}; }}
        """)
        save.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        save.clicked.connect(self.accept)
        dl.addWidget(save)
        
        main_lay.addWidget(self.content_frame)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        grad = QLinearGradient(0, 0, self.width(), self.height())
        grad.setColorAt(0.0, QColor(self._c.get('grad_peach_start', '#F7D0B7')))
        grad.setColorAt(1.0, QColor(self._c.get('grad_green_start', '#D6EAD8')))
        painter.fillRect(self.rect(), grad)
        painter.end()
        super().paintEvent(event)


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
        if self._mode == "dark":
            bg_color = "#1E2A22"
            border_color = "#2D6B3E"
        else:
            bg_color = "#F5FAF6"
            border_color = "#D6EAD8"

        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {bg_color};
                border: 1.5px solid {border_color};
                border-radius: 12px;
            }}
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
        eb.clicked.connect(lambda _, u=user: self._edit_user(u))
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

    def _edit_user(self, user: dict):
        dlg = EditUserDialog(user, self._mode, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            nama = dlg.fields["nama_lengkap"].text().strip()
            email = dlg.fields["email"].text().strip()
            c = palette(self._mode)
            if not nama or not email:
                show_custom_msgbox(self, "Warning", "Name and email cannot be empty.", c, QMessageBox.Icon.Warning)
                return
            ok, msg = update_user(user.get("id"), nama, email)
            if ok:
                show_custom_msgbox(self, "Success", msg, c, QMessageBox.Icon.Information)
                self._rebuild()
            else:
                show_custom_msgbox(self, "Error", msg, c, QMessageBox.Icon.Critical)

    def _del(self, uid):
        c = palette(self._mode)
        r = show_custom_msgbox(self, "Delete", "Delete this user?", c, QMessageBox.Icon.Question, True)
        if r == QMessageBox.StandardButton.Yes:
            ok, msg = delete_user(uid)
            if ok:
                show_custom_msgbox(self, "Success", msg, c, QMessageBox.Icon.Information)
                self._rebuild()
            else:
                show_custom_msgbox(self, "Error", msg, c, QMessageBox.Icon.Critical)

    def _rebuild(self):
        """Replace container with fresh one."""
        old = self._container
        self._outer.removeWidget(old)
        old.deleteLater()
        self._container = QWidget()
        self._outer.addWidget(self._container)
        self._populate()
