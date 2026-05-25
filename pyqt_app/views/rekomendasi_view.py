"""
pyqt_app/views/rekomendasi_view.py
Recommendations page with scholarship comparison feature.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QLineEdit, QMessageBox, QComboBox,
    QSizePolicy, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor

from pyqt_app.styles.theme import FONT_FAMILY, palette, pastel
from controllers.rekomendasi_controller import (
    get_profil_user, hitung_rekomendasi, get_analisis, bandingkan_beasiswa,
)


# ─── Helper: horizontal divider ───────────────────────────────────────────────
def _hdivider(c: dict) -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setStyleSheet(f"color: {c['border']}; background: {c['border']}; max-height: 1px;")
    return line


# ─── Comparison result dialog-style panel ─────────────────────────────────────
class _ComparePanel(QFrame):
    """Side-by-side comparison card for two scholarships."""

    def __init__(self, data: dict, profil: dict, mode: str, back_cb, parent=None):
        super().__init__(parent)
        self._mode = mode
        c = palette(mode)

        self.setProperty("frameClass", "card")
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 24)
        root.setSpacing(14)

        # ── Title row ────────────────────────────────────────────
        title_row = QHBoxLayout()
        icon_lbl = QLabel("⚖️")
        icon_lbl.setFont(QFont(FONT_FAMILY, 18))
        icon_lbl.setFixedWidth(32)
        title_row.addWidget(icon_lbl)
        title_lbl = QLabel("Perbandingan Beasiswa")
        title_lbl.setFont(QFont(FONT_FAMILY, 15, QFont.Weight.Bold))
        title_row.addWidget(title_lbl)
        title_row.addStretch()
        back_btn = QPushButton("← Kembali ke Hasil")
        back_btn.setObjectName("btn_outline")
        back_btn.setFixedHeight(32)
        back_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        back_btn.clicked.connect(back_cb)
        title_row.addWidget(back_btn)
        root.addLayout(title_row)

        root.addWidget(_hdivider(c))

        if not data:
            root.addWidget(QLabel("Gagal memuat data perbandingan."))
            return

        bea_a = data["a"]["beasiswa"]
        bea_b = data["b"]["beasiswa"]
        skor_a = data["a"]["skor"]
        skor_b = data["b"]["skor"]
        krit_a = data["a"]["kriteria"]
        krit_b = data["b"]["kriteria"]

        # ── Score header cards ────────────────────────────────────
        score_row = QHBoxLayout()
        score_row.setSpacing(12)
        score_row.addWidget(self._score_card(bea_a["nama"], skor_a, 0, mode))
        # VS badge
        vs = QLabel("VS")
        vs.setFont(QFont(FONT_FAMILY, 14, QFont.Weight.Bold))
        vs.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vs.setStyleSheet(f"color: {c['text_muted']}; min-width: 36px;")
        score_row.addWidget(vs)
        score_row.addWidget(self._score_card(bea_b["nama"], skor_b, 3, mode))
        root.addLayout(score_row)

        root.addWidget(_hdivider(c))

        # ── Criteria grid ─────────────────────────────────────────
        grid_lbl = QLabel("Detail Kriteria")
        grid_lbl.setFont(QFont(FONT_FAMILY, 12, QFont.Weight.Bold))
        grid_lbl.setStyleSheet(f"color: {c['text_muted']};")
        root.addWidget(grid_lbl)

        grid = QGridLayout()
        grid.setSpacing(0)
        grid.setColumnStretch(0, 2)
        grid.setColumnStretch(1, 3)
        grid.setColumnStretch(2, 3)

        # Header row
        for col, text in enumerate(["Kriteria",
                                     self._short_name(bea_a["nama"]),
                                     self._short_name(bea_b["nama"])]):
            lbl = QLabel(text)
            lbl.setFont(QFont(FONT_FAMILY, 10, QFont.Weight.Bold))
            lbl.setStyleSheet(
                f"background: {pastel(4, mode)}; color: {c['text_dark']}; "
                f"padding: 6px 10px; border-radius: 0px;"
            )
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter if col > 0 else Qt.AlignmentFlag.AlignLeft)
            grid.addWidget(lbl, 0, col)

        for row_i, (ka, kb) in enumerate(zip(krit_a, krit_b), start=1):
            bg = c["card"] if row_i % 2 == 0 else c["bg"]

            # Kriteria label
            lbl_kr = QLabel(ka["label"])
            lbl_kr.setFont(QFont(FONT_FAMILY, 11))
            lbl_kr.setStyleSheet(
                f"background: {bg}; color: {c['text_dark']}; "
                f"padding: 8px 10px; border-bottom: 1px solid {c['border']};"
            )
            grid.addWidget(lbl_kr, row_i, 0)

            # Beasiswa A cell
            grid.addWidget(self._crit_cell(ka, bg, c), row_i, 1)

            # Beasiswa B cell
            grid.addWidget(self._crit_cell(kb, bg, c), row_i, 2)

        root.addLayout(grid)

        # ── Winner line ───────────────────────────────────────────
        if skor_a != skor_b:
            winner_name = bea_a["nama"] if skor_a > skor_b else bea_b["nama"]
            winner_skor = max(skor_a, skor_b)
            wl = QLabel(f"🏆  {winner_name} lebih cocok untuk profil Anda  ({winner_skor}%)")
            wl.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Bold))
            wl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            wl.setStyleSheet(
                f"background: {pastel(3, mode)}; color: {c['btn_primary']}; "
                f"border-radius: 10px; padding: 10px 16px;"
            )
            root.addWidget(wl)
        else:
            tie = QLabel("🤝  Keduanya memiliki skor kecocokan yang sama!")
            tie.setFont(QFont(FONT_FAMILY, 11))
            tie.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tie.setStyleSheet(
                f"background: {pastel(1, mode)}; color: {c['text_dark']}; "
                f"border-radius: 10px; padding: 10px 16px;"
            )
            root.addWidget(tie)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _score_card(self, nama: str, skor: int, pastel_idx: int, mode: str) -> QFrame:
        c = palette(mode)
        f = QFrame()
        f.setStyleSheet(
            f"QFrame {{ background: {pastel(pastel_idx, mode)}; "
            f"border-radius: 14px; border: 1px solid {c['border']}; }}"
        )
        f.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        fl = QVBoxLayout(f)
        fl.setContentsMargins(16, 14, 16, 14)
        fl.setSpacing(6)

        name_lbl = QLabel(nama)
        name_lbl.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Bold))
        name_lbl.setWordWrap(True)
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fl.addWidget(name_lbl)

        skor_color = c["btn_primary"] if skor >= 60 else c["text_accent"]
        skor_lbl = QLabel(f"{skor}%")
        skor_lbl.setFont(QFont(FONT_FAMILY, 28, QFont.Weight.Bold))
        skor_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        skor_lbl.setStyleSheet(f"color: {skor_color};")
        fl.addWidget(skor_lbl)

        match_txt = "Sangat Cocok" if skor >= 80 else ("Cocok" if skor >= 60 else ("Cukup" if skor >= 40 else "Kurang Cocok"))
        match_lbl = QLabel(match_txt)
        match_lbl.setFont(QFont(FONT_FAMILY, 10))
        match_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        match_lbl.setStyleSheet(f"color: {c['text_muted']};")
        fl.addWidget(match_lbl)
        return f

    def _crit_cell(self, k: dict, bg: str, c: dict) -> QFrame:
        """Build a criteria cell showing the requirement value + user pass/fail."""
        cell = QFrame()
        cell.setStyleSheet(
            f"QFrame {{ background: {bg}; padding: 0px; "
            f"border-bottom: 1px solid {c['border']}; border-radius: 0px; }}"
        )
        vl = QVBoxLayout(cell)
        vl.setContentsMargins(10, 6, 10, 6)
        vl.setSpacing(1)

        val_lbl = QLabel(k["nilai"])
        val_lbl.setFont(QFont(FONT_FAMILY, 10, QFont.Weight.Bold))
        val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vl.addWidget(val_lbl)

        lulus = k["lulus"]
        status_icon = "✅" if lulus else "❌"
        status_txt = f"{status_icon} {k['user']}"
        status_lbl = QLabel(status_txt)
        status_lbl.setFont(QFont(FONT_FAMILY, 9))
        status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_color = c["btn_primary"] if lulus else c["danger"]
        status_lbl.setStyleSheet(f"color: {status_color};")
        vl.addWidget(status_lbl)
        return cell

    @staticmethod
    def _short_name(nama: str) -> str:
        words = nama.split()
        return " ".join(words[:3]) + ("…" if len(words) > 3 else "")


# ─── Selection panel ──────────────────────────────────────────────────────────
class _CompareSelectPanel(QFrame):
    """
    Two dropdowns to select scholarships + a Compare button.
    Emitted via compare_requested callback(bea_a_idx, bea_b_idx).
    """

    def __init__(self, hasil: list, mode: str, compare_cb, cancel_cb, parent=None):
        super().__init__(parent)
        self._hasil = hasil
        self._mode = mode
        c = palette(mode)

        self.setProperty("frameClass", "card")
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)

        # Title
        t = QLabel("⚖️  Pilih Dua Beasiswa untuk Dibandingkan")
        t.setFont(QFont(FONT_FAMILY, 13, QFont.Weight.Bold))
        root.addWidget(t)

        sub = QLabel("Pilih dua beasiswa yang berbeda dari hasil rekomendasi Anda.")
        sub.setStyleSheet(f"color: {c['text_muted']}; font-size: 11px;")
        root.addWidget(sub)

        root.addWidget(_hdivider(c))

        names = [f"#{i+1}  {item['beasiswa']['nama']}" for i, item in enumerate(hasil)]

        # Dropdown row
        drop_row = QHBoxLayout()
        drop_row.setSpacing(16)

        # Beasiswa A
        col_a = QVBoxLayout()
        lbl_a = QLabel("Beasiswa Pertama")
        lbl_a.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Bold))
        col_a.addWidget(lbl_a)
        self._combo_a = QComboBox()
        for n in names:
            self._combo_a.addItem(n)
        self._combo_a.setFixedHeight(36)
        col_a.addWidget(self._combo_a)
        drop_row.addLayout(col_a)

        vs_lbl = QLabel("vs")
        vs_lbl.setFont(QFont(FONT_FAMILY, 13, QFont.Weight.Bold))
        vs_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom)
        vs_lbl.setStyleSheet(f"color: {c['text_muted']}; padding-bottom: 4px;")
        vs_lbl.setFixedWidth(28)
        drop_row.addWidget(vs_lbl)

        # Beasiswa B
        col_b = QVBoxLayout()
        lbl_b = QLabel("Beasiswa Kedua")
        lbl_b.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Bold))
        col_b.addWidget(lbl_b)
        self._combo_b = QComboBox()
        for n in names:
            self._combo_b.addItem(n)
        if len(names) > 1:
            self._combo_b.setCurrentIndex(1)
        self._combo_b.setFixedHeight(36)
        col_b.addWidget(self._combo_b)
        drop_row.addLayout(col_b)

        root.addLayout(drop_row)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = QPushButton("Batal")
        cancel_btn.setObjectName("btn_outline")
        cancel_btn.setFixedHeight(34)
        cancel_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        cancel_btn.clicked.connect(cancel_cb)
        btn_row.addWidget(cancel_btn)

        compare_btn = QPushButton("⚖️  Bandingkan Sekarang")
        compare_btn.setObjectName("btn_primary")
        compare_btn.setFixedHeight(34)
        compare_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        compare_btn.clicked.connect(self._on_compare)
        btn_row.addWidget(compare_btn)
        root.addLayout(btn_row)

        self._compare_cb = compare_cb

    def _on_compare(self):
        idx_a = self._combo_a.currentIndex()
        idx_b = self._combo_b.currentIndex()
        if idx_a == idx_b:
            QMessageBox.warning(
                self, "Pilihan Sama",
                "Pilih dua beasiswa yang berbeda untuk membandingkan."
            )
            return
        self._compare_cb(idx_a, idx_b)


# ─── Main Rekomendasi View ─────────────────────────────────────────────────────
class RekomendasiView(QWidget):
    def __init__(self, profil_id, bhs="id", mode="light", parent=None):
        super().__init__(parent)
        self._pid = profil_id
        self._bhs = bhs
        self._mode = mode

        self._results = None
        self._profil = get_profil_user(self._pid) if self._pid else {}

        # Top-level layout — holds the scroll area
        self._root_lay = QVBoxLayout(self)
        self._root_lay.setContentsMargins(0, 0, 0, 0)
        self._root_lay.setSpacing(0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._root_lay.addWidget(self._scroll)

        self._build_initial()

    # ── Scroll-area helpers ────────────────────────────────────────────────────
    def _set_scroll_widget(self, widget: QWidget):
        """Replace the scroll area's inner widget."""
        self._scroll.setWidget(widget)

    def _make_container(self) -> tuple[QWidget, QVBoxLayout]:
        sw = QWidget()
        sl = QVBoxLayout(sw)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.setSpacing(12)
        return sw, sl

    # ── Initial (no results yet) ───────────────────────────────────────────────
    def _build_initial(self):
        c = palette(self._mode)
        sw, sl = self._make_container()

        # Header card
        hdr = QFrame()
        hdr.setStyleSheet(
            f"QFrame {{ background: {pastel(3, self._mode)}; "
            f"border-radius: 16px; border: 1px solid {c['border']}; }}"
        )
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
            card = QFrame()
            card.setProperty("frameClass", "card")
            cl = QVBoxLayout(card)
            cl.setContentsMargins(24, 20, 24, 20)
            cl.addWidget(QLabel("Complete your data to get matches"))
            self._inputs = {}
            for label, key in [("Major", "jurusan"), ("Latest GPA", "ipk"), ("Semester", "sem")]:
                f = QFrame()
                fl = QHBoxLayout(f)
                fl.setContentsMargins(0, 0, 0, 0)
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
            it = QLabel(
                "Click 'Get Recommendations' to analyze your profile\n"
                "and find the best scholarship matches."
            )
            it.setStyleSheet(f"color: {c['text_muted']}; font-size: 13px;")
            it.setAlignment(Qt.AlignmentFlag.AlignCenter)
            il.addWidget(it)
            sl.addWidget(info)

        sl.addStretch()
        self._set_scroll_widget(sw)

    # ── Calculate recommendations ──────────────────────────────────────────────
    def _do_calc(self):
        if not self._profil:
            try:
                self._profil = {
                    "jurusan": self._inputs["jurusan"].text(),
                    "ipk": float(self._inputs["ipk"].text()),
                    "semester": int(self._inputs["sem"].text()),
                    "organisasi": True,
                    "penghasilan_ortu": 5_000_000,
                }
            except (ValueError, AttributeError):
                QMessageBox.warning(self, "Error", "Please enter valid data.")
                return
        self._results = hitung_rekomendasi(self._profil)
        self._build_results()

    # ── Results view ───────────────────────────────────────────────────────────
    def _build_results(self):
        c = palette(self._mode)
        sw, sl = self._make_container()
        sl.setSpacing(8)

        # Header
        hdr = QFrame()
        hdr.setStyleSheet(
            f"QFrame {{ background: {pastel(3, self._mode)}; "
            f"border-radius: 16px; border: 1px solid {c['border']}; }}"
        )
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(24, 14, 24, 14)
        hl.addWidget(QLabel("Your Personalized Matches"))
        hl.addStretch()

        rb = QPushButton("🔄  Refresh")
        rb.setObjectName("btn_outline")
        rb.setFixedHeight(30)
        rb.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        rb.clicked.connect(self._do_calc)
        hl.addWidget(rb)

        # Compare button — only shown when ≥ 2 results
        if self._results and len(self._results) >= 2:
            cmp_btn = QPushButton("⚖️  Bandingkan Beasiswa")
            cmp_btn.setObjectName("btn_outline")
            cmp_btn.setFixedHeight(30)
            cmp_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            cmp_btn.clicked.connect(self._show_compare_select)
            hl.addWidget(cmp_btn)

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
            ll.setContentsMargins(0, 0, 0, 0)
            ll.setSpacing(2)

            rf = QFrame()
            rfl = QHBoxLayout(rf)
            rfl.setContentsMargins(0, 0, 0, 0)
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
            badge.setStyleSheet(
                f"QFrame {{ background: {pastel(i, self._mode)}; border-radius: 12px; }}"
            )
            bc = c["btn_primary"] if skor >= 60 else c["text_accent"]
            bl = QLabel(f"{skor}%")
            bl.setFont(QFont(FONT_FAMILY, 14, QFont.Weight.Bold))
            bl.setStyleSheet(f"color: {bc};")
            bl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            blv = QVBoxLayout(badge)
            blv.setContentsMargins(0, 0, 0, 0)
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
        self._set_scroll_widget(sw)

    # ── Compare: selection panel ───────────────────────────────────────────────
    def _show_compare_select(self):
        """Replace scroll content with the scholarship-picker panel."""
        sw, sl = self._make_container()
        sl.setSpacing(12)

        panel = _CompareSelectPanel(
            hasil=self._results,
            mode=self._mode,
            compare_cb=self._run_compare,
            cancel_cb=self._build_results,
        )
        sl.addWidget(panel)
        sl.addStretch()
        self._set_scroll_widget(sw)

    # ── Compare: run & show result ─────────────────────────────────────────────
    def _run_compare(self, idx_a: int, idx_b: int):
        bea_a = self._results[idx_a]["beasiswa"]
        bea_b = self._results[idx_b]["beasiswa"]
        data = bandingkan_beasiswa(self._profil, bea_a, bea_b)

        sw, sl = self._make_container()
        sl.setSpacing(12)

        panel = _ComparePanel(
            data=data,
            profil=self._profil,
            mode=self._mode,
            back_cb=self._build_results,
        )
        sl.addWidget(panel)
        sl.addStretch()
        self._set_scroll_widget(sw)
