import customtkinter as ctk
from tkinter import messagebox
from ui_utils import (
    t, BG_COLOR, CARD_COLOR, BORDER_COLOR, TEXT_ACCENT,
    BTN_PALE, BTN_PRIMARY, BTN_PRIMARY_HOVER, TEXT_DARK,
    INPUT_BG, TEXT_MUTED, PASTEL_COLORS, konfirm_yesno, hitung_completeness
)
from database import ambil_semua_profil_db
from Profile_dan_Setting.profile import (
    input_data_wajib, input_data_spesifik, simpan_profil, tampil_profil
)
from utils import format_tanggal

# We need a shared global profile id placeholder inside the GUI or pass it locally.
# The original relies on main.py PROFIL_AKTIF_ID. Since we are modularizing,
# we should pass callback properly instead of modifying the global directly,
# but to preserve functionality without breaking, we'll keep the self._pilih setting logic in the callback.

# ════════════════════════════════════════════════════════════
# HALAMAN: Home (setelah login, pilih/buat profil)
# ════════════════════════════════════════════════════════════

class HalamanHome(ctk.CTkFrame):
    def __init__(self, master, buka_buat, buka_dashboard, user_id=None):
        super().__init__(master, fg_color=BG_COLOR)
        self.buka_buat      = buka_buat
        self.buka_dashboard = buka_dashboard
        self.user_id        = user_id
        self._build()

    def _build(self):
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")

        card = ctk.CTkFrame(center, fg_color=CARD_COLOR, corner_radius=24,
                            width=440, height=360, border_width=1,
                            border_color=BORDER_COLOR)
        card.pack()
        card.pack_propagate(False)

        logo_f = ctk.CTkFrame(card, fg_color="transparent")
        logo_f.pack(pady=(36, 0))
        try:
            from PIL import Image
            import os
            logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "logo_beaply.png"))
            img = ctk.CTkImage(light_image=Image.open(logo_path), size=(140, 65))
            ctk.CTkLabel(logo_f, text="", image=img).pack()
        except Exception as e:
            print("Logo Error:", e)
            ctk.CTkLabel(logo_f, text="beaply",
                         font=ctk.CTkFont(family="Segoe UI", size=32, weight="bold"),
                         text_color=TEXT_ACCENT).pack()
        ctk.CTkLabel(card, text=t("tagline"),
                     font=ctk.CTkFont(size=12), text_color=TEXT_MUTED).pack(pady=(4, 24))

        ctk.CTkButton(card, text=t("btn_buat"), width=280, height=44,
                      corner_radius=12, fg_color=BTN_PRIMARY,
                      hover_color=BTN_PRIMARY_HOVER, text_color=TEXT_DARK,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=self.buka_buat).pack(pady=6)
        ctk.CTkButton(card, text=t("btn_pilih"), width=280, height=44,
                      corner_radius=12, fg_color="transparent",
                      border_width=1, border_color=BORDER_COLOR,
                      text_color=TEXT_DARK, hover_color=BTN_PALE,
                      font=ctk.CTkFont(size=13),
                      command=self._pilih_profil).pack(pady=6)

    def _pilih_profil(self):
        profils = ambil_semua_profil_db(self.user_id)
        if not profils:
            messagebox.showinfo("Info", t("info_kosong"))
            return
        win = PilihProfilWindow(self, profils, self.buka_dashboard)
        win.grab_set()


# ════════════════════════════════════════════════════════════
# POPUP: Pilih Profil
# ════════════════════════════════════════════════════════════

