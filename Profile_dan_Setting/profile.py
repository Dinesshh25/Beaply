"""
profile.py
Beaply - Logika bisnis Fitur 1: Manajemen Profil Pribadi
Modul: tampilan_form_profil, input_data_wajib, validasi_data_wajib,
       input_data_spesifik, validasi_data_spesifik,
       simpan_profil, tampil_profil, filter_beasiswa
"""

from utils import (
    validasi_data_wajib,
    validasi_data_spesifik,
    parse_int_or_none,
    parse_float_or_none,
)
from database import (
    simpan_profil_db,
    ambil_profil_db,
    ambil_semua_profil_db,
)


# ─────────────────────────────────────────────────────────────
# input_data_wajib()
# ─────────────────────────────────────────────────────────────

def input_data_wajib(
    nama: str,
    tanggal_lahir: str,
    email: str,
    jurusan: str,
    kampus: str,
    semester: str,
    ip: str,
    jenjang: str,
    jenis_kelamin: str,
) -> dict:
    """
    Kumpulkan input data wajib dari GUI menjadi satu dict.
    Casting tipe dasar dilakukan di sini; validasi ada di validasi_data_wajib().
    """
    return {
        "nama":          nama.strip(),
        "tanggal_lahir": tanggal_lahir.strip(),
        "email":         email.strip().lower(),
        "jurusan":       jurusan.strip(),
        "kampus":        kampus.strip(),
        "semester":      parse_int_or_none(semester),
        "ip":            parse_float_or_none(ip),
        "jenjang":       jenjang.strip(),
        "jenis_kelamin": jenis_kelamin.strip(),
    }


# ─────────────────────────────────────────────────────────────
# input_data_spesifik()
# ─────────────────────────────────────────────────────────────

def input_data_spesifik(
    status_kip: bool,
    skor_ielts: str   = "",
    skor_toefl: str   = "",
    skor_duolingo: str= "",
    skor_sat: str     = "",
    skor_act: str     = "",
    skor_gre: str     = "",
    skor_gmat: str    = "",
    skor_hsk: str     = "",
    level_jlpt: str   = "",
) -> dict:
    """
    Kumpulkan input data spesifik dari GUI menjadi satu dict.
    Semua skor opsional; kosong → None.
    """
    return {
        "status_kip":    int(status_kip),
        "skor_ielts":    parse_float_or_none(skor_ielts),
        "skor_toefl":    parse_int_or_none(skor_toefl),
        "skor_duolingo": parse_int_or_none(skor_duolingo),
        "skor_sat":      parse_int_or_none(skor_sat),
        "skor_act":      parse_int_or_none(skor_act),
        "skor_gre":      parse_int_or_none(skor_gre),
        "skor_gmat":     parse_int_or_none(skor_gmat),
        "skor_hsk":      parse_int_or_none(skor_hsk),
        "level_jlpt":    level_jlpt.strip().upper() if level_jlpt.strip() else None,
    }


# ─────────────────────────────────────────────────────────────
# simpan_profil()
# ─────────────────────────────────────────────────────────────

def simpan_profil(data_wajib: dict, data_spesifik: dict, user_id: str = None) -> tuple[bool, str, int]:
    """
    Validasi keduanya, lalu simpan ke DB.
    Return: (sukses, pesan, id_profil)
    """
    ok, msg = validasi_data_wajib(data_wajib)
    if not ok:
        return False, msg, -1

    ok, msg = validasi_data_spesifik(data_spesifik)
    if not ok:
        return False, msg, -1

    data_lengkap = {**data_wajib, **data_spesifik}
    data_lengkap["user_id"] = user_id
    return simpan_profil_db(data_lengkap)


# ─────────────────────────────────────────────────────────────
# tampil_profil()  →  dipakai GUI untuk render data
# ─────────────────────────────────────────────────────────────

def tampil_profil(profil_id: int) -> dict | None:
    """Ambil satu profil dari DB, siap ditampilkan di GUI."""
    return ambil_profil_db(profil_id)


def tampil_semua_profil() -> list[dict]:
    return ambil_semua_profil_db()
    