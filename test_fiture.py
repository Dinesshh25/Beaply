"""
main.py
Beaply — Aplikasi Desktop Manajemen Profil & Beasiswa
GUI: CustomTkinter
"""

import customtkinter as ctk
from tkinter import messagebox
from Beaply.database import init_db, ambil_semua_profil_db
from profile import (
    input_data_wajib, input_data_spesifik,
    simpan_profil, tampil_profil,
)
from Beaply.settings import (
    edit_profil, simpan_edit_profil,
    hapus_akun, simpan_preferensi, ambil_preferensi,
)
from Beaply.utils import format_tanggal

init_db()

PROFIL_AKTIF_ID = None


# ════════════════════════════════════════════════════════════
# TERJEMAHAN (i18n)
# ════════════════════════════════════════════════════════════

TEKS = {
    "id": {
        "tagline":          "Insight Beasiswa untuk Mahasiswa",
        "btn_buat":         "+ Buat Profil Baru",
        "btn_pilih":        "Pilih Profil yang Ada",
        "info_kosong":      "Belum ada profil. Buat profil dulu ya!",
        "judul_pilih":      "Pilih Profil",
        "judul_buat":       "Buat Profil Baru",
        "btn_kembali":      "← Kembali",
        "btn_simpan":       "Simpan Profil",
        "sek_wajib":        "Data Wajib",
        "sek_spesifik":     "Data Spesifik (Opsional)",
        "f_nama":           "Nama Lengkap *",
        "f_tgl":            "Tanggal Lahir * (YYYY-MM-DD)",
        "f_email":          "Email *",
        "f_jurusan":        "Jurusan *",
        "f_kampus":         "Nama Kampus *",
        "f_jenjang":        "Jenjang *",
        "f_semester":       "Semester *",
        "f_ip":             "IP Terakhir * (0.00–4.00)",
        "f_jk":             "Jenis Kelamin *",
        "f_kip":            "Penerima KIP",
        "f_kip_ya":         "Ya",
        "f_ielts":          "Skor IELTS (0.0–9.0)",
        "f_toefl":          "Skor TOEFL iBT (0–120)",
        "f_duolingo":       "Skor Duolingo (10–160)",
        "f_sat":            "Skor SAT (400–1600)",
        "f_act":            "Skor ACT (1–36)",
        "f_gre":            "Skor GRE (260–340)",
        "f_gmat":           "Skor GMAT (200–800)",
        "f_hsk":            "Skor HSK (1–6)",
        "f_jlpt":           "Level JLPT",
        "ok_buat":          "Profil berhasil dibuat! 🎉",
        "sapa":             "Halo",
        "btn_settings":     "⚙ Pengaturan",
        "btn_logout":       "Keluar",
        "judul_profil":     "📋 Profil Mahasiswa",
        "judul_skor":       "Skor Tes Bahasa / Kemampuan",
        "lb_nama":          "Nama",
        "lb_tgl":           "Tgl Lahir",
        "lb_email":         "Email",
        "lb_jurusan":       "Jurusan",
        "lb_kampus":        "Kampus",
        "lb_jenjang":       "Jenjang",
        "lb_semester":      "Semester",
        "lb_ip":            "IP",
        "lb_jk":            "Jenis Kelamin",
        "lb_kip":           "KIP",
        "v_ya":             "Ya",
        "v_tidak":          "Tidak",
        "judul_settings":   "⚙ Pengaturan",
        "tab_edit":         "Edit Profil",
        "tab_pref":         "Preferensi",
        "tab_hapus":        "Hapus Akun",
        "btn_simpan_edit":  "Simpan Perubahan",
        "ok_edit":          "Profil berhasil diperbarui.",
        "lb_tema":          "Tema Tampilan",
        "lb_ukuran":        "Ukuran Teks",
        "lb_bahasa":        "Bahasa Antarmuka",
        "opt_light":        "☀ Mode Terang",
        "opt_dark":         "🌙 Mode Gelap",
        "opt_small":        "Kecil",
        "opt_medium":       "Sedang",
        "opt_large":        "Besar",
        "opt_id":           "🇮🇩 Bahasa Indonesia",
        "opt_en":           "🇬🇧 English",
        "btn_simpan_pref":  "Simpan Preferensi",
        "ok_pref":          "Preferensi tersimpan!",
        "warn_hapus":       "⚠️ Hapus Akun",
        "teks_hapus":       "Aksi ini tidak bisa dibatalkan.\nSeluruh data profilmu akan dihapus permanen.",
        "btn_hapus":        "Hapus Akun Saya",
        "konfirm_judul":    "Konfirmasi Hapus",
        "konfirm_teks":     "Kamu yakin ingin menghapus akun ini?\nData tidak bisa dipulihkan!",
        "ok_hapus":         "Akun berhasil dihapus.",
        "batal_hapus":      "Penghapusan dibatalkan.",
        "gagal":            "Gagal",
        "berhasil":         "Berhasil",
        "akun_dihapus":     "Akun Dihapus",
        "dibatalkan":       "Dibatalkan",
    },
    "en": {
        "tagline":          "Scholarship Insight for Students",
        "btn_buat":         "+ Create New Profile",
        "btn_pilih":        "Select Existing Profile",
        "info_kosong":      "No profiles yet. Create one first!",
        "judul_pilih":      "Select Profile",
        "judul_buat":       "Create New Profile",
        "btn_kembali":      "← Back",
        "btn_simpan":       "Save Profile",
        "sek_wajib":        "Required Data",
        "sek_spesifik":     "Specific Data (Optional)",
        "f_nama":           "Full Name *",
        "f_tgl":            "Date of Birth * (YYYY-MM-DD)",
        "f_email":          "Email *",
        "f_jurusan":        "Major *",
        "f_kampus":         "University Name *",
        "f_jenjang":        "Degree *",
        "f_semester":       "Semester *",
        "f_ip":             "Latest GPA * (0.00–4.00)",
        "f_jk":             "Gender *",
        "f_kip":            "KIP Recipient",
        "f_kip_ya":         "Yes",
        "f_ielts":          "IELTS Score (0.0–9.0)",
        "f_toefl":          "TOEFL iBT Score (0–120)",
        "f_duolingo":       "Duolingo Score (10–160)",
        "f_sat":            "SAT Score (400–1600)",
        "f_act":            "ACT Score (1–36)",
        "f_gre":            "GRE Score (260–340)",
        "f_gmat":           "GMAT Score (200–800)",
        "f_hsk":            "HSK Score (1–6)",
        "f_jlpt":           "JLPT Level",
        "ok_buat":          "Profile created successfully! 🎉",
        "sapa":             "Hello",
        "btn_settings":     "⚙ Settings",
        "btn_logout":       "Logout",
        "judul_profil":     "📋 Student Profile",
        "judul_skor":       "Language / Proficiency Test Scores",
        "lb_nama":          "Name",
        "lb_tgl":           "Birth Date",
        "lb_email":         "Email",
        "lb_jurusan":       "Major",
        "lb_kampus":        "University",
        "lb_jenjang":       "Degree",
        "lb_semester":      "Semester",
        "lb_ip":            "GPA",
        "lb_jk":            "Gender",
        "lb_kip":           "KIP",
        "v_ya":             "Yes",
        "v_tidak":          "No",
        "judul_settings":   "⚙ Settings",
        "tab_edit":         "Edit Profile",
        "tab_pref":         "Preferences",
        "tab_hapus":        "Delete Account",
        "btn_simpan_edit":  "Save Changes",
        "ok_edit":          "Profile updated successfully.",
        "lb_tema":          "Display Theme",
        "lb_ukuran":        "Text Size",
        "lb_bahasa":        "Interface Language",
        "opt_light":        "☀ Light Mode",
        "opt_dark":         "🌙 Dark Mode",
        "opt_small":        "Small",
        "opt_medium":       "Medium",
        "opt_large":        "Large",
        "opt_id":           "🇮🇩 Bahasa Indonesia",
        "opt_en":           "🇬🇧 English",
        "btn_simpan_pref":  "Save Preferences",
        "ok_pref":          "Preferences saved!",
        "warn_hapus":       "⚠️ Delete Account",
        "teks_hapus":       "This action cannot be undone.\nAll your profile data will be permanently deleted.",
        "btn_hapus":        "Delete My Account",
        "konfirm_judul":    "Confirm Deletion",
        "konfirm_teks":     "Are you sure you want to delete this account?\nThis cannot be undone!",
        "ok_hapus":         "Account successfully deleted.",
        "batal_hapus":      "Deletion cancelled.",
        "gagal":            "Error",
        "berhasil":         "Success",
        "akun_dihapus":     "Account Deleted",
        "dibatalkan":       "Cancelled",
    },
}

