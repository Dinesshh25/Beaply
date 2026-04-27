"""
views/auth_view.py
Beaply - View: Autentikasi (Login / Register / Lupa Sandi)

Dipindahkan dari: Autentikasi_dan_Keamanan/gui_auth.py
Import sekarang dari Autentikasi_dan_Keamanan.auth (shim controller).
"""
import customtkinter as ctk
from tkinter import messagebox
from ui_utils import (
    t, BG_COLOR, CARD_COLOR, BORDER_COLOR, TEXT_ACCENT,
    BTN_PALE, BTN_PRIMARY, BTN_PRIMARY_HOVER, TEXT_DARK,
    INPUT_BG, TEXT_MUTED
)
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
                            border_color=BORDER_COLOR)
        card.pack()
        card.pack_propagate(False)

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
