"""
main.py
Beaply — Aplikasi Desktop Manajemen Profil & Beasiswa
GUI: CustomTkinter
Fitur: Autentikasi, Profil, Beasiswa, Settings,
       Tracker & Pengingat, Eksplorasi & Navigasi, Notifikasi Terpusat
"""

import customtkinter as ctk
from tkinter import messagebox
from database import init_db, ambil_semua_profil_db
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
init_auth()

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
        # ── Autentikasi ──
        "auth_judul":       "🎓 Beaply",
        "auth_tagline":     "Insight Beasiswa untuk Mahasiswa",
        "tab_login":        "Masuk",
        "tab_register":     "Daftar",
        "f_email_login":    "Email",
        "f_pass_login":     "Kata Sandi",
        "btn_login":        "Masuk",
        "btn_register":     "Daftar",
        "f_nama_reg":       "Nama Lengkap",
        "f_email_reg":      "Email",
        "f_pass_reg":       "Kata Sandi",
        "f_confirm_reg":    "Konfirmasi Kata Sandi",
        "link_lupa":        "Lupa Kata Sandi?",
        "sso_google":       "Masuk dengan Google",
        "sso_apple":        "Masuk dengan Apple",
        "sso_segera":       "Segera hadir!",
        "kekuatan_pwd":     "Kekuatan:",
        "lupa_judul":       "🔐 Lupa Kata Sandi",
        "lupa_desc":        "Masukkan email Anda untuk menerima kode OTP.",
        "btn_kirim_otp":    "Kirim Kode OTP",
        "otp_judul":        "Masukkan Kode OTP",
        "otp_desc":         "Kode 6 digit telah dikirim ke email Anda.",
        "btn_verif_otp":    "Verifikasi OTP",
        "btn_kirim_ulang":  "Kirim Ulang OTP",
        "reset_judul":      "🔑 Buat Kata Sandi Baru",
        "f_pwd_baru":       "Kata Sandi Baru",
        "f_pwd_konfirm":    "Konfirmasi Kata Sandi Baru",
        "btn_reset":        "Simpan Kata Sandi Baru",
        "reset_ok":         "Kata sandi berhasil diperbarui!\nSilakan login kembali.",
        "dev_otp_info":     "[DEV MODE] Kode OTP Anda:",
        # ── Sidebar ──
        "nav_dashboard":    "🏠 Dashboard",
        "nav_eksplorasi":   "🔍 Eksplorasi",
        "nav_tracker":      "📋 Tracker",
        "nav_kalender":     "📅 Kalender",
        "nav_notifikasi":   "🔔 Notifikasi",
        "nav_profil":       "👤 Profil",
        "nav_settings":     "⚙ Pengaturan",
        # ── Tracker ──
        "t_judul":          "📋 Tracker Pendaftaran",
        "t_tambah":         "+ Tambah Tracker",
        "t_nama":           "Nama Beasiswa *",
        "t_deadline":       "Deadline (YYYY-MM-DD)",
        "t_catatan":        "Catatan",
        "t_status":         "Status",
        "t_simpan":         "Simpan Tracker",
        "t_ok":             "Tracker berhasil ditambahkan!",
        "t_hapus":          "Hapus",
        "t_edit":           "Edit",
        "t_bookmark":       "⭐",
        "t_statistik":      "📊 Statistik",
        "t_aktif":          "Aktif",
        "t_proses":         "Proses",
        "t_terkirim":       "Terkirim",
        "t_diterima":       "Diterima",
        "t_ditolak":        "Ditolak",
        # ── Kalender ──
        "k_judul":          "📅 Kalender Deadline",
        "k_prev":           "◀",
        "k_next":           "▶",
        "k_detail":         "Detail Deadline",
        # ── Eksplorasi ──
        "e_judul":          "🔍 Eksplorasi Beasiswa",
        "e_cari":           "Cari beasiswa...",
        "e_filter":         "Filter",
        "e_sort":           "Urutkan",
        "e_kategori":       "Kategori",
        "e_jenjang":        "Jenjang",
        "e_ipk_min":        "IPK Min",
        "e_semua":          "Semua",
        "e_bookmark":       "⭐ Bookmark",
        "e_unbookmark":     "☆ Hapus Bookmark",
        "e_hasil":          "hasil ditemukan",
        "e_sort_nama":      "Nama A-Z",
        "e_sort_nama_d":    "Nama Z-A",
        "e_sort_dl":        "Deadline Terdekat",
        "e_sort_dl_d":      "Deadline Terjauh",
        "e_sort_ipk":       "IPK Terendah",
        "e_sort_ipk_d":     "IPK Tertinggi",
        # ── Notifikasi ──
        "n_judul":          "🔔 Notifikasi",
        "n_semua":          "Semua",
        "n_belum":          "Belum Dibaca",
        "n_sudah":          "Sudah Dibaca",
        "n_tandai_semua":   "✓ Tandai Semua Dibaca",
        "n_hapus_semua":    "🗑 Hapus Semua",
        "n_kosong":         "Tidak ada notifikasi.",
        "n_pengaturan":     "⚙ Pengaturan Notifikasi",
        "n_push":           "Push Notification",
        "n_email":          "Email Notification",
        "n_deadline":       "Notifikasi Deadline",
        "n_status":         "Notifikasi Status",
        "n_sistem":         "Notifikasi Sistem",
        "n_simpan":         "Simpan Pengaturan",
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
        # ── Authentication ──
        "auth_judul":       "🎓 Beaply",
        "auth_tagline":     "Scholarship Insight for Students",
        "tab_login":        "Login",
        "tab_register":     "Register",
        "f_email_login":    "Email",
        "f_pass_login":     "Password",
        "btn_login":        "Login",
        "btn_register":     "Register",
        "f_nama_reg":       "Full Name",
        "f_email_reg":      "Email",
        "f_pass_reg":       "Password",
        "f_confirm_reg":    "Confirm Password",
        "link_lupa":        "Forgot Password?",
        "sso_google":       "Sign in with Google",
        "sso_apple":        "Sign in with Apple",
        "sso_segera":       "Coming soon!",
        "kekuatan_pwd":     "Strength:",
        "lupa_judul":       "🔐 Forgot Password",
        "lupa_desc":        "Enter your email to receive an OTP code.",
        "btn_kirim_otp":    "Send OTP Code",
        "otp_judul":        "Enter OTP Code",
        "otp_desc":         "A 6-digit code has been sent to your email.",
        "btn_verif_otp":    "Verify OTP",
        "btn_kirim_ulang":  "Resend OTP",
        "reset_judul":      "🔑 Create New Password",
        "f_pwd_baru":       "New Password",
        "f_pwd_konfirm":    "Confirm New Password",
        "btn_reset":        "Save New Password",
        "reset_ok":         "Password updated successfully!\nPlease login again.",
        "dev_otp_info":     "[DEV MODE] Your OTP code:",
        # ── Sidebar ──
        "nav_dashboard":    "🏠 Dashboard",
        "nav_eksplorasi":   "🔍 Explore",
        "nav_tracker":      "📋 Tracker",
        "nav_kalender":     "📅 Calendar",
        "nav_notifikasi":   "🔔 Notifications",
        "nav_profil":       "👤 Profile",
        "nav_settings":     "⚙ Settings",
        # ── Tracker ──
        "t_judul":          "📋 Application Tracker",
        "t_tambah":         "+ Add Tracker",
        "t_nama":           "Scholarship Name *",
        "t_deadline":       "Deadline (YYYY-MM-DD)",
        "t_catatan":        "Notes",
        "t_status":         "Status",
        "t_simpan":         "Save Tracker",
        "t_ok":             "Tracker added successfully!",
        "t_hapus":          "Delete",
        "t_edit":           "Edit",
        "t_bookmark":       "⭐",
        "t_statistik":      "📊 Statistics",
        "t_aktif":          "Active",
        "t_proses":         "In Progress",
        "t_terkirim":       "Submitted",
        "t_diterima":       "Accepted",
        "t_ditolak":        "Rejected",
        # ── Calendar ──
        "k_judul":          "📅 Deadline Calendar",
        "k_prev":           "◀",
        "k_next":           "▶",
        "k_detail":         "Deadline Details",
        # ── Explore ──
        "e_judul":          "🔍 Explore Scholarships",
        "e_cari":           "Search scholarships...",
        "e_filter":         "Filter",
        "e_sort":           "Sort",
        "e_kategori":       "Category",
        "e_jenjang":        "Degree",
        "e_ipk_min":        "Min GPA",
        "e_semua":          "All",
        "e_bookmark":       "⭐ Bookmark",
        "e_unbookmark":     "☆ Remove",
        "e_hasil":          "results found",
        "e_sort_nama":      "Name A-Z",
        "e_sort_nama_d":    "Name Z-A",
        "e_sort_dl":        "Nearest Deadline",
        "e_sort_dl_d":      "Farthest Deadline",
        "e_sort_ipk":       "Lowest GPA",
        "e_sort_ipk_d":     "Highest GPA",
        # ── Notifications ──
        "n_judul":          "🔔 Notifications",
        "n_semua":          "All",
        "n_belum":          "Unread",
        "n_sudah":          "Read",
        "n_tandai_semua":   "✓ Mark All Read",
        "n_hapus_semua":    "🗑 Delete All",
        "n_kosong":         "No notifications.",
        "n_pengaturan":     "⚙ Notification Settings",
        "n_push":           "Push Notification",
        "n_email":          "Email Notification",
        "n_deadline":       "Deadline Notifications",
        "n_status":         "Status Notifications",
        "n_sistem":         "System Notifications",
        "n_simpan":         "Save Settings",
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
# HALAMAN: Autentikasi (Login / Register)
# ════════════════════════════════════════════════════════════