class PilihProfilWindow(ctk.CTkToplevel):
    def __init__(self, master, profils, callback):
        super().__init__(master)
        self.title(t("judul_pilih"))
        self.geometry("440x400")
        self.resizable(False, False)
        self.configure(fg_color=BG_COLOR)
        self.profils  = profils
        self.callback = callback
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text=t("judul_pilih"),
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=TEXT_DARK).pack(pady=(20, 12))
        frame = ctk.CTkScrollableFrame(self, height=280, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))
        for i, p in enumerate(self.profils):
            bg = PASTEL_COLORS[i % len(PASTEL_COLORS)]
            card = ctk.CTkFrame(frame, fg_color=CARD_COLOR, corner_radius=12,
                                border_width=1, border_color=BORDER_COLOR)
            card.pack(fill="x", pady=4)
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=16, pady=12)
            ctk.CTkLabel(inner, text=p["nama"],
                         font=ctk.CTkFont(size=14, weight="bold"),
                         text_color=TEXT_DARK, anchor="w").pack(fill="x")
            ctk.CTkLabel(inner, text=f"{p['jenjang']} — {p['jurusan']} • {p['kampus']}",
                         font=ctk.CTkFont(size=11), text_color=TEXT_MUTED,
                         anchor="w").pack(fill="x", pady=(2, 0))
            ctk.CTkButton(card, text="Pilih Profil Ini", height=30,
                          fg_color=BTN_PRIMARY, hover_color=BTN_PRIMARY_HOVER,
                          text_color=TEXT_DARK, corner_radius=8,
                          font=ctk.CTkFont(size=11, weight="bold"),
                          command=lambda pid=p["id"]: self._pilih(pid)).pack(
                padx=16, pady=(0, 12))

    def _pilih(self, profil_id):
        self.destroy()
        self.callback(profil_id)


# ════════════════════════════════════════════════════════════
# HALAMAN: Buat Profil Baru
# ════════════════════════════════════════════════════════════

class HalamanBuatProfil(ctk.CTkFrame):
    def __init__(self, master, selesai_callback, kembali_callback, user_id=None):
        super().__init__(master, fg_color="transparent")
        self.selesai = selesai_callback
        self.kembali = kembali_callback
        self.user_id = user_id
        self._bhs    = "id"
        self._build()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(20, 4))
        ctk.CTkButton(hdr, text=t("btn_kembali"), width=90,
                      fg_color="transparent", border_width=1,
                      command=self.kembali).pack(side="left")
        ctk.CTkLabel(hdr, text=t("judul_buat"),
                     font=ctk.CTkFont(size=20, weight="bold")).pack(side="left", padx=16)

        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=24, pady=8)
        self._form_wajib(scroll)
        self._form_spesifik(scroll)

        ctk.CTkButton(self, text=t("btn_simpan"), height=44,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=self._simpan).pack(padx=24, pady=16, fill="x")

    def _form_wajib(self, parent):
        self._sek(parent, t("sek_wajib"))
        self.e_nama    = self._row(parent, t("f_nama"))
        self.e_tgl     = self._row(parent, t("f_tgl"))
        self.e_email   = self._row(parent, t("f_email"))
        self.e_jurusan = self._row(parent, t("f_jurusan"))
        self.e_kampus  = self._row(parent, t("f_kampus"))

        r = ctk.CTkFrame(parent, fg_color="transparent"); r.pack(fill="x", pady=4)
        ctk.CTkLabel(r, text=t("f_jenjang"), width=220, anchor="w").pack(side="left")
        self.dd_jenjang = ctk.CTkComboBox(r, values=["D3","D4","S1","S2","S3"], width=180)
        self.dd_jenjang.set("S1"); self.dd_jenjang.pack(side="left", padx=8)

        self.e_semester = self._row(parent, t("f_semester"))
        self.e_ip       = self._row(parent, t("f_ip"))

        r2 = ctk.CTkFrame(parent, fg_color="transparent"); r2.pack(fill="x", pady=4)
        ctk.CTkLabel(r2, text=t("f_jk"), width=220, anchor="w").pack(side="left")
        self.dd_jk = ctk.CTkComboBox(r2, values=["Laki-laki","Perempuan"], width=180)
        self.dd_jk.set("Laki-laki"); self.dd_jk.pack(side="left", padx=8)

    def _form_spesifik(self, parent):
        self._sek(parent, t("sek_spesifik"))

        r = ctk.CTkFrame(parent, fg_color="transparent"); r.pack(fill="x", pady=4)
        ctk.CTkLabel(r, text=t("f_kip"), width=220, anchor="w").pack(side="left")
        self.var_kip = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(r, text=t("f_kip_ya"), variable=self.var_kip).pack(side="left", padx=8)

        self.e_ielts    = self._row(parent, t("f_ielts"))
        self.e_toefl    = self._row(parent, t("f_toefl"))
        self.e_duolingo = self._row(parent, t("f_duolingo"))
        self.e_sat      = self._row(parent, t("f_sat"))
        self.e_act      = self._row(parent, t("f_act"))
        self.e_gre      = self._row(parent, t("f_gre"))
        self.e_gmat     = self._row(parent, t("f_gmat"))
        self.e_hsk      = self._row(parent, t("f_hsk"))

        r3 = ctk.CTkFrame(parent, fg_color="transparent"); r3.pack(fill="x", pady=4)
        ctk.CTkLabel(r3, text=t("f_jlpt"), width=220, anchor="w").pack(side="left")
        self.dd_jlpt = ctk.CTkComboBox(r3, values=["","N1","N2","N3","N4","N5"], width=180)
        self.dd_jlpt.set(""); self.dd_jlpt.pack(side="left", padx=8)

    def _sek(self, parent, teks):
        ctk.CTkLabel(parent, text=teks,
                     font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(14,2))
        ctk.CTkFrame(parent, height=1, fg_color="gray60").pack(fill="x", pady=(0,6))

    def _row(self, parent, label) -> ctk.CTkEntry:
        r = ctk.CTkFrame(parent, fg_color="transparent"); r.pack(fill="x", pady=4)
        ctk.CTkLabel(r, text=label, width=220, anchor="w", wraplength=210).pack(side="left")
        e = ctk.CTkEntry(r, width=260); e.pack(side="left", padx=8)
        return e

    def _g(self, e): return e.get().strip()

    def _simpan(self):
        dw = input_data_wajib(
            self._g(self.e_nama), self._g(self.e_tgl), self._g(self.e_email),
            self._g(self.e_jurusan), self._g(self.e_kampus),
            self._g(self.e_semester), self._g(self.e_ip),
            self.dd_jenjang.get(), self.dd_jk.get(),
        )
        ds = input_data_spesifik(
            self.var_kip.get(),
            self._g(self.e_ielts), self._g(self.e_toefl), self._g(self.e_duolingo),
            self._g(self.e_sat), self._g(self.e_act), self._g(self.e_gre),
            self._g(self.e_gmat), self._g(self.e_hsk), self.dd_jlpt.get(),
        )
        ok, msg, pid = simpan_profil(dw, ds, user_id=self.user_id)
        if not ok:
            messagebox.showerror(t("gagal"), msg)
            return
        messagebox.showinfo(t("berhasil"), t("ok_buat"))
        self.selesai(pid)


