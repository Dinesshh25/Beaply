"""
pyqt_app/views/profil_view.py
Profile page — left panel with completeness ring, right with personal info.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QLineEdit, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor

from pyqt_app.styles.theme import FONT_FAMILY, palette
from pyqt_app.widgets.progress_ring import ProgressRing
from controllers.profil_controller import (
    tampil_profil, simpan_data_opsional,
)
from utils import format_tanggal


def _hitung_completeness(p):
    """Compute profile completeness percentage."""
    if not p:
        return 0
    fields = ["nama","tanggal_lahir","email","jurusan","kampus",
              "jenjang","semester","ip","jenis_kelamin"]
    opt = ["skor_ielts","skor_toefl","skor_duolingo","skor_sat",
           "skor_act","skor_gre","skor_gmat","skor_hsk","level_jlpt"]
    total = len(fields) + len(opt)
    filled = sum(1 for f in fields if p.get(f))
    filled += sum(1 for f in opt if p.get(f) and p[f] != 0)
    return int((filled / total) * 100)


class ProfilView(QWidget):
    def __init__(self, profil_id, bhs="id", mode="light", parent=None):
        super().__init__(parent)
        self._pid = profil_id
        self._bhs = bhs
        self._mode = mode
        self._build()

    def _clear(self):
        if self.layout():
            while self.layout().count():
                item = self.layout().takeAt(0)
                if item.widget(): item.widget().deleteLater()
        else:
            QHBoxLayout(self)

    def _build(self):
        self._clear()
        c = palette(self._mode)
        lay = self.layout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)

        profil = tampil_profil(self._pid)
        if not profil:
            lay.addWidget(QLabel("Profile not found."))
            return
        completeness = _hitung_completeness(profil)

        # ── Left column ──────────────────────────────────────
        left = QFrame()
        left.setFixedWidth(280)
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(12)

        card1 = QFrame()
        card1.setProperty("frameClass", "card")
        c1l = QVBoxLayout(card1)
        c1l.setContentsMargins(20, 24, 20, 20)
        c1l.setSpacing(8)
        c1l.addWidget(self._bold("Profile\nCompleteness", 17))

        ring = ProgressRing(completeness, 120, 8)
        ring_color = c['btn_primary'] if completeness >= 80 else c['text_accent']
        ring.set_colors("#DFE6E1", ring_color, c['text_dark'])
        c1l.addWidget(ring, alignment=Qt.AlignmentFlag.AlignCenter)
        c1l.addWidget(self._bold("Profile Complete", 12), alignment=Qt.AlignmentFlag.AlignCenter)
        desc = QLabel("Complete your profile to\nget better scholarship matches!")
        desc.setStyleSheet(f"color: {c['text_muted']}; font-size: 10px;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        c1l.addWidget(desc)
        if completeness < 100:
            cb = QPushButton("Complete Profile")
            cb.setObjectName("btn_primary")
            cb.setFixedHeight(32)
            cb.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            cb.clicked.connect(self._show_edit)
            c1l.addWidget(cb)
        ll.addWidget(card1)

        logout = QPushButton("Logout")
        logout.setStyleSheet(f"background: #F6D6D0; color: {c['danger']}; border: none; border-radius: 12px; padding: 10px; font-weight: bold; font-size: 13px;")
        logout.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        logout.clicked.connect(self._logout)
        ll.addWidget(logout)
        ll.addStretch()
        lay.addWidget(left)

        # ── Right column ─────────────────────────────────────
        right = QFrame()
        right.setProperty("frameClass", "card")
        rl = QVBoxLayout(right)
        rl.setContentsMargins(24, 20, 24, 20)

        hdr = QFrame()
        hdl = QHBoxLayout(hdr)
        hdl.setContentsMargins(0, 0, 0, 0)
        hdl.addWidget(self._bold("Personal Informations", 17))
        hdl.addStretch()
        eb = QPushButton("Edit Profile")
        eb.setObjectName("btn_small_primary")
        eb.setFixedHeight(34)
        eb.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        eb.clicked.connect(self._show_edit)
        hdl.addWidget(eb)
        rl.addWidget(hdr)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        sw = QWidget()
        sl = QVBoxLayout(sw)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.setSpacing(4)

        sh = QLabel("Required Information")
        sh.setStyleSheet(f"color: {c['text_accent']}; font-weight: bold; font-size: 13px;")
        sl.addWidget(sh)
        for label, val in [("Full Name", profil["nama"]),
                           ("Date of Birth", format_tanggal(profil["tanggal_lahir"])),
                           ("Email", profil["email"]),
                           ("Major", profil["jurusan"]),
                           ("University", profil["kampus"]),
                           ("Degree", profil["jenjang"]),
                           ("Semester", profil["semester"]),
                           ("GPA", f"{profil['ip']:.2f}"),
                           ("Gender", profil.get("jenis_kelamin",""))]:
            self._info_row(sl, label, val, c)

        oh = QLabel("Optional Information")
        oh.setStyleSheet(f"color: {c['text_accent']}; font-weight: bold; font-size: 13px; margin-top: 12px;")
        sl.addWidget(oh)
        for label, key in [("IELTS","skor_ielts"),("TOEFL iBT","skor_toefl"),
                          ("Duolingo","skor_duolingo"),("SAT","skor_sat"),
                          ("ACT","skor_act"),("GRE","skor_gre"),
                          ("GMAT","skor_gmat"),("HSK","skor_hsk"),("JLPT","level_jlpt")]:
            val = profil.get(key)
            empty = val is None or val == 0 or str(val).strip() == ""
            self._info_row(sl, label, val if not empty else "Not filled", c, muted=empty)

        sl.addStretch()
        scroll.setWidget(sw)
        rl.addWidget(scroll)
        lay.addWidget(right)

    def _info_row(self, lay, label, val, c, muted=False):
        r = QFrame()
        rl = QHBoxLayout(r)
        rl.setContentsMargins(0, 0, 0, 0)
        l = QLabel(label)
        l.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Bold))
        l.setFixedWidth(140)
        rl.addWidget(l)
        v = QLabel(str(val) if val else "Not filled")
        v.setStyleSheet(f"color: {c['text_muted'] if muted else c['text_dark']}; font-size: 12px;")
        rl.addWidget(v)
        rl.addStretch()
        lay.addWidget(r)

    def _bold(self, text, size):
        l = QLabel(text)
        l.setFont(QFont(FONT_FAMILY, size, QFont.Weight.Bold))
        return l

    def _show_edit(self):
        self._clear()
        c = palette(self._mode)
        lay = self.layout()
        lay.setContentsMargins(0, 0, 0, 0)

        # Convert to vertical for the edit form
        wrapper = QWidget()
        wl = QVBoxLayout(wrapper)
        wl.setContentsMargins(0, 0, 0, 0)

        back = QPushButton("< Back to Profile")
        back.setObjectName("btn_outline")
        back.setFixedWidth(160)
        back.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        back.clicked.connect(self._build)
        wl.addWidget(back)
        wl.addWidget(self._bold("Complete Your Profile", 17))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        sw = QWidget()
        sl = QVBoxLayout(sw)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.setSpacing(4)

        profil = tampil_profil(self._pid)
        self._opt_entries = {}
        for key, label, current in [
            ("skor_ielts","IELTS Score (0.0-9.0)", profil.get("skor_ielts")),
            ("skor_toefl","TOEFL iBT (0-120)", profil.get("skor_toefl")),
            ("skor_duolingo","Duolingo (10-160)", profil.get("skor_duolingo")),
            ("skor_sat","SAT (400-1600)", profil.get("skor_sat")),
            ("skor_act","ACT (1-36)", profil.get("skor_act")),
            ("skor_gre","GRE (260-340)", profil.get("skor_gre")),
            ("skor_gmat","GMAT (200-800)", profil.get("skor_gmat")),
            ("skor_hsk","HSK (1-6)", profil.get("skor_hsk")),
        ]:
            card = QFrame()
            card.setProperty("frameClass", "card")
            cl = QHBoxLayout(card)
            cl.setContentsMargins(16, 10, 16, 10)
            cl.addWidget(self._bold(label, 11))
            e = QLineEdit()
            e.setFixedWidth(160)
            e.setFixedHeight(32)
            if current and current != 0:
                e.setText(str(current))
            cl.addWidget(e)
            self._opt_entries[key] = e
            sl.addWidget(card)

        # JLPT
        card = QFrame()
        card.setProperty("frameClass", "card")
        cl = QHBoxLayout(card)
        cl.setContentsMargins(16, 10, 16, 10)
        cl.addWidget(self._bold("JLPT Level", 11))
        self._jlpt_cb = QComboBox()
        self._jlpt_cb.addItems(["", "N1", "N2", "N3", "N4", "N5"])
        self._jlpt_cb.setCurrentText(profil.get("level_jlpt", "") or "")
        self._jlpt_cb.setFixedWidth(160)
        cl.addWidget(self._jlpt_cb)
        sl.addWidget(card)
        sl.addStretch()
        scroll.setWidget(sw)
        wl.addWidget(scroll)

        save = QPushButton("Save Optional Data")
        save.setObjectName("btn_primary")
        save.setFixedHeight(40)
        save.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        save.clicked.connect(self._save_opt)
        wl.addWidget(save)
        lay.addWidget(wrapper)

    def _save_opt(self):
        updates = {}
        for key, entry in self._opt_entries.items():
            val = entry.text().strip()
            if val:
                try:
                    updates[key] = float(val) if key == "skor_ielts" else int(val)
                except ValueError:
                    pass
            else:
                updates[key] = None
        jlpt = self._jlpt_cb.currentText().strip()
        updates["level_jlpt"] = jlpt if jlpt else None
        ok, msg = simpan_data_opsional(self._pid, updates)
        if ok:
            QMessageBox.information(self, "Success", "Optional data saved!")
        else:
            QMessageBox.critical(self, "Error", msg)
        self._build()

    def _logout(self):
        r = QMessageBox.question(self, "Logout", "Are you sure you want to logout?")
        if r == QMessageBox.StandardButton.Yes:
            top = self.window()
            if hasattr(top, '_go_logout'):
                top._go_logout()