class HalamanAuth(ctk.CTkFrame):
    """
    Halaman utama autentikasi: Tab Login & Register.
    Sesuai modul: tampilan_auth, registrasi_pengguna, login_pengguna,
                  sso_google, sso_apple, lupa_sandi.
    """
    def __init__(self, master, login_callback, lupa_sandi_callback):
        super().__init__(master, fg_color="transparent")
        self.login_callback = login_callback
        self.lupa_sandi_cb  = lupa_sandi_callback
        self._bhs = "id"
        self._build()

    def _build(self):
        bhs = self._bhs

        # ── Header ──
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(pady=(30, 0))
        ctk.CTkLabel(hdr, text=t("auth_judul", bhs),
                     font=ctk.CTkFont(size=36, weight="bold")).pack()
        ctk.CTkLabel(hdr, text=t("auth_tagline", bhs),
                     font=ctk.CTkFont(size=14),
                     text_color="gray50").pack(pady=(2, 16))

        # ── Tabs Login / Register ──
        self.tabview = ctk.CTkTabview(self, width=420, height=480)
        self.tabview.pack(padx=40, pady=(0, 10))
        self.tabview.add(t("tab_login", bhs))
        self.tabview.add(t("tab_register", bhs))

        self._build_login(self.tabview.tab(t("tab_login", bhs)), bhs)
        self._build_register(self.tabview.tab(t("tab_register", bhs)), bhs)

        # ── SSO Buttons ──
        sso_frame = ctk.CTkFrame(self, fg_color="transparent")
        sso_frame.pack(pady=(0, 10))

        ctk.CTkLabel(sso_frame, text="─── atau ───",
                     text_color="gray50",
                     font=ctk.CTkFont(size=11)).pack(pady=(0, 8))

        btn_google = ctk.CTkButton(
            sso_frame, text=f"🔵  {t('sso_google', bhs)}", width=280, height=38,
            fg_color="#4285F4", hover_color="#3367D6",
            font=ctk.CTkFont(size=13),
            command=self._sso_google,
        )
        btn_google.pack(pady=3)

        btn_apple = ctk.CTkButton(
            sso_frame, text=f"🍎  {t('sso_apple', bhs)}", width=280, height=38,
            fg_color="#333333", hover_color="#1a1a1a",
            font=ctk.CTkFont(size=13),
            command=self._sso_apple,
        )
        btn_apple.pack(pady=3)

    # ── Tab Login ─────────────────────────────────────────────
    def _build_login(self, parent, bhs):
        ctk.CTkFrame(parent, height=10, fg_color="transparent").pack()

        self.login_email = ctk.CTkEntry(
            parent, placeholder_text=t("f_email_login", bhs),
            width=320, height=40)
        self.login_email.pack(pady=6)

        self.login_pass = ctk.CTkEntry(
            parent, placeholder_text=t("f_pass_login", bhs),
            width=320, height=40, show="●")
        self.login_pass.pack(pady=6)

        self.login_error = ctk.CTkLabel(
            parent, text="", text_color="#FF3B30",
            font=ctk.CTkFont(size=11), wraplength=300)
        self.login_error.pack(pady=(0, 4))

        ctk.CTkButton(
            parent, text=t("btn_login", bhs), width=320, height=44,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._do_login,
        ).pack(pady=6)

        lupa_btn = ctk.CTkButton(
            parent, text=t("link_lupa", bhs), width=200,
            fg_color="transparent", text_color=("gray40", "gray70"),
            hover_color=("gray90", "gray20"),
            font=ctk.CTkFont(size=12, underline=True),
            command=self._go_lupa_sandi,
        )
        lupa_btn.pack(pady=(4, 0))

    # ── Tab Register ──────────────────────────────────────────
    def _build_register(self, parent, bhs):
        ctk.CTkFrame(parent, height=6, fg_color="transparent").pack()

        self.reg_nama = ctk.CTkEntry(
            parent, placeholder_text=t("f_nama_reg", bhs),
            width=320, height=38)
        self.reg_nama.pack(pady=4)

        self.reg_email = ctk.CTkEntry(
            parent, placeholder_text=t("f_email_reg", bhs),
            width=320, height=38)
        self.reg_email.pack(pady=4)

        self.reg_pass = ctk.CTkEntry(
            parent, placeholder_text=t("f_pass_reg", bhs),
            width=320, height=38, show="●")
        self.reg_pass.pack(pady=4)
        self.reg_pass.bind("<KeyRelease>", self._update_strength)

        # Indikator kekuatan password
        self.strength_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.strength_frame.pack(fill="x", padx=40, pady=(0, 2))
        self.strength_label = ctk.CTkLabel(
            self.strength_frame, text="",
            font=ctk.CTkFont(size=10))
        self.strength_label.pack(side="left")
        self.strength_bar = ctk.CTkProgressBar(
            self.strength_frame, width=140, height=6)
        self.strength_bar.pack(side="right", padx=4)
        self.strength_bar.set(0)

        self.reg_confirm = ctk.CTkEntry(
            parent, placeholder_text=t("f_confirm_reg", bhs),
            width=320, height=38, show="●")
        self.reg_confirm.pack(pady=4)

        self.reg_error = ctk.CTkLabel(
            parent, text="", text_color="#FF3B30",
            font=ctk.CTkFont(size=11), wraplength=300)
        self.reg_error.pack(pady=(0, 2))

        ctk.CTkButton(
            parent, text=t("btn_register", bhs), width=320, height=44,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._do_register,
        ).pack(pady=6)

    def _update_strength(self, event=None):
        """Update indikator kekuatan password real-time."""
        pwd = self.reg_pass.get()
        level, label, color = get_password_strength_level(pwd)
        self.strength_label.configure(
            text=f"{t('kekuatan_pwd', self._bhs)} {label}",
            text_color=color)
        self.strength_bar.set(level / 4)
        try:
            self.strength_bar.configure(progress_color=color)
        except Exception:
            pass

    def _do_login(self):
        """Proses login pengguna."""
        email = self.login_email.get().strip()
        pwd = self.login_pass.get()

        if not email or not pwd:
            self.login_error.configure(text="Email dan kata sandi harus diisi.")
            return

        result = login_pengguna(email, pwd)
        if result["success"]:
            self.login_callback(result["user_profile"])
        else:
            self.login_error.configure(text=result["message"])

    def _do_register(self):
        """Proses registrasi pengguna."""
        nama = self.reg_nama.get().strip()
        email = self.reg_email.get().strip()
        pwd = self.reg_pass.get()
        confirm = self.reg_confirm.get()

        result = registrasi_pengguna(email, pwd, confirm, nama)
        if result["success"]:
            messagebox.showinfo(t("berhasil", self._bhs), result["message"])
            self.tabview.set(t("tab_login", self._bhs))
            self.login_email.delete(0, "end")
            self.login_email.insert(0, email)
            self.login_pass.focus()
            self.reg_error.configure(text="")
        else:
            self.reg_error.configure(text=result["message"])

    def _sso_google(self):
        result = sso_google()
        messagebox.showinfo("Google SSO", result["message"])

    def _sso_apple(self):
        result = sso_apple()
        messagebox.showinfo("Apple SSO", result["message"])

    def _go_lupa_sandi(self):
        self.lupa_sandi_cb()


