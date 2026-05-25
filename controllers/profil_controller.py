"""
controllers/profil_controller.py  (diperluas)
Beaply - Controller: Manajemen Profil & Preferensi

Dipindahkan dari: Profile_dan_Setting/profile.py + settings.py
"""

from utils import (
    validasi_data_wajib,
    validasi_data_spesifik,
    validasi_edit_profil,
    parse_int_or_none,
    parse_float_or_none,
)
from database import (
    simpan_profil_db,
    ambil_profil_db,
    ambil_semua_profil_db,
    update_profil_db,
    hapus_profil_db,
    ambil_preferensi_db,
    simpan_preferensi_db,
    ganti_password_db,
)

import logging
logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════
# PROFIL
# ════════════════════════════════════════════════════════════

def input_data_wajib(nama, tanggal_lahir, email, jurusan, kampus,
                     semester, ip, jenjang, jenis_kelamin,
                     aktif_organisasi=False) -> dict:
    """Kumpulkan input data wajib dari GUI menjadi satu dict."""
    return {
        "nama":              nama.strip(),
        "tanggal_lahir":     tanggal_lahir.strip(),
        "email":             email.strip().lower(),
        "jurusan":           jurusan.strip(),
        "kampus":            kampus.strip(),
        "semester":          parse_int_or_none(semester),
        "ip":                parse_float_or_none(ip),
        "jenjang":           jenjang.strip(),
        "jenis_kelamin":     jenis_kelamin.strip(),
        "aktif_organisasi":  int(bool(aktif_organisasi)),
    }


def input_data_spesifik(status_kip, skor_ielts="", skor_toefl="",
                         skor_duolingo="", skor_sat="", skor_act="",
                         skor_gre="", skor_gmat="", skor_hsk="",
                         level_jlpt="") -> dict:
    """Kumpulkan input data spesifik dari GUI menjadi satu dict."""
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


def simpan_profil(data_wajib: dict, data_spesifik: dict,
                  user_id=None) -> tuple:
    """Validasi keduanya, lalu simpan ke DB. Return: (sukses, pesan, id_profil)"""
    ok, msg = validasi_data_wajib(data_wajib)
    if not ok:
        return False, msg, -1
    ok, msg = validasi_data_spesifik(data_spesifik)
    if not ok:
        return False, msg, -1
    data_lengkap = {**data_wajib, **data_spesifik}
    data_lengkap["user_id"] = user_id
    return simpan_profil_db(data_lengkap)


def tampil_profil(profil_id: int) -> dict | None:
    """Ambil satu profil dari DB, siap ditampilkan di GUI."""
    return ambil_profil_db(profil_id)


def tampil_semua_profil(user_id=None) -> list:
    return ambil_semua_profil_db(user_id)


def edit_profil(id_profil, nama, tanggal_lahir, email, jurusan, kampus,
                semester, ip, jenjang, jenis_kelamin, status_kip=False,
                aktif_organisasi=False,
                skor_ielts="", skor_toefl="", skor_duolingo="",
                skor_sat="", skor_act="", skor_gre="", skor_gmat="",
                skor_hsk="", level_jlpt="") -> dict:
    """Kumpulkan data baru dari GUI menjadi satu dict siap validasi."""
    return {
        "id_profil":         id_profil,
        "nama":              nama.strip(),
        "tanggal_lahir":     tanggal_lahir.strip(),
        "email":             email.strip().lower(),
        "jurusan":           jurusan.strip(),
        "kampus":            kampus.strip(),
        "semester":          parse_int_or_none(semester),
        "ip":                parse_float_or_none(ip),
        "jenjang":           jenjang.strip(),
        "jenis_kelamin":     jenis_kelamin.strip(),
        "status_kip":        int(status_kip),
        "aktif_organisasi":  int(bool(aktif_organisasi)),
        "skor_ielts":        parse_float_or_none(skor_ielts),
        "skor_toefl":        parse_int_or_none(skor_toefl),
        "skor_duolingo":     parse_int_or_none(skor_duolingo),
        "skor_sat":          parse_int_or_none(skor_sat),
        "skor_act":          parse_int_or_none(skor_act),
        "skor_gre":          parse_int_or_none(skor_gre),
        "skor_gmat":         parse_int_or_none(skor_gmat),
        "skor_hsk":          parse_int_or_none(skor_hsk),
        "level_jlpt":        level_jlpt.strip().upper() if level_jlpt.strip() else None,
    }


def simpan_edit_profil(data_baru: dict) -> tuple:
    """Validasi lalu simpan perubahan profil ke DB."""
    ok, msg = validasi_edit_profil(data_baru)
    if not ok:
        return False, msg
    id_profil = data_baru.pop("id_profil")
    return update_profil_db(id_profil, data_baru)


def hapus_akun(id_profil: int, konfirmasi: bool) -> tuple:
    """Hapus akun hanya jika konfirmasi = True."""
    if not konfirmasi:
        return False, "Penghapusan dibatalkan."
    return hapus_profil_db(id_profil)


def simpan_data_opsional(profil_id: int, updates: dict) -> tuple:
    """
    Simpan data opsional profil (skor tes bahasa, dll).
    Dipanggil dari views/profil_view.py — controller yang akses DB, bukan view.
    """
    if not updates:
        return True, "Tidak ada perubahan."
    from models.database import get_connection
    try:
        conn = get_connection()
        cur  = conn.cursor()
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        vals = list(updates.values()) + [profil_id]
        cur.execute(f"UPDATE profil SET {set_clause} WHERE id = ?", vals)
        conn.commit()
        conn.close()
        return True, "Data opsional berhasil disimpan."
    except Exception as e:
        logger.error("simpan_data_opsional gagal (profil_id=%s): %s", profil_id, e)
        return False, str(e)


# ════════════════════════════════════════════════════════════
# PREFERENSI / SETTINGS
# ════════════════════════════════════════════════════════════

def ambil_preferensi(id_profil: int) -> dict:
    return ambil_preferensi_db(id_profil)


def simpan_preferensi(id_profil: int, tema: str,
                      ukuran_teks: str, bahasa: str) -> tuple:
    """Validasi lalu simpan preferensi tampilan."""
    if tema not in ("light", "dark", "system"):
        return False, "Tema tidak valid."
    if ukuran_teks not in ("small", "medium", "large"):
        return False, "Ukuran teks tidak valid."
    if bahasa not in ("id", "en"):
        return False, "Bahasa tidak valid."
    preferensi = {"tema": tema, "ukuran_teks": ukuran_teks, "bahasa": bahasa}
    return simpan_preferensi_db(id_profil, preferensi)


def ganti_password(id_profil: int, new_pass: str) -> tuple:
    """Validasi dan ganti password."""
    if len(new_pass) < 6:
        return False, "Password baru minimal 6 karakter."
    return ganti_password_db(id_profil, new_pass)