def t(key: str, bhs: str = "id") -> str:
    return TEKS.get(bhs, TEKS["id"]).get(key, key)


# ════════════════════════════════════════════════════════════
# HELPER
# ════════════════════════════════════════════════════════════

def ukuran_font(pref: dict) -> tuple:
    tbl = {"small": (14, 11, 9), "medium": (18, 13, 11), "large": (22, 16, 13)}
    return tbl.get(pref.get("ukuran_teks", "medium"), tbl["medium"])

def apply_pref(pref: dict):
    ctk.set_appearance_mode(pref.get("tema", "light"))

def get_bahasa(profil_id) -> str:
    pref = ambil_preferensi(profil_id)
    return pref.get("bahasa", "id")


# ════════════════════════════════════════════════════════════
# HALAMAN: Home
# ════════════════════════════════════════════════════════════

class HalamanHome(ctk.CTkFrame):
    def __init__(self, master, buka_buat, buka_dashboard):
        super().__init__(master, fg_color="transparent")
        self.buka_buat      = buka_buat
        self.buka_dashboard = buka_dashboard
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text="🎓 Beaply",
                     font=ctk.CTkFont(size=32, weight="bold")).pack(pady=(40, 4))
        ctk.CTkLabel(self, text=t("tagline"),
                     font=ctk.CTkFont(size=14)).pack(pady=(0, 30))
        ctk.CTkButton(self, text=t("btn_buat"),
                      command=self.buka_buat, width=220, height=44,
                      font=ctk.CTkFont(size=14, weight="bold")).pack(pady=8)
        ctk.CTkButton(self, text=t("btn_pilih"),
                      command=self._pilih_profil, width=220, height=44,
                      fg_color="transparent", border_width=2,
                      font=ctk.CTkFont(size=13)).pack(pady=8)

    def _pilih_profil(self):
        profils = ambil_semua_profil_db()
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
        self.geometry("400x360")
        self.resizable(False, False)
        self.profils  = profils
        self.callback = callback
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text=t("judul_pilih"),
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=14)
        frame = ctk.CTkScrollableFrame(self, height=240)
        frame.pack(fill="both", expand=True, padx=16, pady=4)
        for p in self.profils:
            teks = f"{p['nama']}  •  {p['jenjang']} {p['jurusan']}"
            ctk.CTkButton(
                frame, text=teks, anchor="w",
                fg_color="transparent", border_width=1,
                command=lambda pid=p["id"]: self._pilih(pid)
            ).pack(fill="x", pady=3)

    def _pilih(self, profil_id):
        global PROFIL_AKTIF_ID
        PROFIL_AKTIF_ID = profil_id
        self.destroy()
        self.callback(profil_id)


