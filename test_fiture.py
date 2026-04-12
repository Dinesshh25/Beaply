"""
main.py
Beaply — Aplikasi Desktop Manajemen Profil & Beasiswa
GUI: CustomTkinter
"""

import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
from tkcalendar import DateEntry
from PIL import Image
import os

from database import init_db, ambil_semua_profil_db, ambil_profil_db
from profile import (
    input_data_wajib, input_data_spesifik,
    simpan_profil, tampil_profil,
)
from settings import (
    edit_profil, simpan_edit_profil,
    hapus_akun, simpan_preferensi, ambil_preferensi, ganti_password
)
from utils import format_tanggal

init_db()

PROFIL_AKTIF_ID = None

# Colors
BG_COLOR = "#FDF6F0"
CARD_COLOR = "#FFFFFF"
SIDEBAR_COLOR = "#FDF6F0"
BTN_GREEN = "#B3D4BB"
BTN_PALE = "#E2EBE5"
TEXT_DARK = "#202020"
TEXT_LIGHT = "#FFFFFF"

# ════════════════════════════════════════════════════════════
# TERJEMAHAN (i18n)
# ════════════════════════════════════════════════════════════

TEKS = {
    "id": {
        "tagline":          "Insight Beasiswa untuk Mahasiswa",
        "btn_buat":         "Buat Akun Baru",
        "btn_pilih":        "Log in",
        "btn_guest":        "Log in as Guest",
        "info_kosong":      "Belum ada profil. Buat profil dulu ya!",
        "judul_pilih":      "Login ke Profil",
        "judul_buat":       "Buat Profil Baru",
        "btn_kembali":      "← Kembali",
        "btn_simpan":       "Simpan Profil",
        "sek_wajib":        "Data Wajib",
        "sek_spesifik":     "Data Spesifik (Opsional)",
        "f_nama":           "Nama Lengkap *",
        "f_tgl":            "Tanggal Lahir *",
        "f_email":          "Email *",
        "f_password":       "Password *",
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
        "btn_settings":     "⚙ Settings",
        "btn_logout":       "Logout",
        "judul_profil":     "Profil Lengkap",
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
        "judul_settings":   "Settings",
        "tab_edit":         "Edit Profil",
        "tab_pref":         "Preferensi",
        "tab_hapus":        "Hapus Akun",
        "btn_simpan_edit":  "Simpan Perubahan",
        "ok_edit":          "Profil berhasil diperbarui.",
        "lb_tema":          "Theme",
        "lb_ukuran":        "Text Size",
        "lb_bahasa":        "Language",
        "opt_light":        "Light",
        "opt_dark":         "Dark",
        "opt_system":       "System",
        "opt_small":        "Small",
        "opt_medium":       "Medium",
        "opt_large":        "Large",
        "opt_id":           "Bahasa Indonesia",
        "opt_en":           "English",
        "btn_simpan_pref":  "Simpan Preferensi",
        "ok_pref":          "Preferensi tersimpan!",
        "warn_hapus":       "Delete Account",
        "teks_hapus":       "Aksi ini tidak bisa dibatalkan.\nSeluruh data profilmu akan dihapus permanen.",
        "btn_hapus":        "Delete Account",
        "konfirm_judul":    "Konfirmasi Hapus",
        "konfirm_teks":     "Kamu yakin ingin menghapus akun ini?\nData tidak bisa dipulihkan!",
        "ok_hapus":         "Akun berhasil dihapus.",
        "batal_hapus":      "Penghapusan dibatalkan.",
        "gagal":            "Error",
        "berhasil":         "Berhasil",
        "akun_dihapus":     "Akun Dihapus",
        "dibatalkan":       "Dibatalkan",
        "menu_dashboard":    "Dashboard",
        "menu_scholarships":"Scholarships",
        "menu_recom":       "Recommendations",
        "menu_bookmarks":   "Bookmarks",
        "menu_calendar":    "Calendar",
        "menu_notif":       "Notifications",
        "menu_profile":     "Profile",
        "guest_name":       "Guest User",
        "guest_email":      "guest@beaply.com",
        "lbl_acc_sec":      "Account & Security",
        "lbl_change_pw":    "Change Password",
        "lbl_desc_pw":      "Change password to keep account secure",
        "btn_change_pw":    "Ubah Password",
        "lbl_display":      "Display",
        "btn_edit_profile": "Edit Profile",
        "desc_theme":       "Select application theme",
        "desc_lang":        "Select interface language",
        "desc_size":        "Select text size",
        "lbl_old_pw":       "Password Lama",
        "lbl_new_pw":       "Password Baru",
        "lbl_conf_pw":      "Konfirmasi Password",
        "lbl_password":     "Password",
        "btn_login":        "Login",
        "err_wrong_pw":     "Password salah!",
    },
    "en": {
        "tagline":          "Scholarship Insight for Students",
        "btn_buat":         "Create New Account",
        "btn_pilih":        "Log in",
        "btn_guest":        "Log in as Guest",
        "info_kosong":      "No profiles yet. Create one first!",
        "judul_pilih":      "Login to Profile",
        "judul_buat":       "Create New Profile",
        "btn_kembali":      "← Back",
        "btn_simpan":       "Save Profile",
        "sek_wajib":        "Required Data",
        "sek_spesifik":     "Specific Data (Optional)",
        "f_nama":           "Full Name *",
        "f_tgl":            "Date of Birth *",
        "f_email":          "Email *",
        "f_password":       "Password *",
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
        "judul_profil":     "Profile Details",
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
        "judul_settings":   "Settings",
        "tab_edit":         "Edit Profile",
        "tab_pref":         "Preferences",
        "tab_hapus":        "Delete Account",
        "btn_simpan_edit":  "Save Changes",
        "ok_edit":          "Profile updated successfully.",
        "lb_tema":          "Theme",
        "lb_ukuran":        "Text Size",
        "lb_bahasa":        "Language",
        "opt_light":        "Light",
        "opt_dark":         "Dark",
        "opt_system":       "System",
        "opt_small":        "Small",
        "opt_medium":       "Medium",
        "opt_large":        "Large",
        "opt_id":           "Bahasa Indonesia",
        "opt_en":           "English",
        "btn_simpan_pref":  "Save Preferences",
        "ok_pref":          "Preferences saved!",
        "warn_hapus":       "Delete Account",
        "teks_hapus":       "This action cannot be undone.\nAll your profile data will be permanently deleted.",
        "btn_hapus":        "Delete Account",
        "konfirm_judul":    "Confirm Deletion",
        "konfirm_teks":     "Are you sure you want to delete this account?\nThis cannot be undone!",
        "ok_hapus":         "Account successfully deleted.",
        "batal_hapus":      "Deletion cancelled.",
        "gagal":            "Error",
        "berhasil":         "Success",
        "akun_dihapus":     "Account Deleted",
        "dibatalkan":       "Cancelled",
        "menu_dashboard":    "Dashboard",
        "menu_scholarships":"Scholarships",
        "menu_recom":       "Recommendations",
        "menu_bookmarks":   "Bookmarks",
        "menu_calendar":    "Calendar",
        "menu_notif":       "Notifications",
        "menu_profile":     "Profile",
        "guest_name":       "Guest User",
        "guest_email":      "guest@beaply.com",
        "lbl_acc_sec":      "Account & Security",
        "lbl_change_pw":    "Change Password",
        "lbl_desc_pw":      "Change password to keep account secure",
        "btn_change_pw":    "Change Password",
        "lbl_display":      "Display",
        "btn_edit_profile": "Edit Profile",
        "desc_theme":       "Select application theme",
        "desc_lang":        "Select interface language",
        "desc_size":        "Select text size",
        "lbl_old_pw":       "Old Password",
        "lbl_new_pw":       "New Password",
        "lbl_conf_pw":      "Confirm Password",
        "lbl_password":     "Password",
        "btn_login":        "Login",
        "err_wrong_pw":     "Wrong password!",
    },
}

