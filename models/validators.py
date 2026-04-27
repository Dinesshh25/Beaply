"""
models/validators.py
Beaply - Validasi Data & Fungsi Bantu Parsing

Dipindahkan dari utils.py agar menjadi bagian Model layer.
"""

import re
from datetime import datetime


# ─────────────────────────────────────────────────────────────
# Validasi data WAJIB
# ─────────────────────────────────────────────────────────────

BATAS_SEMESTER = {
    "D3": 10,
    "D4": 14,
    "S1": 14,
    "S2": 8,
    "S3": 14,
}

def validasi_data_wajib(data: dict) -> tuple[bool, str]:
    """
    Validasi semua field wajib mahasiswa.
    Return: (valid: bool, pesan_error: str)
    """
    nama = str(data.get("nama", "")).strip()
    if not nama:
        return False, "Nama tidak boleh kosong."
    if len(nama) < 2:
        return False, "Nama minimal 2 karakter."

    tgl = str(data.get("tanggal_lahir", "")).strip()
    if not tgl:
        return False, "Tanggal lahir tidak boleh kosong."
    try:
        datetime.strptime(tgl, "%Y-%m-%d")
    except ValueError:
        return False, "Format tanggal lahir harus YYYY-MM-DD."

    email = str(data.get("email", "")).strip()
    if not email:
        return False, "Email tidak boleh kosong."
    if not re.match(r"^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$", email):
        return False, "Format email tidak valid."

    jurusan = str(data.get("jurusan", "")).strip()
    if not jurusan:
        return False, "Jurusan tidak boleh kosong."

    kampus = str(data.get("kampus", "")).strip()
    if not kampus:
        return False, "Nama kampus tidak boleh kosong."

    jenjang = str(data.get("jenjang", "")).strip()
    if jenjang not in ("D3", "D4", "S1", "S2", "S3"):
        return False, "Jenjang harus D3, D4, S1, S2, atau S3."

    try:
        semester = int(data.get("semester", 0))
    except (ValueError, TypeError):
        return False, "Semester harus berupa angka."
    if semester < 1:
        return False, "Semester minimal 1."
    maks = BATAS_SEMESTER.get(jenjang, 14)
    if semester > maks:
        return False, f"Semester untuk {jenjang} maksimal {maks}."

    try:
        ip = float(data.get("ip", -1))
    except (ValueError, TypeError):
        return False, "IP harus berupa angka desimal."
    if not (0.0 <= ip <= 4.0):
        return False, "IP harus antara 0.00 hingga 4.00."

    jk = str(data.get("jenis_kelamin", "")).strip()
    if jk not in ("Laki-laki", "Perempuan"):
        return False, "Jenis kelamin harus Laki-laki atau Perempuan."

    return True, ""


# ─────────────────────────────────────────────────────────────
# Validasi data SPESIFIK
# ─────────────────────────────────────────────────────────────

RANGE_SKOR = {
    "skor_ielts":    (0.0,  9.0,  float),
    "skor_toefl":    (0,    120,   int),
    "skor_duolingo": (10,   160,   int),
    "skor_sat":      (400,  1600,  int),
    "skor_act":      (1,    36,    int),
    "skor_gre":      (260,  340,   int),
    "skor_gmat":     (200,  800,   int),
    "skor_hsk":      (1,    6,     int),
}

JLPT_VALID = {"N1", "N2", "N3", "N4", "N5"}

def validasi_data_spesifik(data: dict) -> tuple[bool, str]:
    """
    Validasi data spesifik (semua opsional — boleh None/kosong).
    Return: (valid: bool, pesan_error: str)
    """
    for field, (mn, mx, tipe) in RANGE_SKOR.items():
        val = data.get(field)
        if val is None or str(val).strip() == "":
            continue  # opsional, boleh kosong
        try:
            val = tipe(val)
        except (ValueError, TypeError):
            return False, f"{field} harus berupa angka."
        if not (mn <= val <= mx):
            return False, f"{field} harus antara {mn}–{mx}."

    jlpt = data.get("level_jlpt")
    if jlpt and str(jlpt).strip().upper() not in JLPT_VALID:
        return False, f"Level JLPT harus salah satu dari: {', '.join(sorted(JLPT_VALID))}."

    return True, ""


# ─────────────────────────────────────────────────────────────
# Validasi edit profil (sama seperti wajib+spesifik)
# ─────────────────────────────────────────────────────────────

def validasi_edit_profil(data: dict) -> tuple[bool, str]:
    ok, msg = validasi_data_wajib(data)
    if not ok:
        return False, msg
    return validasi_data_spesifik(data)


# ─────────────────────────────────────────────────────────────
# Fungsi bantu lain
# ─────────────────────────────────────────────────────────────

def parse_int_or_none(val):
    try:
        return int(val) if str(val).strip() != "" else None
    except (ValueError, TypeError):
        return None

def parse_float_or_none(val):
    try:
        return float(val) if str(val).strip() != "" else None
    except (ValueError, TypeError):
        return None

def format_tanggal(tgl_str: str) -> str:
    """Ubah '2002-05-14' → '14 Mei 2002'"""
    bulan = ["","Januari","Februari","Maret","April","Mei","Juni",
             "Juli","Agustus","September","Oktober","November","Desember"]
    try:
        d = datetime.strptime(tgl_str, "%Y-%m-%d")
        return f"{d.day} {bulan[d.month]} {d.year}"
    except:
        return tgl_str
