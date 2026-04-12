"""
main.py
Beaply — Aplikasi Desktop Manajemen Profil & Beasiswa
GUI: CustomTkinter
Fitur: Autentikasi, Profil, Beasiswa, Settings,
       Tracker & Pengingat, Eksplorasi & Navigasi, Notifikasi Terpusat
"""

import sys, traceback, logging
logging.basicConfig(filename='error.log', level=logging.ERROR,
                    format='%(asctime)s %(message)s', filemode='w')

import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os

from database import init_db, ambil_semua_profil_db
from Profile_dan_Setting.profile import (
    input_data_wajib, input_data_spesifik,
    simpan_profil, tampil_profil,
)
from Profile_dan_Setting.settings import (
    edit_profil, simpan_edit_profil,
    hapus_akun, simpan_preferensi, ambil_preferensi, ganti_password
)
from utils import format_tanggal

# ── Modul autentikasi ──
from Autentikasi_dan_Keamanan import (
    init_auth,
    registrasi_pengguna,
    login_pengguna,
    sso_google,
    sso_apple,
    lupa_sandi,
    verifikasi_otp,
    reset_password,
    logout_pengguna,
    get_current_user,
    is_authenticated,
    get_password_strength_level,
    validate_email_format,
)

# ── Modul Tracker & Pengingat ──
from Tracker_dan_Pengingat import (
    tampilan_kalender,
    tambah_penanda_manual,
    ubah_status,
    ubah_tracker,
    toggle_bookmark,
    hitung_statistik,
    buat_pengingat_otomatis,
    cek_pengingat,
    ambil_semua_tracker,
    ambil_tracker_by_id,
    hapus_tracker,
    format_status,
    warna_status,
    format_deadline_display,
    hitung_selisih_hari,
    STATUS_LIST,
)

# ── Modul Eksplorasi & Navigasi ──
from Eksplorasi_dan_Navigasi import (
    tampilan_eksplorasi,
    auto_complete,
    proses_pencarian,
    terapkan_filter,
    urutkan_data,
    toggle_bookmark_beasiswa,
    ambil_bookmark_user,
    cek_bookmark,
    ambil_semua_beasiswa,
    format_kategori,
    warna_kategori,
    format_deadline_beasiswa,
    format_syarat_singkat,
)

# ── Modul Notifikasi Terpusat ──
from Notifikasi_Terpusat import (
    tampilan_laci_notif,
    ambil_riwayat,
    tandai_dibaca,
    tandai_semua_dibaca,
    tampilan_kontrol_notif,
    ubah_preferensi_notif,
    simpan_semua_preferensi,
    buat_notifikasi_deadline,
    buat_notifikasi_status,
    hitung_belum_dibaca,
    hapus_notifikasi,
    hapus_semua,
    format_waktu_relatif,
    ikon_tipe,
    warna_tipe,
)

# ── Modul Pusat Bantuan ──
from PusatBantuan.gui_help_center import HalamanHelpCenter

# ── Modul Rekomendasi ──
from Rekomendasi.gui_rekomendasi import HalamanRekomendasi


init_db()
init_auth()

PROFIL_AKTIF_ID = None

# ── Design System Colors ──
BG_COLOR          = "#FDF6F0"
CARD_COLOR        = "#FFFFFF"
SIDEBAR_BG        = "#FDF6F0"
SIDEBAR_ACTIVE_BG = "#D6EAD8"
SIDEBAR_ACTIVE_TX = "#2D6A4F"
BTN_PRIMARY       = "#A8C5B0"
BTN_PRIMARY_HOVER = "#8FB898"
BTN_PALE          = "#E2EBE5"
TEXT_DARK         = "#2D2D2D"
TEXT_MUTED        = "#888888"
TEXT_ACCENT       = "#D4917B"
BORDER_COLOR      = "#E8E0D8"
INPUT_BG          = "#F0ECE8"
PASTEL_COLORS     = ["#E8EBE4", "#F4EFE6", "#F6E6E4", "#E8EEE4", "#F0E8E4", "#E4EBE8"]
BTN_GREEN         = "#A8C5B0"
TEXT_LIGHT        = "#FFFFFF"


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
        "opt_system":       "🖥 Sistem",
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
        "nav_rekomendasi": "🎯 Rekomendasi",
        "nav_bantuan":     "❓ Pusat Bantuan",
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
        "opt_system":       "🖥 System",
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
        "nav_rekomendasi": "🎯 Recommendations",
        "nav_bantuan":     "❓ Help Center",
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

def ukuran_font(pref: dict) -> tuple:
    tbl = {"small": (14, 11, 9), "medium": (18, 13, 11), "large": (22, 16, 13)}
    return tbl.get(pref.get("ukuran_teks", "medium"), tbl["medium"])

def apply_pref(pref: dict):
    ctk.set_appearance_mode(pref.get("tema", "light"))
    ukuran = pref.get("ukuran_teks", "medium").lower()
    if ukuran == "small":
        ctk.set_widget_scaling(0.9)
    elif ukuran == "large":
        ctk.set_widget_scaling(1.1)
    else:
        ctk.set_widget_scaling(1.0)

def get_bahasa(profil_id) -> str:
    pref = ambil_preferensi(profil_id)
    return pref.get("bahasa", "id")


def konfirm_yesno(parent, judul, pesan):
    return messagebox.askyesno(judul, pesan, parent=parent)

def show_info(parent, judul, pesan):
    messagebox.showinfo(judul, pesan, parent=parent)

def show_error(parent, judul, pesan):
    messagebox.showerror(judul, pesan, parent=parent)


def hitung_completeness(profil):
    """Calculate profile completeness percentage."""
    if not profil:
        return 0
    _required = ["nama", "tanggal_lahir", "email", "jurusan",
                 "kampus", "semester", "ip", "jenjang", "jenis_kelamin"]
    _optional = ["skor_ielts", "skor_toefl", "skor_duolingo",
                 "skor_sat", "skor_act", "skor_gre", "skor_gmat",
                 "skor_hsk", "level_jlpt"]
    _all = _required + _optional
    filled = 0
    for fld in _all:
        val = profil.get(fld)
        if val is not None and str(val).strip() != "" and val != 0 and val != 0.0:
            filled += 1
    return int((filled / len(_all)) * 100)

# ════════════════════════════════════════════════════════════
# HALAMAN: Autentikasi (Login / Register)
# ════════════════════════════════════════════════════════════

