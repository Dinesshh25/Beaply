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

    data_lengkap = {**data_wajib, **data_spesifik, "user_id": user_id}
    return simpan_profil_db(data_lengkap)


# ─────────────────────────────────────────────────────────────
# tampil_profil()  →  dipakai GUI untuk render data
# ─────────────────────────────────────────────────────────────

def tampil_profil(profil_id: int) -> dict | None:
    """Ambil satu profil dari DB, siap ditampilkan di GUI."""
    return ambil_profil_db(profil_id)


def tampil_semua_profil() -> list[dict]:
    return ambil_semua_profil_db()


# ─────────────────────────────────────────────────────────────
# filter_beasiswa()
# ─────────────────────────────────────────────────────────────

BEASISWA_DB = [
    {
        "nama": "Beasiswa KIP-Kuliah",
        "syarat": lambda p: p.get("status_kip") == 1,
        "deskripsi": "Beasiswa pemerintah untuk mahasiswa penerima KIP.",
        "jenjang": ["S1"],
    },
    {
        "nama": "Beasiswa Prestasi Akademik",
        "syarat": lambda p: float(p.get("ip", 0)) >= 3.5,
        "deskripsi": "Untuk mahasiswa dengan IP ≥ 3.50.",
        "jenjang": ["S1", "S2", "S3"],
    },
    {
        "nama": "Beasiswa LPDP",
        "syarat": lambda p: p.get("jenjang") in ("S2", "S3") and float(p.get("ip", 0)) >= 3.0,
        "deskripsi": "Beasiswa S2/S3 dari Lembaga Pengelola Dana Pendidikan.",
        "jenjang": ["S2", "S3"],
    },
    {
        "nama": "Beasiswa IELTS Internasional",
        "syarat": lambda p: p.get("skor_ielts") and float(p.get("skor_ielts", 0)) >= 6.5,
        "deskripsi": "Untuk mahasiswa dengan skor IELTS ≥ 6.5.",
        "jenjang": ["S1", "S2", "S3"],
    },
    {
        "nama": "Beasiswa TOEFL Internasional",
        "syarat": lambda p: p.get("skor_toefl") and int(p.get("skor_toefl", 0)) >= 90,
        "deskripsi": "Untuk mahasiswa dengan skor TOEFL iBT ≥ 90.",
        "jenjang": ["S1", "S2", "S3"],
    },
    {
        "nama": "Beasiswa Duolingo English",
        "syarat": lambda p: p.get("skor_duolingo") and int(p.get("skor_duolingo", 0)) >= 110,
        "deskripsi": "Untuk mahasiswa dengan skor Duolingo ≥ 110.",
        "jenjang": ["S1", "S2"],
    },
    {
        "nama": "Beasiswa SAT Amerika",
        "syarat": lambda p: p.get("skor_sat") and int(p.get("skor_sat", 0)) >= 1300 and p.get("jenjang") == "S1",
        "deskripsi": "Untuk mahasiswa S1 dengan SAT ≥ 1300.",
        "jenjang": ["S1"],
    },
    {
        "nama": "Beasiswa GRE/GMAT Pascasarjana",
        "syarat": lambda p: (
            (p.get("skor_gre") and int(p.get("skor_gre", 0)) >= 310) or
            (p.get("skor_gmat") and int(p.get("skor_gmat", 0)) >= 650)
        ) and p.get("jenjang") in ("S2", "S3"),
        "deskripsi": "Untuk mahasiswa S2/S3 dengan GRE ≥ 310 atau GMAT ≥ 650.",
        "jenjang": ["S2", "S3"],
    },
    {
        "nama": "Beasiswa Bahasa Mandarin (HSK)",
        "syarat": lambda p: p.get("skor_hsk") and int(p.get("skor_hsk", 0)) >= 4,
        "deskripsi": "Untuk mahasiswa dengan sertifikat HSK level 4–6.",
        "jenjang": ["S1", "S2", "S3"],
    },
    {
        "nama": "Beasiswa Bahasa Jepang (JLPT)",
        "syarat": lambda p: p.get("level_jlpt") and p.get("level_jlpt") in ("N1", "N2", "N3"),
        "deskripsi": "Untuk mahasiswa dengan JLPT N1–N3.",
        "jenjang": ["S1", "S2", "S3"],
    },
]


def filter_beasiswa(data_profil: dict) -> list[dict]:
    """
    Saring beasiswa yang sesuai dengan profil mahasiswa.
    Return: list of dict beasiswa yang lolos syarat.
    """
    hasil = []
    for b in BEASISWA_DB:
        try:
            if b["syarat"](data_profil):
                hasil.append({
                    "nama": b["nama"],
                    "deskripsi": b["deskripsi"],
                    "jenjang": ", ".join(b["jenjang"]),
                })
        except Exception:
            pass
    return hasil