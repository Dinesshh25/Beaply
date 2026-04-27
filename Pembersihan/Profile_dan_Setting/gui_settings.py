import customtkinter as ctk
from tkinter import messagebox
from ui_utils import (
    BG_COLOR, CARD_COLOR, BORDER_COLOR, TEXT_DARK, TEXT_MUTED,
    BTN_PALE, BTN_PRIMARY, BTN_PRIMARY_HOVER, INPUT_BG,
    show_error, show_info, konfirm_yesno, get_bahasa
)
from Profile_dan_Setting.settings import ambil_preferensi
from Profile_dan_Setting.profile import tampil_profil
from Profile_dan_Setting.settings import hapus_akun, simpan_preferensi

# ════════════════════════════════════════════════════════════
# WINDOW SETTINGS (Popup)
# ════════════════════════════════════════════════════════════

class SettingsWindow(ctk.CTkToplevel):
    """Settings — redesigned to match mockup."""
    def __init__(self, master, profil_id, logout_callback, apply_pref_callback=None):
        super().__init__(master)
        self.title("Settings")
        self.geometry("650x750")
        self.configure(fg_color=BG_COLOR)
        self.profil_id = profil_id
        self.logout = logout_callback
        self.apply_pref_callback = apply_pref_callback
        self._bhs = get_bahasa(profil_id)
        self._build()

    def _build(self):
        for w in self.winfo_children():
            w.destroy()
        bhs = self._bhs

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=24, pady=20)

        # ── Account & Security ──
        ctk.CTkLabel(scroll, text="Account & Security",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=TEXT_DARK).pack(anchor="w", pady=(0, 8))
        sec_card = ctk.CTkFrame(scroll, fg_color=CARD_COLOR, corner_radius=14,
                                border_width=1, border_color=BORDER_COLOR)
        sec_card.pack(fill="x", pady=(0, 16))

        # Change Password row
        pw_r = ctk.CTkFrame(sec_card, fg_color="transparent")
        pw_r.pack(fill="x", padx=20, pady=16)
        pw_txt = ctk.CTkFrame(pw_r, fg_color="transparent")
        pw_txt.pack(side="left")
        ctk.CTkLabel(pw_txt, text="Change Password",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_DARK).pack(anchor="w")
        ctk.CTkLabel(pw_txt, text="Change password to keep account secure",
                     font=ctk.CTkFont(size=10), text_color=TEXT_MUTED).pack(anchor="w")
        ctk.CTkButton(pw_r, text=">", width=32, height=32,
                      fg_color="transparent", text_color=TEXT_DARK,
                      hover_color=BTN_PALE, corner_radius=8,
                      command=self._popup_change_pw).pack(side="right")

        # Separator
        ctk.CTkFrame(sec_card, height=1, fg_color=BORDER_COLOR).pack(fill="x", padx=20)

        # Email verification row
        profil = tampil_profil(self.profil_id) or {}
        em_r = ctk.CTkFrame(sec_card, fg_color="transparent")
        em_r.pack(fill="x", padx=20, pady=16)
        em_txt = ctk.CTkFrame(em_r, fg_color="transparent")
        em_txt.pack(side="left")
        ctk.CTkLabel(em_txt, text="Email Verification",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_DARK).pack(anchor="w")
        ctk.CTkLabel(em_txt, text=f"Verified email: {profil.get('email', 'N/A')}",
                     font=ctk.CTkFont(size=10), text_color=TEXT_MUTED).pack(anchor="w")
        ctk.CTkLabel(em_r, text="Verified", fg_color=BTN_PRIMARY,
                     corner_radius=8, text_color=TEXT_DARK,
                     font=ctk.CTkFont(size=10, weight="bold"),
                     width=70, height=26).pack(side="right")

        # ── Display ──
        ctk.CTkLabel(scroll, text="Display",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=TEXT_DARK).pack(anchor="w", pady=(8, 8))
        disp_card = ctk.CTkFrame(scroll, fg_color=CARD_COLOR, corner_radius=14,
                                 border_width=1, border_color=BORDER_COLOR)
        disp_card.pack(fill="x", pady=(0, 16))
        pref = ambil_preferensi(self.profil_id)

        # Theme row
        def settings_row(parent, title, desc, widget, sep=True):
            r = ctk.CTkFrame(parent, fg_color="transparent")
            r.pack(fill="x", padx=20, pady=14)
            txt = ctk.CTkFrame(r, fg_color="transparent")
            txt.pack(side="left")
            ctk.CTkLabel(txt, text=title, font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=TEXT_DARK).pack(anchor="w")
            ctk.CTkLabel(txt, text=desc, font=ctk.CTkFont(size=10),
                         text_color=TEXT_MUTED).pack(anchor="w")
            widget.pack(side="right", in_=r)
            if sep:
                ctk.CTkFrame(parent, height=1, fg_color=BORDER_COLOR).pack(fill="x", padx=20)

        t_frame = ctk.CTkSegmentedButton(disp_card,
            values=["Light", "Dark", "System"],
            command=self._change_theme)
        tema = pref.get("tema", "light")
        try:
            t_frame.set(tema.capitalize())
        except:
            pass
        settings_row(disp_card, "Theme", "Select application theme", t_frame)

        l_frame = ctk.CTkComboBox(disp_card,
            values=["Bahasa Indonesia", "English"],
            width=160, height=30, corner_radius=8,
            command=self._change_lang)
        l_frame.set("Bahasa Indonesia" if pref.get("bahasa") == "id" else "English")
        settings_row(disp_card, "Language", "Select interface language", l_frame)

        s_frame = ctk.CTkSegmentedButton(disp_card,
            values=["Small", "Medium", "Large"])
        ukuran = pref.get("ukuran_teks", "medium")
        try:
            s_frame.set(ukuran.capitalize())
        except:
            pass
        settings_row(disp_card, "Text Size", "Select text size", s_frame, sep=False)

        # ── Notification ──
        ctk.CTkLabel(scroll, text="Notification",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=TEXT_DARK).pack(anchor="w", pady=(8, 8))
        notif_card = ctk.CTkFrame(scroll, fg_color=CARD_COLOR, corner_radius=14,
                                  border_width=1, border_color=BORDER_COLOR)
        notif_card.pack(fill="x", pady=(0, 16))
        nr = ctk.CTkFrame(notif_card, fg_color="transparent")
        nr.pack(fill="x", padx=20, pady=16)
        ctk.CTkLabel(nr, text="Push notifications",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_DARK).pack(side="left")
        ctk.CTkSwitch(nr, text="", width=40).pack(side="right")

        # ── Delete Account ──
        del_card = ctk.CTkFrame(scroll, fg_color=CARD_COLOR, corner_radius=14,
                                border_width=2, border_color="#D94040")
        del_card.pack(fill="x", pady=(8, 0))
        ctk.CTkButton(del_card, text="Delete Account",
                      fg_color="transparent", text_color="#D94040",
                      hover_color="#FCE8E8",
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._do_hapus).pack(pady=14)

    def _save_pref_partial(self, key, value):
        pref = ambil_preferensi(self.profil_id)
        pref[key] = value
        simpan_preferensi(self.profil_id, pref["tema"], pref["ukuran_teks"], pref["bahasa"])

    def _change_theme(self, choice):
        val_map = {"Light": "light", "Dark": "dark", "System": "system"}
        act = val_map.get(choice, "system")
        ctk.set_appearance_mode(act)
        self._save_pref_partial("tema", act)

    def _change_lang(self, choice):
        act = "id" if choice == "Bahasa Indonesia" else "en"
        self._save_pref_partial("bahasa", act)
        self._bhs = act
        self._build()
        if self.apply_pref_callback:
            self.apply_pref_callback()

    def _do_hapus(self):
        bhs = self._bhs
        if konfirm_yesno(self, "Delete Account", "Are you sure? This can't be undone."):
            ok, msg = hapus_akun(self.profil_id, True)
            if ok:
                show_info(self, "Done", "Account deleted.")
                self.destroy()
                self.logout()
            else:
                show_error(self, "Error", msg)

    def _popup_change_pw(self):
        bhs = self._bhs
        top = ctk.CTkToplevel(self)
        top.title("Change Password")
        top.geometry("380x320")
        top.configure(fg_color=BG_COLOR)
        top.transient(self)
        top.grab_set()
        ctk.CTkLabel(top, text="Change Password",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=TEXT_DARK).pack(pady=(20, 16))
        e1 = ctk.CTkEntry(top, placeholder_text="Current Password", show="*",
                          height=38, corner_radius=10, fg_color=INPUT_BG, border_width=0)
        e1.pack(pady=5, padx=24, fill="x")
        e2 = ctk.CTkEntry(top, placeholder_text="New Password", show="*",
                          height=38, corner_radius=10, fg_color=INPUT_BG, border_width=0)
        e2.pack(pady=5, padx=24, fill="x")
        e3 = ctk.CTkEntry(top, placeholder_text="Confirm New Password", show="*",
                          height=38, corner_radius=10, fg_color=INPUT_BG, border_width=0)
        e3.pack(pady=5, padx=24, fill="x")

        def save_pw():
            if not e1.get() or not e2.get() or not e3.get():
                return show_error(top, "Error", "All fields required!")
            if e2.get() != e3.get():
                return show_error(top, "Error", "Passwords don't match!")
            show_info(top, "Success", "Password changed!")
            top.destroy()

        ctk.CTkButton(top, text="Change Password", height=40,
                      fg_color=BTN_PRIMARY, hover_color=BTN_PRIMARY_HOVER,
                      text_color=TEXT_DARK, corner_radius=12,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=save_pw).pack(pady=20, padx=24, fill="x")


