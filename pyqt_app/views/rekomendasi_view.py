"""
pyqt_app/views/rekomendasi_view.py
Recommendations page with scholarship comparison feature.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QLineEdit, QMessageBox, QComboBox,
    QSizePolicy, QGridLayout, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor, QColor

from pyqt_app.styles.theme import FONT_FAMILY, palette, pastel, grad_green, grad_peach
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
        root.setContentsMargins(16, 14, 16, 16)
        root.setSpacing(8)

        # ── Title row ────────────────────────────────────────────
        title_row = QHBoxLayout()
        title_lbl = QLabel("Perbandingan Beasiswa")
        title_lbl.setFont(QFont(FONT_FAMILY, 13, QFont.Weight.Bold))
        title_row.addWidget(title_lbl)
        title_row.addStretch()
        
        back_style = f"""
            QPushButton {{
                background: {c['card']}; color: {c['text_dark']};
                border: 1px solid {c['border']}; border-radius: 6px; padding: 6px 14px; font-weight: bold; font-size: 13px;
            }}
            QPushButton:hover {{ background: {c['bg']}; }}
        """
        
        back_btn = QPushButton("← Kembali" if profil.get("bhs", "id") == "id" else "← Back")
        back_btn.setFixedHeight(32)
        back_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        back_btn.setStyleSheet(back_style)
        back_btn.clicked.connect(back_cb)
        title_row.addWidget(back_btn)
        root.addLayout(title_row)

        root.addSpacing(4)

        if not data:
            root.addWidget(QLabel("Gagal memuat data perbandingan."))
            return

        bea_a = data["a"]["beasiswa"]
        bea_b = data["b"]["beasiswa"]
        skor_a = data["a"]["skor"]
        skor_b = data["b"]["skor"]
        krit_a = data["a"]["kriteria"]
        krit_b = data["b"]["kriteria"]

        # ── Side-by-side Cards ────────────────────────────────────
        arena_lay = QHBoxLayout()
        # ── Side-by-side Cards ────────────────────────────────────
        arena_lay = QHBoxLayout()
        arena_lay.setSpacing(12)

        if self._mode == 'dark':
            grad_a = f"qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3D2E28, stop:1 #4A3028)"
            grad_b = f"qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2A3D2E, stop:1 #2E3830)"
        else:
            grad_a = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #FFF5F5, stop:1 #FFE4D6)"
            grad_b = "qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #EFFFF4, stop:1 #D4EEDC)"

        card_a = self._build_comparison_column(bea_a, skor_a, krit_a, grad_a, c)
        card_b = self._build_comparison_column(bea_b, skor_b, krit_b, grad_b, c)

        arena_lay.addWidget(card_a, 1)
        arena_lay.addWidget(card_b, 1)

        root.addLayout(arena_lay)
        
        root.addSpacing(4)
        
        # ── Winner line ───────────────────────────────────────────
        if skor_a != skor_b:
            winner_name = bea_a["nama"] if skor_a > skor_b else bea_b["nama"]
            winner_skor = max(skor_a, skor_b)
            wl = QLabel(f"{winner_name} lebih cocok untuk profil Anda  ({winner_skor}%)")
            wl.setFont(QFont(FONT_FAMILY, 12, QFont.Weight.Bold))
            wl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            _win_text = c['sidebar_active_tx']
            wl.setStyleSheet(
                f"background: {pastel(3, self._mode)}; color: {_win_text}; "
                f"border-radius: 12px; padding: 12px 16px;"
            )
            root.addWidget(wl)
        else:
            tie = QLabel("Keduanya memiliki skor kecocokan yang sama!")
            tie.setFont(QFont(FONT_FAMILY, 11))
            tie.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tie.setStyleSheet(
                f"background: {pastel(1, self._mode)}; color: {c['text_dark']}; "
                f"border-radius: 10px; padding: 10px 16px;"
            )
            root.addWidget(tie)

    def _get_icon(self, label: str) -> str:
        label = label.lower()
        if "ipk" in label: return "📖"
        if "semester" in label: return "🕒"
        if "jurusan" in label: return "🎓"
        if "organisasi" in label: return "👥"
        if "penghasilan" in label or "gaji" in label: return "💰"
        return "📌"

    def _build_comparison_column(self, bea: dict, skor: int, kriteria: list, grad: str, c: dict) -> QFrame:
        f = QFrame()
        f.setStyleSheet(f"""
            QFrame#compCard {{
                background: {grad};
                border-radius: 20px;
            }}
        """)
        f.setObjectName("compCard")
        f.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        from PyQt6.QtGui import QColor
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 4)
        f.setGraphicsEffect(shadow)

        vl = QVBoxLayout(f)
        vl.setContentsMargins(14, 14, 14, 14)
        vl.setSpacing(6)

        nama = bea.get("nama", "")
        if len(nama) > 60:
            nama = nama[:57] + "..."
        name_lbl = QLabel(nama)
        name_lbl.setFont(QFont(FONT_FAMILY, 10, QFont.Weight.Bold))
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_lbl.setStyleSheet(f"color: {c['text_dark']}; background: transparent; margin-bottom: 4px;")
        name_lbl.setWordWrap(True)
        name_lbl.setToolTip(bea.get("nama", ""))
        vl.addWidget(name_lbl)

        match_txt = "Sangat Cocok" if skor >= 80 else ("Cocok" if skor >= 60 else ("Cukup" if skor >= 40 else "Kurang Cocok"))
        
        pr_lay = QHBoxLayout()
        pr_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        circle = QFrame()
        circle.setFixedSize(80, 80)
        _circle_bg = 'rgba(255, 255, 255, 0.6)' if self._mode == 'light' else 'rgba(60, 64, 67, 0.6)'
        _circle_bd = 'rgba(255, 255, 255, 0.9)' if self._mode == 'light' else 'rgba(80, 84, 87, 0.9)'
        circle.setStyleSheet(f"""
            QFrame {{
                background: {_circle_bg};
                border: 3px solid {_circle_bd};
                border-radius: 40px;
            }}
        """)
        
        circle_lay = QVBoxLayout(circle)
        circle_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        circle_lay.setContentsMargins(0, 0, 0, 0)
        circle_lay.setSpacing(0)
        
        skor_lbl = QLabel(f"{skor}%")
        skor_lbl.setFont(QFont(FONT_FAMILY, 20, QFont.Weight.Black))
        skor_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        skor_lbl.setStyleSheet(f"color: {c['text_dark']}; background: transparent; border: none;")
        circle_lay.addWidget(skor_lbl)
        
        match_lbl = QLabel(match_txt)
        match_lbl.setFont(QFont(FONT_FAMILY, 8, QFont.Weight.Bold))
        match_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        match_col = c['sidebar_active_tx'] if skor >= 60 else c['danger']
        match_lbl.setStyleSheet(f"color: {match_col}; background: transparent; border: none;")
        circle_lay.addWidget(match_lbl)
        
        pr_lay.addWidget(circle)
        vl.addLayout(pr_lay)
        vl.addSpacing(6)

        for k in kriteria:
            row = QFrame()
            _row_bg = 'rgba(255, 255, 255, 0.45)' if self._mode == 'light' else 'rgba(60, 64, 67, 0.35)'
            row.setStyleSheet(f"""
                QFrame {{
                    background: {_row_bg};
                    border-radius: 18px;
                }}
            """)
            rl = QHBoxLayout(row)
            rl.setContentsMargins(10, 6, 10, 6)
            rl.setSpacing(6)

            icon = QLabel(self._get_icon(k["label"]))
            icon.setStyleSheet("background: transparent;")
            rl.addWidget(icon)

            k_lbl = QLabel(k["label"])
            k_lbl.setFont(QFont(FONT_FAMILY, 9, QFont.Weight.Bold))
            k_lbl.setStyleSheet(f"color: {c['text_dark']}; background: transparent;")
            rl.addWidget(k_lbl)

            rl.addStretch()

            v_val = k["nilai"]
            val_lbl = QLabel(f"{v_val}")
            val_lbl.setFont(QFont(FONT_FAMILY, 9, QFont.Weight.Bold))
            val_col = c['text_dark'] if k["lulus"] else c['danger']
            val_lbl.setStyleSheet(f"color: {val_col}; background: transparent;")
            rl.addWidget(val_lbl)

            vl.addWidget(row)

        vl.addStretch()
        return f

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

    def __init__(self, hasil: list, mode: str, compare_cb, cancel_cb, bhs: str = "id", parent=None):
        super().__init__(parent)
        self._hasil = hasil
        self._mode = mode
        self._bhs = bhs
        c = palette(mode)

        self.setProperty("frameClass", "card")
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(8)

        # Back button row
        back_row = QHBoxLayout()
        back_style = f"""
            QPushButton {{
                background: {c['card']}; color: {c['text_dark']};
                border: 1px solid {c['border']}; border-radius: 6px; padding: 6px 14px; font-weight: bold; font-size: 13px;
            }}
            QPushButton:hover {{ background: {c['bg']}; }}
        """
        cancel_btn = QPushButton("← Kembali" if self._bhs == "id" else "← Back")
        cancel_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        cancel_btn.setStyleSheet(back_style)
        cancel_btn.clicked.connect(cancel_cb)
        back_row.addWidget(cancel_btn)
        back_row.addStretch()
        root.addLayout(back_row)
        
        root.addSpacing(8)

        t = QLabel("Pilih Dua Beasiswa untuk Dibandingkan" if self._bhs == "id" else "Select Two Scholarships to Compare")
        t.setFont(QFont(FONT_FAMILY, 13, QFont.Weight.Bold))
        root.addWidget(t)

        sub = QLabel("Pilih dua beasiswa yang berbeda dari hasil rekomendasi Anda." if self._bhs == "id" else "Select two different scholarships from your recommendations.")
        sub.setStyleSheet(f"color: {c['text_muted']}; font-size: 11px;")
        root.addWidget(sub)

        root.addSpacing(10)

        names = [f"#{i+1}  {item['beasiswa']['nama']}" for i, item in enumerate(hasil)]

        # ── Vertical layout: Dropdown A → VS → Dropdown B ──
        # Beasiswa A
        lbl_a = QLabel("Beasiswa Pertama" if self._bhs == "id" else "First Scholarship")
        lbl_a.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Bold))
        lbl_a.setStyleSheet(f"color: {c['text_dark']};")
        root.addWidget(lbl_a)

        self._combo_a = QComboBox()
        for n in names:
            self._combo_a.addItem(n)
        self._combo_a.setFixedHeight(36)
        if self._mode == 'dark':
            _combo_a_bg = f"qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {c['card']}, stop:1 #4A3028)"
        else:
            _combo_a_bg = "qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #FFFFFF, stop:1 #FAD6D0)"
        self._combo_a.setStyleSheet(f"""
            QComboBox {{ 
                background: {_combo_a_bg};
                border-radius: 10px; border: 1px solid {c['border']}; 
                padding: 0 12px; font-weight: bold; font-size: 11px; color: {c['text_dark']};
            }}
            QComboBox::drop-down {{ border: none; }}
        """)
        root.addWidget(self._combo_a)

        # VS Badge — centered
        vs_row = QHBoxLayout()
        vs_row.addStretch()
        vs_badge = QLabel("VS")
        vs_badge.setFont(QFont(FONT_FAMILY, 12, QFont.Weight.Black))
        vs_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vs_badge.setFixedSize(36, 36)
        vs_badge.setStyleSheet(f"background: {c['card']}; color: {c['text_muted']}; border-radius: 18px;")
        vs_row.addWidget(vs_badge)
        vs_row.addStretch()
        root.addLayout(vs_row)

        # Beasiswa B
        lbl_b = QLabel("Beasiswa Kedua" if self._bhs == "id" else "Second Scholarship")
        lbl_b.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Bold))
        lbl_b.setStyleSheet(f"color: {c['text_dark']};")
        root.addWidget(lbl_b)

        self._combo_b = QComboBox()
        for n in names:
            self._combo_b.addItem(n)
        if len(names) > 1:
            self._combo_b.setCurrentIndex(1)
        self._combo_b.setFixedHeight(36)
        if self._mode == 'dark':
            _combo_b_bg = f"qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {c['card']}, stop:1 #2A3D2E)"
        else:
            _combo_b_bg = "qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #FFFFFF, stop:1 #C8E6D3)"
        self._combo_b.setStyleSheet(f"""
            QComboBox {{ 
                background: {_combo_b_bg};
                border-radius: 10px; border: 1px solid {c['border']}; 
                padding: 0 12px; font-weight: bold; font-size: 11px; color: {c['text_dark']};
            }}
            QComboBox::drop-down {{ border: none; }}
        """)
        root.addWidget(self._combo_b)
        root.addSpacing(12)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        if self._mode == 'dark':
            _cmp_bg = f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2E3830, stop:1 #2A3D2E)"
            _cmp_hvr = f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2A3D2E, stop:1 #2E3830)"
            _cmp_border = c['border']
        else:
            _cmp_bg = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #B6CCBC, stop:1 #97B79E)"
            _cmp_hvr = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #97B79E, stop:1 #B6CCBC)"
            _cmp_border = "#E6EFE8"
        gradient_style = f"""
            QPushButton {{
                background: {_cmp_bg};
                color: {c['text_light']};
                border: 2px solid {_cmp_border};
                border-radius: 20px;
                padding: 0 40px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: {_cmp_hvr};
            }}
        """

        compare_btn = QPushButton("Bandingkan Sekarang")
        compare_btn.setFixedHeight(40)
        compare_btn.setMinimumWidth(300)
        compare_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        compare_btn.setStyleSheet(gradient_style)
        compare_btn.clicked.connect(self._on_compare)
        
        shadow_btn = QGraphicsDropShadowEffect()
        shadow_btn.setBlurRadius(15)
        shadow_btn.setColor(QColor(0, 0, 0, 20))
        shadow_btn.setOffset(0, 4)
        compare_btn.setGraphicsEffect(shadow_btn)
        
        btn_row.addWidget(compare_btn)
        btn_row.addStretch()
        
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
        
        if self._mode == 'dark':
            _hero_grad = f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {c['card']}, stop:1 #332A28)"
            _hero_border = c['border']
        else:
            _hero_grad = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FFFFFF, stop:1 #FCEAE9)"
            _hero_border = "#FADED7"
        hdr.setStyleSheet(f"""
            #heroCard {{
                background: {_hero_grad};
                border-radius: 18px; border: 1px solid {_hero_border};
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
                background: {grad_green(c)};
                color: {c['text_dark']};
                border: none;
                border-radius: 12px;
                padding: 0 20px;
                font-weight: bold; font-size: 13px;
            }}
        """
        
        pink_gradient_style = f"""
            QPushButton {{
                background: {grad_peach(c)};
                color: {c['text_dark']};
                border: none;
                border-radius: 12px;
                padding: 0 20px;
                font-weight: bold; font-size: 13px;
            }}
        """
        
        gb = QPushButton("✨ Dapatkan Rekomendasi" if self._bhs == "id" else "✨ Get Recommendations")
        gb.setFixedHeight(40)
        gb.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        gb.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        gb.setStyleSheet(green_gradient_style)
        gb.clicked.connect(self._do_calc)
        btn_lay.addWidget(gb)
        
        cmp_btn = QPushButton("🔀 Bandingkan Beasiswa" if self._bhs == "id" else "🔀 Compare Scholarships")
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
        info.setObjectName("emptyCard")
        if self._mode == 'dark':
            _empty_grad = f"qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {c['card']}, stop:1 #332A28)"
            _empty_border = c['border']
        else:
            _empty_grad = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FFFFFF, stop:1 #FCEAE9)"
            _empty_border = "#FADED7"
        info.setStyleSheet(f"""
            #emptyCard {{
                background: {_empty_grad};
                border-radius: 18px; border: 1px solid {_empty_border};
            }}
        """)
        self._apply_card_shadow(info)
        il = QVBoxLayout(info)
        il.setContentsMargins(24, 40, 24, 40)
        
        icon = QLabel("🎯")
        icon.setFont(QFont(FONT_FAMILY, 48))
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("background: transparent;")
        il.addWidget(icon)
        
        it = QLabel("Belum ada rekomendasi yang ditampilkan.\nKlik tombol 'Dapatkan Rekomendasi' di atas untuk memulai!" if self._bhs == "id" else "No recommendations yet.\nClick 'Get Recommendations' above to start!")
        it.setStyleSheet(f"color: {c['text_dark']}; font-size: 13px; background: transparent;")
        it.setAlignment(Qt.AlignmentFlag.AlignCenter)
        il.addWidget(it)
        
        sl.addWidget(info)
        sl.addStretch()
        self._set_scroll_widget(sw)

    # ── Calculate recommendations ──────────────────────────────────────────────
    def _do_calc(self):
        if not self._profil:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Profil Belum Lengkap" if self._bhs == "id" else "Profile Incomplete")
            msg.setText("Silakan lengkapi data profil Anda di menu Profil terlebih dahulu." if self._bhs == "id" else "Please complete your profile data first.")
            c = palette(self._mode)
            msg.setStyleSheet(f"""
                QMessageBox {{ background-color: {c['bg']}; }} 
                QLabel {{ color: {c['text_dark']}; }}
                QPushButton {{ background-color: {c['btn_primary']}; color: white; padding: 6px 16px; border-radius: 4px; border: none; font-weight: bold; }}
            """)
            msg.exec()
            return
        self._results = hitung_rekomendasi(self._profil)
        self._build_results()

    # ── Results view ───────────────────────────────────────────────────────────
    def _build_results(self):
        c = palette(self._mode)
        sw, sl = self._make_container()
        sl.setSpacing(8)

        self._build_hero(c, sl)

        # Tampilkan top 20 saja (bukan 148)
        top_results = self._results[:20]
        cnt = QLabel(f"Top {len(top_results)} dari {len(self._results)} beasiswa tercocok" if self._bhs == "id" else f"Top {len(top_results)} of {len(self._results)} matched scholarships")
        cnt.setFont(QFont(FONT_FAMILY, 13, QFont.Weight.Bold))
        cnt.setStyleSheet(f"color: {c['text_dark']}; margin-top: 8px; margin-bottom: 4px;")
        sl.addWidget(cnt)

        for i, item in enumerate(top_results):
            bea = item["beasiswa"]
            skor = item["skor"]

            card = CardFrame(bea)
            card.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            card.clicked.connect(self._show_detail)
            card.setFixedHeight(70)
            
            # Highlight #1 match
            if i == 0:
                bg_col = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #EAF5EC, stop:1 #DFF0E2)" if self._mode == "light" else c['sidebar_active_bg']
                card.setStyleSheet(f"QFrame {{ background: {bg_col}; border: none; border-radius: 12px; }}")
                
                shadow_c1 = QGraphicsDropShadowEffect()
                shadow_c1.setBlurRadius(15)
                shadow_c1.setColor(QColor(168, 197, 176, 150))
                shadow_c1.setOffset(0, 4)
                card.setGraphicsEffect(shadow_c1)
            else:
                card.setProperty("frameClass", "card")
                
            cl = QHBoxLayout(card)
            cl.setContentsMargins(16, 8, 16, 8)

            left = QFrame()
            left.setStyleSheet("background: transparent;")
            ll = QVBoxLayout(left)
            ll.setContentsMargins(0, 0, 0, 0)
            ll.setSpacing(2)

            title_lay = QHBoxLayout()
            title_lay.setSpacing(8)
            
            rk = QLabel(f"#{i+1}")
            rk_font = 16 if i == 0 else 12
            rk.setFont(QFont(FONT_FAMILY, rk_font, QFont.Weight.Black, italic=True))
            rk.setStyleSheet(f"color: {c['text_accent']}; background: transparent;")
            title_lay.addWidget(rk)

            nama = bea.get("nama", "")
            if len(nama) > 80:
                nama = nama[:77] + "..."
            n = QLabel(nama)
            n.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Bold))
            n.setWordWrap(False)
            n.setStyleSheet("background: transparent;")
            n.setToolTip(bea.get("nama", ""))
            title_lay.addWidget(n)
            
            title_lay.addStretch()
            ll.addLayout(title_lay)

            # Subtitle: penyelenggara + jenjang + deadline
            sub_parts = []
            if bea.get("penyelenggara"):
                sub_parts.append(bea["penyelenggara"])
            if bea.get("jenjang"):
                sub_parts.append(bea["jenjang"])
            if bea.get("deadline"):
                sub_parts.append(f"Deadline: {bea['deadline']}")
            if sub_parts:
                sub = QLabel(" • ".join(sub_parts))
                sub.setStyleSheet(f"color: {c['text_muted']}; font-size: 10px; background: transparent;")
                ll.addWidget(sub)

            cl.addWidget(left)
            cl.addStretch()

            right = QFrame()
            right.setStyleSheet("background: transparent;")
            rl = QVBoxLayout(right)
            rl.setContentsMargins(0, 0, 0, 0)
            rl.setSpacing(0)
            rl.setAlignment(Qt.AlignmentFlag.AlignCenter)

            from pyqt_app.widgets.progress_ring import ProgressRing
            
            if i == 0:
                badge = QLabel(f"{skor}%")
                badge.setFixedSize(44, 44)
                badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
                badge.setStyleSheet(f"background: {c['btn_primary']}; color: white; border-radius: 22px; font-weight: 900; font-size: 13px;")
                rl.addWidget(badge, alignment=Qt.AlignmentFlag.AlignCenter)
            else:
                ring = ProgressRing(skor, 44, 3, bg_color=c['border'], fg_color=c['text_accent'], text_color=c['text_dark'], subtitle="")
                rl.addWidget(ring, alignment=Qt.AlignmentFlag.AlignCenter)

            cl.addWidget(right)
            sl.addWidget(card)

        # Smart tips
        if self._results:
            top = self._results[0]["beasiswa"]
            saran = get_analisis(self._profil, top)
            th = QLabel("Smart Tips For You")
            th.setFont(QFont(FONT_FAMILY, 13, QFont.Weight.Bold))
            sl.addWidget(th)
            tc = QFrame()
            tc.setProperty("frameClass", "card")
            tcl = QVBoxLayout(tc)
            tcl.setContentsMargins(16, 12, 16, 12)
            tcl.addWidget(QLabel(f"Based on your #1 match: {top.get('nama', '')}"))
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
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Belum Ada Hasil" if self._bhs == "id" else "No Results")
            msg.setText("Dapatkan rekomendasi terlebih dahulu, minimal 2 beasiswa diperlukan untuk membandingkan." if self._bhs == "id" else "Get recommendations first, at least 2 scholarships are required to compare.")
            c = palette(self._mode)
            msg.setStyleSheet(f"""
                QMessageBox {{ background-color: {c['bg']}; }} 
                QLabel {{ color: {c['text_dark']}; }}
                QPushButton {{ background-color: {c['btn_primary']}; color: white; padding: 6px 16px; border-radius: 4px; border: none; font-weight: bold; }}
            """)
            msg.exec()
            return

        """Replace scroll content with the scholarship-picker panel."""
        sw, sl = self._make_container()
        sl.setSpacing(12)

        panel = _CompareSelectPanel(
            hasil=self._results,
            mode=self._mode,
            compare_cb=self._run_compare,
            cancel_cb=self._build_results,
            bhs=self._bhs,
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
