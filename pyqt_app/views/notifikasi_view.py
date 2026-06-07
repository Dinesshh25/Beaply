"""
pyqt_app/views/notifikasi_view.py
Notifications page — grouped by date, with read/unread tabs.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QMessageBox, QDialog, QGraphicsDropShadowEffect,
    QTextBrowser
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor, QColor, QPainter, QLinearGradient
from datetime import datetime

from pyqt_app.styles.theme import FONT_FAMILY, palette, grad_green, grad_peach
from controllers.notifikasi_controller import (
    ambil_riwayat, tandai_dibaca, tandai_semua_dibaca, hapus_notifikasi,
)

TRANSLATIONS = {
    'id': {
        'all': 'Semua',
        'read': 'Dibaca',
        'unread': 'Belum Dibaca',
        'mark_all': '✓ Tandai Semua Dibaca',
        'clear_all': '🗑 Hapus Semua',
        'no_notifs': 'Belum ada notifikasi.',
        'today': 'Hari Ini',
        'yesterday': 'Kemarin',
        'days_ago': 'hari yang lalu',
        'older': 'Lebih Lama',
        'notification': 'Notifikasi',
        'detail_title': 'Detail Notifikasi',
        'close': 'Tutup',
        'clear_confirm': 'Hapus semua notifikasi?'
    },
    'en': {
        'all': 'All',
        'read': 'Read',
        'unread': 'Unread',
        'mark_all': '✓ Mark All as Read',
        'clear_all': '🗑 Clear All',
        'no_notifs': 'No notifications yet.',
        'today': 'Today',
        'yesterday': 'Yesterday',
        'days_ago': 'days ago',
        'older': 'Older',
        'notification': 'Notification',
        'detail_title': 'Notification Detail',
        'close': 'Close',
        'clear_confirm': 'Delete all notifications?'
    }
}


class NotifDetailDialog(QDialog):
    def __init__(self, notif_data, mode, bhs="id", parent=None):
        super().__init__(parent)
        self.notif_data = notif_data
        self._c = palette(mode)
        self._t = TRANSLATIONS.get(bhs, TRANSLATIONS['id'])
        
        self.setWindowTitle(self._t['detail_title'])
        self.setFixedSize(450, 320)
        self.setStyleSheet("QDialog { background: transparent; }")
        
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(20, 20, 20, 20)
        
        self.content_frame = QFrame()
        _content_bg = 'rgba(255, 255, 255, 0.95)' if mode == 'light' else f'rgba(41, 42, 45, 0.95)'
        self.content_frame.setStyleSheet(f"QFrame {{ background-color: {_content_bg}; border-radius: 20px; }} QLabel {{ background: transparent; color: {self._c['text_dark']}; }}")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        self.content_frame.setGraphicsEffect(shadow)
        
        lay = QVBoxLayout(self.content_frame)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(12)
        
        # Title
        title = QLabel(notif_data.get("judul", self._t['detail_title']))
        title.setFont(QFont(FONT_FAMILY, 15, QFont.Weight.Bold))
        title.setWordWrap(True)
        lay.addWidget(title)
        
        # Date
        date_lbl = QLabel(notif_data.get("dibuat_pada", "")[:16])
        date_lbl.setStyleSheet(f"color: {self._c['text_muted']}; font-size: 11px;")
        lay.addWidget(date_lbl)
        
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: rgba(0, 0, 0, 0.1);")
        line.setFixedHeight(1)
        lay.addWidget(line)
        
        # Message using QTextBrowser to prevent clipping
        desc = QTextBrowser()
        desc.setPlainText(notif_data.get("pesan", ""))
        desc.setFont(QFont(FONT_FAMILY, 11))
        desc.setStyleSheet(f"QTextBrowser {{ color: {self._c['text_dark']}; background: transparent; border: none; }}")
        lay.addWidget(desc, 1)
        
        # Close btn
        btn_lay = QHBoxLayout()
        btn_lay.addStretch()
        self.btn_close = QPushButton(self._t['close'])
        self.btn_close.setFixedHeight(36)
        self.btn_close.setFixedWidth(100)
        self.btn_close.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_close.setStyleSheet(f"QPushButton {{ background-color: {self._c['btn_primary']}; color: {self._c['text_dark']}; border-radius: 18px; font-weight: bold; font-size: 12px; }} QPushButton:hover {{ background-color: {self._c['btn_primary_hover']}; }}")
        self.btn_close.clicked.connect(self.accept)
        btn_lay.addWidget(self.btn_close)
        
        lay.addLayout(btn_lay)
        main_lay.addWidget(self.content_frame)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        grad = QLinearGradient(0, 0, self.width(), self.height())
        grad.setColorAt(0.0, QColor(self._c['grad_peach_start']))
        grad.setColorAt(1.0, QColor(self._c['grad_green_start']))
        painter.fillRect(self.rect(), grad)
        painter.end()
        super().paintEvent(event)

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
        t = TRANSLATIONS.get(self._bhs, TRANSLATIONS['id'])
        
        lay = self.layout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        # Tabs + actions
        top = QFrame()
        tl = QHBoxLayout(top)
        tl.setContentsMargins(0, 0, 0, 0)

        tab_frame = QFrame()
        bg_pink = c['tab_pill_bg']
        tab_frame.setStyleSheet(f"QFrame {{ background: {bg_pink}; border-radius: 18px; }}")
        tab_frame.setFixedHeight(36)
        tab_lay = QHBoxLayout(tab_frame)
        tab_lay.setContentsMargins(2, 2, 2, 2)
        tab_lay.setSpacing(2)
        for label, fval in [(t['all'], None), (t['read'], 1), (t['unread'], 0)]:
            is_active = self._filter == fval
            btn = QPushButton(label)
            btn.setFixedSize(90, 32)
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

        mark_btn = QPushButton(t['mark_all'])
        mark_btn.setStyleSheet(f"background: {grad_green(c)}; color: {c['text_dark']}; border: none; border-radius: 12px; font-weight: bold; font-size: 13px; padding: 0 16px;")
        mark_btn.setFixedHeight(40)
        mark_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        mark_btn.clicked.connect(self._mark_all)
        tl.addWidget(mark_btn)

        clr_btn = QPushButton(t['clear_all'])
        clr_btn.setStyleSheet(f"background: {grad_peach(c)}; color: {c['text_dark']}; border: none; border-radius: 12px; font-weight: bold; font-size: 13px; padding: 0 16px;")
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
            el = QLabel(t['no_notifs'])
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
                    if diff == 0: group = t['today']
                    elif diff == 1: group = t['yesterday']
                    elif diff < 7: group = f"{diff} {t['days_ago']}"
                    else: group = dt.strftime("%b %d")
                except: group = t['older']
                groups.setdefault(group, []).append(n)

            for gname, items in groups.items():
                gh = QLabel(gname)
                gh.setFont(QFont(FONT_FAMILY, 13, QFont.Weight.Bold))
                sl.addWidget(gh)
                for n in items:
                    unread = not n.get("sudah_dibaca", 0)
                    card = QFrame()
                    card.setObjectName("notif_card")
                    bg = c['card']
                    if unread:
                        card.setStyleSheet(f"""
                            QFrame#notif_card {{
                                background: {bg};
                                border-radius: 12px;
                                border-left: 4px solid {c['text_accent']};
                                border-top: 1px solid {c['border']};
                                border-right: 1px solid {c['border']};
                                border-bottom: 1px solid {c['border']};
                            }}
                        """)
                    else:
                        card.setStyleSheet(f"""
                            QFrame#notif_card {{
                                background: {bg};
                                border-radius: 12px;
                                border: 1px solid {c['border']};
                            }}
                        """)
                    cl = QVBoxLayout(card)
                    cl.setContentsMargins(16, 10, 16, 10)
                    cl.setSpacing(4)

                    title_row = QHBoxLayout()
                    title_row.setContentsMargins(0, 0, 0, 0)
                    icon = "🔔" if unread else "📋"
                    nt = QLabel(f"{icon}  {n.get('judul', t['notification'])}")
                    fw = QFont.Weight.Bold if unread else QFont.Weight.Normal
                    nt.setFont(QFont(FONT_FAMILY, 11, fw))
                    nt.setStyleSheet(f"color: {c['text_dark']}; background: transparent; border: none;")
                    nt.setWordWrap(True)
                    title_row.addWidget(nt)
                    title_row.addStretch()
                    if unread:
                        dot = QLabel("●")
                        dot.setStyleSheet(f"color: {c['text_accent']}; font-size: 10px; background: transparent; border: none;")
                        title_row.addWidget(dot)
                    cl.addLayout(title_row)

                    msg = QLabel(n.get("pesan", ""))
                    msg.setStyleSheet(f"color: {c['text_muted']}; font-size: 10px; background: transparent; border: none;")
                    msg.setWordWrap(True)
                    cl.addWidget(msg)

                    act_row = QHBoxLayout()
                    act_row.setContentsMargins(0, 0, 0, 0)
                    ts_lbl = QLabel(n.get("dibuat_pada", "")[:16])
                    ts_lbl.setStyleSheet(f"color: {c['text_muted']}; font-size: 9px; background: transparent; border: none;")
                    act_row.addWidget(ts_lbl)
                    act_row.addStretch()
                    
                    card.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                    card.mousePressEvent = lambda e, ndata=n: self._on_notif_click(ndata)
                        
                    cl.addLayout(act_row)
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
        t = TRANSLATIONS.get(self._bhs, TRANSLATIONS['id'])
        r = QMessageBox.question(self, t['clear_all'], t['clear_confirm'])
        if r == QMessageBox.StandardButton.Yes:
            for n in ambil_riwayat(self._pid):
                hapus_notifikasi(n["id"])
            self._build()

    def _on_notif_click(self, n):
        from PyQt6.QtCore import QTimer
        dlg = NotifDetailDialog(n, self._mode, self._bhs, self)
        dlg.exec()
        
        if not n.get("sudah_dibaca", 0):
            tandai_dibaca(n["id"])
            QTimer.singleShot(0, self._build)
