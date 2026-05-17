"""
pyqt_app/views/rekomendasi_view.py
Recommendations page.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QLineEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor

from pyqt_app.styles.theme import FONT_FAMILY, palette, pastel
from controllers.rekomendasi_controller import (
    get_profil_user, hitung_rekomendasi, get_analisis,
)


class RekomendasiView(QWidget):
    def __init__(self, profil_id, bhs="id", mode="light", parent=None):
        super().__init__(parent)
        self._pid = profil_id
        self._bhs = bhs
        self._mode = mode

        self._results = None
        self._profil = get_profil_user(self._pid) if self._pid else {}
        self._build_initial()

    def _build_initial(self):
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

        # Header card
        hdr = QFrame()
        hdr.setStyleSheet(f"QFrame {{ background: {pastel(3, self._mode)}; border-radius: 16px; border: 1px solid {c['border']}; }}")
        hdr.setFixedHeight(100)
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(24, 16, 24, 16)
        ht = QLabel("Let us match you with scholarships\ntailored just for you!")
        ht.setFont(QFont(FONT_FAMILY, 14, QFont.Weight.Bold))
        ht.setWordWrap(True)
        hl.addWidget(ht)
        gb = QPushButton("Get Recommendations")
        gb.setObjectName("btn_primary")
        gb.setFixedHeight(38)
        gb.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        gb.clicked.connect(self._do_calc)
        hl.addWidget(gb)
        sl.addWidget(hdr)

        if not self._profil:
            # Input form
            card = QFrame()
            card.setProperty("frameClass", "card")
            cl = QVBoxLayout(card)
            cl.setContentsMargins(24, 20, 24, 20)
            cl.addWidget(QLabel("Complete your data to get matches"))
            self._inputs = {}
            for label, key in [("Major","jurusan"),("Latest GPA","ipk"),("Semester","sem")]:
                f = QFrame()
                fl = QHBoxLayout(f)
                fl.setContentsMargins(0,0,0,0)
                fl.addWidget(QLabel(label))
                e = QLineEdit()
                e.setFixedHeight(36)
                fl.addWidget(e)
                self._inputs[key] = e
                cl.addWidget(f)
            sl.addWidget(card)
        else:
            info = QFrame()
            info.setProperty("frameClass", "card")
            il = QVBoxLayout(info)
            il.setContentsMargins(24, 20, 24, 20)
            it = QLabel("Click 'Get Recommendations' to analyze your profile\nand find the best scholarship matches.")
            it.setStyleSheet(f"color: {c['text_muted']}; font-size: 13px;")
            it.setAlignment(Qt.AlignmentFlag.AlignCenter)
            il.addWidget(it)
            sl.addWidget(info)


        sl.addStretch()
        scroll.setWidget(sw)
        lay.addWidget(scroll)

    def _do_calc(self):
        if not self._profil:
            try:
                self._profil = {
                    "jurusan": self._inputs["jurusan"].text(),
                    "ipk": float(self._inputs["ipk"].text()),
                    "semester": int(self._inputs["sem"].text()),
                    "organisasi": True, "penghasilan_ortu": 5000000,
                }
            except (ValueError, AttributeError):
                QMessageBox.warning(self, "Error", "Please enter valid data.")
                return
        self._results = hitung_rekomendasi(self._profil)
        # Rebuild
        while self.layout().count():
            item = self.layout().takeAt(0)
            if item.widget(): item.widget().deleteLater()
        self._build_results()

    def _build_results(self):
        c = palette(self._mode)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        sw = QWidget()
        sl = QVBoxLayout(sw)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.setSpacing(8)

        hdr = QFrame()
        hdr.setStyleSheet(f"QFrame {{ background: {pastel(3, self._mode)}; border-radius: 16px; border: 1px solid {c['border']}; }}")
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(24, 16, 24, 16)
        hl.addWidget(QLabel("Your Personalized Matches"))
        rb = QPushButton("Refresh")
        rb.setObjectName("btn_outline")
        rb.setFixedHeight(30)
        rb.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        rb.clicked.connect(self._do_calc)
        hl.addWidget(rb)
        sl.addWidget(hdr)

        cnt = QLabel(f"Found {len(self._results)} scholarship matches")
        cnt.setFont(QFont(FONT_FAMILY, 13, QFont.Weight.Bold))
        sl.addWidget(cnt)

        for i, item in enumerate(self._results):
            bea = item["beasiswa"]
            skor = item["skor"]


            card = QFrame()
            card.setProperty("frameClass", "card")
            cl = QHBoxLayout(card)
            cl.setContentsMargins(20, 14, 20, 14)
            left = QFrame()
            ll = QVBoxLayout(left)
            ll.setContentsMargins(0,0,0,0)
            ll.setSpacing(2)
            rf = QFrame()
            rfl = QHBoxLayout(rf)
            rfl.setContentsMargins(0,0,0,0)
            rk = QLabel(f"#{i+1}")
            rk.setStyleSheet(f"color: {c['text_accent']}; font-weight: bold; font-size: 11px;")
            rfl.addWidget(rk)
            if i == 0:
                bm = QLabel("  Best Match")
                bm.setStyleSheet(f"color: {c['btn_primary']}; font-weight: bold; font-size: 10px;")
                rfl.addWidget(bm)
            rfl.addStretch()
            ll.addWidget(rf)
            n = QLabel(bea["nama"])
            n.setFont(QFont(FONT_FAMILY, 12, QFont.Weight.Bold))
            ll.addWidget(n)
            info = QLabel(f"Min IPK: {bea['min_ipk']}  |  Max Sem: {bea['max_semester']}")
            info.setStyleSheet(f"color: {c['text_muted']}; font-size: 10px;")
            ll.addWidget(info)
            cl.addWidget(left)
            cl.addStretch()

            badge = QFrame()
            badge.setFixedSize(72, 44)
            badge.setStyleSheet(f"QFrame {{ background: {pastel(i, self._mode)}; border-radius: 12px; }}")
            bc = c['btn_primary'] if skor >= 60 else c['text_accent']
            bl = QLabel(f"{skor}%")
            bl.setFont(QFont(FONT_FAMILY, 14, QFont.Weight.Bold))
            bl.setStyleSheet(f"color: {bc};")
            bl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            blv = QVBoxLayout(badge)
            blv.addWidget(bl)
            cl.addWidget(badge)
            sl.addWidget(card)

        # Smart tips
        if self._results:
            top = self._results[0]["beasiswa"]
            saran = get_analisis(self._profil, top)
            th = QLabel("Smart Tips For You")
            th.setFont(QFont(FONT_FAMILY, 14, QFont.Weight.Bold))
            sl.addWidget(th)
            tc = QFrame()
            tc.setProperty("frameClass", "card")
            tcl = QVBoxLayout(tc)
            tcl.setContentsMargins(20, 16, 20, 16)
            tcl.addWidget(QLabel(f"Based on your #1 match: {top['nama']}"))
            st = QLabel(saran)
            st.setStyleSheet(f"color: {c['text_muted']}; font-size: 11px;")
            st.setWordWrap(True)
            tcl.addWidget(st)
            sl.addWidget(tc)

        sl.addStretch()
        scroll.setWidget(sw)
        self.layout().addWidget(scroll)
