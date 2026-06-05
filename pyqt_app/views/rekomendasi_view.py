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
from pyqt_app.views.eksplorasi_view import CardFrame, DetailDialog


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
        title_lbl = QLabel("Perbandingan Beasiswa")
        title_lbl.setFont(QFont(FONT_FAMILY, 15, QFont.Weight.Bold))
        title_row.addWidget(title_lbl)
        title_row.addStretch()
        
        gradient_style = f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {c['btn_primary']}, stop:1 #81C784);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 0 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #81C784, stop:1 {c['btn_primary']});
            }}
        """
        
        back_style = f"""
            QPushButton {{
                background: {c['btn_primary']}; color: white;
                border: none; border-radius: 12px; padding: 0 20px; font-weight: bold;
            }}
            QPushButton:hover {{ background: {c['btn_primary_hover']}; }}
        """
        
        back_btn = QPushButton("Kembali")
        back_btn.setFixedHeight(32)
        back_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        back_btn.setStyleSheet(back_style)
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
        score_row.setSpacing(16)
        
        green_grad = "qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #FFFFFF, stop:1 #E8F5E9)" if mode == "light" else "qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #2B302C, stop:1 #272E2B)"
        pink_grad = "qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #FFFFFF, stop:1 #FCEBE3)" if mode == "light" else "qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #382928, stop:1 #332B28)"
        
        score_row.addWidget(self._score_card(bea_a["nama"], skor_a, green_grad, mode))
        # VS badge
        vs = QLabel("VS")
        vs.setFont(QFont(FONT_FAMILY, 14, QFont.Weight.Bold))
        vs.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vs.setStyleSheet(f"color: {c['text_muted']}; min-width: 40px; background: transparent;")
        score_row.addWidget(vs)
        score_row.addWidget(self._score_card(bea_b["nama"], skor_b, pink_grad, mode))
        root.addLayout(score_row)

        root.addWidget(_hdivider(c))

        # ── Criteria grid ─────────────────────────────────────────
        grid_lbl = QLabel("Detail Kriteria")
        grid_lbl.setFont(QFont(FONT_FAMILY, 12, QFont.Weight.Bold))
        grid_lbl.setStyleSheet(f"color: {c['text_muted']};")
        root.addWidget(grid_lbl)

        grid_card = QFrame()
        grid_card.setStyleSheet(f"QFrame {{ background: {c['card']}; border: 1px solid {c['border']}; border-radius: 12px; }}")
        
        grid = QGridLayout(grid_card)
        grid.setSpacing(0)
        grid.setContentsMargins(0, 0, 0, 0)
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
                f"background: {pastel(4, mode)}; color: {c['text_dark']}; border: none; "
                f"padding: 10px 10px; border-bottom: 1px solid {c['border']};"
            )
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter if col > 0 else Qt.AlignmentFlag.AlignLeft)
            grid.addWidget(lbl, 0, col)

        for row_i, (ka, kb) in enumerate(zip(krit_a, krit_b), start=1):
            bg = c["card"] if row_i % 2 == 0 else c["bg"]

            # Kriteria label
            lbl_kr = QLabel(ka["label"])
            lbl_kr.setFont(QFont(FONT_FAMILY, 11))
            lbl_kr.setStyleSheet(
                f"background: {bg}; color: {c['text_dark']}; border: none; "
                f"padding: 12px 10px; border-bottom: 1px solid {c['border']};"
            )
            grid.addWidget(lbl_kr, row_i, 0)

            # Beasiswa A cell
            grid.addWidget(self._crit_cell(ka, bg, c), row_i, 1)

            # Beasiswa B cell
            grid.addWidget(self._crit_cell(kb, bg, c), row_i, 2)

        root.addWidget(grid_card)

        # ── Winner line ───────────────────────────────────────────
        if skor_a != skor_b:
            winner_name = bea_a["nama"] if skor_a > skor_b else bea_b["nama"]
            winner_skor = max(skor_a, skor_b)
            wl = QLabel(f"{winner_name} lebih cocok untuk profil Anda  ({winner_skor}%)")
            wl.setFont(QFont(FONT_FAMILY, 12, QFont.Weight.Bold))
            wl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            wl.setStyleSheet(
                f"background: {pastel(3, mode)}; color: #2D6A4F; "
                f"border-radius: 12px; padding: 12px 16px; margin-top: 10px;"
            )
            root.addWidget(wl)
        else:
            tie = QLabel("Keduanya memiliki skor kecocokan yang sama!")
            tie.setFont(QFont(FONT_FAMILY, 11))
            tie.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tie.setStyleSheet(
                f"background: {pastel(1, mode)}; color: {c['text_dark']}; "
                f"border-radius: 10px; padding: 10px 16px;"
            )
            root.addWidget(tie)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _score_card(self, nama: str, skor: int, gradient_str: str, mode: str) -> QFrame:
        c = palette(mode)
        f = QFrame()
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        from PyQt6.QtGui import QColor
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(2)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 15))
        f.setGraphicsEffect(shadow)
        
        f.setStyleSheet(
            f"QFrame {{ background: {gradient_str}; "
            f"border-radius: 14px; border: none; }}"
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
            f"QFrame {{ background: {bg}; padding: 0px; border: none; "
            f"border-bottom: 1px solid {c['border']}; }}"
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

        # Title row with Back button
        title_row = QHBoxLayout()
        t = QLabel("Pilih Dua Beasiswa untuk Dibandingkan")
        t.setFont(QFont(FONT_FAMILY, 15, QFont.Weight.Bold))
        title_row.addWidget(t)
        title_row.addStretch()
        
        back_style = f"""
            QPushButton {{
                background: {c['btn_primary']}; color: white;
                border: none; border-radius: 12px; padding: 0 20px; font-weight: bold;
            }}
            QPushButton:hover {{ background: {c['btn_primary_hover']}; }}
        """
        cancel_btn = QPushButton("Kembali")
        cancel_btn.setFixedHeight(32)
        cancel_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        cancel_btn.setStyleSheet(back_style)
        cancel_btn.clicked.connect(cancel_cb)
        title_row.addWidget(cancel_btn)
        root.addLayout(title_row)

        sub = QLabel("Pilih dua beasiswa yang berbeda dari hasil rekomendasi Anda.")
        sub.setStyleSheet(f"color: {c['text_muted']}; font-size: 13px;")
        root.addWidget(sub)

        root.addSpacing(20)

        names = [f"#{i+1}  {item['beasiswa']['nama']}" for i, item in enumerate(hasil)]

        # VS Arena Layout
        arena_lay = QHBoxLayout()
        arena_lay.setSpacing(20)

        # Card A (Pink gradient border style)
        card_a = QFrame()
        card_a.setStyleSheet(f"QFrame {{ background: {pastel(2, mode)}; border-radius: 16px; padding: 20px; }}")
        card_a.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        lay_a = QVBoxLayout(card_a)
        lay_a.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_a = QLabel("Beasiswa Pertama")
        lbl_a.setFont(QFont(FONT_FAMILY, 13, QFont.Weight.Bold))
        lbl_a.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay_a.addWidget(lbl_a)
        lay_a.addSpacing(10)
        self._combo_a = QComboBox()
        for n in names:
            self._combo_a.addItem(n)
        self._combo_a.setFixedHeight(40)
        self._combo_a.setStyleSheet(f"QComboBox {{ background: {c['card']}; border-radius: 8px; border: 1px solid {c['border']}; padding: 0 12px; font-weight: bold; font-size: 13px; }}")
        lay_a.addWidget(self._combo_a)
        arena_lay.addWidget(card_a)

        # VS Badge
        vs_badge = QLabel("VS")
        vs_badge.setFont(QFont(FONT_FAMILY, 18, QFont.Weight.Black))
        vs_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vs_badge.setFixedSize(60, 60)
        vs_badge.setStyleSheet(f"background: {c['card']}; color: {c['text_dark']}; border-radius: 30px; border: 2px solid {c['border']};")
        arena_lay.addWidget(vs_badge)

        # Card B (Green gradient border style)
        card_b = QFrame()
        card_b.setStyleSheet(f"QFrame {{ background: {pastel(3, mode)}; border-radius: 16px; padding: 20px; }}")
        card_b.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        lay_b = QVBoxLayout(card_b)
        lay_b.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_b = QLabel("Beasiswa Kedua")
        lbl_b.setFont(QFont(FONT_FAMILY, 13, QFont.Weight.Bold))
        lbl_b.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay_b.addWidget(lbl_b)
        lay_b.addSpacing(10)
        self._combo_b = QComboBox()
        for n in names:
            self._combo_b.addItem(n)
        if len(names) > 1:
            self._combo_b.setCurrentIndex(1)
        self._combo_b.setFixedHeight(40)
        self._combo_b.setStyleSheet(f"QComboBox {{ background: {c['card']}; border-radius: 8px; border: 1px solid {c['border']}; padding: 0 12px; font-weight: bold; font-size: 13px; }}")
        lay_b.addWidget(self._combo_b)
        arena_lay.addWidget(card_b)

        root.addLayout(arena_lay)
        root.addSpacing(30)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        gradient_style = f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {c['btn_primary']}, stop:1 #81C784);
                color: white;
                border: none;
                border-radius: 14px;
                padding: 0 40px;
                font-weight: bold;
                font-size: 15px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #81C784, stop:1 {c['btn_primary']});
            }}
        """

        compare_btn = QPushButton("Bandingkan Sekarang")
        compare_btn.setFixedHeight(46)
        compare_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        compare_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        compare_btn.setStyleSheet(gradient_style)
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
        
    def _show_detail(self, bea_data):
        dlg = DetailDialog(bea_data, self._mode, self._pid, self)
        dlg.exec()

    def _make_container(self) -> tuple[QWidget, QVBoxLayout]:
        sw = QWidget()
        sl = QVBoxLayout(sw)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.setSpacing(12)
        return sw, sl

    def _apply_card_shadow(self, widget):
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        from PyQt6.QtGui import QColor
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(2)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 15))
        widget.setGraphicsEffect(shadow)

    def _build_hero(self, c, sl):
        hdr = QFrame()
        hdr.setObjectName("heroCard")
        self._apply_card_shadow(hdr)
        hdr.setFixedHeight(170)
        
        hdr.setStyleSheet(f"""
            #heroCard {{
                background: {c['greet_bg']};
                border-radius: 18px; border: 1px solid {c['greet_border']};
            }}
        """)
        
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(30, 20, 20, 20)
        hl.setSpacing(20)
        
        text_lay = QVBoxLayout()
        text_lay.setContentsMargins(0, 0, 0, 0)
        text_lay.setSpacing(8)
        
        title = QLabel("Temukan Beasiswa\nImpianmu!" if self._bhs == "id" else "Find Your Perfect\nMatch!")
        title.setFont(QFont(FONT_FAMILY, 24, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {c['text_dark']}; background: transparent;")
        text_lay.addWidget(title)
        
        sub = QLabel("Sistem cerdas kami akan menganalisis profil akademikmu\ndan mencocokkannya dengan beasiswa terbaik." if self._bhs == "id" else "Our smart system will analyze your academic profile\nand match it with the best scholarships.")
        sub.setStyleSheet(f"color: {c['text_muted']}; font-size: 14px; background: transparent;")
        text_lay.addWidget(sub)
        text_lay.addStretch()
        
        hl.addLayout(text_lay)
        hl.addStretch()
        
        import os
        from PyQt6.QtGui import QPixmap
        ASSETS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets"))
        img_path = os.path.join(ASSETS, "scholarship_envelope.png")
        if os.path.exists(img_path):
            img_lbl = QLabel()
            pix = QPixmap(img_path).scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            img_lbl.setPixmap(pix)
            img_lbl.setStyleSheet("background: transparent;")
            hl.addWidget(img_lbl)
            
        sl.addWidget(hdr)
        
        # Action Buttons below the hero card
        btn_lay = QHBoxLayout()
        btn_lay.setSpacing(16)
        
        green_gradient_style = f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #EAF5EC, stop:1 #D9ECDF);
                background-color: #E6F0E8;
                color: {c['text_dark']};
                border: 1px solid #D9EADF;
                border-radius: 20px;
                padding: 0 20px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #D9EADF;
            }}
        """
        
        pink_gradient_style = f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FDF2F0, stop:1 #F7E4DF);
                background-color: #FCECE9;
                color: {c['text_dark']};
                border: 1px solid #F7E4DF;
                border-radius: 20px;
                padding: 0 20px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #F7E4DF;
            }}
        """
        
        gb = QPushButton("✨ Dapatkan Rekomendasi" if self._bhs == "id" else "✨ Get Recommendations")
        gb.setFixedHeight(40)
        gb.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        gb.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        gb.setStyleSheet(green_gradient_style)
        gb.clicked.connect(self._do_calc)
        btn_lay.addWidget(gb)
        
        cmp_btn = QPushButton("Bandingkan Beasiswa" if self._bhs == "id" else "Compare Scholarships")
        cmp_btn.setFixedHeight(40)
        cmp_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        cmp_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        cmp_btn.setStyleSheet(pink_gradient_style)
        cmp_btn.clicked.connect(self._show_compare_select)
        btn_lay.addWidget(cmp_btn)
        
        sl.addLayout(btn_lay)

    # ── Initial (no results yet) ───────────────────────────────────────────────
    def _build_initial(self):
        c = palette(self._mode)
        sw, sl = self._make_container()

        self._build_hero(c, sl)
        
        # Empty state
        info = QFrame()
        info.setProperty("frameClass", "card")
        self._apply_card_shadow(info)
        il = QVBoxLayout(info)
        il.setContentsMargins(24, 40, 24, 40)
        
        icon = QLabel("🎯")
        icon.setFont(QFont(FONT_FAMILY, 48))
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("background: transparent;")
        il.addWidget(icon)
        
        it = QLabel("Belum ada rekomendasi yang ditampilkan.\nKlik tombol 'Dapatkan Rekomendasi' di atas untuk memulai!" if self._bhs == "id" else "No recommendations yet.\nClick 'Get Recommendations' above to start!")
        it.setStyleSheet(f"color: {c['text_muted']}; font-size: 13px; background: transparent;")
        it.setAlignment(Qt.AlignmentFlag.AlignCenter)
        il.addWidget(it)
        
        sl.addWidget(info)
        sl.addStretch()
        self._set_scroll_widget(sw)

    # ── Calculate recommendations ──────────────────────────────────────────────
    def _do_calc(self):
        if not self._profil:
            QMessageBox.warning(self, "Profil Belum Lengkap" if self._bhs == "id" else "Profile Incomplete", "Silakan lengkapi data profil Anda di menu Profil terlebih dahulu." if self._bhs == "id" else "Please complete your profile data first.")
            return
        self._results = hitung_rekomendasi(self._profil)
        self._build_results()

    # ── Results view ───────────────────────────────────────────────────────────
    def _build_results(self):
        c = palette(self._mode)
        sw, sl = self._make_container()
        sl.setSpacing(8)

        self._build_hero(c, sl)

        cnt = QLabel(f"Ditemukan {len(self._results)} kecocokan beasiswa" if self._bhs == "id" else f"Found {len(self._results)} scholarship matches")
        cnt.setFont(QFont(FONT_FAMILY, 14, QFont.Weight.Bold))
        cnt.setStyleSheet(f"color: {c['text_dark']}; margin-top: 10px; margin-bottom: 6px;")
        sl.addWidget(cnt)

        for i, item in enumerate(self._results):
            bea = item["beasiswa"]
            skor = item["skor"]

            card = CardFrame(bea)
            card.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            card.clicked.connect(self._show_detail)
            
            # Highlight #1 match
            if i == 0:
                card.setStyleSheet(f"QFrame {{ background: {pastel(3, self._mode)}; border: 2px solid {c['btn_primary']}; border-radius: 14px; }}")
            else:
                card.setProperty("frameClass", "card")
                
            cl = QHBoxLayout(card)
            cl.setContentsMargins(20, 14, 20, 14)

            left = QFrame()
            ll = QVBoxLayout(left)
            ll.setContentsMargins(0, 0, 0, 0)
            ll.setSpacing(2)

            title_lay = QHBoxLayout()
            title_lay.setSpacing(10)
            
            rk = QLabel(f"#{i+1}")
            rk_font = 26 if i == 0 else 18
            rk.setFont(QFont(FONT_FAMILY, rk_font, QFont.Weight.Black, italic=True))
            rk.setStyleSheet(f"color: {c['text_accent']};")
            title_lay.addWidget(rk)

            n = QLabel(bea["nama"])
            n.setFont(QFont(FONT_FAMILY, 14, QFont.Weight.Bold))
            title_lay.addWidget(n)
            
            if i == 0:
                bm = QLabel(" Best Match")
                bm.setStyleSheet(f"color: {c['btn_primary']}; font-weight: bold; font-size: 12px; padding-left: 10px;")
                title_lay.addWidget(bm)
                
            title_lay.addStretch()
            ll.addLayout(title_lay)

            info = QLabel(f"Min IPK: {bea['min_ipk']}  |  Max Sem: {bea['max_semester']}")
            info.setStyleSheet(f"color: {c['text_muted']}; font-size: 12px;")
            ll.addWidget(info)

            cl.addWidget(left)
            cl.addStretch()

            badge = QFrame()
            badge.setFixedSize(80, 50)
            badge.setStyleSheet(
                f"QFrame {{ background: {pastel(i, self._mode)}; border-radius: 12px; }}"
            )
            bc = c["btn_primary"] if skor >= 60 else c["text_accent"]
            bl = QLabel(f"{skor}%")
            bl.setFont(QFont(FONT_FAMILY, 16, QFont.Weight.Bold))
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
        if not getattr(self, '_results', None) or len(self._results) < 2:
            QMessageBox.warning(self, "Belum Ada Hasil" if self._bhs == "id" else "No Results", "Dapatkan rekomendasi terlebih dahulu, minimal 2 beasiswa diperlukan untuk membandingkan." if self._bhs == "id" else "Get recommendations first, at least 2 scholarships are required to compare.")
            return

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