def t(key: str, bhs: str = "id") -> str:
    return TEKS.get(bhs, TEKS["id"]).get(key, key)

# ════════════════════════════════════════════════════════════
# HELPER
# ════════════════════════════════════════════════════════════

def show_error(master, title, msg):
    """Custom error popup with red text"""
    top = ctk.CTkToplevel(master)
    top.title(title)
    top.geometry("300x150")
    top.resizable(False, False)
    top.transient(master)
    top.grab_set()
    ctk.CTkLabel(top, text=msg, text_color="red", wraplength=260, 
                 font=ctk.CTkFont(weight="bold")).pack(expand=True, pady=10)
    ctk.CTkButton(top, text="OK", command=top.destroy, width=80, 
                  fg_color=BTN_GREEN, text_color=TEXT_DARK).pack(pady=10)

def show_info(master, title, msg):
    """Custom info popup"""
    top = ctk.CTkToplevel(master)
    top.title(title)
    top.geometry("300x150")
    top.resizable(False, False)
    top.transient(master)
    top.grab_set()
    ctk.CTkLabel(top, text=msg, wraplength=260, text_color=TEXT_DARK).pack(expand=True, pady=10)
    ctk.CTkButton(top, text="OK", command=top.destroy, width=80, 
                  fg_color=BTN_GREEN, text_color=TEXT_DARK).pack(pady=10)