class HalamanAuth(ctk.CTkFrame):
    """Login/Register — redesigned to match mockup."""
    def __init__(self, master, login_callback, lupa_sandi_callback):
        super().__init__(master, fg_color=BG_COLOR)
        self.login_callback = login_callback
        self.lupa_sandi_cb  = lupa_sandi_callback
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
            import os
            logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "assets", "logo_beaply.png"))
            img = ctk.CTkImage(light_image=Image.open(logo_path), size=(140, 65))
            ctk.CTkLabel(logo_frame, text="", image=img).pack()
        except Exception as e:
            print("Logo Error:", e)
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
        for w in self.form_container.winfo_children():
            w.destroy()
        if value == "Log in":
            self._build_login_form()
        else:
            self._build_register_form()

    def _build_login_form(self):
        p = self.form_container
        ctk.CTkLabel(p, text="Email", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_DARK, anchor="w").pack(fill="x", pady=(16, 4))
        self.login_email = ctk.CTkEntry(p, height=42, corner_radius=10,
            fg_color=INPUT_BG, border_width=0, text_color=TEXT_DARK,
            placeholder_text="your@email.com", placeholder_text_color=TEXT_MUTED)
        self.login_email.pack(fill="x")

        ctk.CTkLabel(p, text="Password", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color=TEXT_DARK, anchor="w").pack(fill="x", pady=(14, 4))
        self.login_pass = ctk.CTkEntry(p, height=42, corner_radius=10,
            fg_color=INPUT_BG, border_width=0, text_color=TEXT_DARK, show="●",
            placeholder_text="••••••••", placeholder_text_color=TEXT_MUTED)
        self.login_pass.pack(fill="x")

        self.login_error = ctk.CTkLabel(p, text="", text_color="#D94040",
            font=ctk.CTkFont(size=11), wraplength=300, anchor="w")
        self.login_error.pack(fill="x", pady=(6, 0))

        ctk.CTkButton(p, text="Log in", height=44, corner_radius=12,
            fg_color=BTN_PRIMARY, hover_color=BTN_PRIMARY_HOVER,
            text_color=TEXT_DARK, font=ctk.CTkFont(size=14, weight="bold"),
            command=self._do_login).pack(fill="x", pady=(16, 8))

        ctk.CTkButton(p, text=t("link_lupa", self._bhs), height=28,
            fg_color="transparent", text_color=TEXT_MUTED, hover_color=BG_COLOR,
            font=ctk.CTkFont(size=11, underline=True),
            command=self._go_lupa_sandi).pack()

    def _build_register_form(self):
        p = self.form_container
        bhs = self._bhs
        scroll = ctk.CTkScrollableFrame(p, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        for label, attr, show in [
            (t("f_nama_reg", bhs), "reg_nama", ""),
            (t("f_email_reg", bhs), "reg_email", ""),
            (t("f_pass_reg", bhs), "reg_pass", "●"),
            (t("f_confirm_reg", bhs), "reg_confirm", "●"),
        ]:
            ctk.CTkLabel(scroll, text=label, font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=TEXT_DARK, anchor="w").pack(fill="x", pady=(8, 3))
            e = ctk.CTkEntry(scroll, height=38, corner_radius=10,
                             fg_color=INPUT_BG, border_width=0, text_color=TEXT_DARK,
                             show=show if show else None)
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

        self.reg_error = ctk.CTkLabel(scroll, text="", text_color="#D94040",
            font=ctk.CTkFont(size=11), wraplength=280, anchor="w")
        self.reg_error.pack(fill="x", pady=(4, 0))
        ctk.CTkButton(scroll, text="Sign up", height=42, corner_radius=12,
            fg_color=BTN_PRIMARY, hover_color=BTN_PRIMARY_HOVER,
            text_color=TEXT_DARK, font=ctk.CTkFont(size=14, weight="bold"),
            command=self._do_register).pack(fill="x", pady=(12, 8))

    def _update_strength(self, event=None):
        pwd = self.reg_pass.get()
        level, label, color = get_password_strength_level(pwd)
        self.strength_label.configure(text=f"{t('kekuatan_pwd', self._bhs)} {label}", text_color=color)
        self.strength_bar.set(level / 4)
        try: self.strength_bar.configure(progress_color=color)
        except: pass

    def _do_login(self):
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
        nama = self.reg_nama.get().strip()
        email = self.reg_email.get().strip()
        pwd = self.reg_pass.get()
        confirm = self.reg_confirm.get()
        result = registrasi_pengguna(email, pwd, confirm, nama)
        if result["success"]:
            messagebox.showinfo(t("berhasil", self._bhs), result["message"])
            self.seg_btn.set("Log in")
            self._switch_tab("Log in")
        else:
            self.reg_error.configure(text=result["message"])

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
            logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "assets", "logo_beaply.png"))
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
        global PROFIL_AKTIF_ID
        PROFIL_AKTIF_ID = profil_id
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
# HALAMAN: Dashboard (dengan sidebar)
# ════════════════════════════════════════════════════════════

