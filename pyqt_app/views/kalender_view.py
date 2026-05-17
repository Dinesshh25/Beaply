"""
pyqt_app/views/kalender_view.py
Calendar Deadline — two-column layout with calendar grid and events panel.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QGridLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor
from datetime import datetime

from pyqt_app.styles.theme import FONT_FAMILY, palette
from controllers.tracker_controller import (
    tampilan_kalender, fmt_status, get_semua_tracker as ambil_semua_tracker,
)


class KalenderView(QWidget):
    def __init__(self, profil_id, bhs="id", mode="light", parent=None):
        super().__init__(parent)
        self._pid = profil_id
        self._bhs = bhs
        self._mode = mode
        now = datetime.now()
        self._bulan = now.month
        self._tahun = now.year
        self._build()

    def _build(self):
        if self.layout():
            while self.layout().count():
                item = self.layout().takeAt(0)
                if item.widget(): item.widget().deleteLater()
        else:
            QHBoxLayout(self)

        c = palette(self._mode)
        lay = self.layout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        data = tampilan_kalender(self._pid, self._bulan, self._tahun)

        # ── Left: Calendar ─────────────────────────────────
        left = QFrame()
        left.setProperty("frameClass", "card")
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 12)

        # Month header
        mh = QFrame()
        mh.setStyleSheet(f"QFrame {{ background: {c['calendar_header']}; border-radius: 14px; }}")
        mh.setFixedHeight(50)
        mhl = QHBoxLayout(mh)
        prev_btn = QPushButton("<")
        prev_btn.setFixedSize(36, 36)
        prev_btn.setStyleSheet(f"background: transparent; border: none; font-size: 16px; font-weight: bold; color: {c['text_dark']};")
        prev_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        prev_btn.clicked.connect(self._prev)
        mhl.addWidget(prev_btn)
        mhl.addStretch()
        mt = QLabel(f"{data['nama_bulan']} {data['tahun']}")
        mt.setFont(QFont(FONT_FAMILY, 15, QFont.Weight.Bold))
        mhl.addWidget(mt)
        mhl.addStretch()
        next_btn = QPushButton(">")
        next_btn.setFixedSize(36, 36)
        next_btn.setStyleSheet(f"background: transparent; border: none; font-size: 16px; font-weight: bold; color: {c['text_dark']};")
        next_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        next_btn.clicked.connect(self._next)
        mhl.addWidget(next_btn)
        ll.addWidget(mh)

        # Day headers
        grid = QWidget()
        gl = QGridLayout(grid)
        gl.setSpacing(4)
        for i, d in enumerate(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]):
            lbl = QLabel(d)
            lbl.setStyleSheet(f"color: {c['text_muted']}; font-size: 10px; font-weight: bold;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            gl.addWidget(lbl, 0, i)

        today = datetime.now()
        row = 1
        col = data["hari_pertama"]
        tgl_warna = data.get("tanggal_warna", {})
        tgl_tracker = data.get("tanggal_tracker", {})

        for day in range(1, data["total_hari"] + 1):
            warna = tgl_warna.get(day)
            is_today = (day == today.day and self._bulan == today.month and self._tahun == today.year)
            bg = warna if warna else (c['btn_primary'] if is_today else "transparent")
            txt_c = "white" if (warna or is_today) else c['text_dark']
            btn = QPushButton(str(day))
            btn.setFixedSize(44, 36)
            fw = "bold" if (warna or is_today) else "normal"
            btn.setStyleSheet(f"""
                QPushButton {{ background: {bg}; color: {txt_c}; border: none;
                               border-radius: 8px; font-size: 12px; font-weight: {fw}; }}
                QPushButton:hover {{ background: {c['btn_pale']}; }}
            """)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.clicked.connect(lambda _, d=day: self._click_day(d, tgl_tracker))
            gl.addWidget(btn, row, col)
            col += 1
            if col > 6:
                col = 0
                row += 1
        ll.addWidget(grid)

        # Legend
        leg = QFrame()
        legl = QHBoxLayout(leg)
        legl.setContentsMargins(12, 0, 12, 0)
        for txt, clr in [("Deadline","#EF4444"),("Today",c['btn_primary']),("Bookmark","#3B82F6")]:
            f = QFrame()
            fl = QHBoxLayout(f)
            fl.setContentsMargins(0,0,0,0)
            dot = QFrame()
            dot.setFixedSize(10, 10)
            dot.setStyleSheet(f"background: {clr}; border-radius: 5px;")
            fl.addWidget(dot)
            fl.addWidget(QLabel(txt))
            legl.addWidget(f)
        legl.addStretch()
        ll.addWidget(leg)
        lay.addWidget(left, 7)

        # ── Right: Events ──────────────────────────────────
        right = QFrame()
        right.setFixedWidth(260)
        right.setStyleSheet(f"QFrame {{ background: {c['btn_pale']}; border-radius: 16px; border: 1px solid {c['border']}; }}")
        rl = QVBoxLayout(right)
        rl.setContentsMargins(16, 20, 16, 12)
        rh = QLabel("Upcoming Events")
        rh.setFont(QFont(FONT_FAMILY, 15, QFont.Weight.Bold))
        rl.addWidget(rh)

        esc = QScrollArea()
        esc.setWidgetResizable(True)
        esc.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        esw = QWidget()
        esl = QVBoxLayout(esw)
        esl.setContentsMargins(0, 0, 0, 0)
        esl.setSpacing(4)
        trackers = ambil_semua_tracker(self._pid) if self._pid else []
        upcoming = sorted([t for t in trackers if t.get("deadline")], key=lambda x: x["deadline"])
        if not upcoming:
            el = QLabel("No upcoming events.\nAdd deadlines via Tracker.")
            el.setStyleSheet(f"color: {c['text_muted']}; font-size: 11px;")
            el.setAlignment(Qt.AlignmentFlag.AlignCenter)
            esl.addWidget(el)
        else:
            for tr in upcoming[:10]:
                ev = QFrame()
                ev.setStyleSheet(f"QFrame {{ background: {c['card']}; border-radius: 10px; }}")
                evl = QVBoxLayout(ev)
                evl.setContentsMargins(10, 8, 10, 8)
                en = QLabel(tr.get("nama_beasiswa", ""))
                en.setFont(QFont(FONT_FAMILY, 10, QFont.Weight.Bold))
                en.setWordWrap(True)
                evl.addWidget(en)
                ed = QLabel(tr.get("deadline", ""))
                ed.setStyleSheet(f"color: {c['text_accent']}; font-size: 10px;")
                evl.addWidget(ed)
                esl.addWidget(ev)
        esl.addStretch()
        esc.setWidget(esw)
        rl.addWidget(esc)
        lay.addWidget(right, 3)

    def _prev(self):
        self._bulan -= 1
        if self._bulan < 1:
            self._bulan = 12
            self._tahun -= 1
        self._build()

    def _next(self):
        self._bulan += 1
        if self._bulan > 12:
            self._bulan = 1
            self._tahun += 1
        self._build()

    def _click_day(self, day, tgl_tracker):
        items = tgl_tracker.get(day, [])
        if not items: return
        msg = "\n".join([f"• {it['nama_beasiswa']} — {fmt_status(it['status'], self._bhs)}" for it in items])
        QMessageBox.information(self, "Deadline Details", msg)