def konfirm_yesno(master, title, msg) -> bool:
    res = messagebox.askyesno(title, msg, parent=master)
    return res

def ukuran_font(pref: dict) -> tuple:
    tbl = {"small": (14, 11, 9), "medium": (18, 13, 11), "large": (22, 16, 13)}
    return tbl.get(pref.get("ukuran_teks", "medium"), tbl["medium"])

def apply_pref(pref: dict):
    t = pref.get("tema", "light")
    if t == "light" or t == "dark" or t == "system":
        ctk.set_appearance_mode(t)

def get_bahasa(profil_id) -> str:
    if profil_id == "guest" or not profil_id: return "en"
    pref = ambil_preferensi(profil_id)
    return pref.get("bahasa", "en")


# ════════════════════════════════════════════════════════════
# HALAMAN: Home
# ════════════════════════════════════════════════════════════

class HalamanHome(ctk.CTkFrame):
    def __init__(self, master, buka_buat, buka_dashboard):
        super().__init__(master, fg_color=BG_COLOR)
        self.buka_buat      = buka_buat
        self.buka_dashboard = buka_dashboard
        self._build()

    def _build(self):
        # Center container
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")

        logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
        if os.path.exists(logo_path):
            img = ctk.CTkImage(light_image=Image.open(logo_path), size=(200, 80))
            ctk.CTkLabel(container, image=img, text="").pack(pady=(0, 30))
        else:
            ctk.CTkLabel(container, text="beaply",
                         font=ctk.CTkFont(size=48, weight="bold"), text_color=TEXT_DARK).pack(pady=(0, 4))
            ctk.CTkLabel(container, text="beaply",
                         font=ctk.CTkFont(size=48, weight="bold"), text_color=TEXT_DARK).pack(pady=(0, 30))
        
        ctk.CTkButton(container, text=t("btn_pilih", "en"),
                      command=self._pilih_profil, width=220, height=44,
                      fg_color=TEXT_DARK, text_color=TEXT_LIGHT,
                      font=ctk.CTkFont(size=14, weight="bold")).pack(pady=8)
                      
        ctk.CTkButton(container, text=t("btn_buat", "en"),
                      command=self.buka_buat, width=220, height=44,
                      fg_color=BTN_GREEN, text_color=TEXT_DARK,
                      font=ctk.CTkFont(size=14, weight="bold")).pack(pady=8)

    def _pilih_profil(self):
        profils = ambil_semua_profil_db()
        if not profils:
            show_error(self, "Info", t("info_kosong", "en"))
            return
        win = LoginWindow(self, profils, self.buka_dashboard)
        win.grab_set()

# ════════════════════════════════════════════════════════════
# POPUP: Login
# ════════════════════════════════════════════════════════════

class LoginWindow(ctk.CTkToplevel):
    def __init__(self, master, profils, callback):
        super().__init__(master)
        self.title("Login")
        self.geometry("400x420")
        self.resizable(False, False)
        self.profils  = profils
        self.callback = callback
        self.selected_profil = None
        self._build()

    def _build(self):
        ctk.CTkLabel(self, text=t("judul_pilih", "en"),
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=14)
                     
        frame = ctk.CTkScrollableFrame(self, height=150)
        frame.pack(fill="x", padx=20, pady=4)
        
        self.var_profil = ctk.IntVar(value=-1)
        for p in self.profils:
            teks = f"{p['nama']}  •  {p['email']}"
            r = ctk.CTkRadioButton(frame, text=teks, value=p["id"], variable=self.var_profil)
            r.pack(anchor="w", pady=5)
            
        self.entry_pw = ctk.CTkEntry(self, placeholder_text=t("f_password", "en"), show="*")
        self.entry_pw.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkButton(self, text=t("btn_login", "en"), fg_color=BTN_GREEN, text_color=TEXT_DARK,
                      command=self._do_login).pack(pady=10)

    def _do_login(self):
        pid = self.var_profil.get()
        if pid == -1:
            show_error(self, "Error", "Milih profil dulu!")
            return
        pw = self.entry_pw.get().strip()
        p = ambil_profil_db(pid)
        if p["password"] != pw:
            show_error(self, "Error", t("err_wrong_pw", "en"))
            return
        global PROFIL_AKTIF_ID
        PROFIL_AKTIF_ID = pid
        self.destroy()
        self.callback(pid)

