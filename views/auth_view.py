<<<<<<< HEAD
import re
import customtkinter as ctk
from tkinter import messagebox
import os

from utils.ui_utils import (
=======
"""
views/auth_view.py
Beaply - View: Autentikasi (Login / Register / Lupa Sandi)

Dipindahkan dari: Autentikasi_dan_Keamanan/gui_auth.py
Import sekarang dari Autentikasi_dan_Keamanan.auth (shim controller).
"""
import customtkinter as ctk
from tkinter import messagebox
from ui_utils import (
>>>>>>> 14a6b3f28e0f19b0c641fd9179026190a55f2248
    t, BG_COLOR, CARD_COLOR, BORDER_COLOR, TEXT_ACCENT,
    BTN_PALE, BTN_PRIMARY, BTN_PRIMARY_HOVER, TEXT_DARK,
    INPUT_BG, TEXT_MUTED
)
<<<<<<< HEAD

def get_password_strength_level(password: str) -> tuple:
    if not password: return 0, "", "#555555"
    score = 0
    if len(password) >= 8: score += 1
    if re.search(r"[A-Z]", password) and re.search(r"[a-z]", password): score += 1
    if re.search(r"\d", password): score += 1
    if re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?`~]", password): score += 1

    levels = {
        0: ("Sangat Lemah", "#FF3B30"),
        1: ("Lemah", "#FF9500"),
        2: ("Cukup", "#FFCC00"),
        3: ("Kuat", "#34C759"),
        4: ("Sangat Kuat", "#00C7BE"),
    }
    label, color = levels.get(score, levels[0])
    return score, label, color

class HalamanAuth(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color=BG_COLOR)
        self.controller = controller
        self._bhs = "id"
        self._build()

    def _build(self):
        bhs = self._bhs
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")

        card = ctk.CTkFrame(center, fg_color=CARD_COLOR, corner_radius=24,
                            width=440, height=520, border_width=1,
=======
from controllers.auth_controller import (
    login as _login, register as _register,
    forgot_password, verify_reset_otp, reset_password as _reset_pw,
    validate_email_format, get_password_strength_level,
)


def login_pengguna(email, password):
    ok, msg, data = _login(email, password)
    return (True, data) if ok else (False, msg)


def registrasi_pengguna(nama, email, password):
    ok, msg, _uid = _register(nama, email, password, password)
    return ok, msg


def lupa_sandi(email):
    return forgot_password(email)


def verifikasi_otp(email, otp):
    return verify_reset_otp(email, otp)


def reset_password(email, new_pass):
    return _reset_pw(email, new_pass, new_pass)



# ════════════════════════════════════════════════════════════
# HALAMAN: Login / Register
# ════════════════════════════════════════════════════════════

class HalamanAuth(ctk.CTkFrame):
    """Login/Register — matches mockup design."""
    def __init__(self, master, login_callback, lupa_sandi_callback):
        super().__init__(master, fg_color=BG_COLOR)
        self.login_cb      = login_callback
        self.lupa_sandi_cb = lupa_sandi_callback
        self._mode         = "login"
        self._build()

    def _build(self):
        for w in self.winfo_children():
            w.destroy()
        if self._mode == "login":
            self._build_login()
        else:
            self._build_register()

    # ── LOGIN ────────────────────────────────────────────────

    def _build_login(self):
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")
        card = ctk.CTkFrame(center, fg_color=CARD_COLOR, corner_radius=24,
                            width=440, height=560, border_width=1,
>>>>>>> 14a6b3f28e0f19b0c641fd9179026190a55f2248
                            border_color=BORDER_COLOR)
        card.pack()
        card.pack_propagate(False)

<<<<<<< HEAD
        logo_frame = ctk.CTkFrame(card, fg_color="transparent")
        logo_frame.pack(pady=(36, 0))
        try:
            from PIL import Image
            logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Pembersihan", "assets", "logo_beaply.png"))
            img = ctk.CTkImage(light_image=Image.open(logo_path), size=(140, 65))
            ctk.CTkLabel(logo_frame, text="", image=img).pack()
        except:
            ctk.CTkLabel(logo_frame, text="beaply",
                         font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
                         text_color=TEXT_ACCENT).pack()

        self.tab_var = ctk.StringVar(value="Log in")
        tab_frame = ctk.CTkFrame(card, fg_color="transparent")
        tab_frame.pack(pady=(20, 16))
        self.seg_btn = ctk.CTkSegmentedButton(
            tab_frame, values=["Log in", "Sign up"],
            variable=self.tab_var, command=self._switch_tab,
            font=ctk.CTkFont(size=13), fg_color=BTN_PALE,
            selected_color=BTN_PRIMARY, selected_hover_color=BTN_PRIMARY_HOVER,
            unselected_color=BTN_PALE, unselected_hover_color="#D8E4DC",
            text_color=TEXT_DARK, corner_radius=20, width=220, height=34)
        self.seg_btn.pack()

        self.form_container = ctk.CTkFrame(card, fg_color="transparent")
        self.form_container.pack(fill="both", expand=True, padx=48, pady=(0, 24))
        self._build_login_form()

    def _switch_tab(self, value):
        for w in self.form_container.winfo_children(): w.destroy()
        if value == "Log in": self._build_login_form()
        else: self._build_register_form()

    def _build_login_form(self):
        p = self.form_container
        ctk.CTkLabel(p, text="Email", font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT_DARK, anchor="w").pack(fill="x", pady=(16, 4))
        self.login_email = ctk.CTkEntry(p, height=42, corner_radius=10, fg_color=INPUT_BG, border_width=0, text_color=TEXT_DARK, placeholder_text="your@email.com")
        self.login_email.pack(fill="x")

        ctk.CTkLabel(p, text="Password", font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT_DARK, anchor="w").pack(fill="x", pady=(14, 4))
        self.login_pass = ctk.CTkEntry(p, height=42, corner_radius=10, fg_color=INPUT_BG, border_width=0, text_color=TEXT_DARK, show="●", placeholder_text="••••••••")
        self.login_pass.pack(fill="x")

        self.login_error = ctk.CTkLabel(p, text="", text_color="#D94040", font=ctk.CTkFont(size=11), wraplength=300, anchor="w")
        self.login_error.pack(fill="x", pady=(6, 0))

        ctk.CTkButton(p, text="Log in", height=44, corner_radius=12, fg_color=BTN_PRIMARY, hover_color=BTN_PRIMARY_HOVER, text_color=TEXT_DARK, font=ctk.CTkFont(size=14, weight="bold"), command=self._do_login).pack(fill="x", pady=(16, 8))

        ctk.CTkButton(p, text=t("link_lupa", self._bhs), height=28, fg_color="transparent", text_color=TEXT_MUTED, hover_color=BG_COLOR, font=ctk.CTkFont(size=11, underline=True), command=self.controller.tampilkan_lupa_sandi).pack()

    def _build_register_form(self):
        p = self.form_container
        bhs = self._bhs
        scroll = ctk.CTkScrollableFrame(p, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        for label, attr, show in [(t("f_nama_reg", bhs), "reg_nama", ""), (t("f_email_reg", bhs), "reg_email", ""), (t("f_pass_reg", bhs), "reg_pass", "●"), (t("f_confirm_reg", bhs), "reg_confirm", "●")]:
            ctk.CTkLabel(scroll, text=label, font=ctk.CTkFont(size=12, weight="bold"), text_color=TEXT_DARK, anchor="w").pack(fill="x", pady=(8, 3))
            e = ctk.CTkEntry(scroll, height=38, corner_radius=10, fg_color=INPUT_BG, border_width=0, text_color=TEXT_DARK, show=show if show else None)
            e.pack(fill="x")
            setattr(self, attr, e)

        self.reg_pass.bind("<KeyRelease>", self._update_strength)
        sf = ctk.CTkFrame(scroll, fg_color="transparent", height=14)
        sf.pack(fill="x", pady=(2, 0))
        self.strength_label = ctk.CTkLabel(sf, text="", font=ctk.CTkFont(size=9))
        self.strength_label.pack(side="left")
        self.strength_bar = ctk.CTkProgressBar(sf, width=120, height=5)
        self.strength_bar.pack(side="right", padx=4)
        self.strength_bar.set(0)

        self.reg_error = ctk.CTkLabel(scroll, text="", text_color="#D94040", font=ctk.CTkFont(size=11), wraplength=280, anchor="w")
        self.reg_error.pack(fill="x", pady=(4, 0))
        ctk.CTkButton(scroll, text="Sign up", height=42, corner_radius=12, fg_color=BTN_PRIMARY, hover_color=BTN_PRIMARY_HOVER, text_color=TEXT_DARK, font=ctk.CTkFont(size=14, weight="bold"), command=self._do_register).pack(fill="x", pady=(12, 8))

    def _update_strength(self, event=None):
        pwd = self.reg_pass.get()
        level, label, color = get_password_strength_level(pwd)
        self.strength_label.configure(text=f"{t('kekuatan_pwd', self._bhs)} {label}", text_color=color)
        self.strength_bar.set(level / 4)

    def _do_login(self):
        email, pwd = self.login_email.get().strip(), self.login_pass.get()
        if not email or not pwd:
            self.login_error.configure(text="Email dan kata sandi harus diisi.")
            return
        self.controller.proses_login(email, pwd)

    def tampilkan_error_login(self, message):
        self.login_error.configure(text=message)
        
    def _do_register(self):
        nama, email, pwd, confirm = self.reg_nama.get().strip(), self.reg_email.get().strip(), self.reg_pass.get(), self.reg_confirm.get()
        self.controller.proses_register(nama, email, pwd, confirm)

    def tampilkan_pesan_sukses(self, message):
        messagebox.showinfo("Berhasil", message)
        self.seg_btn.set("Log in")
        self._switch_tab("Log in")
        
    def tampilkan_error_register(self, message):
        self.reg_error.configure(text=message)


class HalamanLupaSandi(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self._bhs = "id"
        self._email = ""
        self._build_step1()

    def _clear(self):
        for w in self.winfo_children(): w.destroy()

    def _build_step1(self):
        self._clear()
        bhs = self._bhs

        ctk.CTkButton(self, text=t("btn_kembali", bhs), width=100, fg_color="transparent", border_width=1, command=self.controller.tampilkan_auth).pack(anchor="w", padx=30, pady=(20, 0))

        ctk.CTkFrame(self, height=30, fg_color="transparent").pack()
        ctk.CTkLabel(self, text=t("lupa_judul", bhs), font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(0, 4))
        ctk.CTkLabel(self, text=t("lupa_desc", bhs), font=ctk.CTkFont(size=13), text_color="gray50").pack(pady=(0, 20))

        self.lupa_email = ctk.CTkEntry(self, placeholder_text="Email", width=320, height=40)
        self.lupa_email.pack(pady=6)

        self.lupa_error = ctk.CTkLabel(self, text="", text_color="#FF3B30", font=ctk.CTkFont(size=11), wraplength=300)
        self.lupa_error.pack(pady=(0, 4))

        ctk.CTkButton(self, text=t("btn_kirim_otp", bhs), width=320, height=44, font=ctk.CTkFont(size=14, weight="bold"), command=self._kirim_otp).pack(pady=8)

    def _kirim_otp(self):
        self._email = self.lupa_email.get().strip()
        self.controller.proses_permintaan_otp(self._email)
        
    def tampilkan_error_lupa(self, message):
        self.lupa_error.configure(text=message)

    def lanjut_ke_step2(self, otp_dev):
        self._clear()
        bhs = self._bhs

        ctk.CTkButton(self, text=t("btn_kembali", bhs), width=100, fg_color="transparent", border_width=1, command=self._build_step1).pack(anchor="w", padx=30, pady=(20, 0))
        ctk.CTkFrame(self, height=30, fg_color="transparent").pack()
        ctk.CTkLabel(self, text=t("otp_judul", bhs), font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(0, 4))
        ctk.CTkLabel(self, text=f"{t('otp_desc', bhs)}\n({self._email})", font=ctk.CTkFont(size=13), text_color="gray50", justify="center").pack(pady=(0, 10))

        if otp_dev:
            # Karena offline, kita akan print ke layar untuk kemudahan
            dev_frame = ctk.CTkFrame(self, fg_color=("#FFF3CD", "#665200"), corner_radius=8)
            dev_frame.pack(padx=40, pady=(0, 10), fill="x")
            ctk.CTkLabel(dev_frame, text=f"[OFFLINE DEV MODE] Kode Anda: {otp_dev}", font=ctk.CTkFont(size=13, weight="bold"), text_color=("#856404", "#FFD700")).pack(padx=12, pady=8)

        self.otp_entry = ctk.CTkEntry(self, placeholder_text="000000", width=200, height=50, font=ctk.CTkFont(size=24, weight="bold"), justify="center")
        self.otp_entry.pack(pady=8)

        self.otp_error = ctk.CTkLabel(self, text="", text_color="#FF3B30", font=ctk.CTkFont(size=11), wraplength=300)
        self.otp_error.pack(pady=(0, 4))
        ctk.CTkButton(self, text=t("btn_verif_otp", bhs), width=280, height=44, font=ctk.CTkFont(size=14, weight="bold"), command=self._verif_otp).pack(pady=6)

    def _verif_otp(self):
        otp = self.otp_entry.get().strip()
        if not otp or len(otp) != 6 or not otp.isdigit():
            self.otp_error.configure(text="Masukkan 6 digit kode OTP.")
            return
        self.controller.proses_verifikasi_otp(self._email, otp)
        
    def tampilkan_error_otp(self, message):
        self.otp_error.configure(text=message)

    def lanjut_ke_step3(self, reset_token):
        self._clear()
        bhs = self._bhs

        ctk.CTkFrame(self, height=40, fg_color="transparent").pack()
        ctk.CTkLabel(self, text=t("reset_judul", bhs), font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(0, 4))
        ctk.CTkFrame(self, height=10, fg_color="transparent").pack()

        self.reset_pwd = ctk.CTkEntry(self, placeholder_text=t("f_pwd_baru", bhs), width=320, height=40, show="●")
        self.reset_pwd.pack(pady=6)
        
        self.reset_confirm = ctk.CTkEntry(self, placeholder_text=t("f_pwd_konfirm", bhs), width=320, height=40, show="●")
        self.reset_confirm.pack(pady=6)

        self.reset_error = ctk.CTkLabel(self, text="", text_color="#FF3B30", font=ctk.CTkFont(size=11), wraplength=300)
        self.reset_error.pack(pady=(0, 4))

        ctk.CTkButton(self, text=t("btn_reset", bhs), width=320, height=44, font=ctk.CTkFont(size=14, weight="bold"), command=self._do_reset).pack(pady=8)

    def _do_reset(self):
        pwd = self.reset_pwd.get()
        confirm = self.reset_confirm.get()
        self.controller.proses_reset_password(self._email, pwd, confirm)
        
    def tampilkan_error_reset(self, message):
        self.reset_error.configure(text=message)
        
    def tampilkan_pesan_sukses(self, message):
        messagebox.showinfo("Berhasil", message)
        self.controller.tampilkan_auth()
=======
        # Logo
        logo_f = ctk.CTkFrame(card, fg_color="transparent")
        logo_f.pack(pady=(36, 0))
        try:
            from PIL import Image
            import os
            logo_path = os.path.abspath(os.path.join(
                os.path.dirname(__file__), "..", "assets", "logo_beaply.png"))
            img = ctk.CTkImage(light_image=Image.open(logo_path), size=(140, 65))
            ctk.CTkLabel(logo_f, text="", image=img).pack()
        except Exception:
            ctk.CTkLabel(logo_f, text="beaply",
                         font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
                         text_color=TEXT_ACCENT).pack()

        ctk.CTkLabel(card, text=t("login_subjudul"),
                     font=ctk.CTkFont(size=12), text_color=TEXT_MUTED).pack(pady=(4, 24))

        self.e_email = ctk.CTkEntry(card, placeholder_text="Email",
                                    width=340, height=42, corner_radius=10,
                                    fg_color=INPUT_BG, border_width=0, text_color=TEXT_DARK)
        self.e_email.pack(pady=6)
        self.e_pass = ctk.CTkEntry(card, placeholder_text=t("field_password"),
                                   width=340, height=42, corner_radius=10,
                                   fg_color=INPUT_BG, border_width=0,
                                   text_color=TEXT_DARK, show="•")
        self.e_pass.pack(pady=6)

        ctk.CTkButton(card, text=t("login_lupa_sandi"), fg_color="transparent",
                      text_color=TEXT_ACCENT, hover_color=BTN_PALE,
                      font=ctk.CTkFont(size=11), height=24,
                      command=self._go_lupa_sandi).pack(anchor="e", padx=50)

        self.err_lbl = ctk.CTkLabel(card, text="", text_color="#FF3B30",
                                    font=ctk.CTkFont(size=11))
        self.err_lbl.pack(pady=2)

        ctk.CTkButton(card, text=t("btn_masuk"), width=280, height=44,
                      corner_radius=12, fg_color=BTN_PRIMARY,
                      hover_color=BTN_PRIMARY_HOVER, text_color=TEXT_DARK,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=self._do_login).pack(pady=8)

        foot = ctk.CTkFrame(card, fg_color="transparent")
        foot.pack(pady=(12, 0))
        ctk.CTkLabel(foot, text=t("login_blm_punya"),
                     font=ctk.CTkFont(size=11), text_color=TEXT_MUTED).pack(side="left")
        ctk.CTkButton(foot, text=t("btn_daftar"), fg_color="transparent",
                      text_color=TEXT_ACCENT, hover_color=BTN_PALE,
                      font=ctk.CTkFont(size=11, weight="bold"), height=24,
                      command=self._go_register).pack(side="left")

    # ── REGISTER ─────────────────────────────────────────────

    def _build_register(self):
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")
        card = ctk.CTkFrame(center, fg_color=CARD_COLOR, corner_radius=24,
                            width=440, height=600, border_width=1,
                            border_color=BORDER_COLOR)
        card.pack()
        card.pack_propagate(False)

        ctk.CTkLabel(card, text=t("reg_judul"),
                     font=ctk.CTkFont(size=24, weight="bold"),
                     text_color=TEXT_DARK).pack(pady=(32, 4))
        ctk.CTkLabel(card, text=t("reg_subjudul"),
                     font=ctk.CTkFont(size=11), text_color=TEXT_MUTED).pack(pady=(0, 20))

        def field(ph, show=""):
            e = ctk.CTkEntry(card, placeholder_text=ph, width=340, height=42,
                             corner_radius=10, fg_color=INPUT_BG, border_width=0,
                             text_color=TEXT_DARK, show=show)
            e.pack(pady=5)
            return e

        self.r_nama  = field(t("field_nama"))
        self.r_email = field("Email")
        self.r_pass  = field(t("field_password"), "•")
        self.r_pass2 = field(t("field_konfirmasi_pass"), "•")

        self.pw_strength = ctk.CTkLabel(card, text="", font=ctk.CTkFont(size=10))
        self.pw_strength.pack()
        self.r_pass.bind("<KeyRelease>", self._check_pw_strength)

        self.err_reg = ctk.CTkLabel(card, text="", text_color="#FF3B30",
                                    font=ctk.CTkFont(size=11))
        self.err_reg.pack(pady=2)

        ctk.CTkButton(card, text=t("btn_daftar_sekarang"), width=280, height=44,
                      corner_radius=12, fg_color=BTN_PRIMARY,
                      hover_color=BTN_PRIMARY_HOVER, text_color=TEXT_DARK,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=self._do_register).pack(pady=6)

        foot = ctk.CTkFrame(card, fg_color="transparent")
        foot.pack(pady=(8, 0))
        ctk.CTkLabel(foot, text=t("reg_sdh_punya"),
                     font=ctk.CTkFont(size=11), text_color=TEXT_MUTED).pack(side="left")
        ctk.CTkButton(foot, text=t("btn_masuk"), fg_color="transparent",
                      text_color=TEXT_ACCENT, hover_color=BTN_PALE,
                      font=ctk.CTkFont(size=11, weight="bold"), height=24,
                      command=self._go_login).pack(side="left")

    # ── Actions ──────────────────────────────────────────────

    def _do_login(self):
        email = self.e_email.get().strip()
        pw    = self.e_pass.get()
        ok, data = login_pengguna(email, pw)
        if not ok:
            self.err_lbl.configure(text=data if isinstance(data, str) else "Login gagal.")
            return
        self.login_cb(data)

    def _do_register(self):
        nama  = self.r_nama.get().strip()
        email = self.r_email.get().strip()
        pw    = self.r_pass.get()
        pw2   = self.r_pass2.get()
        if not nama or not email or not pw:
            self.err_reg.configure(text="Semua field wajib diisi.")
            return
        if pw != pw2:
            self.err_reg.configure(text="Password tidak cocok.")
            return
        if not validate_email_format(email):
            self.err_reg.configure(text="Format email tidak valid.")
            return
        ok, msg = registrasi_pengguna(nama, email, pw)
        if not ok:
            self.err_reg.configure(text=msg)
            return
        messagebox.showinfo("Berhasil", "Akun berhasil dibuat! Silakan login.")
        self._go_login()

    def _check_pw_strength(self, event=None):
        pw = self.r_pass.get()
        level, label, color = get_password_strength_level(pw)
        self.pw_strength.configure(text=f"Password strength: {label}", text_color=color)

    def _go_login(self):
        self._mode = "login"
        self._build()

    def _go_register(self):
        self._mode = "register"
        self._build()

    def _go_lupa_sandi(self):
        self.lupa_sandi_cb()


# ════════════════════════════════════════════════════════════
# HALAMAN: Lupa Sandi (3 langkah)
# ════════════════════════════════════════════════════════════

class HalamanLupaSandi(ctk.CTkFrame):
    """Lupa Sandi — 3 step: email → OTP → reset password."""
    def __init__(self, master, kembali_callback):
        super().__init__(master, fg_color=BG_COLOR)
        self._kembali = kembali_callback
        self._step    = 1
        self._email   = ""
        self._build()

    def _build(self):
        for w in self.winfo_children():
            w.destroy()
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")
        card = ctk.CTkFrame(center, fg_color=CARD_COLOR, corner_radius=24,
                            width=400, height=420, border_width=1,
                            border_color=BORDER_COLOR)
        card.pack()
        card.pack_propagate(False)

        ctk.CTkButton(card, text="← Kembali", width=80, height=28,
                      fg_color="transparent", text_color=TEXT_MUTED,
                      hover_color=BTN_PALE, font=ctk.CTkFont(size=11),
                      command=self._kembali).pack(anchor="w", padx=16, pady=(16, 0))

        step_fn = {1: self._build_step1, 2: self._build_step2, 3: self._build_step3}
        step_fn[self._step](card)

    def _entry(self, parent, ph, show=""):
        e = ctk.CTkEntry(parent, placeholder_text=ph, width=300, height=42,
                         corner_radius=10, fg_color=INPUT_BG, border_width=0,
                         text_color=TEXT_DARK, show=show)
        e.pack(pady=6)
        return e

    def _err_lbl(self, parent):
        lbl = ctk.CTkLabel(parent, text="", text_color="#FF3B30", font=ctk.CTkFont(size=11))
        lbl.pack(pady=2)
        return lbl

    def _btn(self, parent, text, cmd):
        ctk.CTkButton(parent, text=text, width=240, height=42, corner_radius=12,
                      fg_color=BTN_PRIMARY, hover_color=BTN_PRIMARY_HOVER,
                      text_color=TEXT_DARK, font=ctk.CTkFont(size=13, weight="bold"),
                      command=cmd).pack(pady=10)

    def _build_step1(self, card):
        ctk.CTkLabel(card, text="Reset Password",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=TEXT_DARK).pack(pady=(12, 4))
        ctk.CTkLabel(card, text="Masukkan email terdaftar Anda.",
                     font=ctk.CTkFont(size=11), text_color=TEXT_MUTED).pack(pady=(0, 20))
        self.e_email_ls = self._entry(card, "Email")
        self.err_ls = self._err_lbl(card)
        self._btn(card, "Kirim Kode OTP", self._kirim_otp)

    def _build_step2(self, card):
        ctk.CTkLabel(card, text="Masukkan Kode OTP",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=TEXT_DARK).pack(pady=(12, 4))
        ctk.CTkLabel(card, text=f"Kode dikirim ke {self._email}",
                     font=ctk.CTkFont(size=11), text_color=TEXT_MUTED).pack(pady=(0, 20))
        self.e_otp = self._entry(card, "Kode OTP (6 digit)")
        self.err_ls = self._err_lbl(card)
        self._btn(card, "Verifikasi", self._verif_otp)

    def _build_step3(self, card):
        ctk.CTkLabel(card, text="Password Baru",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color=TEXT_DARK).pack(pady=(12, 4))
        self.e_new_pw  = self._entry(card, "Password baru", "•")
        self.e_conf_pw = self._entry(card, "Konfirmasi password", "•")
        self.err_ls = self._err_lbl(card)
        self._btn(card, "Reset Password", self._do_reset)

    def _kirim_otp(self):
        email = self.e_email_ls.get().strip()
        ok, msg = lupa_sandi(email)
        if not ok:
            self.err_ls.configure(text=msg)
            return
        self._email = email
        self._step  = 2
        self._build()

    def _verif_otp(self):
        ok, msg = verifikasi_otp(self._email, self.e_otp.get().strip())
        if not ok:
            self.err_ls.configure(text=msg)
            return
        self._step = 3
        self._build()

    def _do_reset(self):
        pw1 = self.e_new_pw.get()
        pw2 = self.e_conf_pw.get()
        if pw1 != pw2:
            self.err_ls.configure(text="Password tidak cocok.")
            return
        ok, msg = reset_password(self._email, pw1)
        if not ok:
            self.err_ls.configure(text=msg)
            return
        messagebox.showinfo("Berhasil", "Password berhasil direset! Silakan login.")
        self._kembali()
>>>>>>> 14a6b3f28e0f19b0c641fd9179026190a55f2248