class HalamanDashboardUtama(ctk.CTkFrame):
    """Dashboard — redesigned to match mockup with 2-column layout."""
    def __init__(self, master, profil_id, bhs="id", navigate_cb=None):
        super().__init__(master, fg_color="transparent")
        self.profil_id = profil_id
        self._bhs = bhs
        self._navigate_cb = navigate_cb
        self._build()

    def _build(self):
        bhs = self._bhs
        profil = tampil_profil(self.profil_id)
        nama = profil["nama"].split()[0] if profil else "Anonymous"
        stats = hitung_statistik(self.profil_id)

        # ── Two-column layout ──
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True)

        # LEFT COLUMN (main content)
        left = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        # ── Greeting Card ──
        # Mockup has a soft peach/skin-toned background
        greet = ctk.CTkFrame(left, fg_color="#FCEBE3", corner_radius=16,
                             border_width=1, border_color="#EED5C9")
        greet.pack(fill="x", pady=(0, 12))
        gp = ctk.CTkFrame(greet, fg_color="transparent")
        gp.pack(fill="x", padx=24, pady=24)
        ctk.CTkLabel(gp, text=f"Good morning, {nama}!",
                     font=ctk.CTkFont(size=14, weight="bold"), text_color="#555555",
                     anchor="w").pack(fill="x")
        # Title with accent
        title_f = ctk.CTkFrame(gp, fg_color="transparent")
        title_f.pack(fill="x", pady=(4, 0))
        ctk.CTkLabel(title_f, text="Let's find your next",
                     font=ctk.CTkFont(size=24, weight="bold"),
                     text_color="#333333").pack(anchor="w")
        accent_f = ctk.CTkFrame(gp, fg_color="transparent")
        accent_f.pack(fill="x")
        # Split "life-changing" into two colors to match mockup
        ctk.CTkLabel(accent_f, text="life-",
                     font=ctk.CTkFont(size=24, weight="bold"),
                     text_color="#A2D2A2").pack(side="left")
        ctk.CTkLabel(accent_f, text="changing",
                     font=ctk.CTkFont(size=24, weight="bold"),
                     text_color="#EAA6A6").pack(side="left")
        ctk.CTkLabel(accent_f, text=" opportunity",
                     font=ctk.CTkFont(size=24, weight="bold"),
                     text_color="#333333").pack(side="left")
        ctk.CTkLabel(gp, text="Explore thousands of opportunities, discover\nscholarships, and make your dreams happen!",
                     font=ctk.CTkFont(size=13), text_color="#555555",
                     anchor="w", justify="left").pack(fill="x", pady=(12, 0))

        # ── Stats Row ──
        stats_f = ctk.CTkFrame(left, fg_color="transparent")
        stats_f.pack(fill="x", pady=(0, 12))
        beasiswa_count = len(ambil_semua_beasiswa())
        bookmark_count = len(ambil_bookmark_user(self.profil_id))
        dl_count = stats.get("total", 0)
        stat_data = [
            (str(beasiswa_count), "Opportunities\nAvailable", PASTEL_COLORS[0]),
            (str(bookmark_count), "Bookmarked\nScholarship", PASTEL_COLORS[1]),
            (str(dl_count), "Upcoming\nDeadlines", PASTEL_COLORS[2]),
            ("7", "Smart Tips\nFor You", PASTEL_COLORS[3]),
        ]
        for val, lbl, bg in stat_data:
            c = ctk.CTkFrame(stats_f, fg_color=bg, corner_radius=12,
                             height=80, border_width=1, border_color=BORDER_COLOR)
            c.pack(side="left", padx=3, expand=True, fill="x")
            c.pack_propagate(False)
            ctk.CTkLabel(c, text=val, font=ctk.CTkFont(size=22, weight="bold"),
                         text_color=TEXT_DARK).pack(pady=(14, 0))
            ctk.CTkLabel(c, text=lbl, font=ctk.CTkFont(size=10),
                         text_color=TEXT_MUTED, justify="center").pack()

        # ── Trending Scholarships ──
        trend_card = ctk.CTkFrame(left, fg_color="transparent", border_width=1,
                                  corner_radius=16, border_color=BORDER_COLOR)
        trend_card.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(trend_card, text="Scholarships Trending Now",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#555555").pack(anchor="w", padx=20, pady=(16, 10))
        trend_grid = ctk.CTkFrame(trend_card, fg_color="transparent")
        trend_grid.pack(fill="x", padx=16, pady=(0, 16))
        all_bea = ambil_semua_beasiswa()[:3]
        for i, bea in enumerate(all_bea):
            bg = PASTEL_COLORS[i % len(PASTEL_COLORS)]
            tc = ctk.CTkFrame(trend_grid, fg_color=bg, corner_radius=14,
                              height=140, border_width=0)
            tc.pack(side="left", padx=4, expand=True, fill="both")
            tc.pack_propagate(False)
            ctk.CTkLabel(tc, text=bea.get("nama", "Beasiswa"),
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=TEXT_DARK, wraplength=120,
                         justify="center").pack(pady=(20, 4))
            ctk.CTkLabel(tc, text=bea.get("penyelenggara", ""),
                         font=ctk.CTkFont(size=9), text_color=TEXT_MUTED,
                         wraplength=110).pack()

        # ── Smart Tips ──
        tips_card = ctk.CTkFrame(left, fg_color=CARD_COLOR, corner_radius=16,
                                 border_width=1, border_color=BORDER_COLOR)
        tips_card.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(tips_card, text="Smart Tips For You",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_DARK).pack(anchor="w", padx=20, pady=(16, 6))
        ctk.CTkLabel(tips_card, text="Complete your profile to unlock personalized scholarship recommendations.\nThe more details you provide, the better matches we can find!",
                     font=ctk.CTkFont(size=12), text_color=TEXT_MUTED,
                     anchor="w", justify="left", wraplength=500).pack(
            anchor="w", padx=20, pady=(0, 16))

        # RIGHT COLUMN (sidebar info)
        right = ctk.CTkFrame(main_frame, fg_color="transparent", width=280)
        right.pack(side="right", fill="y", padx=(0, 0))
        right.pack_propagate(False)

        # Profile Completeness
        pc_card = ctk.CTkFrame(right, fg_color=CARD_COLOR, corner_radius=16,
                               border_width=1, border_color=BORDER_COLOR)
        pc_card.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(pc_card, text="Profile\nCompleteness",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#555555", justify="left").pack(
            anchor="w", padx=20, pady=(16, 8))
        # Circle placeholder
        circ_f = ctk.CTkFrame(pc_card, fg_color="transparent")
        circ_f.pack(fill="x", padx=16, pady=(0, 4))
        
        # We will use CTkCanvas to draw a nice completion arc
        canv = ctk.CTkCanvas(circ_f, width=70, height=70, bg=CARD_COLOR, highlightthickness=0)
        canv.pack(side="left", padx=(0, 8))
        completeness = hitung_completeness(profil)
        
        # Background circle
        canv.create_arc(5, 5, 65, 65, start=0, extent=359, width=6, style="arc", outline="#DFE6E1")
        # Foreground arc
        extent = int((completeness / 100) * 359)
        if extent > 0:
            canv.create_arc(5, 5, 65, 65, start=90, extent=-extent, width=6, style="arc", outline="#F4B3AD")
        
        canv.create_text(35, 35, text=f"{completeness}%", font=("Helvetica", 14, "bold"), fill="#555555")

        desc_f = ctk.CTkFrame(circ_f, fg_color="transparent")
        desc_f.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(desc_f, text="Profile Complete", font=ctk.CTkFont(size=10, weight="bold"), text_color="#555555", anchor="w").pack(fill="x")
        ctk.CTkLabel(desc_f, text="Complete your profile to\nget more better\nscholarship matches!",
                     font=ctk.CTkFont(size=8), text_color=TEXT_MUTED,
                     justify="left", anchor="w").pack(fill="x")
                     
        ctk.CTkButton(pc_card, text="Complete Profile >",
                      fg_color="#8EA996", hover_color="#7A9382",
                      text_color="white", corner_radius=10, height=32,
                      font=ctk.CTkFont(size=11, weight="bold"),
                      command=lambda: self._navigate_cb("profil") if self._navigate_cb else None).pack(
            fill="x", padx=20, pady=(12, 16))

        # Upcoming Deadlines
        dl_card = ctk.CTkFrame(right, fg_color=CARD_COLOR, corner_radius=16,
                               border_width=1, border_color=BORDER_COLOR)
        dl_card.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(dl_card, text="Upcoming Deadlines",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#555555").pack(anchor="w", padx=20, pady=(16, 8))
        trackers = ambil_semua_tracker(self.profil_id)
        
        # Ensure 3 rows exist to match mockup
        for i in range(3):
            r = ctk.CTkFrame(dl_card, fg_color="transparent")
            r.pack(fill="x", padx=20, pady=6)
            
            # Bottom border line for empty slots
            if i < len(trackers) and trackers[i].get("deadline"):
                tr = trackers[i]
                ctk.CTkLabel(r, text=tr["nama_beasiswa"],
                             font=ctk.CTkFont(size=11, weight="bold"),
                             text_color=TEXT_DARK, anchor="w").pack(fill="x")
                ctk.CTkLabel(r, text=format_deadline_display(tr["deadline"]),
                             font=ctk.CTkFont(size=9),
                             text_color=TEXT_MUTED, anchor="w").pack(fill="x")
            else:
                # Add horizontal line placeholder
                ctk.CTkFrame(r, fg_color="#EAEAEA", height=2).pack(fill="x", pady=12)
                
        ctk.CTkFrame(dl_card, height=16, fg_color="transparent").pack()

        # Calendar mini
        cal_card = ctk.CTkFrame(right, fg_color=CARD_COLOR, corner_radius=16,
                                border_width=1, border_color=BORDER_COLOR)
        cal_card.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(cal_card, text="Calendar",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_DARK).pack(anchor="w", padx=16, pady=(16, 8))
        import datetime
        today = datetime.date.today()
        ctk.CTkLabel(cal_card, text=today.strftime("%B %Y"),
                     font=ctk.CTkFont(size=12), text_color=TEXT_MUTED).pack(
            padx=16, pady=(0, 4))
        ctk.CTkLabel(cal_card, text=today.strftime("%d"),
                     font=ctk.CTkFont(size=28, weight="bold"),
                     text_color=BTN_PRIMARY).pack(pady=(0, 16))

# ════════════════════════════════════════════════════════════
# HALAMAN: Tracker Pendaftaran
# ════════════════════════════════════════════════════════════

class HalamanTracker(ctk.CTkFrame):
    def __init__(self, master, profil_id, bhs="id"):
        super().__init__(master, fg_color="transparent")
        self.profil_id = profil_id
        self._bhs = bhs
        self._build()

    def _build(self):
        self._refresh_list()

    def _refresh_list(self):
        for w in self.winfo_children():
            w.destroy()
        bhs = self._bhs

        # Header
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=8, pady=(8, 4))
        ctk.CTkLabel(hdr, text=t("t_judul", bhs),
                     font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")
        ctk.CTkButton(hdr, text=t("t_tambah", bhs), width=140, height=32,
                      font=ctk.CTkFont(size=12, weight="bold"),
                      command=self._form_tambah).pack(side="right")

        # List tracker
        trackers = ambil_semua_tracker(self.profil_id)
        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=8, pady=4)

        if not trackers:
            ctk.CTkLabel(scroll, text="Belum ada tracker. Tambahkan yang pertama!",
                         text_color="gray50",
                         font=ctk.CTkFont(size=12)).pack(pady=40)
            return

        for tr in trackers:
            self._card_tracker(scroll, tr)

    def _card_tracker(self, parent, tr):
        bhs = self._bhs
        card = ctk.CTkFrame(parent, corner_radius=10)
        card.pack(fill="x", pady=4)

        # Header row
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=12, pady=(8, 2))
        ctk.CTkLabel(top, text=tr["nama_beasiswa"],
                     font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")

        # Bookmark star
        bm_text = "⭐" if tr["dibookmark"] else "☆"
        ctk.CTkButton(top, text=bm_text, width=30, height=26,
                      fg_color="transparent",
                      command=lambda tid=tr["id"]: self._toggle_bm(tid)).pack(side="right")

        # Status badge
        status_lbl = format_status(tr["status"], bhs)
        status_clr = warna_status(tr["status"])
        ctk.CTkLabel(top, text=f"  {status_lbl}  ",
                     font=ctk.CTkFont(size=10),
                     text_color="white",
                     fg_color=status_clr,
                     corner_radius=4).pack(side="right", padx=4)

        # Info row
        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(fill="x", padx=12, pady=2)
        dl_text = format_deadline_display(tr["deadline"]) if tr["deadline"] else "Tidak ada deadline"
        ctk.CTkLabel(info, text=f"📅 {dl_text}",
                     font=ctk.CTkFont(size=10),
                     text_color="gray50").pack(side="left")

        if tr["catatan"]:
            ctk.CTkLabel(info, text=f"📝 {tr['catatan'][:40]}",
                         font=ctk.CTkFont(size=10),
                         text_color="gray50").pack(side="left", padx=12)

        # Action buttons
        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.pack(fill="x", padx=12, pady=(2, 8))

        # Status dropdown
        status_var = ctk.StringVar(value=tr["status"])
        status_dd = ctk.CTkComboBox(
            actions, values=STATUS_LIST, width=140, height=26,
            variable=status_var,
            font=ctk.CTkFont(size=10),
            command=lambda val, tid=tr["id"]: self._ubah_status(tid, val))
        status_dd.pack(side="left")

        ctk.CTkButton(actions, text=t("t_hapus", bhs), width=60, height=26,
                      fg_color="#EF4444", hover_color="#DC2626",
                      font=ctk.CTkFont(size=10),
                      command=lambda tid=tr["id"]: self._hapus(tid)).pack(side="right")

    def _form_tambah(self):
        for w in self.winfo_children():
            w.destroy()
        bhs = self._bhs

        ctk.CTkButton(self, text=t("btn_kembali", bhs), width=100,
                      fg_color="transparent", border_width=1,
                      command=self._refresh_list).pack(anchor="w", padx=8, pady=(8, 4))

        ctk.CTkLabel(self, text=t("t_tambah", bhs),
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(4, 12))

        form = ctk.CTkFrame(self, corner_radius=10)
        form.pack(fill="x", padx=8, pady=4)

        self.e_nama_t = ctk.CTkEntry(form, placeholder_text=t("t_nama", bhs),
                                     width=400, height=38)
        self.e_nama_t.pack(padx=16, pady=(12, 6))
        self.e_deadline_t = ctk.CTkEntry(form, placeholder_text=t("t_deadline", bhs),
                                         width=400, height=38)
        self.e_deadline_t.pack(padx=16, pady=6)
        self.e_catatan_t = ctk.CTkEntry(form, placeholder_text=t("t_catatan", bhs),
                                        width=400, height=38)
        self.e_catatan_t.pack(padx=16, pady=6)

        self.err_tracker = ctk.CTkLabel(form, text="", text_color="#FF3B30",
                                        font=ctk.CTkFont(size=11))
        self.err_tracker.pack(pady=4)

        ctk.CTkButton(form, text=t("t_simpan", bhs), width=200, height=40,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._simpan_tracker).pack(pady=(4, 16))

    def _simpan_tracker(self):
        nama = self.e_nama_t.get().strip()
        dl = self.e_deadline_t.get().strip()
        cat = self.e_catatan_t.get().strip()

        ok, msg, tid = tambah_penanda_manual(self.profil_id, nama, dl, cat)
        if not ok:
            self.err_tracker.configure(text=msg)
            return
        # Buat pengingat otomatis jika ada deadline
        if dl:
            buat_pengingat_otomatis(tid)
        messagebox.showinfo(t("berhasil", self._bhs), t("t_ok", self._bhs))
        self._refresh_list()

    def _ubah_status(self, tracker_id, status_baru):
        ok, msg = ubah_status(tracker_id, status_baru)
        if ok:
            # Buat notifikasi perubahan status
            tr = ambil_tracker_by_id(tracker_id)
            if tr:
                buat_notifikasi_status(self.profil_id, tr["nama_beasiswa"], status_baru)

    def _toggle_bm(self, tracker_id):
        toggle_bookmark(tracker_id)
        self._refresh_list()

    def _hapus(self, tracker_id):
        if messagebox.askyesno("Konfirmasi", "Hapus tracker ini?"):
            hapus_tracker(tracker_id)
            self._refresh_list()


# ════════════════════════════════════════════════════════════
# HALAMAN: Kalender Deadline
# ════════════════════════════════════════════════════════════

class HalamanKalender(ctk.CTkFrame):
    """Calendar — redesigned to match mockup with two-column layout."""
    def __init__(self, master, profil_id, bhs="id"):
        super().__init__(master, fg_color="transparent")
        self.profil_id = profil_id
        self._bhs = bhs
        from datetime import datetime
        now = datetime.now()
        self._bulan = now.month
        self._tahun = now.year
        self._build()

    def _build(self):
        self._refresh_kalender()

    def _refresh_kalender(self):
        for w in self.winfo_children():
            w.destroy()
        bhs = self._bhs

        data = tampilan_kalender(self.profil_id, self._bulan, self._tahun)

        # Two-column layout
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True)

        # LEFT: Calendar grid
        left = ctk.CTkFrame(main_frame, fg_color=CARD_COLOR, corner_radius=16,
                            border_width=1, border_color=BORDER_COLOR)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        # Month header with pink/salmon color
        month_hdr = ctk.CTkFrame(left, fg_color="#F6D6D0", corner_radius=16,
                                 height=50)
        month_hdr.pack(fill="x")
        month_hdr.pack_propagate(False)
        ctk.CTkButton(month_hdr, text="<", width=36, height=36,
                      fg_color="transparent", text_color=TEXT_DARK,
                      hover_color="#EECAC4", corner_radius=8,
                      font=ctk.CTkFont(size=16, weight="bold"),
                      command=self._prev_bulan).pack(side="left", padx=8)
        ctk.CTkLabel(month_hdr, text=f"{data['nama_bulan']} {data['tahun']}",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=TEXT_DARK).pack(side="left", expand=True)
        ctk.CTkButton(month_hdr, text=">", width=36, height=36,
                      fg_color="transparent", text_color=TEXT_DARK,
                      hover_color="#EECAC4", corner_radius=8,
                      font=ctk.CTkFont(size=16, weight="bold"),
                      command=self._next_bulan).pack(side="right", padx=8)

        # Day headers
        grid = ctk.CTkFrame(left, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=8, pady=8)

        hari_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for c, h in enumerate(hari_labels):
            ctk.CTkLabel(grid, text=h, font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=TEXT_MUTED).grid(row=0, column=c, padx=4, pady=6)

        # Date cells
        from datetime import datetime
        today = datetime.now()
        hari_pertama = data["hari_pertama"]
        total_hari = data["total_hari"]
        tgl_warna = data.get("tanggal_warna", {})
        tgl_tracker = data.get("tanggal_tracker", {})

        row = 1
        col = hari_pertama
        for day in range(1, total_hari + 1):
            warna = tgl_warna.get(day, None)
            is_today = (day == today.day and self._bulan == today.month
                        and self._tahun == today.year)
            fg = warna if warna else ("transparent" if not is_today else BTN_PRIMARY)
            txt_color = "white" if (warna or is_today) else TEXT_DARK

            btn = ctk.CTkButton(
                grid, text=str(day), width=44, height=36,
                fg_color=fg if fg != "transparent" else "transparent",
                text_color=txt_color,
                hover_color=BTN_PALE, corner_radius=8,
                font=ctk.CTkFont(size=12, weight="bold" if (warna or is_today) else "normal"),
                command=lambda d=day: self._klik_tanggal(d, tgl_tracker),
            )
            btn.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")
            col += 1
            if col > 6:
                col = 0
                row += 1

        for c in range(7):
            grid.grid_columnconfigure(c, weight=1)

        # Legend
        leg = ctk.CTkFrame(left, fg_color="transparent")
        leg.pack(fill="x", padx=12, pady=(0, 12))
        legends = [("Deadline", "#EF4444"), ("Today", BTN_PRIMARY),
                   ("Bookmark", "#3B82F6")]
        for txt, clr in legends:
            f = ctk.CTkFrame(leg, fg_color="transparent")
            f.pack(side="left", padx=8)
            dot = ctk.CTkFrame(f, fg_color=clr, width=10, height=10,
                               corner_radius=5)
            dot.pack(side="left", padx=(0, 4))
            ctk.CTkLabel(f, text=txt, font=ctk.CTkFont(size=9),
                         text_color=TEXT_MUTED).pack(side="left")

        # RIGHT: Upcoming events sidebar
        right = ctk.CTkFrame(main_frame, fg_color="#E8EBE4", corner_radius=16,
                             width=260, border_width=1, border_color=BORDER_COLOR)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        ctk.CTkLabel(right, text="Upcoming Events",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=TEXT_DARK).pack(anchor="w", padx=16, pady=(20, 12))

        events_scroll = ctk.CTkScrollableFrame(right, fg_color="transparent")
        events_scroll.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # Get tracker events
        trackers = ambil_semua_tracker(self.profil_id) if self.profil_id else []
        upcoming = [t for t in trackers if t.get("deadline")]
        upcoming.sort(key=lambda x: x.get("deadline", "9999"))

        if not upcoming:
            ctk.CTkLabel(events_scroll, text="No upcoming events.\nAdd deadlines via Tracker.",
                         font=ctk.CTkFont(size=11), text_color=TEXT_MUTED,
                         justify="center").pack(pady=40)
        else:
            for tr in upcoming[:10]:
                ev = ctk.CTkFrame(events_scroll, fg_color=CARD_COLOR,
                                  corner_radius=10)
                ev.pack(fill="x", pady=3)
                ctk.CTkLabel(ev, text=tr.get("nama_beasiswa", ""),
                             font=ctk.CTkFont(size=11, weight="bold"),
                             text_color=TEXT_DARK, wraplength=200,
                             anchor="w").pack(padx=10, pady=(8, 2), anchor="w")
                ctk.CTkLabel(ev, text=tr.get("deadline", ""),
                             font=ctk.CTkFont(size=10), text_color=TEXT_ACCENT,
                             anchor="w").pack(padx=10, pady=(0, 8), anchor="w")

    def _prev_bulan(self):
        self._bulan -= 1
        if self._bulan < 1:
            self._bulan = 12
            self._tahun -= 1
        self._refresh_kalender()

    def _next_bulan(self):
        self._bulan += 1
        if self._bulan > 12:
            self._bulan = 1
            self._tahun += 1
        self._refresh_kalender()

    def _klik_tanggal(self, day, tgl_tracker):
        items = tgl_tracker.get(day, [])
        if not items:
            return
        msg = "\n".join([f"\u2022 {it['nama_beasiswa']} \u2014 {format_status(it['status'], self._bhs)}"
                         for it in items])
        messagebox.showinfo(t("k_detail", self._bhs), msg)



