import re
import customtkinter as ctk
from tkinter import messagebox
import os

from utils.ui_utils import (
    t, BG_COLOR, CARD_COLOR, BORDER_COLOR, TEXT_ACCENT,
    BTN_PALE, BTN_PRIMARY, BTN_PRIMARY_HOVER, TEXT_DARK,
    INPUT_BG, TEXT_MUTED
)

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
                            border_color=BORDER_COLOR)
        card.pack()
        card.pack_propagate(False)

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
