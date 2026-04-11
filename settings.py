"""
settings.py
Beaply - Logika bisnis Fitur 2: Manajemen Profil & Preferensi (Settings)
Modul: edit_profil, validasi_edit_profil, simpan_edit_profil,
       konfirmasi_hapus, hapus_akun,
       ubah_tema, ubah_ukuran_teks, ubah_bahasa, simpan_preferensi
"""

from utils import validasi_edit_profil, parse_int_or_none, parse_float_or_none
from Beaply.database import (
    update_profil_db,
    hapus_profil_db,
    ambil_preferensi_db,
    simpan_preferensi_db,
)


# ─────────────────────────────────────────────────────────────
# edit_profil()
# ─────────────────────────────────────────────────────────────

def edit_profil(
    id_profil: int,
    nama: str,
    tanggal_lahir: str,
    email: str,
    jurusan: str,
    kampus: str,
    semester: str,
    ip: str,
    jenjang: str,
    jenis_kelamin: str,
    status_kip: bool  = False,
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
    Kumpulkan data baru dari GUI menjadi satu dict siap validasi.
    """
    return {
        "id_profil":     id_profil,
        "nama":          nama.strip(),
        "tanggal_lahir": tanggal_lahir.strip(),
        "email":         email.strip().lower(),
        "jurusan":       jurusan.strip(),
        "kampus":        kampus.strip(),
        "semester":      parse_int_or_none(semester),
        "ip":            parse_float_or_none(ip),
        "jenjang":       jenjang.strip(),
        "jenis_kelamin": jenis_kelamin.strip(),
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
# simpan_edit_profil()
# ─────────────────────────────────────────────────────────────

def simpan_edit_profil(data_baru: dict) -> tuple[bool, str]:
    """
    Validasi lalu simpan perubahan profil ke DB.
    Return: (sukses, pesan)
    """
    ok, msg = validasi_edit_profil(data_baru)
    if not ok:
        return False, msg
    id_profil = data_baru.pop("id_profil")
    return update_profil_db(id_profil, data_baru)


# ─────────────────────────────────────────────────────────────
# hapus_akun()
# ─────────────────────────────────────────────────────────────

def hapus_akun(id_profil: int, konfirmasi: bool) -> tuple[bool, str]:
    """
    Hapus akun hanya jika konfirmasi = True.
    Return: (sukses, pesan)
    """
    if not konfirmasi:
        return False, "Penghapusan dibatalkan."
    return hapus_profil_db(id_profil)


# ─────────────────────────────────────────────────────────────
# Preferensi: ubah_tema / ubah_ukuran_teks / ubah_bahasa
# ─────────────────────────────────────────────────────────────

def ubah_tema(tema: str) -> tuple[bool, str]:
    if tema not in ("light", "dark"):
        return False, "Tema harus 'light' atau 'dark'."
    return True, tema


def ubah_ukuran_teks(ukuran: str) -> tuple[bool, str]:
    if ukuran not in ("small", "medium", "large"):
        return False, "Ukuran teks harus 'small', 'medium', atau 'large'."
    return True, ukuran


def ubah_bahasa(kode_bahasa: str) -> tuple[bool, str]:
    if kode_bahasa not in ("id", "en"):
        return False, "Bahasa harus 'id' atau 'en'."
    return True, kode_bahasa


# ─────────────────────────────────────────────────────────────
# simpan_preferensi()
# ─────────────────────────────────────────────────────────────

def simpan_preferensi(
    id_profil: int,
    tema: str,
    ukuran_teks: str,
    bahasa: str,
) -> tuple[bool, str]:
    """
    Validasi lalu simpan preferensi tampilan.
    Return: (sukses, pesan)
    """
    ok, msg = ubah_tema(tema)
    if not ok:
        return False, msg

    ok, msg = ubah_ukuran_teks(ukuran_teks)
    if not ok:
        return False, msg

    ok, msg = ubah_bahasa(bahasa)
    if not ok:
        return False, msg

    preferensi = {"tema": tema, "ukuran_teks": ukuran_teks, "bahasa": bahasa}
    return simpan_preferensi_db(id_profil, preferensi)


def ambil_preferensi(id_profil: int) -> dict:
    return ambil_preferensi_db(id_profil)