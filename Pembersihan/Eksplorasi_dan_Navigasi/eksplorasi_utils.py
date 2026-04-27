"""
eksplorasi_utils.py
Beaply - Utilitas untuk Eksplorasi Data & Navigasi

Modul:
  - normalisasi_keyword    — Bersihkan keyword pencarian
  - validasi_filter        — Validasi kriteria filter
  - format_beasiswa        — Format data beasiswa untuk display
"""

from datetime import datetime


# ════════════════════════════════════════════════════════════
# NORMALISASI
# ════════════════════════════════════════════════════════════

def normalisasi_keyword(keyword: str) -> str:
    """Bersihkan dan normalisasi keyword pencarian."""
    if not keyword:
        return ""
    return keyword.strip().lower()


# ════════════════════════════════════════════════════════════
# VALIDASI FILTER
# ════════════════════════════════════════════════════════════

KATEGORI_VALID = ("pemerintah", "swasta", "internasional")
JENJANG_VALID = ("S1", "S2", "S3")
SORT_VALID = ("nama_asc", "nama_desc", "deadline_asc", "deadline_desc",
              "ipk_asc", "ipk_desc")


def validasi_filter(kriteria: dict) -> tuple:
    """
    Validasi kriteria filter.
    Return: (valid, pesan)
    """
    kategori = kriteria.get("kategori")
    if kategori and kategori not in KATEGORI_VALID:
        return False, f"Kategori harus: {', '.join(KATEGORI_VALID)}"

    jenjang = kriteria.get("jenjang")
    if jenjang and jenjang not in JENJANG_VALID:
        return False, f"Jenjang harus: {', '.join(JENJANG_VALID)}"

    ipk_min = kriteria.get("ipk_min")
    if ipk_min is not None:
        try:
            val = float(ipk_min)
            if val < 0 or val > 4.0:
                return False, "IPK min harus 0.00 - 4.00"
        except (ValueError, TypeError):
            return False, "IPK min harus berupa angka."

    return True, ""


# ════════════════════════════════════════════════════════════
# FORMAT DATA
# ════════════════════════════════════════════════════════════

KATEGORI_LABEL = {
    "id": {"pemerintah": "🏛 Pemerintah", "swasta": "🏢 Swasta",
           "internasional": "🌍 Internasional"},
    "en": {"pemerintah": "🏛 Government", "swasta": "🏢 Private",
           "internasional": "🌍 International"},
}

KATEGORI_COLOR = {
    "pemerintah": "#3B82F6",
    "swasta": "#8B5CF6",
    "internasional": "#10B981",
}


def format_kategori(kategori: str, bhs: str = "id") -> str:
    """Label kategori dengan emoji."""
    return KATEGORI_LABEL.get(bhs, KATEGORI_LABEL["id"]).get(kategori, kategori)


def warna_kategori(kategori: str) -> str:
    """Warna hex untuk kategori."""
    return KATEGORI_COLOR.get(kategori, "#6B7280")


def format_deadline_beasiswa(deadline_str: str) -> str:
    """Format deadline beasiswa untuk display."""
    if not deadline_str:
        return "Tidak ada deadline"

    bulan_id = ["", "Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
                "Jul", "Ags", "Sep", "Okt", "Nov", "Des"]
    try:
        d = datetime.strptime(deadline_str, "%Y-%m-%d")
        now = datetime.now()
        selisih = (d.date() - now.date()).days

        tgl = f"{d.day} {bulan_id[d.month]} {d.year}"
        if selisih < 0:
            return f"{tgl} (Ditutup)"
        elif selisih <= 7:
            return f"{tgl} (⚠ {selisih} hari lagi)"
        elif selisih <= 30:
            return f"{tgl} ({selisih} hari lagi)"
        else:
            return tgl
    except ValueError:
        return deadline_str


def format_syarat_singkat(beasiswa: dict) -> str:
    """Rangkum syarat dalam satu baris."""
    parts = []
    if beasiswa.get("syarat_ipk") and beasiswa["syarat_ipk"] > 0:
        parts.append(f"IPK ≥ {beasiswa['syarat_ipk']:.1f}")
    if beasiswa.get("syarat_toefl") and beasiswa["syarat_toefl"] > 0:
        parts.append(f"TOEFL ≥ {beasiswa['syarat_toefl']}")
    if beasiswa.get("syarat_ielts") and beasiswa["syarat_ielts"] > 0:
        parts.append(f"IELTS ≥ {beasiswa['syarat_ielts']:.1f}")
    return " • ".join(parts) if parts else "Tidak ada syarat khusus"