# ════════════════════════════════════════════════════════════
# HALAMAN: Lupa Kata Sandi
# ════════════════════════════════════════════════════════════

class HalamanLupaSandi(ctk.CTkFrame):
    """Alur pemulihan kata sandi: Email → OTP → Reset."""
    def __init__(self, master, kembali_callback, reset_selesai_callback):
        super().__init__(master, fg_color="transparent")
        self.kembali_cb = kembali_callback
        self.reset_cb   = reset_selesai_callback
        self._bhs = "id"
        self._email = ""
        self._otp_dev = ""
        self._reset_token = ""
        self._step = 1
        self._resend_job = None
        self._resend_countdown = 0
        self._build_step1()

    def _clear(self):
        for w in self.winfo_children():
            w.destroy()
        if self._resend_job:
            try:
                self.after_cancel(self._resend_job)
            except Exception:
                pass

    def _build_step1(self):
        self._clear()
        self._step = 1
        bhs = self._bhs

        ctk.CTkButton(self, text=t("btn_kembali", bhs), width=100,
                      fg_color="transparent", border_width=1,
                      command=self.kembali_cb).pack(anchor="w", padx=30, pady=(20, 0))

        ctk.CTkFrame(self, height=30, fg_color="transparent").pack()
        ctk.CTkLabel(self, text=t("lupa_judul", bhs),
                     font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(0, 4))
        ctk.CTkLabel(self, text=t("lupa_desc", bhs),
                     font=ctk.CTkFont(size=13),
                     text_color="gray50").pack(pady=(0, 20))

        self.lupa_email = ctk.CTkEntry(
            self, placeholder_text="Email", width=320, height=40)
        self.lupa_email.pack(pady=6)

        self.lupa_error = ctk.CTkLabel(
            self, text="", text_color="#FF3B30",
            font=ctk.CTkFont(size=11), wraplength=300)
        self.lupa_error.pack(pady=(0, 4))

        ctk.CTkButton(
            self, text=t("btn_kirim_otp", bhs), width=320, height=44,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._kirim_otp,
        ).pack(pady=8)

    def _kirim_otp(self):
        email = self.lupa_email.get().strip()
        if not email or not validate_email_format(email):
            self.lupa_error.configure(text="Masukkan email yang valid.")
            return
        self._email = email
        result = lupa_sandi(email)
        if not result["success"]:
            self.lupa_error.configure(text=result["message"])
            return
        self._otp_dev = result.get("otp_dev", "")
        self._build_step2()

    def _build_step2(self):
        self._clear()
        self._step = 2
        bhs = self._bhs

        ctk.CTkButton(self, text=t("btn_kembali", bhs), width=100,
                      fg_color="transparent", border_width=1,
                      command=self._build_step1).pack(anchor="w", padx=30, pady=(20, 0))

        ctk.CTkFrame(self, height=30, fg_color="transparent").pack()
        ctk.CTkLabel(self, text=t("otp_judul", bhs),
                     font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(0, 4))
        ctk.CTkLabel(self, text=f"{t('otp_desc', bhs)}\n({self._email})",
                     font=ctk.CTkFont(size=13),
                     text_color="gray50", justify="center").pack(pady=(0, 10))

        if self._otp_dev:
            dev_frame = ctk.CTkFrame(self, fg_color=("#FFF3CD", "#665200"),
                                     corner_radius=8)
            dev_frame.pack(padx=40, pady=(0, 10), fill="x")
            ctk.CTkLabel(dev_frame,
                         text=f"{t('dev_otp_info', bhs)} {self._otp_dev}",
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=("#856404", "#FFD700")).pack(padx=12, pady=8)

        self.otp_entry = ctk.CTkEntry(
            self, placeholder_text="000000", width=200, height=50,
            font=ctk.CTkFont(size=24, weight="bold"),
            justify="center")
        self.otp_entry.pack(pady=8)

        self.otp_error = ctk.CTkLabel(
            self, text="", text_color="#FF3B30",
            font=ctk.CTkFont(size=11), wraplength=300)
        self.otp_error.pack(pady=(0, 4))

        ctk.CTkButton(
            self, text=t("btn_verif_otp", bhs), width=280, height=44,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._verif_otp,
        ).pack(pady=6)

        self.resend_btn = ctk.CTkButton(
            self, text=t("btn_kirim_ulang", bhs), width=200,
            fg_color="transparent", text_color=("gray40", "gray70"),
            hover_color=("gray90", "gray20"),
            font=ctk.CTkFont(size=12),
            command=self._resend_otp, state="disabled")
        self.resend_btn.pack(pady=4)
        self._resend_countdown = 60
        self._tick_countdown()

    def _tick_countdown(self):
        if self._resend_countdown > 0:
            self.resend_btn.configure(
                text=f"{t('btn_kirim_ulang', self._bhs)} ({self._resend_countdown}s)",
                state="disabled")
            self._resend_countdown -= 1
            self._resend_job = self.after(1000, self._tick_countdown)
        else:
            self.resend_btn.configure(
                text=t("btn_kirim_ulang", self._bhs),
                state="normal")

    def _resend_otp(self):
        result = lupa_sandi(self._email)
        if result["success"]:
            self._otp_dev = result.get("otp_dev", "")
            self._build_step2()
        else:
            self.otp_error.configure(text=result["message"])

    def _verif_otp(self):
        otp = self.otp_entry.get().strip()
        if not otp or len(otp) != 6 or not otp.isdigit():
            self.otp_error.configure(text="Masukkan 6 digit kode OTP.")
            return
        result = verifikasi_otp(self._email, otp)
        if result["valid"]:
            self._reset_token = result["reset_token"]
            self._build_step3()
        else:
            self.otp_error.configure(text=result["message"])

    def _build_step3(self):
        self._clear()
        self._step = 3
        bhs = self._bhs

        ctk.CTkFrame(self, height=40, fg_color="transparent").pack()
        ctk.CTkLabel(self, text=t("reset_judul", bhs),
                     font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(0, 4))
        ctk.CTkFrame(self, height=10, fg_color="transparent").pack()

        self.reset_pwd = ctk.CTkEntry(
            self, placeholder_text=t("f_pwd_baru", bhs),
            width=320, height=40, show="●")
        self.reset_pwd.pack(pady=6)
        self.reset_pwd.bind("<KeyRelease>", self._update_reset_strength)

        self.reset_strength_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.reset_strength_frame.pack(fill="x", padx=50, pady=(0, 2))
        self.reset_strength_label = ctk.CTkLabel(
            self.reset_strength_frame, text="",
            font=ctk.CTkFont(size=10))
        self.reset_strength_label.pack(side="left")
        self.reset_strength_bar = ctk.CTkProgressBar(
            self.reset_strength_frame, width=120, height=6)
        self.reset_strength_bar.pack(side="right", padx=4)
        self.reset_strength_bar.set(0)

        self.reset_confirm = ctk.CTkEntry(
            self, placeholder_text=t("f_pwd_konfirm", bhs),
            width=320, height=40, show="●")
        self.reset_confirm.pack(pady=6)

        self.reset_error = ctk.CTkLabel(
            self, text="", text_color="#FF3B30",
            font=ctk.CTkFont(size=11), wraplength=300)
        self.reset_error.pack(pady=(0, 4))

        ctk.CTkButton(
            self, text=t("btn_reset", bhs), width=320, height=44,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._do_reset,
        ).pack(pady=8)

    def _update_reset_strength(self, event=None):
        pwd = self.reset_pwd.get()
        level, label, color = get_password_strength_level(pwd)
        self.reset_strength_label.configure(
            text=f"{t('kekuatan_pwd', self._bhs)} {label}",
            text_color=color)
        self.reset_strength_bar.set(level / 4)
        try:
            self.reset_strength_bar.configure(progress_color=color)
        except Exception:
            pass

    def _do_reset(self):
        pwd = self.reset_pwd.get()
        confirm = self.reset_confirm.get()
        result = reset_password(self._email, pwd, confirm)
        if result["success"]:
            messagebox.showinfo(t("berhasil", self._bhs), result["message"])
            self.reset_cb()
        else:
            self.reset_error.configure(text=result["message"])