# ════════════════════════════════════════════════════════════
# HALAMAN: Buat Profil Baru
# ════════════════════════════════════════════════════════════

class HalamanBuatProfil(ctk.CTkFrame):
    def __init__(self, master, selesai_callback, kembali_callback):
        super().__init__(master, fg_color="transparent")
        self.selesai = selesai_callback
        self.kembali = kembali_callback
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
        self.dd_jenjang = ctk.CTkComboBox(r, values=["S1","S2","S3"], width=180)
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
        ok, msg, pid = simpan_profil(dw, ds)
        if not ok:
            messagebox.showerror(t("gagal"), msg)
            return
        messagebox.showinfo(t("berhasil"), t("ok_buat"))
        self.selesai(pid)


# ════════════════════════════════════════════════════════════
# HALAMAN: Dashboard
# ════════════════════════════════════════════════════════════

class HalamanDashboard(ctk.CTkFrame):
    def __init__(self, master, profil_id, buka_settings, logout_callback):
        super().__init__(master, fg_color="transparent")
        self.profil_id     = profil_id
        self.buka_settings = buka_settings
        self.logout        = logout_callback
        self._refresh()

    def _refresh(self):
        for w in self.winfo_children():
            w.destroy()

        profil = tampil_profil(self.profil_id)
        if not profil:
            ctk.CTkLabel(self, text="Profil tidak ditemukan.").pack(pady=40)
            return

        pref = ambil_preferensi(self.profil_id)
        apply_pref(pref)
        bhs = pref.get("bahasa", "id")
        fs_j, fs_n, fs_s = ukuran_font(pref)

        # ── top bar ──
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=24, pady=(16, 4))
        nama_depan = profil["nama"].split()[0]
        ctk.CTkLabel(bar, text=f"{t('sapa', bhs)}, {nama_depan}! 👋",
                     font=ctk.CTkFont(size=fs_j, weight="bold")).pack(side="left")
        ctk.CTkButton(bar, text=t("btn_logout", bhs), width=80,
                      fg_color="transparent", border_width=1,
                      command=self.logout).pack(side="right", padx=4)
        ctk.CTkButton(bar, text=t("btn_settings", bhs), width=120,
                      fg_color="transparent", border_width=1,
                      command=lambda: self.buka_settings(self.profil_id, self._refresh)
                      ).pack(side="right", padx=4)

        # ── scroll ──
        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=24, pady=8)
        self._card_profil(scroll, profil, bhs, fs_n, fs_s)

    def _card_profil(self, parent, p, bhs, fs_n, fs_s):
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.pack(fill="x", pady=8)

        ctk.CTkLabel(card, text=t("judul_profil", bhs),
                     font=ctk.CTkFont(size=fs_n+1, weight="bold")).pack(
            anchor="w", padx=16, pady=(12, 4))

        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(fill="x", padx=16, pady=(0, 4))
        kiri  = ctk.CTkFrame(grid, fg_color="transparent")
        kanan = ctk.CTkFrame(grid, fg_color="transparent")
        kiri.pack(side="left", fill="both", expand=True)
        kanan.pack(side="left", fill="both", expand=True)

        def baris(frm, key_lbl, val):
            r = ctk.CTkFrame(frm, fg_color="transparent"); r.pack(fill="x", pady=2)
            ctk.CTkLabel(r, text=f"{t(key_lbl, bhs)}:", width=110, anchor="w",
                         font=ctk.CTkFont(size=fs_s, weight="bold")).pack(side="left")
            ctk.CTkLabel(r, text=str(val), anchor="w",
                         font=ctk.CTkFont(size=fs_s)).pack(side="left", padx=4)

        baris(kiri,  "lb_nama",     p["nama"])
        baris(kiri,  "lb_tgl",      format_tanggal(p["tanggal_lahir"]))
        baris(kiri,  "lb_email",    p["email"])
        baris(kiri,  "lb_jurusan",  p["jurusan"])
        baris(kiri,  "lb_kampus",   p["kampus"])
        baris(kanan, "lb_jenjang",  p["jenjang"])
        baris(kanan, "lb_semester", p["semester"])
        baris(kanan, "lb_ip",       f"{p['ip']:.2f}")
        baris(kanan, "lb_jk",       p["jenis_kelamin"])
        baris(kanan, "lb_kip",      t("v_ya", bhs) if p["status_kip"] else t("v_tidak", bhs))

        # Skor tes (hanya yang diisi)
        tes = {
            "IELTS": p.get("skor_ielts"), "TOEFL": p.get("skor_toefl"),
            "Duolingo": p.get("skor_duolingo"), "SAT": p.get("skor_sat"),
            "ACT": p.get("skor_act"), "GRE": p.get("skor_gre"),
            "GMAT": p.get("skor_gmat"), "HSK": p.get("skor_hsk"),
            "JLPT": p.get("level_jlpt"),
        }
        ada = {k: v for k, v in tes.items() if v is not None and str(v).strip() != ""}
        if ada:
            ctk.CTkLabel(card, text=t("judul_skor", bhs),
                         font=ctk.CTkFont(size=fs_s, weight="bold")).pack(
                anchor="w", padx=16, pady=(6, 2))
            baris_tes = ctk.CTkFrame(card, fg_color="transparent")
            baris_tes.pack(fill="x", padx=16, pady=(0, 10))
            for k, v in ada.items():
                ctk.CTkLabel(baris_tes, text=f"{k}: {v}",
                             font=ctk.CTkFont(size=fs_s)).pack(side="left", padx=8)

        ctk.CTkFrame(card, height=10, fg_color="transparent").pack()