# ════════════════════════════════════════════════════════════
# HALAMAN: Buat Profil Baru
# ════════════════════════════════════════════════════════════

class HalamanBuatProfil(ctk.CTkFrame):
    def __init__(self, master, selesai_callback, kembali_callback):
        super().__init__(master, fg_color=BG_COLOR)
        self.selesai = selesai_callback
        self.kembali = kembali_callback
        self._bhs    = "en"
        self._build()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=24, pady=(20, 4))
        ctk.CTkButton(hdr, text=t("btn_kembali", self._bhs), width=90,
                      fg_color="transparent", border_width=1, text_color=TEXT_DARK, border_color=TEXT_DARK,
                      command=self.kembali).pack(side="left")
        ctk.CTkLabel(hdr, text=t("judul_buat", self._bhs), text_color=TEXT_DARK,
                     font=ctk.CTkFont(size=20, weight="bold")).pack(side="left", padx=16)

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=24, pady=8)
        self._form_wajib(scroll)
        self._form_spesifik(scroll)

        ctk.CTkButton(self, text=t("btn_simpan", self._bhs), height=44,
                      font=ctk.CTkFont(size=14, weight="bold"), fg_color=BTN_GREEN, text_color=TEXT_DARK,
                      command=self._simpan).pack(padx=24, pady=16, fill="x")

    def _form_wajib(self, parent):
        self._sek(parent, t("sek_wajib", self._bhs))
        self.e_nama    = self._row(parent, t("f_nama", self._bhs))
        self.e_email   = self._row(parent, t("f_email", self._bhs))
        self.e_password= self._row(parent, t("f_password", self._bhs), show="*")
        
        # Calendar using tkcalendar
        rc = ctk.CTkFrame(parent, fg_color="transparent"); rc.pack(fill="x", pady=4)
        ctk.CTkLabel(rc, text=t("f_tgl", self._bhs), width=220, anchor="w", text_color=TEXT_DARK).pack(side="left")
        
        cal_frame = ctk.CTkFrame(rc, fg_color="white", width=260, height=28)
        cal_frame.pack_propagate(False)
        cal_frame.pack(side="left", padx=8)
        self.e_tgl = DateEntry(cal_frame, date_pattern='yyyy-mm-dd', background='darkblue',
                               foreground='white', borderwidth=0)
        self.e_tgl.pack(fill="both", expand=True)

        self.e_jurusan = self._row(parent, t("f_jurusan", self._bhs))
        self.e_kampus  = self._row(parent, t("f_kampus", self._bhs))

        r = ctk.CTkFrame(parent, fg_color="transparent"); r.pack(fill="x", pady=4)
        ctk.CTkLabel(r, text=t("f_jenjang", self._bhs), width=220, anchor="w", text_color=TEXT_DARK).pack(side="left")
        self.dd_jenjang = ctk.CTkComboBox(r, values=["S1","S2","S3"], width=180)
        self.dd_jenjang.set("S1"); self.dd_jenjang.pack(side="left", padx=8)

        self.e_semester = self._row(parent, t("f_semester", self._bhs))
        self.e_ip       = self._row(parent, t("f_ip", self._bhs))

        r2 = ctk.CTkFrame(parent, fg_color="transparent"); r2.pack(fill="x", pady=4)
        ctk.CTkLabel(r2, text=t("f_jk", self._bhs), width=220, anchor="w", text_color=TEXT_DARK).pack(side="left")
        self.dd_jk = ctk.CTkComboBox(r2, values=["Laki-laki","Perempuan"], width=180)
        self.dd_jk.set("Laki-laki"); self.dd_jk.pack(side="left", padx=8)

    def _form_spesifik(self, parent):
        self._sek(parent, t("sek_spesifik", self._bhs))

        r = ctk.CTkFrame(parent, fg_color="transparent"); r.pack(fill="x", pady=4)
        ctk.CTkLabel(r, text=t("f_kip", self._bhs), width=220, anchor="w", text_color=TEXT_DARK).pack(side="left")
        self.var_kip = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(r, text=t("f_kip_ya", self._bhs), variable=self.var_kip, text_color=TEXT_DARK).pack(side="left", padx=8)

        self.e_ielts    = self._row(parent, t("f_ielts", self._bhs))
        self.e_toefl    = self._row(parent, t("f_toefl", self._bhs))
        self.e_duolingo = self._row(parent, t("f_duolingo", self._bhs))
        self.e_sat      = self._row(parent, t("f_sat", self._bhs))
        self.e_act      = self._row(parent, t("f_act", self._bhs))
        self.e_gre      = self._row(parent, t("f_gre", self._bhs))
        self.e_gmat     = self._row(parent, t("f_gmat", self._bhs))
        self.e_hsk      = self._row(parent, t("f_hsk", self._bhs))

        r3 = ctk.CTkFrame(parent, fg_color="transparent"); r3.pack(fill="x", pady=4)
        ctk.CTkLabel(r3, text=t("f_jlpt", self._bhs), width=220, anchor="w", text_color=TEXT_DARK).pack(side="left")
        self.dd_jlpt = ctk.CTkComboBox(r3, values=["","N1","N2","N3","N4","N5"], width=180)
        self.dd_jlpt.set(""); self.dd_jlpt.pack(side="left", padx=8)

    def _sek(self, parent, teks):
        ctk.CTkLabel(parent, text=teks, text_color=TEXT_DARK,
                     font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(14,2))
        ctk.CTkFrame(parent, height=1, fg_color="gray60").pack(fill="x", pady=(0,6))

    def _row(self, parent, label, show="") -> ctk.CTkEntry:
        r = ctk.CTkFrame(parent, fg_color="transparent"); r.pack(fill="x", pady=4)
        ctk.CTkLabel(r, text=label, width=220, anchor="w", wraplength=210, text_color=TEXT_DARK).pack(side="left")
        e = ctk.CTkEntry(r, width=260, show=show); e.pack(side="left", padx=8)
        return e

    def _simpan(self):
        dw = input_data_wajib(
            self.e_password.get().strip(),
            self.e_nama.get().strip(), self.e_tgl.get_date().strftime("%Y-%m-%d"), self.e_email.get().strip(),
            self.e_jurusan.get().strip(), self.e_kampus.get().strip(),
            self.e_semester.get().strip(), self.e_ip.get().strip(),
            self.dd_jenjang.get(), self.dd_jk.get(),
        )
        ds = input_data_spesifik(
            self.var_kip.get(),
            self.e_ielts.get().strip(), self.e_toefl.get().strip(), self.e_duolingo.get().strip(),
            self.e_sat.get().strip(), self.e_act.get().strip(), self.e_gre.get().strip(),
            self.e_gmat.get().strip(), self.e_hsk.get().strip(), self.dd_jlpt.get(),
        )
        ok, msg, pid = simpan_profil(dw, ds)
        if not ok:
            show_error(self, t("gagal", self._bhs), msg)
            return
        show_info(self, t("berhasil", self._bhs), t("ok_buat", self._bhs))
        self.selesai(pid)


