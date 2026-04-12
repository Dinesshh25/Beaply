"""
eksplorasi.py
Beaply - Logika Bisnis Eksplorasi Data & Navigasi

Modul sesuai Structure Chart:
  1. tampilan_eksplorasi  — Siapkan data awal eksplorasi
  2. auto_complete        — Sugesti pencarian real-time
  3. proses_pencarian     — Pencarian by keyword
  4. terapkan_filter      — Filter hasil pencarian
  5. urutkan_data         — Sorting hasil
"""

from .eksplorasi_database import (
    ambil_semua_beasiswa,
    cari_beasiswa,
    ambil_beasiswa_by_id,
    ambil_nama_beasiswa_list,
    toggle_bookmark as db_toggle_bookmark,
    ambil_bookmark as db_ambil_bookmark,
    is_bookmarked as db_is_bookmarked,
)
from .eksplorasi_utils import (
    normalisasi_keyword,
    validasi_filter,
    format_kategori,
    warna_kategori,
    format_deadline_beasiswa,
    format_syarat_singkat,
    KATEGORI_VALID,
    JENJANG_VALID,
    SORT_VALID,
)


# ════════════════════════════════════════════════════════════
# 1. TAMPILAN EKSPLORASI
# ════════════════════════════════════════════════════════════

def tampilan_eksplorasi() -> dict:
    """
    Siapkan data awal untuk halaman eksplorasi.
    Return: {
        semua_beasiswa: list,
        total: int,
        kategori_list: list,
        jenjang_list: list,
        sort_list: list,
    }
    """
    semua = ambil_semua_beasiswa()
    return {
        "semua_beasiswa": semua,
        "total": len(semua),
        "kategori_list": list(KATEGORI_VALID),
        "jenjang_list": list(JENJANG_VALID),
        "sort_list": list(SORT_VALID),
    }


# ════════════════════════════════════════════════════════════
# 2. AUTO COMPLETE
# ════════════════════════════════════════════════════════════

def auto_complete(keyword_sementara: str) -> list:
    """
    Memberikan sugesti teks secara real-time saat pengguna mengetik.

    Args:
        keyword_sementara: teks yang sedang diketik

    Return: list_sugesti (max 8 item)
    """
    kw = normalisasi_keyword(keyword_sementara)
    if not kw or len(kw) < 2:
        return []

    semua_nama = ambil_nama_beasiswa_list()
    sugesti = [n for n in semua_nama if kw in n.lower()]
    return sugesti[:8]


# ════════════════════════════════════════════════════════════
# 3. PROSES PENCARIAN
# ════════════════════════════════════════════════════════════

def proses_pencarian(keyword: str) -> list:
    """
    Mengambil data beasiswa dari database berdasarkan keyword.

    Args:
        keyword: kata kunci pencarian

    Return: hasil_mentah (list[dict])
    """
    kw = normalisasi_keyword(keyword)
    if not kw:
        return ambil_semua_beasiswa()
    return cari_beasiswa(kw)


# ════════════════════════════════════════════════════════════
# 4. TERAPKAN FILTER
# ════════════════════════════════════════════════════════════

def terapkan_filter(hasil_mentah: list, kriteria_filter: dict) -> list:
    """
    Mengerucutkan hasil pencarian berdasarkan parameter.

    Args:
        hasil_mentah: list data beasiswa
        kriteria_filter: {
            kategori: str (opsional),
            jenjang: str (opsional),
            ipk_min: float (opsional),
            hanya_aktif: bool (opsional) — hanya deadline belum lewat
        }

    Return: hasil_terfilter (list[dict])
    """
    ok, msg = validasi_filter(kriteria_filter)
    if not ok:
        return hasil_mentah  # kembalikan apa adanya jika filter invalid

    hasil = hasil_mentah[:]

    # Filter by kategori
    kat = kriteria_filter.get("kategori")
    if kat and kat != "semua":
        hasil = [b for b in hasil if b.get("kategori") == kat]

    # Filter by jenjang
    jenj = kriteria_filter.get("jenjang")
    if jenj and jenj != "semua":
        hasil = [b for b in hasil if jenj in b.get("jenjang", "")]

    # Filter by IPK minimum
    ipk = kriteria_filter.get("ipk_min")
    if ipk is not None and str(ipk).strip():
        try:
            ipk_val = float(ipk)
            hasil = [b for b in hasil
                     if b.get("syarat_ipk", 0) <= ipk_val or b.get("syarat_ipk", 0) == 0]
        except (ValueError, TypeError):
            pass

    # Filter hanya deadline belum lewat
    if kriteria_filter.get("hanya_aktif"):
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        hasil = [b for b in hasil
                 if not b.get("deadline") or b["deadline"] >= today]

    return hasil


# ════════════════════════════════════════════════════════════
# 5. URUTKAN DATA
# ════════════════════════════════════════════════════════════

def urutkan_data(hasil_terfilter: list, kriteria_sort: str = "nama_asc") -> list:
    """
    Melakukan penyortiran data berdasarkan kriteria.

    Args:
        hasil_terfilter: list data beasiswa
        kriteria_sort: salah satu dari SORT_VALID

    Return: data_final (list[dict])
    """
    data = hasil_terfilter[:]

    if kriteria_sort == "nama_asc":
        data.sort(key=lambda x: x.get("nama", "").lower())
    elif kriteria_sort == "nama_desc":
        data.sort(key=lambda x: x.get("nama", "").lower(), reverse=True)
    elif kriteria_sort == "deadline_asc":
        data.sort(key=lambda x: x.get("deadline") or "9999-12-31")
    elif kriteria_sort == "deadline_desc":
        data.sort(key=lambda x: x.get("deadline") or "0000-01-01", reverse=True)
    elif kriteria_sort == "ipk_asc":
        data.sort(key=lambda x: x.get("syarat_ipk", 0))
    elif kriteria_sort == "ipk_desc":
        data.sort(key=lambda x: x.get("syarat_ipk", 0), reverse=True)

    return data


# ════════════════════════════════════════════════════════════
# BOOKMARK (wrapper)
# ════════════════════════════════════════════════════════════

def toggle_bookmark_beasiswa(profil_id: int, beasiswa_id: int) -> tuple:
    """Toggle bookmark beasiswa. Return: (sukses, pesan, is_bookmarked)"""
    return db_toggle_bookmark(profil_id, beasiswa_id)


def ambil_bookmark_user(profil_id: int) -> list:
    """Ambil semua beasiswa yang di-bookmark."""
    return db_ambil_bookmark(profil_id)


def cek_bookmark(profil_id: int, beasiswa_id: int) -> bool:
    """Cek apakah beasiswa di-bookmark."""
    return db_is_bookmarked(profil_id, beasiswa_id)
