"""
pyqt_app/views/notifikasi_view.py
Notifications page — grouped by date, with read/unread tabs.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor
from datetime import datetime

from pyqt_app.styles.theme import FONT_FAMILY, palette
from controllers.notifikasi_controller import (
    ambil_riwayat, tandai_dibaca, tandai_semua_dibaca, hapus_notifikasi,
)


class NotifikasiView(QWidget):
    def __init__(self, profil_id, bhs="id", mode="light", parent=None):
        super().__init__(parent)
        self._pid = profil_id
        self._bhs = bhs
        self._mode = mode
        self._filter = None  # None=all, 0=unread, 1=read
        self._build()

    def _clear(self):
        if self.layout():
            while self.layout().count():
                item = self.layout().takeAt(0)
                if item.widget(): item.widget().deleteLater()
        else:
            QVBoxLayout(self)

    def _build(self):
        self._clear()
        c = palette(self._mode)
        lay = self.layout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        # Tabs + actions
        top = QFrame()
        tl = QHBoxLayout(top)
        tl.setContentsMargins(0, 0, 0, 0)

        tab_frame = QFrame()
        bg_pink = "#FADBD8" if self._mode == "light" else c['bg']
        tab_frame.setStyleSheet(f"QFrame {{ background: {bg_pink}; border-radius: 18px; }}")
        tab_frame.setFixedHeight(36)
        tab_lay = QHBoxLayout(tab_frame)
        tab_lay.setContentsMargins(2, 2, 2, 2)
        tab_lay.setSpacing(2)
        for label, fval in [("All", None), ("Read", 1), ("Unread", 0)]:
            is_active = self._filter == fval
            btn = QPushButton(label)
            btn.setFixedSize(80, 32)
            bg = c['card'] if is_active else "transparent"
            fw = "bold" if is_active else "normal"
            shadow = f"border: 1px solid {c['border']};" if is_active else "border: none;"
            btn.setStyleSheet(f"""
                QPushButton {{ background: {bg}; color: {c['text_dark']};
                               {shadow} border-radius: 16px; font-size: 13px; font-weight: {fw}; }}
                QPushButton:hover {{ background: {c['card']}; }}
            """)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.clicked.connect(lambda _, f=fval: self._set_filter(f))
            tab_lay.addWidget(btn)
        tl.addWidget(tab_frame)
        tl.addStretch()

        mark_btn = QPushButton("✓ Mark All as Read")
        mark_btn.setStyleSheet(f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #D8E0D8, stop:1 #D5EBD5); color: {c['text_dark']}; border: none; border-radius: 12px; font-weight: bold; font-size: 13px; padding: 0 16px;")
        mark_btn.setFixedHeight(40)
        mark_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        mark_btn.clicked.connect(self._mark_all)
        tl.addWidget(mark_btn)

        clr_btn = QPushButton("🗑 Clear All")
        clr_btn.setStyleSheet(f"background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FFE0D1, stop:1 #FFBDAD); color: {c['text_dark']}; border: none; border-radius: 12px; font-weight: bold; font-size: 13px; padding: 0 16px;")
        clr_btn.setFixedHeight(40)
        clr_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        clr_btn.clicked.connect(self._clear_all)
        tl.addWidget(clr_btn)
        lay.addWidget(top)

        # Notifications list
        notifs = ambil_riwayat(self._pid)
        if self._filter is not None:
            notifs = [n for n in notifs if n.get("sudah_dibaca", 0) == self._filter]

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        sw = QWidget()
        sl = QVBoxLayout(sw)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.setSpacing(12)

        if not notifs:
            el = QLabel("No notifications yet.")
            el.setStyleSheet(f"color: {c['text_muted']}; font-size: 14px;")
            el.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sl.addWidget(el)
            sl.addStretch()
        else:
            now = datetime.now()
            groups = {}
            for n in notifs:
                ts = n.get("dibuat_pada", "")
                try:
                    dt = datetime.strptime(ts[:10], "%Y-%m-%d")
                    diff = (now.date() - dt.date()).days
                    if diff == 0: group = "Today"
                    elif diff == 1: group = "Yesterday"
                    elif diff < 7: group = f"{diff} days ago"
                    else: group = dt.strftime("%b %d")
                except: group = "Older"
                groups.setdefault(group, []).append(n)

            for gname, items in groups.items():
                gh = QLabel(gname)
                gh.setFont(QFont(FONT_FAMILY, 13, QFont.Weight.Bold))
                sl.addWidget(gh)
                for n in items:
                    unread = not n.get("sudah_dibaca", 0)
                    card = QFrame()
                    bg = c['card']
                    bdr = "2px solid #A8C5B0" if unread else f"1px solid {c['border']}"
                    card.setStyleSheet(f"QFrame {{ background: {bg}; border-radius: 16px; border: {bdr}; }}")
                    cl = QVBoxLayout(card)
                    cl.setContentsMargins(16, 12, 16, 12)

                    title_row = QFrame()
                    trl = QHBoxLayout(title_row)
                    trl.setContentsMargins(0,0,0,0)
                    nt = QLabel(n.get("judul", "Notification"))
                    fw = QFont.Weight.Bold if unread else QFont.Weight.Normal
                    nt.setFont(QFont(FONT_FAMILY, 12, fw))
                    trl.addWidget(nt)
                    trl.addStretch()
                    if unread:
                        dot = QFrame()
                        dot.setFixedSize(8, 8)
                        dot.setStyleSheet(f"background: {c['text_accent']}; border-radius: 4px;")
                        trl.addWidget(dot)
                    cl.addWidget(title_row)

                    msg = QLabel(n.get("pesan", ""))
                    msg.setStyleSheet(f"color: {c['text_muted']}; font-size: 11px;")
                    msg.setWordWrap(True)
                    cl.addWidget(msg)

                    act_row = QFrame()
                    arl = QHBoxLayout(act_row)
                    arl.setContentsMargins(0,0,0,0)
                    ts_lbl = QLabel(n.get("dibuat_pada", "")[:16])
                    ts_lbl.setStyleSheet(f"color: {c['text_muted']}; font-size: 9px;")
                    arl.addWidget(ts_lbl)
                    arl.addStretch()
                    if unread:
                        mr = QPushButton("Mark Read")
                        mr.setStyleSheet(f"background: transparent; color: {c['text_muted']}; border: 1px solid {c['border']}; border-radius: 6px; font-size: 9px; padding: 2px 8px;")
                        mr.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                        mr.clicked.connect(lambda _, nid=n["id"]: (tandai_dibaca(nid), self._build()))
                        arl.addWidget(mr)
                    cl.addWidget(act_row)
                    sl.addWidget(card)
            sl.addStretch()
        scroll.setWidget(sw)
        lay.addWidget(scroll)

    def _set_filter(self, f):
        self._filter = f
        self._build()

    def _mark_all(self):
        tandai_semua_dibaca(self._pid)
        self._build()

    def _clear_all(self):
        r = QMessageBox.question(self, "Clear All", "Delete all notifications?")
        if r == QMessageBox.StandardButton.Yes:
            for n in ambil_riwayat(self._pid):
                hapus_notifikasi(n["id"])
            self._build()
