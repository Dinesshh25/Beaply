"""
controllers/eksplorasi_controller.py
Beaply - Controller: Eksplorasi & Navigasi Beasiswa

Mediator antara View (gui_eksplorasi) dan Model (beasiswa_model).
"""

from models.beasiswa_model import (
    ambil_semua_beasiswa, cari_beasiswa, ambil_beasiswa_by_id,
    ambil_nama_beasiswa_list,
    toggle_bookmark, ambil_bookmark, is_bookmarked,
    validasi_filter, normalisasi_keyword,
    format_kategori, warna_kategori, format_deadline_beasiswa,
    format_syarat_singkat,
    KATEGORI_VALID, JENJANG_VALID, SORT_VALID,
)


# Jenjang yang valid untuk perguruan tinggi (user-facing)
_JENJANG_PT = {"D3", "D4", "S1", "S2", "S3"}


def _parse_jenjang(jenjang_str: str) -> list:
    """Parse jenjang string dari kedua format database:
    - Comma-separated: 'S1, S2, D3'
    - JSON array: '["S1", "D3", "D4"]'
    """
    if not jenjang_str:
        return []
    s = jenjang_str.strip()
    # Handle JSON array format
    if s.startswith("["):
        import json
        try:
            parsed = json.loads(s)
            if isinstance(parsed, list):
                return [str(p).strip().upper() for p in parsed]
        except (json.JSONDecodeError, ValueError):
            pass
    # Fallback: comma/slash separated
    return [p.strip().upper() for p in s.replace("/", ",").split(",") if p.strip()]


def _is_perguruan_tinggi(jenjang_str: str) -> bool:
    """Check if jenjang contains at least one perguruan tinggi level."""
    parts = _parse_jenjang(jenjang_str)
    if not parts:
        return False
    return any(p in _JENJANG_PT for p in parts)


def get_semua_beasiswa() -> list:
    """Ambil semua beasiswa perguruan tinggi untuk ditampilkan ke user."""
    all_bea = ambil_semua_beasiswa()
    # Filter: hanya tampilkan jenjang perguruan tinggi (D3/D4/S1/S2/S3)
    return [b for b in all_bea if _is_perguruan_tinggi(b.get("jenjang", ""))]


def search_beasiswa(keyword: str) -> list:
    """Cari beasiswa berdasarkan keyword."""
    keyword = normalisasi_keyword(keyword)
    if not keyword:
        return ambil_semua_beasiswa()
    return cari_beasiswa(keyword)


def get_beasiswa_detail(beasiswa_id: int) -> dict | None:
    """Ambil detail beasiswa."""
    return ambil_beasiswa_by_id(beasiswa_id)


def get_nama_beasiswa_list() -> list:
    """Ambil daftar nama beasiswa (untuk autocomplete)."""
    return ambil_nama_beasiswa_list()


def toggle_bookmark_beasiswa(profil_id: int, beasiswa_id: int) -> tuple:
    """Toggle bookmark beasiswa."""
    return toggle_bookmark(profil_id, beasiswa_id)


def get_bookmarks(profil_id: int) -> list:
    """Ambil semua bookmark user."""
    return ambil_bookmark(profil_id)


def check_bookmarked(profil_id: int, beasiswa_id: int) -> bool:
    """Cek apakah beasiswa sudah di-bookmark."""
    return is_bookmarked(profil_id, beasiswa_id)


def filter_beasiswa(beasiswa_list: list, kriteria: dict) -> list:
    """
    Filter daftar beasiswa berdasarkan kriteria.
    kriteria: {kategori, jenjang, ipk_min, sort}
    """
    ok, msg = validasi_filter(kriteria)
    if not ok:
        return beasiswa_list

    result = beasiswa_list

    kategori = kriteria.get("kategori")
    if kategori:
        result = [b for b in result if b.get("kategori") == kategori]

    jenjang = kriteria.get("jenjang")
    if jenjang:
        result = [b for b in result if jenjang in str(b.get("jenjang", ""))]

    ipk_min = kriteria.get("ipk_min")
    if ipk_min is not None:
        try:
            ipk_val = float(ipk_min)
            result = [b for b in result
                      if b.get("syarat_ipk", 0) <= ipk_val or b.get("syarat_ipk", 0) == 0]
        except (ValueError, TypeError):
            pass

    sort_by = kriteria.get("sort", "nama_asc")
    if sort_by == "nama_asc":
        result.sort(key=lambda b: b.get("nama", "").lower())
    elif sort_by == "nama_desc":
        result.sort(key=lambda b: b.get("nama", "").lower(), reverse=True)
    elif sort_by == "deadline_asc":
        result.sort(key=lambda b: b.get("deadline") or "9999")
    elif sort_by == "deadline_desc":
        result.sort(key=lambda b: b.get("deadline") or "0000", reverse=True)
    elif sort_by == "ipk_asc":
        result.sort(key=lambda b: b.get("syarat_ipk", 0))
    elif sort_by == "ipk_desc":
        result.sort(key=lambda b: b.get("syarat_ipk", 0), reverse=True)

    return result


# Re-export format helpers for views
def fmt_kategori(kategori: str, bhs: str = "id") -> str:
    return format_kategori(kategori, bhs)


def clr_kategori(kategori: str) -> str:
    return warna_kategori(kategori)


def fmt_deadline(deadline_str: str) -> str:
    return format_deadline_beasiswa(deadline_str)


def fmt_syarat(beasiswa: dict) -> str:
    return format_syarat_singkat(beasiswa)