# ════════════════════════════════════════════════════════════
# HALAMAN: Main Dashboard Layout (Sidebar + Content)
# ════════════════════════════════════════════════════════════

class HalamanDashboard(ctk.CTkFrame):
    def __init__(self, master, profil_id, logout_callback, active_tab="profile"):
        super().__init__(master, fg_color=BG_COLOR)
        self.profil_id = profil_id
        self.logout = logout_callback
        self.active_tab = active_tab
        
        pref = ambil_preferensi(self.profil_id)
        apply_pref(pref)
        
        self.bhs = get_bahasa(self.profil_id)
        
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=SIDEBAR_COLOR)
        self.sidebar_frame.pack(side="left", fill="y")
        
        self.content_frame = ctk.CTkFrame(self, corner_radius=15, fg_color=BG_COLOR)
        self.content_frame.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        
        self._build_sidebar()
        self._switch_tab(self.active_tab)

    def force_refresh_settings(self):
        # Callback triggered when language changes
        self.bhs = get_bahasa(self.profil_id)
        for w in self.sidebar_frame.winfo_children(): w.destroy()
        self._build_sidebar()
        self._switch_tab("settings")

    def _build_sidebar(self):
        bhs = self.bhs
        
        logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
        if os.path.exists(logo_path):
            img = ctk.CTkImage(light_image=Image.open(logo_path), size=(150, 60))
            ctk.CTkLabel(self.sidebar_frame, image=img, text="").pack(pady=(40, 30), padx=20, anchor="w")
        else:
            ctk.CTkLabel(self.sidebar_frame, text="beaply\nbeaply", font=ctk.CTkFont(size=24, weight="bold"),
                         text_color=TEXT_DARK, justify="left").pack(pady=(40, 30), padx=20, anchor="w")
                     
        menus = [
            ("menu_dashboard", "dashboard"),
            ("menu_scholarships", "scholarships"),
            ("menu_recom", "recom"),
            ("menu_bookmarks", "bookmarks"),
            ("menu_calendar", "calendar"),
            ("menu_notif", "notif"),
            ("menu_profile", "profile"),
        ]
        
        self.menu_btns = {}
        for text_key, tab_id in menus:
            btn = ctk.CTkButton(self.sidebar_frame, text=t(text_key, bhs), 
                                fg_color="transparent", text_color=TEXT_DARK, hover_color=BTN_PALE,
                                anchor="w", command=lambda t_id=tab_id: self._switch_tab(t_id))
            btn.pack(fill="x", padx=10, pady=2)
            self.menu_btns[tab_id] = btn

        # Spacer
        ctk.CTkFrame(self.sidebar_frame, fg_color="transparent").pack(expand=True)
        
        # Upgrade Card
        card = ctk.CTkFrame(self.sidebar_frame, fg_color=BTN_PALE, corner_radius=10)
        card.pack(padx=20, pady=20, fill="x")
        ctk.CTkLabel(card, text="Upgrade to\nBeaply Pro", font=ctk.CTkFont(weight="bold"), text_color=TEXT_DARK).pack(pady=(10,0))
        ctk.CTkLabel(card, text="Unlock premium features", font=ctk.CTkFont(size=10), text_color=TEXT_DARK).pack()
        ctk.CTkButton(card, text="Upgrade Now >", fg_color="#91AD99", text_color="white", height=28).pack(pady=10, padx=10)

        # Settings
        self.menu_btns["settings"] = ctk.CTkButton(self.sidebar_frame, text=t("judul_settings", bhs), 
                            fg_color="transparent", text_color=TEXT_DARK, hover_color=BTN_PALE,
                            anchor="w", command=lambda: self._switch_tab("settings"))
        self.menu_btns["settings"].pack(fill="x", padx=10, pady=(10, 20))
        
    def _switch_tab(self, tab_id):
        self.active_tab = tab_id
        for tid, btn in self.menu_btns.items():
            if tid == tab_id:
                btn.configure(fg_color=BTN_PALE)
            else:
                btn.configure(fg_color="transparent")
                
        for w in self.content_frame.winfo_children(): w.destroy()
        
        # Only implement Profile and Settings
        if tab_id == "profile":
            self._render_profile()
        elif tab_id == "settings":
            self._render_settings()
        else:
            ctk.CTkLabel(self.content_frame, text=f"Work in progress: {tab_id}", text_color=TEXT_DARK).pack(expand=True)

    def _top_bar(self, parent, title):
        bar = ctk.CTkFrame(parent, fg_color="transparent")
        bar.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(bar, text=title, font=ctk.CTkFont(size=24, weight="bold"), text_color=TEXT_DARK).pack(side="left")
        
        if self.profil_id:
            name = t("guest_name", self.bhs)
            email = t("guest_email", self.bhs)
        
        p = tampil_profil(self.profil_id)
        if p:
            name = p["nama"]
            email = "Student"
            
        user_info = ctk.CTkLabel(bar, text=f"{name}\n{email}", justify="left", text_color=TEXT_DARK, font=ctk.CTkFont(size=12))
        user_info.pack(side="right", padx=10)

    # === PROFILE VIEW ===
    def _render_profile(self):
        bhs = self.bhs
        self._top_bar(self.content_frame, t("menu_profile", bhs))
        
        profil = tampil_profil(self.profil_id)
        if not profil:
            return
            
        grid = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        grid.pack(fill="both", expand=True)
        
        # Left Panel (Completeness & Logout)
        left = ctk.CTkFrame(grid, fg_color="transparent", width=250)
        left.pack(side="left", fill="y", padx=(0, 10))
        left.pack_propagate(False)
        
        card1 = ctk.CTkFrame(left, fg_color=CARD_COLOR, corner_radius=15, border_width=1, border_color="#E0E0E0")
        card1.pack(fill="both", expand=True, pady=(0, 10))
        ctk.CTkLabel(card1, text="Profile\nCompleteness", font=ctk.CTkFont(size=18, weight="bold"), justify="left", text_color=TEXT_DARK).pack(pady=20, padx=20, anchor="w")
        
        # Mock Progress Circle
        circ = ctk.CTkFrame(card1, fg_color=BG_COLOR, width=120, height=120, corner_radius=60)
        circ.pack(pady=10)
        circ.pack_propagate(False)
        ctk.CTkLabel(circ, text="100%", font=ctk.CTkFont(size=24, weight="bold"), text_color=TEXT_DARK).place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkButton(left, text=t("btn_logout", bhs), fg_color="#F6C4BA", text_color=TEXT_DARK, hover_color="#eba99d",
                      command=self.logout).pack(fill="x", pady=(10,0))
                      
        # Right Panel (Personal Information)
        right = ctk.CTkFrame(grid, fg_color=CARD_COLOR, corner_radius=15, border_width=1, border_color="#E0E0E0")
        right.pack(side="left", fill="both", expand=True)
        
        header = ctk.CTkFrame(right, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(header, text="Personal Informations", font=ctk.CTkFont(size=18, weight="bold"), text_color=TEXT_DARK).pack(side="left")
        ctk.CTkButton(header, text=t("btn_edit_profile", bhs), fg_color=BTN_GREEN, text_color=TEXT_DARK).pack(side="right")
        
        scroll = ctk.CTkScrollableFrame(right, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        def baris(lbl, val):
            r = ctk.CTkFrame(scroll, fg_color="transparent"); r.pack(fill="x", pady=5)
            ctk.CTkLabel(r, text=f"{t(lbl, bhs)}:", width=150, anchor="w", font=ctk.CTkFont(weight="bold"), text_color=TEXT_DARK).pack(side="left")
            ctk.CTkLabel(r, text=str(val), anchor="w", text_color=TEXT_DARK).pack(side="left", padx=10)

        baris("lb_nama",     profil["nama"])
        baris("lb_tgl",      format_tanggal(profil["tanggal_lahir"]))
        baris("lb_email",    profil["email"])
        baris("lb_jurusan",  profil["jurusan"])
        baris("lb_kampus",   profil["kampus"])
        baris("lb_jenjang",  profil["jenjang"])
        baris("lb_semester", profil["semester"])
        baris("lb_ip",       f"{profil['ip']:.2f}")

    # === SETTINGS VIEW ===
    def _render_settings(self):
        bhs = self.bhs
        self._top_bar(self.content_frame, t("judul_settings", bhs))
        
        scroll = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        # --- Account & Security ---
        ctk.CTkLabel(scroll, text=t("lbl_acc_sec", bhs), font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_DARK).pack(anchor="w", pady=(10, 5))
        sec_card = ctk.CTkFrame(scroll, fg_color=CARD_COLOR, corner_radius=15, border_width=1, border_color="#E0E0E0")
        sec_card.pack(fill="x", pady=5)
        
        pw_r = ctk.CTkFrame(sec_card, fg_color="transparent")
        pw_r.pack(fill="x", padx=15, pady=15)
        
        txt_box = ctk.CTkFrame(pw_r, fg_color="transparent")
        txt_box.pack(side="left")
        ctk.CTkLabel(txt_box, text=t("lbl_change_pw", bhs), font=ctk.CTkFont(weight="bold"), text_color=TEXT_DARK, anchor="w").pack(fill="x")
        ctk.CTkLabel(txt_box, text=t("lbl_desc_pw", bhs), text_color="gray", anchor="w").pack(fill="x")
        
        ctk.CTkButton(pw_r, text=">", width=30, fg_color="transparent", text_color=TEXT_DARK, hover_color=BTN_PALE,
                      command=self._popup_change_pw).pack(side="right")
        
        # --- Display ---
        ctk.CTkLabel(scroll, text=t("lbl_display", bhs), font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_DARK).pack(anchor="w", pady=(20, 5))
        disp_card = ctk.CTkFrame(scroll, fg_color=CARD_COLOR, corner_radius=15, border_width=1, border_color="#E0E0E0")
        disp_card.pack(fill="x", pady=5)
        
        pref = ambil_preferensi(self.profil_id)
            
        def settings_row(parent, title, desc, widget):
            r = ctk.CTkFrame(parent, fg_color="transparent")
            r.pack(fill="x", padx=15, pady=15)
            txt_bx = ctk.CTkFrame(r, fg_color="transparent")
            txt_bx.pack(side="left")
            ctk.CTkLabel(txt_bx, text=title, font=ctk.CTkFont(weight="bold"), text_color=TEXT_DARK, anchor="w").pack(fill="x")
            ctk.CTkLabel(txt_bx, text=desc, text_color="gray", anchor="w").pack(fill="x")
            widget.pack(side="right", in_=r)
            
        # Theme
        t_frame = ctk.CTkSegmentedButton(disp_card, values=[t("opt_light", bhs), t("opt_dark", bhs), t("opt_system", bhs)],
                                         command=self._change_theme)
        val = t("opt_" + pref.get("tema", "system"), bhs)
        try: t_frame.set(val) 
        except: pass
        settings_row(disp_card, t("lb_tema", bhs), t("desc_theme", bhs), t_frame)
        
        # Language
        l_frame = ctk.CTkComboBox(disp_card, values=["Bahasa Indonesia", "English"], command=self._change_lang)
        l_frame.set("Bahasa Indonesia" if pref.get("bahasa") == "id" else "English")
        settings_row(disp_card, t("lb_bahasa", bhs), t("desc_lang", bhs), l_frame)
        
        # Text Size
        s_frame = ctk.CTkSegmentedButton(disp_card, values=[t("opt_small", bhs), t("opt_medium", bhs), t("opt_large", bhs)])
        val = t("opt_" + pref.get("ukuran_teks", "medium"), bhs)
        try: s_frame.set(val)
        except: pass
        settings_row(disp_card, t("lb_ukuran", bhs), t("desc_size", bhs), s_frame)
        
        # Delete Account
        del_card = ctk.CTkFrame(scroll, fg_color=CARD_COLOR, corner_radius=15, border_width=1, border_color="#E0E0E0")
        del_card.pack(fill="x", pady=20)
        ctk.CTkButton(del_card, text=t("btn_hapus", bhs), fg_color="transparent", text_color="red", hover_color="#fceae8",
                      command=self._do_hapus).pack(pady=15)

    def _save_pref_partial(self, key, value):
        pref = ambil_preferensi(self.profil_id)
        pref[key] = value
        simpan_preferensi(self.profil_id, pref["tema"], pref["ukuran_teks"], pref["bahasa"])

    def _change_theme(self, choice):
        bhs = self.bhs
        val_map = {t("opt_light", bhs): "light", t("opt_dark", bhs): "dark", t("opt_system", bhs): "system"}
        act = val_map.get(choice, "system")
        if act in ["light", "dark", "system"]:
            ctk.set_appearance_mode(act)
        self._save_pref_partial("tema", act)

    def _change_lang(self, choice):
        act = "id" if choice == "Bahasa Indonesia" else "en"
        self._save_pref_partial("bahasa", act)
        # Immediately re-render layout to switch translation
        self.force_refresh_settings()

    def _do_hapus(self):
        bhs = self.bhs
        if konfirm_yesno(self, t("konfirm_judul", bhs), t("konfirm_teks", bhs)):
            ok, msg = hapus_akun(self.profil_id, True)
            if ok:
                show_info(self, t("akun_dihapus", bhs), t("ok_hapus", bhs))
                self.logout()
            else:
                show_error(self, t("gagal", bhs), msg)

    def _popup_change_pw(self):
        bhs = self.bhs
        top = ctk.CTkToplevel(self)
        top.title(t("lbl_change_pw", bhs))
        top.geometry("350x300")
        top.transient(self)
        top.grab_set()
        
        ctk.CTkLabel(top, text=t("lbl_change_pw", bhs), font=ctk.CTkFont(weight="bold", size=16)).pack(pady=10)
        
        e1 = ctk.CTkEntry(top, placeholder_text=t("lbl_old_pw", bhs), show="*")
        e1.pack(pady=5, padx=20, fill="x")
        e2 = ctk.CTkEntry(top, placeholder_text=t("lbl_new_pw", bhs), show="*")
        e2.pack(pady=5, padx=20, fill="x")
        e3 = ctk.CTkEntry(top, placeholder_text=t("lbl_conf_pw", bhs), show="*")
        e3.pack(pady=5, padx=20, fill="x")
        
        def save_pw():
            ok, msg = ganti_password(self.profil_id, e1.get().strip(), e2.get().strip(), e3.get().strip())
            if ok:
                show_info(top, t("berhasil", bhs), msg)
                top.destroy()
            else:
                show_error(top, t("gagal", bhs), msg)
                
        ctk.CTkButton(top, text=t("btn_change_pw", bhs), fg_color=BTN_GREEN, text_color=TEXT_DARK, 
                      command=save_pw).pack(pady=20)


# ════════════════════════════════════════════════════════════
# APP ROOT
# ════════════════════════════════════════════════════════════

class BeaplyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Beaply — Insight Beasiswa")
        self.geometry("1100x680")
        self.minsize(800, 600)
        ctk.set_appearance_mode("light")
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
        
        HalamanDashboard(self, PROFIL_AKTIF_ID,
                         logout_callback=self._go_logout
                         ).pack(fill="both", expand=True)

    def _go_logout(self):
        global PROFIL_AKTIF_ID
        PROFIL_AKTIF_ID = None
        ctk.set_appearance_mode("light")
        self._go_home()


if __name__ == "__main__":
    app = BeaplyApp()
    app.mainloop()