# ════════════════════════════════════════════════════════════
# HALAMAN: Settings (Inline)
# ════════════════════════════════════════════════════════════

class HalamanSettings(ctk.CTkFrame):
    """Settings — inline version matching mockup."""
    def __init__(self, master, profil_id, bhs="id", logout_cb=None):
        super().__init__(master, fg_color="transparent")
        self.profil_id = profil_id
        self._bhs = bhs
        self._logout_cb = logout_cb
        self._build()

    def _build(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        ctk.CTkLabel(scroll, text="Manage your account preferences and security",
                     font=ctk.CTkFont(size=12), text_color=TEXT_MUTED).pack(
            anchor="w", pady=(0, 16))

        # ── Account & Security ──
        ctk.CTkLabel(scroll, text="Account & Security",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=TEXT_DARK).pack(anchor="w", pady=(0, 8))
        sec_card = ctk.CTkFrame(scroll, fg_color=CARD_COLOR, corner_radius=14,
                                border_width=1, border_color=BORDER_COLOR)
        sec_card.pack(fill="x", pady=(0, 16))

        pw_r = ctk.CTkFrame(sec_card, fg_color="transparent")
        pw_r.pack(fill="x", padx=20, pady=14)
        pw_txt = ctk.CTkFrame(pw_r, fg_color="transparent")
        pw_txt.pack(side="left")
        ctk.CTkLabel(pw_txt, text="Change Password",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_DARK).pack(anchor="w")
        ctk.CTkLabel(pw_txt, text="Change password to keep account secure",
                     font=ctk.CTkFont(size=10), text_color=TEXT_MUTED).pack(anchor="w")
        ctk.CTkButton(pw_r, text=">", width=32, height=32,
                      fg_color="transparent", text_color=TEXT_DARK,
                      hover_color=BTN_PALE, corner_radius=8,
                      command=self._popup_change_pw).pack(side="right")

        ctk.CTkFrame(sec_card, height=1, fg_color=BORDER_COLOR).pack(fill="x", padx=20)

        profil = tampil_profil(self.profil_id) or {}
        em_r = ctk.CTkFrame(sec_card, fg_color="transparent")
        em_r.pack(fill="x", padx=20, pady=14)
        em_txt = ctk.CTkFrame(em_r, fg_color="transparent")
        em_txt.pack(side="left")
        ctk.CTkLabel(em_txt, text="Email Verification",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_DARK).pack(anchor="w")
        ctk.CTkLabel(em_txt, text=f"Verified email: {profil.get('email', 'N/A')}",
                     font=ctk.CTkFont(size=10), text_color=TEXT_MUTED).pack(anchor="w")
        ctk.CTkLabel(em_r, text="Verified", fg_color=BTN_PRIMARY,
                     corner_radius=8, text_color=TEXT_DARK,
                     font=ctk.CTkFont(size=10, weight="bold"),
                     width=70, height=26).pack(side="right")

        # ── Display ──
        ctk.CTkLabel(scroll, text="Display",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=TEXT_DARK).pack(anchor="w", pady=(8, 8))
        disp_card = ctk.CTkFrame(scroll, fg_color=CARD_COLOR, corner_radius=14,
                                 border_width=1, border_color=BORDER_COLOR)
        disp_card.pack(fill="x", pady=(0, 16))
        pref = ambil_preferensi(self.profil_id)

        # --- Theme ---
        rt = ctk.CTkFrame(disp_card, fg_color="transparent")
        rt.pack(fill="x", padx=20, pady=12)
        tt = ctk.CTkFrame(rt, fg_color="transparent")
        tt.pack(side="left")
        ctk.CTkLabel(tt, text="Theme", font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT_DARK).pack(anchor="w")
        ctk.CTkLabel(tt, text="Select application theme", font=ctk.CTkFont(size=10), text_color=TEXT_MUTED).pack(anchor="w")
        
        t_frame = ctk.CTkSegmentedButton(rt, values=["Light", "Dark"], command=self._change_theme)
        try: t_frame.set(pref.get("tema", "light").capitalize())
        except: pass
        t_frame.pack(side="right")
        ctk.CTkFrame(disp_card, height=1, fg_color=BORDER_COLOR).pack(fill="x", padx=20)

        # --- Language ---
        rl = ctk.CTkFrame(disp_card, fg_color="transparent")
        rl.pack(fill="x", padx=20, pady=12)
        tl = ctk.CTkFrame(rl, fg_color="transparent")
        tl.pack(side="left")
        ctk.CTkLabel(tl, text="Language", font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT_DARK).pack(anchor="w")
        ctk.CTkLabel(tl, text="Select interface language", font=ctk.CTkFont(size=10), text_color=TEXT_MUTED).pack(anchor="w")
        
        l_frame = ctk.CTkComboBox(rl, values=["Bahasa Indonesia", "English"], width=160, height=30, corner_radius=8, command=self._change_lang)
        l_frame.set("Bahasa Indonesia" if pref.get("bahasa") == "id" else "English")
        l_frame.pack(side="right")
        ctk.CTkFrame(disp_card, height=1, fg_color=BORDER_COLOR).pack(fill="x", padx=20)

        # --- Text Size ---
        rs = ctk.CTkFrame(disp_card, fg_color="transparent")
        rs.pack(fill="x", padx=20, pady=12)
        ts = ctk.CTkFrame(rs, fg_color="transparent")
        ts.pack(side="left")
        ctk.CTkLabel(ts, text="Text Size", font=ctk.CTkFont(size=13, weight="bold"), text_color=TEXT_DARK).pack(anchor="w")
        ctk.CTkLabel(ts, text="Select text size", font=ctk.CTkFont(size=10), text_color=TEXT_MUTED).pack(anchor="w")
        
        s_frame = ctk.CTkSegmentedButton(rs, values=["Small", "Medium", "Large"], command=self._change_text_size)
        try: s_frame.set(pref.get("ukuran_teks", "medium").capitalize())
        except: pass
        s_frame.pack(side="right")

        # ── Notification ──
        ctk.CTkLabel(scroll, text="Notification",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=TEXT_DARK).pack(anchor="w", pady=(8, 8))
        notif_card = ctk.CTkFrame(scroll, fg_color=CARD_COLOR, corner_radius=14,
                                  border_width=1, border_color=BORDER_COLOR)
        notif_card.pack(fill="x", pady=(0, 16))
        nr = ctk.CTkFrame(notif_card, fg_color="transparent")
        nr.pack(fill="x", padx=20, pady=14)
        ctk.CTkLabel(nr, text="Push notifications",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_DARK).pack(side="left")
        ctk.CTkSwitch(nr, text="", width=40).pack(side="right")

        # ── Delete Account ──
        del_card = ctk.CTkFrame(scroll, fg_color=CARD_COLOR, corner_radius=14,
                                border_width=2, border_color="#D94040")
        del_card.pack(fill="x", pady=(8, 0))
        ctk.CTkButton(del_card, text="Delete Account",
                      fg_color="transparent", text_color="#D94040",
                      hover_color="#FCE8E8",
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._do_hapus).pack(pady=14)

    def _save_pref_partial(self, key, value):
        pref = ambil_preferensi(self.profil_id)
        pref[key] = value
        simpan_preferensi(self.profil_id, pref["tema"], pref["ukuran_teks"], pref["bahasa"])

    def _change_theme(self, choice):
        val_map = {"Light": "light", "Dark": "dark"}
        act = val_map.get(choice, "light")
        ctk.set_appearance_mode(act)
        self._save_pref_partial("tema", act)

    def _change_lang(self, choice):
        act = "id" if choice == "Bahasa Indonesia" else "en"
        self._save_pref_partial("bahasa", act)
        if self._logout_cb:
            self._logout_cb()

    def _change_text_size(self, choice):
        act = choice.lower()
        self._save_pref_partial("ukuran_teks", act)
        if act == "small":
            ctk.set_widget_scaling(0.9)
        elif act == "large":
            ctk.set_widget_scaling(1.1)
        else:
            ctk.set_widget_scaling(1.0)

    def _do_hapus(self):
        if konfirm_yesno(self, "Delete Account", "Are you sure? This can't be undone."):
            ok, msg = hapus_akun(self.profil_id, True)
            if ok:
                show_info(self, "Done", "Account deleted.")
                if self._logout_cb:
                    self._logout_cb()
            else:
                show_error(self, "Error", msg)

    def _popup_change_pw(self):
        top = ctk.CTkToplevel(self)
        top.title("Change Password")
        top.geometry("380x320")
        top.configure(fg_color=BG_COLOR)
        top.transient(self.winfo_toplevel())
        top.grab_set()
        ctk.CTkLabel(top, text="Change Password",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=TEXT_DARK).pack(pady=(20, 16))
        e1 = ctk.CTkEntry(top, placeholder_text="Current Password", show="*",
                          height=38, corner_radius=10, fg_color=INPUT_BG, border_width=0)
        e1.pack(pady=5, padx=24, fill="x")
        e2 = ctk.CTkEntry(top, placeholder_text="New Password", show="*",
                          height=38, corner_radius=10, fg_color=INPUT_BG, border_width=0)
        e2.pack(pady=5, padx=24, fill="x")
        e3 = ctk.CTkEntry(top, placeholder_text="Confirm New Password", show="*",
                          height=38, corner_radius=10, fg_color=INPUT_BG, border_width=0)
        e3.pack(pady=5, padx=24, fill="x")
        def save_pw():
            if not e1.get() or not e2.get() or not e3.get():
                return show_error(top, "Error", "All fields required!")
            if e2.get() != e3.get():
                return show_error(top, "Error", "Passwords don't match!")
            show_info(top, "Success", "Password changed!")
            top.destroy()
        ctk.CTkButton(top, text="Change Password", height=40,
                      fg_color=BTN_PRIMARY, hover_color=BTN_PRIMARY_HOVER,
                      text_color=TEXT_DARK, corner_radius=12,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=save_pw).pack(pady=20, padx=24, fill="x")
