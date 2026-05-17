"""
pyqt_app/views/home_view.py
Home page after login — choose existing profile or create a new one.
Matches the Beaply Figma reference design.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QGraphicsDropShadowEffect, QLineEdit,
    QComboBox, QCheckBox, QMessageBox
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import (
    QFont, QPixmap, QCursor, QLinearGradient, QPainter,
    QColor, QBrush
)
import os

from pyqt_app.styles.theme import FONT_FAMILY

from controllers.profil_controller import (
    tampil_semua_profil, input_data_wajib, input_data_spesifik, simpan_profil,
)


# ═══════════════════════════════════════════════════════════════
# Gradient Background (reuse same style as auth)
# ═══════════════════════════════════════════════════════════════

class GradientBackground(QWidget):
    """Paints a soft diagonal pastel gradient as the full background."""

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        grad = QLinearGradient(0, 0, self.width(), self.height())
        grad.setColorAt(0.0, QColor("#F5E6DC"))
        grad.setColorAt(0.3, QColor("#F0EBE3"))
        grad.setColorAt(0.6, QColor("#E8EDE4"))
        grad.setColorAt(1.0, QColor("#D8DFD0"))
        painter.fillRect(self.rect(), QBrush(grad))
        painter.end()


# ═══════════════════════════════════════════════════════════════
# Home View — Choose / Create Profile
# ═══════════════════════════════════════════════════════════════

class HomeView(QWidget):
    """
    After login, show two options:
      - 'Buat Profil Baru' → create profile form
      - 'Pilih Profil'      → list existing profiles
    Emits profile_selected(int) with the chosen profil_id.
    """

    profile_selected = pyqtSignal(int)

    # ── Colour tokens ─────────────────────────────────────────
    CARD_BG       = "#FFFFFF"
    BTN_GREEN     = "#A8C5B0"
    BTN_GREEN_HVR = "#8FB898"
    TEXT_DARK     = "#2D2D2D"
    TEXT_MUTED    = "#888888"
    TEXT_ACCENT   = "#D4917B"
    BORDER        = "#E8E0D8"
    BTN_PALE      = "#E2EBE5"
    INPUT_BG      = "#F0ECE8"

    def __init__(self, user_id, parent=None):
        super().__init__(parent)
        self._user_id = user_id

        root_lay = QVBoxLayout(self)
        root_lay.setContentsMargins(0, 0, 0, 0)
        root_lay.setSpacing(0)

        # Gradient background
        self._bg = GradientBackground()
        bg_lay = QVBoxLayout(self._bg)
        bg_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bg_lay.setContentsMargins(0, 0, 0, 0)
        root_lay.addWidget(self._bg)

        # Card
        self._card = QFrame()
        self._card.setObjectName("HomeCard")
        self._card.setFixedSize(480, 400)
        self._card.setStyleSheet(f"""
            #HomeCard {{
                background-color: {self.CARD_BG};
                border-radius: 20px;
                border: none;
            }}
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 30))
        self._card.setGraphicsEffect(shadow)

        self._card_lay = QVBoxLayout(self._card)
        self._card_lay.setContentsMargins(50, 36, 50, 36)
        self._card_lay.setSpacing(0)
        bg_lay.addWidget(self._card)

        self._build_home()

    # ── Home Page (buttons) ──────────────────────────────────
    def _build_home(self):
        self._clear_card()
        lay = self._card_lay
        self._card.setFixedSize(480, 400)

        # Logo
        self._add_logo(lay)
        lay.addSpacing(8)

        # Tagline
        tag = QLabel("Temukan Beasiswa Terbaik Untuk Anda")
        tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tag.setStyleSheet(f"color: {self.TEXT_MUTED}; font-size: 12px; background: transparent;")
        lay.addWidget(tag)
        lay.addSpacing(28)

        # Button: Buat Profil Baru
        btn_buat = QPushButton("Buat Profil Baru")
        btn_buat.setFixedHeight(46)
        btn_buat.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_buat.setFont(QFont(FONT_FAMILY, 13, QFont.Weight.Bold))
        btn_buat.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.BTN_GREEN};
                color: {self.TEXT_DARK};
                border: none;
                border-radius: 14px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {self.BTN_GREEN_HVR};
            }}
        """)
        btn_buat.clicked.connect(self._show_create_form)
        lay.addWidget(btn_buat)
        lay.addSpacing(10)

        # Button: Pilih Profil
        btn_pilih = QPushButton("Pilih Profil")
        btn_pilih.setFixedHeight(46)
        btn_pilih.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_pilih.setFont(QFont(FONT_FAMILY, 13))
        btn_pilih.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {self.TEXT_DARK};
                border: 1px solid {self.BORDER};
                border-radius: 14px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {self.BTN_PALE};
            }}
        """)
        btn_pilih.clicked.connect(self._show_profiles)
        lay.addWidget(btn_pilih)

        lay.addStretch()

    # ── Profile List ─────────────────────────────────────────
    def _show_profiles(self):
        profiles = tampil_semua_profil(self._user_id)
        if not profiles:
            QMessageBox.information(self, "Info", "Belum ada profil. Silakan buat profil baru.")
            return
        self._clear_card()
        lay = self._card_lay
        self._card.setFixedSize(480, 520)

        # Back button
        back = self._make_link_btn("← Kembali")
        back.clicked.connect(self._build_home)
        lay.addWidget(back, alignment=Qt.AlignmentFlag.AlignLeft)

        title = QLabel("Pilih Profil")
        title.setFont(QFont(FONT_FAMILY, 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(f"color: {self.TEXT_DARK}; background: transparent;")
        lay.addWidget(title)
        lay.addSpacing(12)

        # Scrollable profile list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollArea > QWidget > QWidget { background: transparent; }
        """)
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background: transparent;")
        scroll_lay = QVBoxLayout(scroll_widget)
        scroll_lay.setContentsMargins(0, 0, 0, 0)
        scroll_lay.setSpacing(8)

        for p in profiles:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {self.CARD_BG};
                    border: 1px solid {self.BORDER};
                    border-radius: 12px;
                }}
                QFrame:hover {{
                    border-color: {self.BTN_GREEN};
                }}
            """)
            card_inner = QVBoxLayout(card)
            card_inner.setContentsMargins(16, 12, 16, 12)
            card_inner.setSpacing(4)

            name = QLabel(p["nama"])
            name.setFont(QFont(FONT_FAMILY, 13, QFont.Weight.Bold))
            name.setStyleSheet(f"color: {self.TEXT_DARK}; background: transparent; border: none;")
            card_inner.addWidget(name)

            info = QLabel(f"{p['jenjang']} — {p['jurusan']} • {p['kampus']}")
            info.setFont(QFont(FONT_FAMILY, 10))
            info.setStyleSheet(f"color: {self.TEXT_MUTED}; background: transparent; border: none;")
            card_inner.addWidget(info)

            btn = QPushButton("Pilih Profil Ini")
            btn.setFixedHeight(32)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setFont(QFont(FONT_FAMILY, 10, QFont.Weight.Bold))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.BTN_GREEN};
                    color: {self.TEXT_DARK};
                    border: none;
                    border-radius: 8px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {self.BTN_GREEN_HVR};
                }}
            """)
            pid = p["id"]
            btn.clicked.connect(lambda checked, _pid=pid: self.profile_selected.emit(_pid))
            card_inner.addWidget(btn)

            scroll_lay.addWidget(card)

        scroll_lay.addStretch()
        scroll.setWidget(scroll_widget)
        lay.addWidget(scroll, 1)

    # ── Helper: make input field ────────────────────────────────
    def _make_input(self, ph="", echo=QLineEdit.EchoMode.Normal):
        inp = QLineEdit()
        inp.setPlaceholderText(ph)
        inp.setFixedHeight(44)
        inp.setEchoMode(echo)
        inp.setFont(QFont(FONT_FAMILY, 11))
        inp.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.INPUT_BG};
                color: {self.TEXT_DARK};
                border: none;
                border-radius: 12px;
                padding: 10px 16px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 2px solid {self.BTN_GREEN};
            }}
        """)
        return inp

    def _make_combo(self, items):
        c = QComboBox()
        c.addItems(items)
        c.setFixedHeight(44)
        c.setStyleSheet(f"""
            QComboBox {{
                background-color: {self.INPUT_BG};
                color: {self.TEXT_DARK};
                border: none;
                border-radius: 12px;
                padding: 10px 16px;
                font-size: 13px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
                subcontrol-position: center right;
            }}
        """)
        return c

    def _make_field_label(self, text):
        lbl = QLabel(text)
        lbl.setFont(QFont(FONT_FAMILY, 11))
        lbl.setStyleSheet(f"color: {self.TEXT_DARK}; background: transparent; margin-bottom: 0px;")
        return lbl

    # ── Create Profile Form (Two-Column Figma Design) ────────
    def _show_create_form(self):
        self._clear_card()
        lay = self._card_lay
        self._card.setFixedSize(900, 680)

        # Logo at top
        self._add_logo(lay)
        lay.addSpacing(4)

        # Subtitle
        sub = QLabel("Complete your personal data")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"color: {self.TEXT_MUTED}; font-size: 12px; background: transparent;")
        lay.addWidget(sub)
        lay.addSpacing(12)

        # Scroll area for two-column form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea { background: transparent; border: none; }
            QScrollArea > QWidget > QWidget { background: transparent; }
        """)
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background: transparent;")
        columns_lay = QHBoxLayout(scroll_widget)
        columns_lay.setContentsMargins(0, 0, 8, 0)
        columns_lay.setSpacing(30)

        # ── LEFT COLUMN: Required Data ──
        left = QWidget()
        left.setStyleSheet("background: transparent;")
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(4)

        sec1 = QLabel("Required Data")
        sec1.setFont(QFont(FONT_FAMILY, 14, QFont.Weight.Bold))
        sec1.setStyleSheet(f"color: {self.TEXT_DARK}; background: transparent;")
        ll.addWidget(sec1)
        ll.addSpacing(8)

        ll.addWidget(self._make_field_label("Full Name*"))
        self._f_nama = self._make_input()
        ll.addWidget(self._f_nama); ll.addSpacing(4)

        ll.addWidget(self._make_field_label("Email*"))
        self._f_email = self._make_input()
        ll.addWidget(self._f_email); ll.addSpacing(4)

        ll.addWidget(self._make_field_label("Date of Birth*"))
        self._f_tgl = self._make_input("YYYY-MM-DD")
        ll.addWidget(self._f_tgl); ll.addSpacing(4)

        ll.addWidget(self._make_field_label("Major*"))
        self._f_jurusan = self._make_input()
        ll.addWidget(self._f_jurusan); ll.addSpacing(4)

        ll.addWidget(self._make_field_label("University Name*"))
        self._f_kampus = self._make_input()
        ll.addWidget(self._f_kampus); ll.addSpacing(4)

        ll.addWidget(self._make_field_label("Degree*"))
        self._f_jenjang = self._make_combo(["D3", "D4", "S1", "S2", "S3"])
        self._f_jenjang.setCurrentText("S1")
        ll.addWidget(self._f_jenjang); ll.addSpacing(4)

        ll.addWidget(self._make_field_label("Semester*"))
        self._f_semester = self._make_input()
        ll.addWidget(self._f_semester); ll.addSpacing(4)

        ll.addWidget(self._make_field_label("Latest GPA (0.00-4.00)*"))
        self._f_ip = self._make_input()
        ll.addWidget(self._f_ip); ll.addSpacing(4)

        ll.addWidget(self._make_field_label("Gender*"))
        self._f_jk = self._make_combo(["Laki-laki", "Perempuan"])
        ll.addWidget(self._f_jk)

        ll.addStretch()
        columns_lay.addWidget(left)

        # ── RIGHT COLUMN: Specific Data (Optional) ──
        right = QWidget()
        right.setStyleSheet("background: transparent;")
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(4)

        sec2 = QLabel("Specific Data (Optional)")
        sec2.setFont(QFont(FONT_FAMILY, 14, QFont.Weight.Bold))
        sec2.setStyleSheet(f"color: {self.TEXT_DARK}; background: transparent;")
        rl.addWidget(sec2)
        rl.addSpacing(8)

        rl.addWidget(self._make_field_label("KIP Recipient"))
        self._f_kip = QCheckBox("Yes")
        self._f_kip.setStyleSheet(f"""
            QCheckBox {{ color: {self.TEXT_DARK}; font-size: 12px; background: transparent; }}
            QCheckBox::indicator {{ width: 18px; height: 18px; border: 2px solid {self.BORDER}; border-radius: 4px; background: white; }}
            QCheckBox::indicator:checked {{ background: {self.BTN_GREEN}; border-color: {self.BTN_GREEN}; }}
        """)
        rl.addWidget(self._f_kip); rl.addSpacing(4)

        rl.addWidget(self._make_field_label("IELTS Score (0.0-9.0)"))
        self._f_ielts = self._make_input()
        rl.addWidget(self._f_ielts); rl.addSpacing(4)

        rl.addWidget(self._make_field_label("TOEFL iBT Score (0-120)"))
        self._f_toefl = self._make_input()
        rl.addWidget(self._f_toefl); rl.addSpacing(4)

        rl.addWidget(self._make_field_label("Duolingo Score (10-160)"))
        self._f_duo = self._make_input()
        rl.addWidget(self._f_duo); rl.addSpacing(4)

        rl.addWidget(self._make_field_label("SAT Score (400-1600)"))
        self._f_sat = self._make_input()
        rl.addWidget(self._f_sat); rl.addSpacing(4)

        rl.addWidget(self._make_field_label("ACT Score (1-36)"))
        self._f_act = self._make_input()
        rl.addWidget(self._f_act); rl.addSpacing(4)

        rl.addWidget(self._make_field_label("GRE Score (260-340)"))
        self._f_gre = self._make_input()
        rl.addWidget(self._f_gre); rl.addSpacing(4)

        rl.addWidget(self._make_field_label("GMAT Score (200-800)"))
        self._f_gmat = self._make_input()
        rl.addWidget(self._f_gmat); rl.addSpacing(4)

        rl.addWidget(self._make_field_label("HSK Score (1-6)"))
        self._f_hsk = self._make_input()
        rl.addWidget(self._f_hsk); rl.addSpacing(4)

        rl.addWidget(self._make_field_label("JLPT Level"))
        self._f_jlpt = self._make_combo(["", "N5", "N4", "N3", "N2", "N1"])
        rl.addWidget(self._f_jlpt)

        rl.addStretch()
        columns_lay.addWidget(right)

        scroll.setWidget(scroll_widget)
        lay.addWidget(scroll, 1)
        lay.addSpacing(8)

        # Error label
        self._create_err = QLabel("")
        self._create_err.setStyleSheet("color: #FF3B30; font-size: 11px; background: transparent;")
        self._create_err.setWordWrap(True)
        lay.addWidget(self._create_err)

        # Save Profile button
        save_btn = QPushButton("Save Profile")
        save_btn.setFixedHeight(46)
        save_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        save_btn.setFont(QFont(FONT_FAMILY, 13, QFont.Weight.Bold))
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.BTN_GREEN};
                color: {self.TEXT_DARK};
                border: none;
                border-radius: 14px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {self.BTN_GREEN_HVR};
            }}
        """)
        save_btn.clicked.connect(self._do_create)
        lay.addWidget(save_btn)

    def _do_create(self):
        dw = input_data_wajib(
            self._f_nama.text().strip(),
            self._f_tgl.text().strip(),
            self._f_email.text().strip(),
            self._f_jurusan.text().strip(),
            self._f_kampus.text().strip(),
            self._f_semester.text().strip(),
            self._f_ip.text().strip(),
            self._f_jenjang.currentText(),
            self._f_jk.currentText(),
        )
        ds = input_data_spesifik(
            self._f_kip.isChecked(),
            self._f_ielts.text().strip(),
            self._f_toefl.text().strip(),
            self._f_duo.text().strip(),
            self._f_sat.text().strip(),
            self._f_act.text().strip(),
            self._f_gre.text().strip(),
            self._f_gmat.text().strip(),
            self._f_hsk.text().strip(),
            self._f_jlpt.currentText(),
        )
        ok, msg, pid = simpan_profil(dw, ds, user_id=self._user_id)
        if not ok:
            self._create_err.setText(msg)
            return
        QMessageBox.information(self, "Berhasil", "Profil berhasil dibuat!")
        self.profile_selected.emit(pid)

    # ── Helpers ──────────────────────────────────────────────
    def _clear_card(self):
        while self._card_lay.count():
            item = self._card_lay.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def _add_logo(self, lay):
        logo_container = QWidget()
        logo_container.setStyleSheet("background: transparent;")
        logo_h = QHBoxLayout(logo_container)
        logo_h.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_h.setContentsMargins(0, 0, 0, 0)
        try:
            logo_path = os.path.abspath(os.path.join(
                os.path.dirname(__file__), "..", "..", "assets", "logo_beaply.png"))
            pix = QPixmap(logo_path).scaled(
                160, 75, Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            logo_lbl = QLabel()
            logo_lbl.setPixmap(pix)
            logo_lbl.setStyleSheet("background: transparent;")
            logo_h.addWidget(logo_lbl)
        except Exception:
            logo_lbl = QLabel("beaply")
            logo_lbl.setFont(QFont(FONT_FAMILY, 28, QFont.Weight.Bold))
            logo_lbl.setStyleSheet(f"color: {self.TEXT_ACCENT}; background: transparent;")
            logo_h.addWidget(logo_lbl)
        lay.addWidget(logo_container)

    def _make_link_btn(self, text):
        btn = QPushButton(text)
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {self.TEXT_ACCENT};
                border: none;
                font-size: 11px;
                padding: 4px;
            }}
            QPushButton:hover {{
                text-decoration: underline;
            }}
        """)
        return btn
