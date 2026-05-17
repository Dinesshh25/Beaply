"""
pyqt_app/views/tracker_view.py
Application Tracker — list with status management.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QLineEdit, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor

from pyqt_app.styles.theme import FONT_FAMILY, palette
from controllers.tracker_controller import (
    tambah_penanda_manual, ubah_status, toggle_bookmark, hapus,
    get_semua_tracker, get_tracker_by_id,
    fmt_status, clr_status, fmt_deadline,
    buat_pengingat_otomatis, STATUS_LIST,
    ambil_semua_tracker, ambil_tracker_by_id,
)
from controllers.notifikasi_controller import buat_notifikasi_status


class TrackerView(QWidget):
    def __init__(self, profil_id, bhs="id", mode="light", parent=None):
        super().__init__(parent)
        self._pid = profil_id
        self._bhs = bhs
        self._mode = mode
        self._build_list()

    def _clear(self):
        if self.layout():
            while self.layout().count():
                item = self.layout().takeAt(0)
                if item.widget(): item.widget().deleteLater()
        else:
            QVBoxLayout(self)

    def _build_list(self):
        self._clear()
        c = palette(self._mode)
        lay = self.layout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        hdr = QFrame()
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(0, 0, 0, 0)
        t = QLabel("Application Tracker")
        t.setFont(QFont(FONT_FAMILY, 17, QFont.Weight.Bold))
        hl.addWidget(t)
        hl.addStretch()
        ab = QPushButton("+ Add Tracker")
        ab.setObjectName("btn_primary")
        ab.setFixedHeight(34)
        ab.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        ab.clicked.connect(self._build_form)
        hl.addWidget(ab)
        lay.addWidget(hdr)

        trackers = ambil_semua_tracker(self._pid)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        sw = QWidget()
        sl = QVBoxLayout(sw)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.setSpacing(6)

        if not trackers:
            el = QLabel("Belum ada tracker. Tambahkan yang pertama!")
            el.setStyleSheet(f"color: {c['text_muted']}; font-size: 12px;")
            el.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sl.addWidget(el)
        else:
            for tr in trackers:
                self._card(sl, tr, c)
        sl.addStretch()
        scroll.setWidget(sw)
        lay.addWidget(scroll)

    def _card(self, parent_lay, tr, c):
        card = QFrame()
        card.setProperty("frameClass", "card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(12, 8, 12, 8)

        top = QFrame()
        tl = QHBoxLayout(top)
        tl.setContentsMargins(0, 0, 0, 0)
        n = QLabel(tr["nama_beasiswa"])
        n.setFont(QFont(FONT_FAMILY, 12, QFont.Weight.Bold))
        tl.addWidget(n)
        tl.addStretch()
        slbl = QLabel(f"  {fmt_status(tr['status'], self._bhs)}  ")
        sc = clr_status(tr['status'])
        slbl.setStyleSheet(f"background: {sc}; color: white; border-radius: 4px; font-size: 10px; padding: 2px 6px;")
        tl.addWidget(slbl)
        bm_txt = "⭐" if tr["dibookmark"] else "☆"
        bmb = QPushButton(bm_txt)
        bmb.setStyleSheet("background: transparent; border: none; font-size: 16px;")
        bmb.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        bmb.clicked.connect(lambda _, tid=tr["id"]: (toggle_bookmark(tid), self._build_list()))
        tl.addWidget(bmb)
        cl.addWidget(top)

        info = QFrame()
        il = QHBoxLayout(info)
        il.setContentsMargins(0, 0, 0, 0)
        dl_txt = fmt_deadline(tr["deadline"]) if tr.get("deadline") else "Tidak ada deadline"
        il.addWidget(QLabel(f"📅 {dl_txt}"))
        if tr.get("catatan"):
            il.addWidget(QLabel(f"📝 {tr['catatan'][:40]}"))
        il.addStretch()
        cl.addWidget(info)

        act = QFrame()
        al = QHBoxLayout(act)
        al.setContentsMargins(0, 0, 0, 0)
        cb = QComboBox()
        cb.addItems(STATUS_LIST)
        cb.setCurrentText(tr["status"])
        cb.setFixedWidth(140)
        cb.currentTextChanged.connect(lambda val, tid=tr["id"]: self._change_status(tid, val))
        al.addWidget(cb)
        al.addStretch()
        db = QPushButton("Delete")
        db.setStyleSheet("background: #EF4444; color: white; border: none; border-radius: 6px; padding: 4px 12px; font-size: 10px;")
        db.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        db.clicked.connect(lambda _, tid=tr["id"]: self._delete(tid))
        al.addWidget(db)
        cl.addWidget(act)
        parent_lay.addWidget(card)

    def _build_form(self):
        self._clear()
        c = palette(self._mode)
        lay = self.layout()
        lay.setContentsMargins(0, 0, 0, 0)

        back = QPushButton("← Back")
        back.setObjectName("btn_outline")
        back.setFixedWidth(100)
        back.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        back.clicked.connect(self._build_list)
        lay.addWidget(back)

        t = QLabel("Add Tracker")
        t.setFont(QFont(FONT_FAMILY, 17, QFont.Weight.Bold))
        lay.addWidget(t)

        form = QFrame()
        form.setProperty("frameClass", "card")
        fl = QVBoxLayout(form)
        fl.setContentsMargins(16, 12, 16, 16)
        self._e_nama = QLineEdit()
        self._e_nama.setPlaceholderText("Scholarship Name *")
        self._e_nama.setFixedHeight(38)
        fl.addWidget(self._e_nama)
        self._e_dl = QLineEdit()
        self._e_dl.setPlaceholderText("Deadline (YYYY-MM-DD)")
        self._e_dl.setFixedHeight(38)
        fl.addWidget(self._e_dl)
        self._e_cat = QLineEdit()
        self._e_cat.setPlaceholderText("Notes")
        self._e_cat.setFixedHeight(38)
        fl.addWidget(self._e_cat)
        self._err = QLabel("")
        self._err.setObjectName("error")
        fl.addWidget(self._err)
        sb = QPushButton("Save Tracker")
        sb.setObjectName("btn_primary")
        sb.setFixedHeight(40)
        sb.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        sb.clicked.connect(self._save)
        fl.addWidget(sb)
        lay.addWidget(form)
        lay.addStretch()

    def _save(self):
        nama = self._e_nama.text().strip()
        dl = self._e_dl.text().strip()
        cat = self._e_cat.text().strip()
        ok, msg, tid = tambah_penanda_manual(self._pid, nama, dl, cat)
        if not ok:
            self._err.setText(msg)
            return
        if dl:
            buat_pengingat_otomatis(tid)
        QMessageBox.information(self, "Success", "Tracker added!")
        self._build_list()

    def _change_status(self, tid, status):
        ok, msg = ubah_status(tid, status)
        if ok:
            tr = ambil_tracker_by_id(tid)
            if tr:
                buat_notifikasi_status(self._pid, tr["nama_beasiswa"], status)

    def _delete(self, tid):
        r = QMessageBox.question(self, "Confirm", "Delete this tracker?")
        if r == QMessageBox.StandardButton.Yes:
            hapus(tid)
            self._build_list()