# ════════════════════════════════════════════════════════════
# HALAMAN: Eksplorasi Beasiswa
# ════════════════════════════════════════════════════════════

class HalamanEksplorasi(ctk.CTkFrame):
    """Scholarships page — with sort, filter, deadline colors."""
    def __init__(self, master, profil_id, bhs="id"):
        super().__init__(master, fg_color="transparent")
        self.profil_id = profil_id
        self._bhs = bhs
        self._all_beasiswa = ambil_semua_beasiswa()
        self._filtered = list(self._all_beasiswa)
        self._sort_mode = "default"
        self._filter_jenjang = None
        self._filter_toefl = False
        self._filter_ielts = False
        self._check_deadline_notifs()
        self._build()

    def _check_deadline_notifs(self):
        """Auto-create notifications for bookmarked scholarships with deadline <7 days."""
        from datetime import datetime, timedelta
        today = datetime.now().date()
        bookmarks = ambil_bookmark_user(self.profil_id)
        for bea in bookmarks:
            dl = bea.get("deadline", "")
            if not dl:
                continue
            try:
                dl_date = datetime.strptime(dl, "%Y-%m-%d").date()
                days_left = (dl_date - today).days
                if 0 <= days_left <= 7:
                    buat_notifikasi_deadline(
                        self.profil_id,
                        bea.get("nama", "Beasiswa"),
                        dl,
                    )
            except (ValueError, TypeError):
                pass

    def _build(self):
        bhs = self._bhs

        # ── Search bar + Sort/Filter ──
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=(0, 10))

        self.search_entry = ctk.CTkEntry(
            top, placeholder_text="Search Scholarships...",
            placeholder_text_color=TEXT_MUTED, height=40,
            corner_radius=12, fg_color=CARD_COLOR, border_width=1,
            border_color=BORDER_COLOR, text_color=TEXT_DARK)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.search_entry.bind("<KeyRelease>", self._on_search)

        ctk.CTkButton(top, text="\u2195 Sort by", width=100, height=40,
                      corner_radius=12, fg_color=CARD_COLOR,
                      border_width=1, border_color=BORDER_COLOR,
                      text_color=TEXT_DARK, hover_color=BTN_PALE,
                      font=ctk.CTkFont(size=12),
                      command=self._show_sort).pack(side="left", padx=(0, 6))

        ctk.CTkButton(top, text="\u2699 Filters", width=100, height=40,
                      corner_radius=12, fg_color=CARD_COLOR,
                      border_width=1, border_color=BORDER_COLOR,
                      text_color=TEXT_DARK, hover_color=BTN_PALE,
                      font=ctk.CTkFont(size=12),
                      command=self._show_filter).pack(side="left")

        # ── Active filters display ──
        self.filter_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.filter_bar.pack(fill="x", pady=(0, 4))
        self._update_filter_bar()

        # ── Count label ──
        self.count_label = ctk.CTkLabel(
            self, text=f"{len(self._filtered)} Scholarships Found",
            font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_DARK,
            anchor="w")
        self.count_label.pack(fill="x", pady=(0, 8))

        # ── Grid container ──
        self.grid_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.grid_scroll.pack(fill="both", expand=True)
        self._apply_filters_and_sort()
        self._render_grid()

    def _update_filter_bar(self):
        for w in self.filter_bar.winfo_children():
            w.destroy()
        tags = []
        if self._filter_jenjang:
            tags.append(f"Jenjang: {self._filter_jenjang}")
        if self._filter_toefl:
            tags.append("TOEFL Required")
        if self._filter_ielts:
            tags.append("IELTS Required")
        if self._sort_mode != "default":
            sort_names = {"deadline_asc": "Deadline \u2191", "deadline_desc": "Deadline \u2193",
                          "name_asc": "Name A-Z", "name_desc": "Name Z-A"}
            tags.append(f"Sort: {sort_names.get(self._sort_mode, self._sort_mode)}")
        for tag in tags:
            pill = ctk.CTkButton(self.filter_bar, text=f"{tag}  \u2715", height=26,
                                 fg_color=BTN_PRIMARY, hover_color=BTN_PRIMARY_HOVER,
                                 text_color=TEXT_DARK, corner_radius=12,
                                 font=ctk.CTkFont(size=10),
                                 command=lambda t=tag: self._remove_filter(t))
            pill.pack(side="left", padx=(0, 6))
        if tags:
            ctk.CTkButton(self.filter_bar, text="Clear All", height=26,
                          fg_color="transparent", text_color="#D94040",
                          hover_color="#FCE8E8", corner_radius=12,
                          font=ctk.CTkFont(size=10),
                          command=self._clear_filters).pack(side="left", padx=4)

    def _remove_filter(self, tag):
        if "Jenjang" in tag:
            self._filter_jenjang = None
        elif "TOEFL" in tag:
            self._filter_toefl = False
        elif "IELTS" in tag:
            self._filter_ielts = False
        elif "Sort" in tag:
            self._sort_mode = "default"
        self._apply_filters_and_sort()
        self._update_filter_bar()
        self._render_grid()

    def _clear_filters(self):
        self._filter_jenjang = None
        self._filter_toefl = False
        self._filter_ielts = False
        self._sort_mode = "default"
        self._apply_filters_and_sort()
        self._update_filter_bar()
        self._render_grid()

    def _apply_filters_and_sort(self):
        q = self.search_entry.get().strip().lower() if hasattr(self, 'search_entry') else ""
        result = list(self._all_beasiswa)

        # Search
        if q:
            result = [b for b in result
                      if q in b.get("nama", "").lower()
                      or q in b.get("penyelenggara", "").lower()
                      or q in b.get("jenjang", "").lower()]

        # Filter jenjang
        if self._filter_jenjang:
            fj = self._filter_jenjang.upper()
            result = [b for b in result if fj in b.get("jenjang", "").upper()]

        # Filter TOEFL
        if self._filter_toefl:
            result = [b for b in result if b.get("syarat_toefl")]

        # Filter IELTS
        if self._filter_ielts:
            result = [b for b in result if b.get("syarat_ielts")]

        # Sort
        if self._sort_mode == "deadline_asc":
            result.sort(key=lambda b: b.get("deadline") or "9999-99-99")
        elif self._sort_mode == "deadline_desc":
            result.sort(key=lambda b: b.get("deadline") or "0000-00-00", reverse=True)
        elif self._sort_mode == "name_asc":
            result.sort(key=lambda b: b.get("nama", "").lower())
        elif self._sort_mode == "name_desc":
            result.sort(key=lambda b: b.get("nama", "").lower(), reverse=True)

        self._filtered = result

    def _get_deadline_color(self, deadline_str):
        """Return color based on days until deadline."""
        if not deadline_str:
            return None
        from datetime import datetime
        try:
            dl = datetime.strptime(deadline_str, "%Y-%m-%d").date()
            days = (dl - datetime.now().date()).days
            if days < 0:
                return "#999999"   # Expired (gray)
            elif days <= 7:
                return "#EF4444"   # Red
            elif days <= 14:
                return "#F59E0B"   # Orange
            else:
                return "#22C55E"   # Green
        except (ValueError, TypeError):
            return None

    def _render_grid(self):
        for w in self.grid_scroll.winfo_children():
            w.destroy()

        cols = 3
        for i, bea in enumerate(self._filtered):
            row_idx = i // cols
            col_idx = i % cols
            bg = PASTEL_COLORS[i % len(PASTEL_COLORS)]

            # Check if bookmarked and get deadline color
            is_bm = cek_bookmark(self.profil_id, bea.get("id", 0))
            dl_color = self._get_deadline_color(bea.get("deadline")) if is_bm else None

            card = ctk.CTkFrame(self.grid_scroll, fg_color=bg, corner_radius=14,
                                border_width=2 if dl_color else 1,
                                border_color=dl_color if dl_color else BORDER_COLOR)
            card.grid(row=row_idx, column=col_idx, padx=6, pady=6, sticky="nsew")
            self.grid_scroll.grid_columnconfigure(col_idx, weight=1)

            # Title
            ctk.CTkLabel(card, text=bea.get("nama", "Beasiswa"),
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=TEXT_DARK, wraplength=200,
                         justify="left", anchor="w").pack(
                anchor="w", padx=14, pady=(14, 2))

            # Penyelenggara
            penyelenggara = bea.get("penyelenggara", "")
            if penyelenggara:
                ctk.CTkLabel(card, text=penyelenggara,
                             font=ctk.CTkFont(size=10), text_color=TEXT_MUTED,
                             anchor="w", wraplength=200).pack(anchor="w", padx=14, pady=(0, 4))

            # Jenjang
            jenjang = bea.get("jenjang", "-")
            ctk.CTkLabel(card, text=f"Jenjang: {jenjang}",
                         font=ctk.CTkFont(size=9), text_color=TEXT_MUTED,
                         anchor="w").pack(anchor="w", padx=14, pady=(2, 0))

            # Deadline with color indicator
            deadline = bea.get("deadline", "")
            if deadline:
                color = self._get_deadline_color(deadline)
                dl_frame = ctk.CTkFrame(card, fg_color="transparent")
                dl_frame.pack(anchor="w", padx=14, pady=(4, 0))
                if color:
                    dot = ctk.CTkFrame(dl_frame, fg_color=color, width=8, height=8,
                                       corner_radius=4)
                    dot.pack(side="left", padx=(0, 4), pady=2)
                ctk.CTkLabel(dl_frame, text=f"Deadline: {deadline}",
                             font=ctk.CTkFont(size=9),
                             text_color=color if color else TEXT_ACCENT,
                             anchor="w").pack(side="left")

            # Bottom row: bookmark button
            bot = ctk.CTkFrame(card, fg_color="transparent")
            bot.pack(fill="x", padx=10, pady=(6, 10))
            bm_text = "\u2605" if is_bm else "\u2606"
            bm_color = TEXT_ACCENT if is_bm else TEXT_MUTED
            ctk.CTkButton(bot, text=bm_text, width=28, height=24,
                          fg_color="transparent", text_color=bm_color,
                          hover_color=BORDER_COLOR, font=ctk.CTkFont(size=16),
                          command=lambda b=bea: self._toggle_bm(b)).pack(side="right")

        self.count_label.configure(text=f"{len(self._filtered)} Scholarships Found")

    def _on_search(self, event=None):
        self._apply_filters_and_sort()
        self._render_grid()

    def _toggle_bm(self, bea):
        toggle_bookmark_beasiswa(self.profil_id, bea.get("id", 0))
        self._render_grid()

    def _show_sort(self):
        top = ctk.CTkToplevel(self)
        top.title("Sort Scholarships")
        top.geometry("300x280")
        top.configure(fg_color=BG_COLOR)
        top.transient(self.winfo_toplevel())
        top.grab_set()
        ctk.CTkLabel(top, text="Sort By",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=TEXT_DARK).pack(pady=(20, 12))
        options = [
            ("Default", "default"),
            ("Deadline (Closest First)", "deadline_asc"),
            ("Deadline (Furthest First)", "deadline_desc"),
            ("Name (A \u2192 Z)", "name_asc"),
            ("Name (Z \u2192 A)", "name_desc"),
        ]
        for label, mode in options:
            is_active = self._sort_mode == mode
            ctk.CTkButton(top, text=label, height=36,
                          fg_color=BTN_PRIMARY if is_active else CARD_COLOR,
                          hover_color=BTN_PRIMARY_HOVER,
                          text_color=TEXT_DARK, corner_radius=10,
                          border_width=1, border_color=BORDER_COLOR,
                          font=ctk.CTkFont(size=12, weight="bold" if is_active else "normal"),
                          command=lambda m=mode, t=top: self._apply_sort(m, t)).pack(
                fill="x", padx=24, pady=3)

    def _apply_sort(self, mode, popup):
        self._sort_mode = mode
        popup.destroy()
        self._apply_filters_and_sort()
        self._update_filter_bar()
        self._render_grid()

    def _show_filter(self):
        top = ctk.CTkToplevel(self)
        top.title("Filter Scholarships")
        top.geometry("340x420")
        top.configure(fg_color=BG_COLOR)
        top.transient(self.winfo_toplevel())
        top.grab_set()

        scroll = ctk.CTkScrollableFrame(top, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(scroll, text="Filter By Jenjang",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_DARK).pack(anchor="w", pady=(0, 8))
        jenjang_options = ["All", "S1", "S2", "S3", "D3", "D4", "SMA"]
        jenjang_var = ctk.StringVar(value=self._filter_jenjang or "All")
        for j in jenjang_options:
            ctk.CTkRadioButton(scroll, text=j, variable=jenjang_var, value=j,
                               text_color=TEXT_DARK,
                               font=ctk.CTkFont(size=12)).pack(anchor="w", pady=2)

        ctk.CTkLabel(scroll, text="Test Score Requirements",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_DARK).pack(anchor="w", pady=(16, 8))
        toefl_var = ctk.BooleanVar(value=self._filter_toefl)
        ielts_var = ctk.BooleanVar(value=self._filter_ielts)
        ctk.CTkCheckBox(scroll, text="Requires TOEFL", variable=toefl_var,
                        text_color=TEXT_DARK, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(scroll, text="Requires IELTS", variable=ielts_var,
                        text_color=TEXT_DARK, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=2)

        def apply():
            jv = jenjang_var.get()
            self._filter_jenjang = None if jv == "All" else jv
            self._filter_toefl = toefl_var.get()
            self._filter_ielts = ielts_var.get()
            top.destroy()
            self._apply_filters_and_sort()
            self._update_filter_bar()
            self._render_grid()

        ctk.CTkButton(scroll, text="Apply Filters", height=40,
                      fg_color=BTN_PRIMARY, hover_color=BTN_PRIMARY_HOVER,
                      text_color=TEXT_DARK, corner_radius=12,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=apply).pack(fill="x", pady=(16, 0))



class HalamanBookmarks(ctk.CTkFrame):
    """Bookmarks page — with deadline color indicators."""
    def __init__(self, master, profil_id, bhs="id"):
        super().__init__(master, fg_color="transparent")
        self.profil_id = profil_id
        self._bhs = bhs
        self._build()

    def _get_deadline_info(self, deadline_str):
        """Return (color, label) based on days until deadline."""
        if not deadline_str:
            return None, ""
        from datetime import datetime
        try:
            dl = datetime.strptime(deadline_str, "%Y-%m-%d").date()
            days = (dl - datetime.now().date()).days
            if days < 0:
                return "#999999", "Expired"
            elif days <= 7:
                return "#EF4444", f"{days} days left!"
            elif days <= 14:
                return "#F59E0B", f"{days} days left"
            else:
                return "#22C55E", f"{days} days left"
        except (ValueError, TypeError):
            return None, ""

    def _build(self):
        bm_list = ambil_bookmark_user(self.profil_id)

        # ── Header ──
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(hdr, text=f"{len(bm_list)} Bookmarks",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=TEXT_DARK).pack(side="left")
        ctk.CTkButton(hdr, text="\ud83d\uddd1 Clear All", width=100, height=32,
                      fg_color=CARD_COLOR, border_width=1,
                      border_color=BORDER_COLOR, text_color="#D94040",
                      hover_color="#FCE8E8", corner_radius=10,
                      font=ctk.CTkFont(size=11),
                      command=self._clear_all).pack(side="right")

        # Legend
        leg = ctk.CTkFrame(self, fg_color="transparent")
        leg.pack(fill="x", pady=(0, 8))
        for txt, clr in [("\u2022 >14 days", "#22C55E"), ("\u2022 7-14 days", "#F59E0B"),
                          ("\u2022 <7 days", "#EF4444"), ("\u2022 Expired", "#999999")]:
            ctk.CTkLabel(leg, text=txt, font=ctk.CTkFont(size=9), text_color=clr).pack(
                side="left", padx=6)

        # ── List ──
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        if not bm_list:
            ctk.CTkLabel(scroll, text="No bookmarked scholarships yet.\nExplore and save scholarships you're interested in!",
                         font=ctk.CTkFont(size=13), text_color=TEXT_MUTED,
                         justify="center").pack(pady=60)
            return

        for bea in bm_list:
            dl_color, dl_label = self._get_deadline_info(bea.get("deadline"))
            border_clr = dl_color if dl_color else BORDER_COLOR
            card = ctk.CTkFrame(scroll, fg_color=CARD_COLOR, corner_radius=14,
                                border_width=2 if dl_color else 1,
                                border_color=border_clr)
            card.pack(fill="x", pady=5)
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=20, pady=16)

            # Title row
            title_row = ctk.CTkFrame(inner, fg_color="transparent")
            title_row.pack(fill="x")
            ctk.CTkLabel(title_row, text=bea.get("nama", ""),
                         font=ctk.CTkFont(size=14, weight="bold"),
                         text_color=TEXT_DARK, anchor="w",
                         wraplength=500).pack(side="left", fill="x", expand=True)
            if dl_label:
                ctk.CTkLabel(title_row, text=dl_label,
                             font=ctk.CTkFont(size=10, weight="bold"),
                             text_color=dl_color).pack(side="right")

            ctk.CTkLabel(inner, text=bea.get("penyelenggara", ""),
                         font=ctk.CTkFont(size=11), text_color=TEXT_MUTED,
                         anchor="w").pack(fill="x", pady=(2, 0))

            info = f"Jenjang: {bea.get('jenjang', '-')}"
            if bea.get("deadline"):
                info += f"  |  Deadline: {bea['deadline']}"
            ctk.CTkLabel(inner, text=info,
                         font=ctk.CTkFont(size=10), text_color=TEXT_MUTED,
                         anchor="w").pack(fill="x", pady=(4, 0))

            # Remove button
            ctk.CTkButton(inner, text="Remove", width=70, height=24,
                          fg_color="transparent", border_width=1,
                          border_color="#D94040", text_color="#D94040",
                          hover_color="#FCE8E8", corner_radius=8,
                          font=ctk.CTkFont(size=10),
                          command=lambda bid=bea.get("id", 0): self._remove_bm(bid)).pack(
                anchor="e", pady=(6, 0))

    def _remove_bm(self, beasiswa_id):
        toggle_bookmark_beasiswa(self.profil_id, beasiswa_id)
        for w in self.winfo_children():
            w.destroy()
        self._build()

    def _clear_all(self):
        if konfirm_yesno(self, "Clear All", "Remove all bookmarks?"):
            for bm in ambil_bookmark_user(self.profil_id):
                toggle_bookmark_beasiswa(self.profil_id, bm.get("id", 0))
            for w in self.winfo_children():
                w.destroy()
            self._build()



class HalamanNotifikasi(ctk.CTkFrame):
    """Notifications page — redesigned to match mockup."""
    def __init__(self, master, profil_id, bhs="id"):
        super().__init__(master, fg_color="transparent")
        self.profil_id = profil_id
        self._bhs = bhs
        self._filter = None  # None=all, 0=unread, 1=read
        self._build()

    def _build(self):
        self._refresh_notif()

    def _refresh_notif(self):
        for w in self.winfo_children():
            w.destroy()
        bhs = self._bhs

        # Filter tabs + action buttons
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=(0, 16))

        # Pill filter tabs
        tabs_frame = ctk.CTkFrame(top, fg_color="#E8EBE4", corner_radius=20,
                                  height=36)
        tabs_frame.pack(side="left")
        tabs_frame.pack_propagate(False)
        for label, fval in [("All", None), ("Read", 1), ("Unread", 0)]:
            is_active = self._filter == fval
            ctk.CTkButton(
                tabs_frame, text=label, width=80, height=32,
                corner_radius=16,
                fg_color=CARD_COLOR if is_active else "transparent",
                text_color=TEXT_DARK,
                hover_color=CARD_COLOR,
                font=ctk.CTkFont(size=12, weight="bold" if is_active else "normal"),
                command=lambda f=fval: self._set_filter(f),
            ).pack(side="left", padx=2, pady=2)

        # Action buttons
        ctk.CTkButton(top, text="Clear All", width=90, height=32,
                      fg_color="#F6E6E4", text_color="#D94040",
                      hover_color="#FCE0E0", corner_radius=10,
                      border_width=0, font=ctk.CTkFont(size=11),
                      command=self._hapus_semua).pack(side="right", padx=(6, 0))
        ctk.CTkButton(top, text="Mark All as Read", width=130, height=32,
                      fg_color=BTN_PRIMARY, text_color=TEXT_DARK,
                      hover_color=BTN_PRIMARY_HOVER, corner_radius=10,
                      font=ctk.CTkFont(size=11, weight="bold"),
                      command=self._tandai_semua).pack(side="right")

        # Notifications list
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        notifs = ambil_riwayat(self.profil_id)
        if self._filter is not None:
            notifs = [n for n in notifs if n.get("dibaca", 0) == self._filter]

        if not notifs:
            ctk.CTkLabel(scroll, text="No notifications yet.",
                         font=ctk.CTkFont(size=14), text_color=TEXT_MUTED,
                         justify="center").pack(pady=60)
            return

        # Group by date
        from datetime import datetime, timedelta
        now = datetime.now()
        groups = {}
        for n in notifs:
            ts = n.get("dibuat_pada", "")
            try:
                dt = datetime.strptime(ts[:10], "%Y-%m-%d")
                diff = (now.date() - dt.date()).days
                if diff == 0:
                    group = "Today"
                elif diff == 1:
                    group = "Yesterday"
                elif diff < 7:
                    group = f"{diff} days ago"
                else:
                    group = dt.strftime("%b %d")
            except (ValueError, TypeError):
                group = "Older"
            groups.setdefault(group, []).append(n)

        for group_name, items in groups.items():
            ctk.CTkLabel(scroll, text=group_name,
                         font=ctk.CTkFont(size=14, weight="bold"),
                         text_color=TEXT_DARK).pack(anchor="w", pady=(12, 6))
            for n in items:
                is_unread = not n.get("dibaca", 0)
                card_bg = CARD_COLOR if is_unread else "#F8F6F4"
                card = ctk.CTkFrame(scroll, fg_color=card_bg, corner_radius=12,
                                    border_width=1, border_color=BORDER_COLOR)
                card.pack(fill="x", pady=3)
                inner = ctk.CTkFrame(card, fg_color="transparent")
                inner.pack(fill="x", padx=16, pady=12)
                # Title
                title_f = ctk.CTkFrame(inner, fg_color="transparent")
                title_f.pack(fill="x")
                ctk.CTkLabel(title_f, text=n.get("judul", "Notification"),
                             font=ctk.CTkFont(size=13, weight="bold" if is_unread else "normal"),
                             text_color=TEXT_DARK, anchor="w").pack(side="left")
                if is_unread:
                    dot = ctk.CTkFrame(title_f, fg_color=TEXT_ACCENT,
                                       width=8, height=8, corner_radius=4)
                    dot.pack(side="right")
                # Message
                ctk.CTkLabel(inner, text=n.get("pesan", ""),
                             font=ctk.CTkFont(size=11), text_color=TEXT_MUTED,
                             anchor="w", wraplength=600, justify="left").pack(
                    fill="x", pady=(2, 0))
                # Actions
                act_f = ctk.CTkFrame(inner, fg_color="transparent")
                act_f.pack(fill="x", pady=(6, 0))
                ts_text = n.get("dibuat_pada", "")[:16]
                ctk.CTkLabel(act_f, text=ts_text,
                             font=ctk.CTkFont(size=9), text_color=TEXT_MUTED).pack(side="left")
                if is_unread:
                    ctk.CTkButton(act_f, text="Mark Read", width=70, height=22,
                                  fg_color="transparent", border_width=1,
                                  border_color=BORDER_COLOR, text_color=TEXT_MUTED,
                                  corner_radius=6, font=ctk.CTkFont(size=9),
                                  command=lambda nid=n["id"]: self._mark_read(nid)).pack(side="right")

    def _set_filter(self, f):
        self._filter = f
        self._refresh_notif()

    def _tandai_semua(self):
        tandai_semua_dibaca(self.profil_id)
        self._refresh_notif()

    def _mark_read(self, nid):
        tandai_dibaca(nid)
        self._refresh_notif()

    def _hapus_semua(self):
        if konfirm_yesno(self, "Clear All", "Delete all notifications?"):
            for n in ambil_riwayat(self.profil_id):
                hapus_notifikasi(n["id"])
            self._refresh_notif()


