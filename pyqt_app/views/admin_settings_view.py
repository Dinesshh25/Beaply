"""
pyqt_app/views/admin_settings_view.py
Admin — Standalone Settings page.

Does NOT inherit from SettingsView to avoid profil_id dependency.
Admin has simpler settings: theme toggle, logout.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor

from pyqt_app.styles.theme import FONT_FAMILY, palette
from pyqt_app.views.auth_view import clear_session


class AdminSettingsView(QWidget):
    """Standalone admin settings — no profil_id dependency."""

    def __init__(self, mode="light", refresh_cb=None, parent=None):
        super().__init__(parent)
        self._mode = mode
        self._refresh_cb = refresh_cb
        self._refreshing = False
        self._build()

    def _build(self):
        c = palette(self._mode)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        sw = QWidget()
        sl = QVBoxLayout(sw)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.setSpacing(12)

        sub = QLabel("Manage admin panel preferences")
        sub.setObjectName("subtitle")
        sl.addWidget(sub)

        # ── Account & Security ───────────────────────────────
        sl.addWidget(self._section("Account & Security"))
        sec = QFrame()
        sec.setProperty("frameClass", "card")
        secl = QVBoxLayout(sec)
        secl.setContentsMargins(20, 14, 20, 14)

        lo_row = QFrame()
        lol = QHBoxLayout(lo_row)
        lol.setContentsMargins(0, 0, 0, 0)
        lol_left = QFrame()
        loll = QVBoxLayout(lol_left)
        loll.setContentsMargins(0, 0, 0, 0)
        loll.setSpacing(0)
        loll.addWidget(self._bold("Logout", 12))
        loll.addWidget(self._muted("Sign out of admin panel"))
        lol.addWidget(lol_left)
        lol.addStretch()
        lob = QPushButton("Logout")
        lob.setStyleSheet(
            f"background: #F6D6D0; color: {c['danger']}; border: none; "
            f"border-radius: 8px; padding: 6px 16px; font-size: 11px; font-weight: bold;"
        )
        lob.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        lob.clicked.connect(self._logout)
        lol.addWidget(lob)
        secl.addWidget(lo_row)

        sl.addWidget(sec)

        # ── Display ──────────────────────────────────────────
        sl.addWidget(self._section("Display"))
        disp = QFrame()
        disp.setProperty("frameClass", "card")
        displ = QVBoxLayout(disp)
        displ.setContentsMargins(20, 12, 20, 12)

        # Theme
        th_row = QFrame()
        thl = QHBoxLayout(th_row)
        thl.setContentsMargins(0, 0, 0, 0)
        thl_left = QFrame()
        thll = QVBoxLayout(thl_left)
        thll.setContentsMargins(0, 0, 0, 0)
        thll.setSpacing(0)
        thll.addWidget(self._bold("Theme", 12))
        thll.addWidget(self._muted("Select admin panel theme"))
        thl.addWidget(thl_left)
        thl.addStretch()
        theme_grp = QFrame()
        tgl = QHBoxLayout(theme_grp)
        tgl.setContentsMargins(0, 0, 0, 0)
        tgl.setSpacing(4)
        for label, val in [("Light", "light"), ("Dark", "dark")]:
            active = self._mode == val
            b = QPushButton(label)
            bg = c['btn_primary'] if active else c['btn_pale']
            b.setStyleSheet(
                f"background: {bg}; border: none; border-radius: 8px; "
                f"padding: 6px 16px; font-size: 11px; "
                f"font-weight: {'bold' if active else 'normal'};"
            )
            b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            b.clicked.connect(lambda _, v=val: self._set_theme(v))
            tgl.addWidget(b)
        thl.addWidget(theme_grp)
        displ.addWidget(th_row)

        sl.addWidget(disp)

        sl.addStretch()
        scroll.setWidget(sw)
        lay.addWidget(scroll)

    def _section(self, text):
        l = QLabel(text)
        l.setFont(QFont(FONT_FAMILY, 15, QFont.Weight.Bold))
        return l

    def _bold(self, text, size):
        l = QLabel(text)
        l.setFont(QFont(FONT_FAMILY, size, QFont.Weight.Bold))
        return l

    def _muted(self, text):
        l = QLabel(text)
        l.setObjectName("muted")
        return l

    def _set_theme(self, val):
        if self._refreshing:
            return
        # Update the mode on the main window directly
        top = self.window()
        if hasattr(top, '_mode'):
            top._mode = val
        if self._refresh_cb:
            self._refreshing = True
            self._refresh_cb()
            self._refreshing = False

    def _logout(self):
        c = palette(self._mode)
        reply = QMessageBox(self)
        reply.setWindowTitle("Logout")
        reply.setText("Are you sure you want to logout from admin panel?")
        reply.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        reply.setStyleSheet(
            f"QMessageBox {{ background-color: {c['card']}; }} "
            f"QLabel {{ color: {c['text_dark']}; font-weight: bold; }} "
            f"QPushButton {{ background-color: {c['btn_primary']}; "
            f"color: {c['text_dark']}; padding: 6px 16px; border-radius: 6px; "
            f"font-weight: bold; border: none; }}"
        )

        res = reply.exec()
        if res == QMessageBox.StandardButton.Yes:
            top = self.window()
            if hasattr(top, '_go_logout'):
                top._go_logout()