# ════════════════════════════════════════════════════════════
# WINDOW SETTINGS (Popup)
# ════════════════════════════════════════════════════════════

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, master, profil_id, refresh_callback):
        super().__init__(master)
        self.profil_id = profil_id
        self.refresh   = refresh_callback
        self._bhs      = get_bahasa(profil_id)
        self.title(t("judul_settings", self._bhs))
        self.geometry("580x700")
        self.resizable(False, False)
        self._build()

    def _build(self):
        bhs = self._bhs
        ctk.CTkLabel(self, text=t("judul_settings", bhs),
                     font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 4))

        tab = ctk.CTkTabview(self)
        tab.pack(fill="both", expand=True, padx=16, pady=8)
        for key in ["tab_edit", "tab_pref", "tab_hapus"]:
            tab.add(t(key, bhs))

        self._tab_edit( tab.tab(t("tab_edit",  bhs)))
        self._tab_pref( tab.tab(t("tab_pref",  bhs)))
        self._tab_hapus(tab.tab(t("tab_hapus", bhs)))

    # ── Tab Edit Profil ──────────────────────────────────
    def _tab_edit(self, parent):
        profil = tampil_profil(self.profil_id)
        if not profil:
            ctk.CTkLabel(parent, text="Profil tidak ditemukan.").pack(pady=20)
            return
        bhs = self._bhs

        scroll = ctk.CTkScrollableFrame(parent, height=480)
        scroll.pack(fill="both", expand=True, pady=4)

        def row(lbl, default=""):
            f = ctk.CTkFrame(scroll, fg_color="transparent"); f.pack(fill="x", pady=3)
            ctk.CTkLabel(f, text=lbl, width=210, anchor="w").pack(side="left")
            e = ctk.CTkEntry(f, width=240)
            e.insert(0, str(default) if default is not None else "")
            e.pack(side="left", padx=6); return e

        self.edit_nama     = row(t("f_nama",     bhs), profil["nama"])
        self.edit_tgl      = row(t("f_tgl",      bhs), profil["tanggal_lahir"])
        self.edit_email    = row(t("f_email",    bhs), profil["email"])
        self.edit_jurusan  = row(t("f_jurusan",  bhs), profil["jurusan"])
        self.edit_kampus   = row(t("f_kampus",   bhs), profil["kampus"])

        fj = ctk.CTkFrame(scroll, fg_color="transparent"); fj.pack(fill="x", pady=3)
        ctk.CTkLabel(fj, text=t("f_jenjang", bhs), width=210, anchor="w").pack(side="left")
        self.dd_edit_jenjang = ctk.CTkComboBox(fj, values=["S1","S2","S3"], width=180)
        self.dd_edit_jenjang.set(profil["jenjang"]); self.dd_edit_jenjang.pack(side="left", padx=6)

        self.edit_semester = row(t("f_semester", bhs), profil["semester"])
        self.edit_ip       = row(t("f_ip",       bhs), profil["ip"])

        fjk = ctk.CTkFrame(scroll, fg_color="transparent"); fjk.pack(fill="x", pady=3)
        ctk.CTkLabel(fjk, text=t("f_jk", bhs), width=210, anchor="w").pack(side="left")
        self.dd_edit_jk = ctk.CTkComboBox(fjk, values=["Laki-laki","Perempuan"], width=180)
        self.dd_edit_jk.set(profil["jenis_kelamin"]); self.dd_edit_jk.pack(side="left", padx=6)

        ctk.CTkLabel(scroll, text=t("sek_spesifik", bhs),
                     font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(10,2))

        fkip = ctk.CTkFrame(scroll, fg_color="transparent"); fkip.pack(fill="x", pady=3)
        ctk.CTkLabel(fkip, text=t("f_kip", bhs), width=210, anchor="w").pack(side="left")
        self.edit_kip = ctk.BooleanVar(value=bool(profil.get("status_kip", 0)))
        ctk.CTkCheckBox(fkip, text=t("f_kip_ya", bhs), variable=self.edit_kip).pack(side="left", padx=6)

        def rowsp(lbl, key):
            f = ctk.CTkFrame(scroll, fg_color="transparent"); f.pack(fill="x", pady=3)
            ctk.CTkLabel(f, text=lbl, width=210, anchor="w").pack(side="left")
            e = ctk.CTkEntry(f, width=180)
            v = profil.get(key)
            e.insert(0, str(v) if v is not None else ""); e.pack(side="left", padx=6); return e

        self.edit_ielts    = rowsp(t("f_ielts",    bhs), "skor_ielts")
        self.edit_toefl    = rowsp(t("f_toefl",    bhs), "skor_toefl")
        self.edit_duolingo = rowsp(t("f_duolingo", bhs), "skor_duolingo")
        self.edit_sat      = rowsp(t("f_sat",      bhs), "skor_sat")
        self.edit_act      = rowsp(t("f_act",      bhs), "skor_act")
        self.edit_gre      = rowsp(t("f_gre",      bhs), "skor_gre")
        self.edit_gmat     = rowsp(t("f_gmat",     bhs), "skor_gmat")
        self.edit_hsk      = rowsp(t("f_hsk",      bhs), "skor_hsk")

        fjlpt = ctk.CTkFrame(scroll, fg_color="transparent"); fjlpt.pack(fill="x", pady=3)
        ctk.CTkLabel(fjlpt, text=t("f_jlpt", bhs), width=210, anchor="w").pack(side="left")
        self.dd_edit_jlpt = ctk.CTkComboBox(fjlpt, values=["","N1","N2","N3","N4","N5"], width=180)
        self.dd_edit_jlpt.set(profil.get("level_jlpt") or ""); self.dd_edit_jlpt.pack(side="left", padx=6)

        ctk.CTkButton(parent, text=t("btn_simpan_edit", bhs), height=40,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._simpan_edit).pack(fill="x", padx=8, pady=10)

    def _simpan_edit(self):
        g = lambda e: e.get().strip()
        bhs = self._bhs
        data = edit_profil(
            self.profil_id,
            g(self.edit_nama), g(self.edit_tgl), g(self.edit_email),
            g(self.edit_jurusan), g(self.edit_kampus),
            g(self.edit_semester), g(self.edit_ip),
            self.dd_edit_jenjang.get(), self.dd_edit_jk.get(),
            self.edit_kip.get(),
            g(self.edit_ielts), g(self.edit_toefl), g(self.edit_duolingo),
            g(self.edit_sat), g(self.edit_act), g(self.edit_gre),
            g(self.edit_gmat), g(self.edit_hsk), self.dd_edit_jlpt.get(),
        )
        ok, msg = simpan_edit_profil(data)
        if not ok:
            messagebox.showerror(t("gagal", bhs), msg, parent=self); return
        messagebox.showinfo(t("berhasil", bhs), t("ok_edit", bhs), parent=self)
        self.refresh()

    # ── Tab Preferensi ───────────────────────────────────
    def _tab_pref(self, parent):
        pref = ambil_preferensi(self.profil_id)
        bhs  = self._bhs

        ctk.CTkLabel(parent, text=t("lb_tema", bhs),
                     font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=16, pady=(16,4))
        self.var_tema = ctk.StringVar(value=pref.get("tema","light"))
        for val, key in [("light","opt_light"), ("dark","opt_dark")]:
            ctk.CTkRadioButton(parent, text=t(key, bhs),
                               variable=self.var_tema, value=val).pack(anchor="w", padx=32, pady=2)

        ctk.CTkLabel(parent, text=t("lb_ukuran", bhs),
                     font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=16, pady=(16,4))
        self.var_ukuran = ctk.StringVar(value=pref.get("ukuran_teks","medium"))
        for val, key in [("small","opt_small"), ("medium","opt_medium"), ("large","opt_large")]:
            ctk.CTkRadioButton(parent, text=t(key, bhs),
                               variable=self.var_ukuran, value=val).pack(anchor="w", padx=32, pady=2)

        ctk.CTkLabel(parent, text=t("lb_bahasa", bhs),
                     font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=16, pady=(16,4))
        self.var_bahasa = ctk.StringVar(value=pref.get("bahasa","id"))
        for val, key in [("id","opt_id"), ("en","opt_en")]:
            ctk.CTkRadioButton(parent, text=t(key, bhs),
                               variable=self.var_bahasa, value=val).pack(anchor="w", padx=32, pady=2)

        ctk.CTkButton(parent, text=t("btn_simpan_pref", bhs), height=40,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._simpan_pref).pack(fill="x", padx=16, pady=24)

    def _simpan_pref(self):
        bhs = self._bhs
        ok, msg = simpan_preferensi(
            self.profil_id,
            self.var_tema.get(), self.var_ukuran.get(), self.var_bahasa.get(),
        )
        if not ok:
            messagebox.showerror(t("gagal", bhs), msg, parent=self); return
        messagebox.showinfo(t("berhasil", bhs), t("ok_pref", bhs), parent=self)
        self.refresh()

    # ── Tab Hapus Akun ───────────────────────────────────
    def _tab_hapus(self, parent):
        bhs = self._bhs
        ctk.CTkFrame(parent, height=40, fg_color="transparent").pack()
        ctk.CTkLabel(parent, text=t("warn_hapus", bhs),
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color="red").pack(pady=8)
        ctk.CTkLabel(parent, text=t("teks_hapus", bhs),
                     font=ctk.CTkFont(size=12), justify="center").pack(pady=8)
        ctk.CTkButton(parent, text=t("btn_hapus", bhs),
                      fg_color="red", hover_color="#cc0000", height=40,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._hapus_akun).pack(padx=40, pady=20, fill="x")

    def _hapus_akun(self):
        bhs = self._bhs
        konfirmasi = messagebox.askyesno(
            t("konfirm_judul", bhs), t("konfirm_teks", bhs), parent=self,
        )
        ok, msg = hapus_akun(self.profil_id, konfirmasi)
        if not ok:
            messagebox.showinfo(t("dibatalkan", bhs), t("batal_hapus", bhs), parent=self); return
        messagebox.showinfo(t("akun_dihapus", bhs), t("ok_hapus", bhs), parent=self)
        self.destroy()
        self.master._go_logout()