# ════════════════════════════════════════════════════════════
# HALAMAN: Profil (tampilan profil lengkap)
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


# ════════════════════════════════════════════════════════════
# LAYOUT: Sidebar + Content Area
# ════════════════════════════════════════════════════════════

class LayoutDenganSidebar(ctk.CTkFrame):
    """Main layout with sidebar navigation — redesigned to match mockup."""
    def __init__(self, master, user_profile_or_id, logout_callback):
        super().__init__(master, fg_color=BG_COLOR)
        if isinstance(user_profile_or_id, dict):
            self.user_profile = user_profile_or_id
            self.profil_id = user_profile_or_id.get("profil_id") or user_profile_or_id.get("id")
        else:
            self.profil_id = user_profile_or_id
            profil_data = tampil_profil(self.profil_id) if self.profil_id else {}
            self.user_profile = profil_data or {}
        self.logout_cb = logout_callback
        self._bhs = get_bahasa(self.profil_id) if self.profil_id else "id"
        self._current_nav = "dashboard"
        self._build()
        self._navigate("dashboard")

    def _build(self):
        bhs = self._bhs

        # ══════ SIDEBAR ══════
        self.sidebar = ctk.CTkFrame(self, fg_color=SIDEBAR_BG, width=200,
                                    corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Bottom items FIRST (pack side=bottom so they stay pinned)
        bottom_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom_frame.pack(side="bottom", fill="x", pady=(0, 10))

        self.nav_buttons = {}
        for key, icon, label in [
            ("settings", "\u2699", "Settings"),
            ("bantuan", "\u2753", "Help Center"),
        ]:
            btn = ctk.CTkButton(
                bottom_frame, text=f"  {icon}  {label}",
                anchor="w", height=32, corner_radius=8,
                fg_color="transparent", text_color=TEXT_MUTED,
                hover_color=BTN_PALE, font=ctk.CTkFont(size=12),
                command=lambda k=key: self._navigate(k),
            )
            btn.pack(fill="x", padx=12, pady=1)
            self.nav_buttons[key] = btn

        # Beaply Pro card (pack side=bottom, above settings/help)
        pro_card = ctk.CTkFrame(self.sidebar, fg_color="#E8F0EA",
                                corner_radius=14)
        pro_card.pack(side="bottom", fill="x", padx=10, pady=(0, 8))
        ctk.CTkLabel(pro_card, text="Upgrade to",
                     font=ctk.CTkFont(size=9), text_color=TEXT_MUTED).pack(pady=(8, 0))
        ctk.CTkLabel(pro_card, text="Beaply Pro",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=SIDEBAR_ACTIVE_TX).pack()
        ctk.CTkLabel(pro_card, text="Unlock premium features\nand scholarship matches\ntailored just for you.",
                     font=ctk.CTkFont(size=8), text_color=TEXT_MUTED,
                     justify="center").pack(padx=6, pady=(2, 4))
        ctk.CTkButton(pro_card, text="Upgrade Now >", height=26,
                      fg_color=BTN_PRIMARY, hover_color=BTN_PRIMARY_HOVER,
                      text_color=TEXT_DARK, corner_radius=8,
                      font=ctk.CTkFont(size=10, weight="bold")).pack(
            fill="x", padx=10, pady=(0, 8))

        # Logo (top, packed normally)
        logo_f = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_f.pack(pady=(16, 16), padx=16)
        try:
            from PIL import Image
            import os
            logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "assets", "logo_beaply.png"))
            img = ctk.CTkImage(light_image=Image.open(logo_path), size=(110, 55))
            ctk.CTkLabel(logo_f, text="", image=img).pack()
        except Exception as e:
            print("Logo Error:", e)
            ctk.CTkLabel(logo_f, text="beaply",
                         font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
                         text_color=TEXT_ACCENT).pack()

        # Nav items (packed top-down, fill remaining space)
        nav_items = [
            ("dashboard",    "\ud83c\udfe0", "Dashboard"),
            ("eksplorasi",   "\ud83d\udcda", "Scholarships"),
            ("rekomendasi",  "\u2728", "Recommendations"),
            ("bookmarks",    "\ud83d\udd16", "Bookmarks"),
            ("kalender",     "\ud83d\udcc5", "Calendar"),
            ("notifikasi",   "\ud83d\udd14", "Notifications"),
            ("profil",       "\ud83d\udc64", "Profile"),
        ]

        for nav_key, icon, label in nav_items:
            btn = ctk.CTkButton(
                self.sidebar, text=f"  {icon}  {label}",
                anchor="w", height=34, corner_radius=10,
                fg_color="transparent",
                text_color=TEXT_DARK,
                hover_color=BTN_PALE,
                font=ctk.CTkFont(size=12),
                command=lambda k=nav_key: self._navigate(k),
            )
            btn.pack(fill="x", padx=12, pady=1)
            self.nav_buttons[nav_key] = btn


        # ══════ RIGHT AREA (Top bar + Content) ══════
        right_area = ctk.CTkFrame(self, fg_color="transparent")
        right_area.pack(side="right", fill="both", expand=True)

        # ── Top Bar ──
        self.topbar = ctk.CTkFrame(right_area, fg_color="transparent", height=56)
        self.topbar.pack(fill="x", padx=20, pady=(12, 8))
        self.topbar.pack_propagate(False)

        self.page_title = ctk.CTkLabel(
            self.topbar, text="Dashboard",
            font=ctk.CTkFont(size=22, weight="bold"), text_color=TEXT_DARK)
        self.page_title.pack(side="left")

        # User info (right side of topbar)
        user_frame = ctk.CTkFrame(self.topbar, fg_color="transparent")
        user_frame.pack(side="right")
        
        # Avatar
        try:
            from PIL import Image
            ava_img = ctk.CTkImage(light_image=Image.open("assets/default_avatar.png"), size=(40, 40))
            ctk.CTkLabel(user_frame, text="", image=ava_img).pack(side="left", padx=(0, 8))
        except:
            ctk.CTkLabel(user_frame, text="👤", font=ctk.CTkFont(size=24)).pack(side="left", padx=(0, 8))
            
        # Details Stack
        user_text = ctk.CTkFrame(user_frame, fg_color="transparent")
        user_text.pack(side="left")
        
        nama = self.user_profile.get("nama", t("guest_name", bhs))
        ctk.CTkLabel(user_text, text=nama,
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_DARK).pack(anchor="w")
        ctk.CTkLabel(user_text, text="Student",
                     font=ctk.CTkFont(size=11), text_color=TEXT_MUTED).pack(anchor="w")

        # Bell icon
        bell_btn = ctk.CTkButton(self.topbar, text="🔔", width=36, height=36,
                                 fg_color="transparent", text_color=TEXT_DARK,
                                 hover_color=BTN_PALE, corner_radius=18,
                                 font=ctk.CTkFont(size=16),
                                 command=lambda: self._navigate("notifikasi"))
        bell_btn.pack(side="right", padx=(0, 12))

        # ── Content Area ──
        self.content = ctk.CTkFrame(right_area, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=20, pady=(0, 12))

    def _navigate(self, key):
        self._current_nav = key

        # Update page title
        titles = {
            "dashboard": "Dashboard", "eksplorasi": "Scholarships",
            "rekomendasi": "Recommendations", "bookmarks": "Bookmarks",
            "kalender": "Calendar", "notifikasi": "Notifications",
            "profil": "Profile", "tracker": "Tracker",
            "bantuan": "FAQ & Help Center", "settings": "Settings",
        }
        self.page_title.configure(text=titles.get(key, key.title()))

        # Update sidebar highlight
        for nav_key, btn in self.nav_buttons.items():
            if nav_key == key:
                btn.configure(fg_color=SIDEBAR_ACTIVE_BG,
                              text_color=SIDEBAR_ACTIVE_TX)
            else:
                btn.configure(fg_color="transparent",
                              text_color=TEXT_DARK)

        # Clear content
        for w in self.content.winfo_children():
            w.destroy()

        bhs = self._bhs

        if key == "dashboard":
            HalamanDashboardUtama(self.content, self.profil_id, bhs,
                                  navigate_cb=self._navigate).pack(
                fill="both", expand=True)
        elif key == "eksplorasi":
            HalamanEksplorasi(self.content, self.profil_id, bhs).pack(
                fill="both", expand=True)
        elif key == "rekomendasi":
            HalamanRekomendasi(self.content, profil_id=self.profil_id).pack(
                fill="both", expand=True)
        elif key == "bookmarks":
            HalamanBookmarks(self.content, self.profil_id, bhs).pack(
                fill="both", expand=True)
        elif key == "tracker":
            HalamanTracker(self.content, self.profil_id, bhs).pack(
                fill="both", expand=True)
        elif key == "kalender":
            HalamanKalender(self.content, self.profil_id, bhs).pack(
                fill="both", expand=True)
        elif key == "notifikasi":
            HalamanNotifikasi(self.content, self.profil_id, bhs).pack(
                fill="both", expand=True)
        elif key == "profil":
            HalamanProfil(self.content, self.profil_id, bhs).pack(
                fill="both", expand=True)
        elif key == "bantuan":
            HalamanHelpCenter(self.content, profil_id=self.profil_id).pack(
                fill="both", expand=True)
        elif key == "settings":
            HalamanSettings(self.content, self.profil_id, self._bhs,
                            logout_cb=self._refresh_all).pack(
                fill="both", expand=True)

    def _refresh_all(self):
        pref = ambil_preferensi(self.profil_id)
        apply_pref(pref)
        self._bhs = pref.get("bahasa", "id")
        for w in self.winfo_children():
            w.destroy()
        self._build()
        self._navigate(self._current_nav)

class BeaplyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Beaply — Insight Beasiswa")
        self.geometry("960x720")
        self.minsize(860, 600)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self._current_user = None
        # Log Tkinter callback errors
        self.report_callback_exception = self._on_tk_error
        self._go_auth()

    def _on_tk_error(self, exc_type, exc_value, exc_tb):
        err = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
        logging.error(err)
        print(err, file=sys.stderr)


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
        pref = ambil_preferensi(PROFIL_AKTIF_ID)
        apply_pref(pref)
        LayoutDenganSidebar(self, PROFIL_AKTIF_ID,
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