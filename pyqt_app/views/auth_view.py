"""
pyqt_app/views/auth_view.py
Login / Register+Biodata / Forgot-Password — PyQt6 version.
Redesigned to match the Beaply Figma reference.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QStackedWidget, QMessageBox,
    QGraphicsDropShadowEffect, QSizePolicy, QScrollArea,
    QComboBox, QCheckBox, QSpacerItem
)
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import (
    QFont, QPixmap, QCursor, QLinearGradient, QPainter,
    QColor, QBrush, QPalette
)
import os, json

from pyqt_app.styles.theme import FONT_FAMILY
from controllers.auth_controller import (
    login as _login, register as _register,
    forgot_password, verify_reset_otp, reset_password as _reset_pw,
    validate_email_format, get_password_strength_level,
)
from controllers.profil_controller import (
    input_data_wajib, input_data_spesifik, simpan_profil,
)

SESSION_FILE = os.path.join(os.path.expanduser("~"), ".beaply_session.json")

def save_session(data):
    try:
        with open(SESSION_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        pass

def load_session():
    try:
        with open(SESSION_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return None

def clear_session():
    try:
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
    except Exception:
        pass


class GradientBackground(QWidget):
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        g = QLinearGradient(0, 0, self.width(), self.height())
        g.setColorAt(0.0, QColor("#FFE0D0"))
        g.setColorAt(1.0, QColor("#D8E0D8"))
        p.fillRect(self.rect(), QBrush(g))
        p.end()


class AuthView(QWidget):
    login_success = pyqtSignal(dict)
    register_success = pyqtSignal(dict, int)  # user_data, profil_id

    CARD_BG = "#FFFFFF"
    INPUT_BG = "#F0ECE8"
    INPUT_BORDER = "#E8E0D8"
    BTN_GREEN = "#A8C5B0"
    BTN_GREEN_HVR = "#8FB898"
    TEXT_DARK = "#2D2D2D"
    TEXT_MUTED = "#888888"
    TEXT_ACCENT = "#D4917B"
    ACCENT_PINK = "#E8B4A2"
    TAB_BORDER = "#D4917B"
    TAB_ACTIVE_BG = "#FCEAE3"
    TAB_INACTIVE = "#F5F0EC"

    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._bg = GradientBackground()
        bg_lay = QVBoxLayout(self._bg)
        bg_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bg_lay.setContentsMargins(0, 0, 0, 0)
        root.addWidget(self._bg)

        # Card
        self._card = QFrame()
        self._card.setObjectName("AuthCard")
        self._card.setFixedSize(480, 540)
        self._card.setStyleSheet(f"#AuthCard {{ background-color: {self.CARD_BG}; border-radius: 20px; border: none; }}")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(50); shadow.setOffset(0, 10); shadow.setColor(QColor(0, 0, 0, 45))
        self._card.setGraphicsEffect(shadow)

        card_lay = QVBoxLayout(self._card)
        card_lay.setContentsMargins(50, 36, 50, 36)
        card_lay.setSpacing(0)
        bg_lay.addWidget(self._card)

        # Logo
        self._add_logo(card_lay)
        card_lay.addSpacing(16)

        # Tabs
        tab_c = QWidget()
        tab_c.setStyleSheet("background: transparent;")
        tab_h = QHBoxLayout(tab_c)
        tab_h.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tab_h.setContentsMargins(0, 0, 0, 0); tab_h.setSpacing(0)

        tw = QFrame()
        tw.setObjectName("TabsContainer")
        tw.setFixedHeight(38)
        shadow_tw = QGraphicsDropShadowEffect()
        shadow_tw.setBlurRadius(15); shadow_tw.setOffset(0, 4); shadow_tw.setColor(QColor(0, 0, 0, 25))
        tw.setGraphicsEffect(shadow_tw)
        tw.setStyleSheet(f"#TabsContainer {{ background-color: {self.CARD_BG}; border: 1px solid #D0D0D0; border-radius: 19px; }}")
        tw_l = QHBoxLayout(tw)
        tw_l.setContentsMargins(1, 1, 1, 1); tw_l.setSpacing(0)

        self._tab_login = QPushButton("Log in")
        self._tab_signup = QPushButton("Sign up")
        for b in (self._tab_login, self._tab_signup):
            b.setFixedSize(100, 34)
            b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            b.setFont(QFont(FONT_FAMILY, 10))
        tw_l.addWidget(self._tab_login); tw_l.addWidget(self._tab_signup)
        tab_h.addWidget(tw)
        card_lay.addWidget(tab_c)
        card_lay.addSpacing(20)

        # Stack
        self._stack = QStackedWidget()
        self._stack.setStyleSheet("background: transparent;")
        card_lay.addWidget(self._stack, 1)

        self._login_page = self._build_login_form()
        self._register_page = self._build_register_form()
        self._forgot_page = self._build_forgot_form()
        self._stack.addWidget(self._login_page)
        self._stack.addWidget(self._register_page)
        self._stack.addWidget(self._forgot_page)

        self._tab_login.clicked.connect(lambda: self._switch_tab(0))
        self._tab_signup.clicked.connect(lambda: self._switch_tab(1))
        self._switch_tab(0)

        self._forgot_email = ""
        self._forgot_step = 1

    def _add_logo(self, lay):
        c = QWidget(); c.setStyleSheet("background: transparent;")
        h = QHBoxLayout(c); h.setAlignment(Qt.AlignmentFlag.AlignCenter); h.setContentsMargins(0,0,0,0)
        try:
            p = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "logo_beaply.png"))
            px = QPixmap(p).scaled(300, 140, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            l = QLabel(); l.setPixmap(px); l.setStyleSheet("background: transparent;"); h.addWidget(l)
        except Exception:
            l = QLabel("beaply"); l.setFont(QFont(FONT_FAMILY, 28, QFont.Weight.Bold))
            l.setStyleSheet(f"color: {self.TEXT_ACCENT}; background: transparent;"); h.addWidget(l)
        lay.addWidget(c)

    def _switch_tab(self, idx):
        self._stack.setCurrentIndex(idx)
        active_ss = lambda: f"QPushButton {{ background-color: {self.TAB_ACTIVE_BG}; color: {self.TEXT_DARK}; border: none; border-radius: 17px; font-weight: bold; }}"
        inactive_ss = lambda: f"QPushButton {{ background-color: transparent; color: {self.TEXT_MUTED}; border: none; border-radius: 17px; }} QPushButton:hover {{ color: {self.TEXT_DARK}; }}"
        if idx == 0:
            self._tab_login.setStyleSheet(active_ss()); self._tab_signup.setStyleSheet(inactive_ss())
            self._card.setFixedSize(480, 540)
        elif idx == 1:
            self._tab_signup.setStyleSheet(active_ss()); self._tab_login.setStyleSheet(inactive_ss())
            self._card.setFixedSize(900, 680)
        elif idx == 2:
            self._tab_login.setStyleSheet(inactive_ss()); self._tab_signup.setStyleSheet(inactive_ss())
            self._card.setFixedSize(480, 540)

    def _lbl(self, text):
        l = QLabel(text); l.setFont(QFont(FONT_FAMILY, 11))
        l.setStyleSheet(f"color: {self.TEXT_DARK}; background: transparent; margin-bottom: 0px;"); return l

    def _apply_shadow(self, widget, blur=15, y_offset=4, alpha=30):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur); shadow.setOffset(0, y_offset); shadow.setColor(QColor(0, 0, 0, alpha))
        widget.setGraphicsEffect(shadow)

    def _inp(self, ph="", echo=QLineEdit.EchoMode.Normal, shadow=True):
        e = QLineEdit(); e.setPlaceholderText(ph); e.setFixedHeight(44); e.setEchoMode(echo)
        e.setFont(QFont(FONT_FAMILY, 11))
        e.setStyleSheet(f"QLineEdit {{ background-color: {self.INPUT_BG}; color: {self.TEXT_DARK}; border: 2px solid transparent; border-radius: 12px; padding: 10px 16px; font-size: 13px; }} QLineEdit:focus {{ border: 2px solid {self.BTN_GREEN}; }}")
        if shadow: self._apply_shadow(e)
        return e

    def _password_inp(self, ph=""):
        frame = QFrame(); frame.setFixedHeight(44)
        frame.setStyleSheet(f"QFrame {{ background-color: {self.INPUT_BG}; border-radius: 12px; border: 2px solid transparent; }}")
        self._apply_shadow(frame)
        
        flay = QHBoxLayout(frame); flay.setContentsMargins(16, 0, 10, 0); flay.setSpacing(4)
        
        e = QLineEdit(); e.setPlaceholderText(ph); e.setEchoMode(QLineEdit.EchoMode.Password)
        e.setFont(QFont(FONT_FAMILY, 11))
        e.setStyleSheet(f"QLineEdit {{ background-color: transparent; color: {self.TEXT_DARK}; border: none; font-size: 13px; padding: 0px; }} QLineEdit:focus {{ border: none; }}")
        
        from PyQt6.QtWidgets import QToolButton
        from PyQt6.QtGui import QIcon, QPixmap
        import os
        btn = QToolButton()
        
        p_closed = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "see_password.png"))
        p_seen = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "hide_password.png"))
        
        icon_closed = QIcon(p_closed); icon_seen = QIcon(p_seen)
        btn.setIcon(icon_closed)
        btn.setIconSize(QSize(20, 20))
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn.setStyleSheet("QToolButton { border: none; background: transparent; }")
        
        def toggle_echo():
            if e.echoMode() == QLineEdit.EchoMode.Password:
                e.setEchoMode(QLineEdit.EchoMode.Normal); btn.setIcon(icon_seen)
            else:
                e.setEchoMode(QLineEdit.EchoMode.Password); btn.setIcon(icon_closed)
                
        btn.clicked.connect(toggle_echo)
        
        flay.addWidget(e); flay.addWidget(btn)
        
        from PyQt6.QtCore import QObject, QEvent
        class FocusFilter(QObject):
            def __init__(self, fr, bg, brd):
                super().__init__(e)
                self.fr = fr; self.bg = bg; self.brd = brd
            def eventFilter(self, obj, event):
                if event.type() == QEvent.Type.FocusIn:
                    self.fr.setStyleSheet(f"QFrame {{ background-color: {self.bg}; border-radius: 12px; border: 2px solid {self.brd}; }}")
                elif event.type() == QEvent.Type.FocusOut:
                    self.fr.setStyleSheet(f"QFrame {{ background-color: {self.bg}; border-radius: 12px; border: 2px solid transparent; }}")
                return False
                
        e._focus_filter = FocusFilter(frame, self.INPUT_BG, self.BTN_GREEN)
        e.installEventFilter(e._focus_filter)
        
        return frame, e

    def _combo(self, items):
        c = QComboBox(); c.addItems(items); c.setFixedHeight(44)
        c.setStyleSheet(f"QComboBox {{ background-color: {self.INPUT_BG}; color: {self.TEXT_DARK}; border: 2px solid transparent; border-radius: 12px; padding: 10px 16px; font-size: 13px; }} QComboBox:focus {{ border: 2px solid {self.BTN_GREEN}; }} QComboBox::drop-down {{ border: none; width: 30px; subcontrol-position: center right; }} QComboBox::down-arrow {{ width: 12px; height: 12px; }}")
        self._apply_shadow(c)
        return c

    def _btn(self, text, shadow=True):
        b = QPushButton(text); b.setFixedHeight(46)
        b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        b.setFont(QFont(FONT_FAMILY, 13, QFont.Weight.Bold))
        b.setStyleSheet(f"QPushButton {{ background-color: {self.BTN_GREEN}; color: {self.TEXT_DARK}; border: none; border-radius: 14px; font-weight: bold; font-size: 14px; }} QPushButton:hover {{ background-color: {self.BTN_GREEN_HVR}; }} QPushButton:pressed {{ background-color: #7DAA86; }}")
        if shadow: self._apply_shadow(b, blur=20, y_offset=6, alpha=35)
        return b

    def _link(self, text):
        b = QPushButton(text); b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        b.setStyleSheet(f"QPushButton {{ background: transparent; color: {self.TEXT_ACCENT}; border: none; font-size: 11px; padding: 4px; }} QPushButton:hover {{ text-decoration: underline; }}")
        return b

    def _err_lbl(self):
        l = QLabel(""); l.setStyleSheet("color: #FF3B30; font-size: 11px; background: transparent;"); l.setWordWrap(True); return l

    # ── LOGIN ──
    def _build_login_form(self):
        page = QWidget(); page.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(page); lay.setContentsMargins(0,0,0,0); lay.setSpacing(6)

        lay.addWidget(self._lbl("Email"))
        self.login_email = self._inp(); lay.addWidget(self.login_email); lay.addSpacing(10)

        lay.addWidget(self._lbl("Password"))
        pw_container, self.login_pass = self._password_inp("")
        lay.addWidget(pw_container)

        # Remember me + forgot row
        row = QWidget(); row.setStyleSheet("background: transparent;")
        rh = QHBoxLayout(row); rh.setContentsMargins(0,4,0,0); rh.setSpacing(0)
        self.remember_me = QCheckBox("Remember me")
        check_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "check.svg")).replace("\\", "/")
        self.remember_me.setStyleSheet(
            f"QCheckBox {{ color: {self.TEXT_MUTED}; font-size: 11px; background: transparent; }} "
            f"QCheckBox::indicator {{ width: 16px; height: 16px; border: 2px solid {self.INPUT_BORDER}; border-radius: 4px; background: white; }} "
            f"QCheckBox::indicator:checked {{ background: {self.BTN_GREEN}; border-color: {self.BTN_GREEN}; image: url('{check_path}'); }}"
        )
        rh.addWidget(self.remember_me)
        rh.addStretch()
        forgot = self._link("Lupa Kata Sandi?")
        forgot.clicked.connect(self._show_forgot)
        rh.addWidget(forgot)
        lay.addWidget(row)

        self.login_err = self._err_lbl(); lay.addWidget(self.login_err)
        lay.addSpacing(12)

        login_btn = self._btn("Log in"); login_btn.clicked.connect(self._do_login)
        lay.addWidget(login_btn); lay.addStretch()
        return page

    # ── SIGN UP (two-column biodata) ──
    def _build_register_form(self):
        page = QWidget(); page.setStyleSheet("background: transparent;")
        outer = QVBoxLayout(page); outer.setContentsMargins(0,0,0,0); outer.setSpacing(0)

        # Subtitle
        sub = QLabel("Complete your personal data")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub.setStyleSheet(f"color: {self.TEXT_MUTED}; font-size: 12px; background: transparent;")
        outer.addWidget(sub); outer.addSpacing(12)

        # Scroll area
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; } QScrollArea > QWidget > QWidget { background: transparent; }")
        sw = QWidget(); sw.setStyleSheet("background: transparent;")
        sl = QHBoxLayout(sw); sl.setContentsMargins(0,0,8,0); sl.setSpacing(30)

        # LEFT COLUMN - Required
        left = QWidget(); left.setStyleSheet("background: transparent;")
        ll = QVBoxLayout(left); ll.setContentsMargins(0,0,0,0); ll.setSpacing(4)

        sec1 = QLabel("Required Data"); sec1.setFont(QFont(FONT_FAMILY, 14, QFont.Weight.Bold))
        sec1.setStyleSheet(f"color: {self.TEXT_DARK}; background: transparent;")
        ll.addWidget(sec1); ll.addSpacing(8)

        ll.addWidget(self._lbl("Full Name*")); self.reg_nama = self._inp(); ll.addWidget(self.reg_nama); ll.addSpacing(4)
        ll.addWidget(self._lbl("Email*")); self.reg_email = self._inp(); ll.addWidget(self.reg_email); ll.addSpacing(4)
        ll.addWidget(self._lbl("Password*"))
        pw_cont, self.reg_pass = self._password_inp("")
        ll.addWidget(pw_cont); ll.addSpacing(4)
        ll.addWidget(self._lbl("Date of Birth*")); self.reg_dob = self._inp("YYYY-MM-DD"); ll.addWidget(self.reg_dob); ll.addSpacing(4)
        ll.addWidget(self._lbl("Major*"))
        self.reg_major = self._combo([
            "Teknik Informatika", "Ilmu Komputer", "Sistem Informasi",
            "Teknik Elektro", "Teknik Mesin", "Teknik Sipil",
            "Teknik Kimia", "Teknik Industri", "Teknik Lingkungan",
            "Arsitektur", "Matematika", "Fisika", "Kimia", "Biologi",
            "Statistika", "Ekonomi", "Manajemen", "Akuntansi",
            "Ilmu Komunikasi", "Psikologi", "Hukum", "Kedokteran",
            "Farmasi", "Kesehatan Masyarakat", "Keperawatan",
            "Pendidikan", "Sastra Indonesia", "Sastra Inggris",
            "Hubungan Internasional", "Ilmu Politik", "Sosiologi",
            "Agribisnis", "Pertanian", "Perikanan", "Kehutanan",
            "Seni Rupa", "Desain Komunikasi Visual", "Lainnya",
        ])
        ll.addWidget(self.reg_major); ll.addSpacing(4)
        ll.addWidget(self._lbl("University Name*")); self.reg_univ = self._inp(); ll.addWidget(self.reg_univ); ll.addSpacing(4)
        ll.addWidget(self._lbl("Degree*")); self.reg_degree = self._combo(["D3","D4","S1","S2","S3"]); self.reg_degree.setCurrentText("S1"); ll.addWidget(self.reg_degree); ll.addSpacing(4)
        ll.addWidget(self._lbl("Semester*")); self.reg_sem = self._inp(); ll.addWidget(self.reg_sem); ll.addSpacing(4)
        ll.addWidget(self._lbl("Latest GPA (0.00-4.00)*")); self.reg_gpa = self._inp(); ll.addWidget(self.reg_gpa); ll.addSpacing(4)
        ll.addWidget(self._lbl("Gender*")); self.reg_gender = self._combo(["Laki-laki","Perempuan"]); ll.addWidget(self.reg_gender); ll.addSpacing(4)

        ll.addStretch()
        sl.addWidget(left)

        # RIGHT COLUMN - Optional
        right = QWidget(); right.setStyleSheet("background: transparent;")
        rl = QVBoxLayout(right); rl.setContentsMargins(0,0,0,0); rl.setSpacing(4)

        sec2 = QLabel("Specific Data (Optional)"); sec2.setFont(QFont(FONT_FAMILY, 14, QFont.Weight.Bold))
        sec2.setStyleSheet(f"color: {self.TEXT_DARK}; background: transparent;")
        rl.addWidget(sec2); rl.addSpacing(8)

        rl.addWidget(self._lbl("Aktif Organisasi"))
        self.reg_organisasi = QCheckBox("Ya, saya aktif berorganisasi")
        check_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "check.svg")).replace("\\", "/")
        self.reg_organisasi.setStyleSheet(
            f"QCheckBox {{ color: {self.TEXT_DARK}; font-size: 12px; background: transparent; }}"
            f"QCheckBox::indicator {{ width: 18px; height: 18px; border: 2px solid {self.INPUT_BORDER}; border-radius: 4px; background: white; }}"
            f"QCheckBox::indicator:checked {{ background: {self.BTN_GREEN}; border-color: {self.BTN_GREEN}; image: url('{check_path}'); }}"
        )
        rl.addWidget(self.reg_organisasi); rl.addSpacing(4)

        rl.addWidget(self._lbl("KIP Recipient"))
        self.reg_kip = QCheckBox("Yes")
        self.reg_kip.setStyleSheet(f"QCheckBox {{ color: {self.TEXT_DARK}; font-size: 12px; background: transparent; }} QCheckBox::indicator {{ width: 18px; height: 18px; border: 2px solid {self.INPUT_BORDER}; border-radius: 4px; background: white; }} QCheckBox::indicator:checked {{ background: {self.BTN_GREEN}; border-color: {self.BTN_GREEN}; image: url('{check_path}'); }}")
        rl.addWidget(self.reg_kip); rl.addSpacing(4)

        rl.addWidget(self._lbl("IELTS Score (0.0-9.0)")); self.reg_ielts = self._inp(); rl.addWidget(self.reg_ielts); rl.addSpacing(4)
        rl.addWidget(self._lbl("TOEFL iBT Score (0-120)")); self.reg_toefl = self._inp(); rl.addWidget(self.reg_toefl); rl.addSpacing(4)
        rl.addWidget(self._lbl("Duolingo Score (10-160)")); self.reg_duo = self._inp(); rl.addWidget(self.reg_duo); rl.addSpacing(4)
        rl.addWidget(self._lbl("SAT Score (400-1600)")); self.reg_sat = self._inp(); rl.addWidget(self.reg_sat); rl.addSpacing(4)
        rl.addWidget(self._lbl("ACT Score (1-36)")); self.reg_act = self._inp(); rl.addWidget(self.reg_act); rl.addSpacing(4)
        rl.addWidget(self._lbl("GRE Score (260-340)")); self.reg_gre = self._inp(); rl.addWidget(self.reg_gre); rl.addSpacing(4)
        rl.addWidget(self._lbl("GMAT Score (200-800)")); self.reg_gmat = self._inp(); rl.addWidget(self.reg_gmat); rl.addSpacing(4)
        rl.addWidget(self._lbl("HSK Score (1-6)")); self.reg_hsk = self._inp(); rl.addWidget(self.reg_hsk); rl.addSpacing(4)
        rl.addWidget(self._lbl("JLPT Level")); self.reg_jlpt = self._combo(["","N5","N4","N3","N2","N1"]); rl.addWidget(self.reg_jlpt)
        rl.addStretch()
        sl.addWidget(right)

        scroll.setWidget(sw)
        outer.addWidget(scroll, 1)
        outer.addSpacing(8)

        self.reg_err = self._err_lbl(); outer.addWidget(self.reg_err)
        outer.addSpacing(4)

        save_btn = self._btn("Save Profile"); save_btn.clicked.connect(self._do_register)
        outer.addWidget(save_btn)
        return page

    # ── FORGOT PASSWORD ──
    def _build_forgot_form(self):
        page = QWidget(); page.setStyleSheet("background: transparent;")
        self._forgot_lay = QVBoxLayout(page); self._forgot_lay.setContentsMargins(0,0,0,0); self._forgot_lay.setSpacing(8)
        self._build_forgot_step1()
        return page

    def _show_forgot(self):
        self._build_forgot_step1(); self._switch_tab(2)

    def _clear_forgot(self):
        while self._forgot_lay.count():
            item = self._forgot_lay.takeAt(0)
            if item.widget(): item.widget().deleteLater()

    def _build_forgot_step1(self):
        self._clear_forgot(); lay = self._forgot_lay
        back = self._link("← Kembali"); back.clicked.connect(lambda: self._switch_tab(0))
        lay.addWidget(back, alignment=Qt.AlignmentFlag.AlignLeft)
        t = QLabel("Reset Password"); t.setFont(QFont(FONT_FAMILY, 18, QFont.Weight.Bold))
        t.setAlignment(Qt.AlignmentFlag.AlignCenter); t.setStyleSheet(f"color: {self.TEXT_DARK}; background: transparent;")
        lay.addWidget(t)
        s = QLabel("Masukkan email terdaftar Anda."); s.setAlignment(Qt.AlignmentFlag.AlignCenter)
        s.setStyleSheet(f"color: {self.TEXT_MUTED}; font-size: 12px; background: transparent;")
        lay.addWidget(s); lay.addSpacing(12)
        lay.addWidget(self._lbl("Email")); self.forgot_email_input = self._inp(); lay.addWidget(self.forgot_email_input)
        self.forgot_err = self._err_lbl(); lay.addWidget(self.forgot_err); lay.addSpacing(8)
        btn = self._btn("Kirim Kode OTP"); btn.clicked.connect(self._send_otp); lay.addWidget(btn); lay.addStretch()

    def _build_forgot_step2(self):
        self._clear_forgot(); lay = self._forgot_lay
        t = QLabel("Masukkan Kode OTP"); t.setFont(QFont(FONT_FAMILY, 18, QFont.Weight.Bold))
        t.setAlignment(Qt.AlignmentFlag.AlignCenter); t.setStyleSheet(f"color: {self.TEXT_DARK}; background: transparent;"); lay.addWidget(t)
        s = QLabel(f"Kode dikirim ke {self._forgot_email}"); s.setAlignment(Qt.AlignmentFlag.AlignCenter)
        s.setStyleSheet(f"color: {self.TEXT_MUTED}; font-size: 12px; background: transparent;"); lay.addWidget(s); lay.addSpacing(12)
        lay.addWidget(self._lbl("Kode OTP")); self.otp_input = self._inp("6 digit"); lay.addWidget(self.otp_input)
        self.forgot_err = self._err_lbl(); lay.addWidget(self.forgot_err); lay.addSpacing(8)
        btn = self._btn("Verifikasi"); btn.clicked.connect(self._verify_otp); lay.addWidget(btn); lay.addStretch()

    def _build_forgot_step3(self):
        self._clear_forgot(); lay = self._forgot_lay
        t = QLabel("Password Baru"); t.setFont(QFont(FONT_FAMILY, 18, QFont.Weight.Bold))
        t.setAlignment(Qt.AlignmentFlag.AlignCenter); t.setStyleSheet(f"color: {self.TEXT_DARK}; background: transparent;"); lay.addWidget(t); lay.addSpacing(12)
        lay.addWidget(self._lbl("Password Baru"))
        pw_cont1, self.new_pw = self._password_inp("")
        lay.addWidget(pw_cont1); lay.addSpacing(6)
        lay.addWidget(self._lbl("Konfirmasi Password"))
        pw_cont2, self.conf_pw = self._password_inp("")
        lay.addWidget(pw_cont2)
        self.forgot_err = self._err_lbl(); lay.addWidget(self.forgot_err); lay.addSpacing(8)
        btn = self._btn("Reset Password"); btn.clicked.connect(self._do_reset); lay.addWidget(btn); lay.addStretch()

    # ── ACTIONS ──
    def _do_login(self):
        email = self.login_email.text().strip()
        pw = self.login_pass.text()
        ok, msg, data = _login(email, pw)
        if not ok:
            self.login_err.setText(msg); return
        if self.remember_me.isChecked():
            save_session(data)
        else:
            clear_session()
        self.login_success.emit(data)

    def _do_register(self):
        nama = self.reg_nama.text().strip()
        email = self.reg_email.text().strip()
        pw = self.reg_pass.text()
        dob = self.reg_dob.text().strip()
        major = self.reg_major.currentText().strip()
        univ = self.reg_univ.text().strip()
        sem = self.reg_sem.text().strip()
        gpa = self.reg_gpa.text().strip()

        if not all([nama, email, pw, dob, major, univ, sem, gpa]):
            self.reg_err.setText("Semua field wajib (*) harus diisi."); return
        if not validate_email_format(email):
            self.reg_err.setText("Format email tidak valid."); return

        # 1. Validate profile data FIRST (before creating user)
        dw = input_data_wajib(nama, dob, email, major, univ, sem, gpa,
                              self.reg_degree.currentText(), self.reg_gender.currentText(),
                              self.reg_organisasi.isChecked())
        ds = input_data_spesifik(
            self.reg_kip.isChecked(),
            self.reg_ielts.text().strip(),
            self.reg_toefl.text().strip(),
            self.reg_duo.text().strip(),
            self.reg_sat.text().strip(),
            self.reg_act.text().strip(),
            self.reg_gre.text().strip(),
            self.reg_gmat.text().strip(),
            self.reg_hsk.text().strip(),
            self.reg_jlpt.currentText(),
        )

        from utils import validasi_data_wajib, validasi_data_spesifik
        ok_w, msg_w = validasi_data_wajib(dw)
        if not ok_w:
            self.reg_err.setText(msg_w); return
        ok_s, msg_s = validasi_data_spesifik(ds)
        if not ok_s:
            self.reg_err.setText(msg_s); return

        # 2. Register user (only after all validations pass)
        ok, msg, uid = _register(nama, email, pw, pw)
        if not ok:
            self.reg_err.setText(msg); return

        # 3. Create profile (data already validated above)
        ok2, msg2, pid = simpan_profil(dw, ds, user_id=uid)
        if not ok2:
            self.reg_err.setText(f"Akun dibuat tapi profil gagal: {msg2}"); return

        # 3. Auto-login
        ok3, msg3, data = _login(email, pw)
        if not ok3:
            QMessageBox.information(self, "Berhasil", "Akun & profil dibuat! Silakan login.")
            self._switch_tab(0); return

        save_session(data)
        self.register_success.emit(data, pid)

    def _send_otp(self):
        email = self.forgot_email_input.text().strip()
        ok, msg = forgot_password(email)
        if not ok: self.forgot_err.setText(msg); return
        self._forgot_email = email; self._build_forgot_step2()

    def _verify_otp(self):
        ok, msg = verify_reset_otp(self._forgot_email, self.otp_input.text().strip())
        if not ok: self.forgot_err.setText(msg); return
        self._build_forgot_step3()

    def _do_reset(self):
        pw1 = self.new_pw.text(); pw2 = self.conf_pw.text()
        if pw1 != pw2: self.forgot_err.setText("Password tidak cocok."); return
        ok, msg = _reset_pw(self._forgot_email, pw1, pw1)
        if not ok: self.forgot_err.setText(msg); return
        QMessageBox.information(self, "Berhasil", "Password berhasil direset! Silakan login.")
        self._build_forgot_step1(); self._switch_tab(0)