# ════════════════════════════════════════════════════════════
# HALAMAN: Profil
# ════════════════════════════════════════════════════════════

class HalamanProfil(ctk.CTkFrame):
    """Profile page — redesigned to match mockup."""
    def __init__(self, master, profil_id, bhs="id", logout_cb=None):
        super().__init__(master, fg_color="transparent")
        self.profil_id = profil_id
        self._bhs = bhs
        self._logout_cb = logout_cb
        self._build()

    def _build(self):
        bhs = self._bhs
        profil = tampil_profil(self.profil_id)
        if not profil:
            return

        completeness = hitung_completeness(profil)

        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="both", expand=True)

        # LEFT: Profile Completeness
        left = ctk.CTkFrame(grid, fg_color="transparent", width=280)
        left.pack(side="left", fill="y", padx=(0, 12))
        left.pack_propagate(False)

        # Completeness card
        card1 = ctk.CTkFrame(left, fg_color=CARD_COLOR, corner_radius=16,
                             border_width=1, border_color=BORDER_COLOR)
        card1.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(card1, text="Profile\nCompleteness",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=TEXT_DARK, justify="left").pack(
            pady=(24, 16), padx=20, anchor="w")

        # Circle with percentage
        circ = ctk.CTkFrame(card1, fg_color=BG_COLOR, width=120, height=120,
                            corner_radius=60)
        circ.pack(pady=(0, 12))
        circ.pack_propagate(False)
        pct_color = BTN_PRIMARY if completeness >= 80 else TEXT_ACCENT
        ctk.CTkLabel(circ, text=f"{completeness}%",
                     font=ctk.CTkFont(size=26, weight="bold"),
                     text_color=pct_color).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(card1, text="Profile Complete",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_DARK).pack(pady=(0, 4))
        ctk.CTkLabel(card1, text="Complete your profile to\nget more better scholarship\nmatches!",
                     font=ctk.CTkFont(size=10), text_color=TEXT_MUTED,
                     justify="center").pack(pady=(0, 20))

        if completeness < 100:
            ctk.CTkButton(card1, text="Complete Profile",
                          fg_color=BTN_PRIMARY, hover_color=BTN_PRIMARY_HOVER,
                          text_color=TEXT_DARK, corner_radius=10, height=32,
                          font=ctk.CTkFont(size=11, weight="bold"),
                          command=self._show_optional_form).pack(
                fill="x", padx=20, pady=(0, 20))

        # Logout button
        ctk.CTkButton(left, text="Logout", height=40,
                      fg_color="#F6D6D0", hover_color="#F0C0B8",
                      text_color="#D94040", corner_radius=12,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._do_logout).pack(fill="x", pady=(4, 0))

        # RIGHT: Personal info
        right_frame = ctk.CTkFrame(grid, fg_color=CARD_COLOR, corner_radius=16,
                                   border_width=1, border_color=BORDER_COLOR)
        right_frame.pack(side="left", fill="both", expand=True)

        header = ctk.CTkFrame(right_frame, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 12))
        ctk.CTkLabel(header, text="Personal Informations",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=TEXT_DARK).pack(side="left")
        ctk.CTkButton(header, text="Edit Profile", width=110, height=34,
                      fg_color=BTN_PRIMARY, hover_color=BTN_PRIMARY_HOVER,
                      text_color=TEXT_DARK, corner_radius=10,
                      font=ctk.CTkFont(size=11, weight="bold"),
                      command=self._show_optional_form).pack(side="right")

        scroll = ctk.CTkScrollableFrame(right_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        def baris(label, val, is_empty=False):
            r = ctk.CTkFrame(scroll, fg_color="transparent")
            r.pack(fill="x", pady=4)
            ctk.CTkLabel(r, text=label, width=160, anchor="w",
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=TEXT_DARK).pack(side="left")
            val_color = TEXT_MUTED if is_empty else TEXT_DARK
            val_text = str(val) if val and str(val).strip() else "Not filled"
            ctk.CTkLabel(r, text=val_text, anchor="w",
                         font=ctk.CTkFont(size=12),
                         text_color=val_color).pack(side="left", padx=8)

        # Required fields
        ctk.CTkLabel(scroll, text="Required Information",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_ACCENT).pack(anchor="w", pady=(4, 6))
        baris("Full Name", profil["nama"])
        baris("Date of Birth", format_tanggal(profil["tanggal_lahir"]))
        baris("Email", profil["email"])
        baris("Major", profil["jurusan"])
        baris("University", profil["kampus"])
        baris("Degree", profil["jenjang"])
        baris("Semester", profil["semester"])
        baris("GPA", f"{profil['ip']:.2f}")
        baris("Gender", profil.get("jenis_kelamin", ""))

        # Optional fields
        ctk.CTkLabel(scroll, text="Optional Information",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_ACCENT).pack(anchor="w", pady=(16, 6))
        opt_fields = [
            ("IELTS", profil.get("skor_ielts")),
            ("TOEFL iBT", profil.get("skor_toefl")),
            ("Duolingo", profil.get("skor_duolingo")),
            ("SAT", profil.get("skor_sat")),
            ("ACT", profil.get("skor_act")),
            ("GRE", profil.get("skor_gre")),
            ("GMAT", profil.get("skor_gmat")),
            ("HSK", profil.get("skor_hsk")),
            ("JLPT", profil.get("level_jlpt")),
        ]
        for lbl, val in opt_fields:
            is_empty = val is None or val == 0 or val == 0.0 or str(val).strip() == ""
            baris(lbl, val, is_empty=is_empty)

    def _do_logout(self):
        if konfirm_yesno(self, "Logout", "Are you sure you want to logout?"):
            # Find the main app and call logout
            parent = self.winfo_toplevel()
            if hasattr(parent, '_go_logout'):
                parent._go_logout()

    def _show_optional_form(self):
        profil = tampil_profil(self.profil_id)
        if not profil:
            return
        for w in self.winfo_children():
            w.destroy()
        bhs = self._bhs
        ctk.CTkButton(self, text="< Back to Profile", width=140,
                      fg_color="transparent", border_width=1,
                      border_color=BORDER_COLOR, text_color=TEXT_DARK,
                      corner_radius=8, command=self._back_to_profile).pack(
            anchor="w", padx=8, pady=(8, 4))
        ctk.CTkLabel(self, text="Complete Your Profile",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=TEXT_DARK).pack(pady=(4, 12))
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=8)
        self._opt_entries = {}
        opt_fields = [
            ("skor_ielts", "IELTS Score (0.0-9.0)", profil.get("skor_ielts")),
            ("skor_toefl", "TOEFL iBT (0-120)", profil.get("skor_toefl")),
            ("skor_duolingo", "Duolingo (10-160)", profil.get("skor_duolingo")),
            ("skor_sat", "SAT (400-1600)", profil.get("skor_sat")),
            ("skor_act", "ACT (1-36)", profil.get("skor_act")),
            ("skor_gre", "GRE (260-340)", profil.get("skor_gre")),
            ("skor_gmat", "GMAT (200-800)", profil.get("skor_gmat")),
            ("skor_hsk", "HSK (1-6)", profil.get("skor_hsk")),
        ]
        for key, label, current in opt_fields:
            card = ctk.CTkFrame(scroll, fg_color=CARD_COLOR, corner_radius=10,
                                border_width=1, border_color=BORDER_COLOR)
            card.pack(fill="x", pady=3)
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=16, pady=10)
            ctk.CTkLabel(inner, text=label, width=180, anchor="w",
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=TEXT_DARK).pack(side="left")
            e = ctk.CTkEntry(inner, width=160, height=32, corner_radius=8,
                             fg_color=INPUT_BG, border_width=0, text_color=TEXT_DARK)
            e.pack(side="left")
            if current and current != 0 and current != 0.0:
                e.insert(0, str(current))
            self._opt_entries[key] = e

        card = ctk.CTkFrame(scroll, fg_color=CARD_COLOR, corner_radius=10,
                            border_width=1, border_color=BORDER_COLOR)
        card.pack(fill="x", pady=3)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=10)
        ctk.CTkLabel(inner, text="JLPT Level", width=180, anchor="w",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=TEXT_DARK).pack(side="left")
        profil_data = tampil_profil(self.profil_id) or {}
        self._jlpt_dd = ctk.CTkComboBox(inner, values=["", "N1", "N2", "N3", "N4", "N5"],
                                        width=160, height=32)
        self._jlpt_dd.set(profil_data.get("level_jlpt", "") or "")
        self._jlpt_dd.pack(side="left")

        ctk.CTkButton(self, text="Save Optional Data", height=40,
                      fg_color=BTN_PRIMARY, hover_color=BTN_PRIMARY_HOVER,
                      text_color=TEXT_DARK, corner_radius=12,
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=self._save_optional).pack(fill="x", padx=8, pady=(12, 16))

    def _save_optional(self):
        from database import get_connection
        updates = {}
        for key, entry in self._opt_entries.items():
            val = entry.get().strip()
            if val:
                try:
                    if key == "skor_ielts":
                        updates[key] = float(val)
                    else:
                        updates[key] = int(val)
                except ValueError:
                    pass
            else:
                updates[key] = None
        jlpt = self._jlpt_dd.get().strip()
        updates["level_jlpt"] = jlpt if jlpt else None
        if updates:
            conn = get_connection()
            cur = conn.cursor()
            set_clause = ", ".join(f"{k} = ?" for k in updates)
            vals = list(updates.values()) + [self.profil_id]
            cur.execute(f"UPDATE profil SET {set_clause} WHERE id = ?", vals)
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Optional data saved!")
        self._back_to_profile()

    def _back_to_profile(self):
        for w in self.winfo_children():
            w.destroy()
        self._build()