# ════════════════════════════════════════════════════════════
# APP ROOT
# ════════════════════════════════════════════════════════════

class BeaplyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Beaply — Insight Beasiswa")
        self.geometry("860x640")
        self.minsize(760, 560)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self._go_home()

    def _clear(self):
        for w in self.winfo_children(): w.destroy()

    def _go_home(self):
        self._clear()
        HalamanHome(self,
                    buka_buat=self._go_buat_profil,
                    buka_dashboard=self._go_dashboard
                    ).pack(fill="both", expand=True)

    def _go_buat_profil(self):
        self._clear()
        HalamanBuatProfil(self,
                          selesai_callback=self._go_dashboard,
                          kembali_callback=self._go_home
                          ).pack(fill="both", expand=True)

    def _go_dashboard(self, profil_id=None):
        global PROFIL_AKTIF_ID
        if profil_id: PROFIL_AKTIF_ID = profil_id
        self._clear()
        pref = ambil_preferensi(PROFIL_AKTIF_ID)
        apply_pref(pref)
        HalamanDashboard(self, PROFIL_AKTIF_ID,
                         buka_settings=self._buka_settings,
                         logout_callback=self._go_logout
                         ).pack(fill="both", expand=True)

    def _buka_settings(self, profil_id, refresh_cb):
        win = SettingsWindow(self, profil_id, refresh_cb)
        win.grab_set()

    def _go_logout(self):
        global PROFIL_AKTIF_ID
        PROFIL_AKTIF_ID = None
        ctk.set_appearance_mode("light")
        self._go_home()


if __name__ == "__main__":
    app = BeaplyApp()
    app.mainloop()