# ════════════════════════════════════════════════════════════
# HALAMAN: Home (setelah login, pilih/buat profil)
# ════════════════════════════════════════════════════════════

class HalamanHome(ctk.CTkFrame):
    def __init__(self, master, buka_buat, buka_dashboard, user_id=None):
        super().__init__(master, fg_color="transparent")
        self.buka_buat      = buka_buat
        self.buka_dashboard = buka_dashboard
        self.user_id        = user_id
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
        profils = ambil_semua_profil_db(self.user_id)
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
        ok, msg, pid = simpan_profil(dw, ds, user_id=self.user_id)
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

    # ── Navigasi: Autentikasi ─────────────────────────────
    def _go_auth(self):
        self._clear()
        self._current_user = None
        HalamanAuth(self,
                    login_callback=self._on_login_success,
                    lupa_sandi_callback=self._go_lupa_sandi
                    ).pack(fill="both", expand=True)

    def _on_login_success(self, user_profile: dict):
        self._current_user = user_profile
        self._go_home_after_login()

    def _go_lupa_sandi(self):
        self._clear()
        HalamanLupaSandi(self,
                         kembali_callback=self._go_auth,
                         reset_selesai_callback=self._go_auth,
                         ).pack(fill="both", expand=True)

    # ── Navigasi: Utama (setelah auth) ────────────────────
    def _go_home_after_login(self):
        self._clear()
        user_id = self._current_user["id"] if self._current_user else None
        HalamanHome(self,
                    buka_buat=self._go_buat_profil,
                    buka_dashboard=self._go_dashboard,
                    user_id=user_id,
                    ).pack(fill="both", expand=True)

    def _go_buat_profil(self):
        self._clear()
        user_id = self._current_user["id"] if self._current_user else None
        HalamanBuatProfil(self,
                          selesai_callback=self._go_dashboard,
                          kembali_callback=self._go_home_after_login,
                          user_id=user_id,
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
        logout_pengguna()
        self._current_user = None
        ctk.set_appearance_mode("light")
        self._go_auth()


if __name__ == "__main__":
    app = BeaplyApp()
    app.mainloop()