"""
tracker_utils.py
Beaply - Utilitas untuk Tracker & Pengingat

Modul:
  - validasi_deadline       — Validasi format tanggal deadline
  - hitung_selisih_hari     — Hitung selisih hari dari sekarang
  - logika_warna_tanggal    — Tentukan warna berdasarkan jarak deadline
  - format_status           — Label status dalam bahasa Indonesia/Inggris
"""

from datetime import datetime, timedelta


# ════════════════════════════════════════════════════════════
# VALIDASI
# ════════════════════════════════════════════════════════════

def validasi_deadline(tanggal_str: str) -> tuple:
    """
    Validasi format deadline (YYYY-MM-DD).
    Return: (valid: bool, pesan: str)
    """
    if not tanggal_str or not tanggal_str.strip():
        return True, ""  # deadline opsional

    try:
        datetime.strptime(tanggal_str.strip(), "%Y-%m-%d")
        return True, ""
    except ValueError:
        return False, "Format deadline harus YYYY-MM-DD."


def validasi_tracker_input(nama: str, deadline: str = "") -> tuple:
    """
    Validasi input tracker baru.
    Return: (valid: bool, pesan: str)
    """
    if not nama or not nama.strip():
        return False, "Nama beasiswa tidak boleh kosong."

    if len(nama.strip()) < 3:
        return False, "Nama beasiswa minimal 3 karakter."

    ok, msg = validasi_deadline(deadline)
    if not ok:
        return False, msg

    return True, ""


# ════════════════════════════════════════════════════════════
# HITUNG SELISIH HARI
# ════════════════════════════════════════════════════════════

def hitung_selisih_hari(deadline_str: str) -> int | None:
    """
    Hitung selisih hari antara deadline dan hari ini.
    Positif = masih ada waktu, negatif = sudah lewat.
    Return: int atau None jika deadline kosong.
    """
    if not deadline_str or not deadline_str.strip():
        return None
    try:
        dl = datetime.strptime(deadline_str.strip(), "%Y-%m-%d").date()
        today = datetime.now().date()
        return (dl - today).days
    except ValueError:
        return None


# ════════════════════════════════════════════════════════════
# LOGIKA WARNA TANGGAL (untuk kalender)
# ════════════════════════════════════════════════════════════

def logika_warna_tanggal(deadline_str: str, dibookmark: bool = False) -> str:
    """
    Menentukan warna tanggal di kalender berdasarkan selisih hari.

    Aturan:
      - 🔵 Biru (#3B82F6)     : Di-bookmark
      - 🟢 Hijau (#22C55E)    : > 30 hari
      - 🟡 Kuning (#EAB308)   : ≤ 30 hari
      - 🔴 Merah (#EF4444)    : ≤ 15 hari
      - 🟤 Merah Tua (#991B1B): Sudah lewat

    Return: hex color string
    """
    if dibookmark:
        return "#3B82F6"  # biru

    selisih = hitung_selisih_hari(deadline_str)
    if selisih is None:
        return "#6B7280"  # abu-abu (default)

    if selisih < 0:
        return "#991B1B"  # merah tua — sudah lewat
    elif selisih <= 15:
        return "#EF4444"  # merah — darurat
    elif selisih <= 30:
        return "#EAB308"  # kuning — segera
    else:
        return "#22C55E"  # hijau — masih lama


# ════════════════════════════════════════════════════════════
# FORMAT STATUS
# ════════════════════════════════════════════════════════════

STATUS_LABEL = {
    "id": {
        "belum_mulai":   "Belum Mulai",
        "sedang_proses": "Sedang Proses",
        "terkirim":      "Terkirim",
        "diterima":      "Diterima ✅",
        "ditolak":       "Ditolak ❌",
    },
    "en": {
        "belum_mulai":   "Not Started",
        "sedang_proses": "In Progress",
        "terkirim":      "Submitted",
        "diterima":      "Accepted ✅",
        "ditolak":       "Rejected ❌",
    },
}

STATUS_COLOR = {
    "belum_mulai":   "#6B7280",
    "sedang_proses": "#3B82F6",
    "terkirim":      "#EAB308",
    "diterima":      "#22C55E",
    "ditolak":       "#EF4444",
}

STATUS_LIST = ["belum_mulai", "sedang_proses", "terkirim", "diterima", "ditolak"]


def format_status(status: str, bhs: str = "id") -> str:
    """Label status dalam bahasa yang dipilih."""
    return STATUS_LABEL.get(bhs, STATUS_LABEL["id"]).get(status, status)


def warna_status(status: str) -> str:
    """Warna hex untuk status."""
    return STATUS_COLOR.get(status, "#6B7280")


def format_deadline_display(deadline_str: str) -> str:
    """Format deadline untuk ditampilkan: '14 Mei 2026 (dalam 30 hari)'"""
    if not deadline_str or not deadline_str.strip():
        return "Tidak ada deadline"

    bulan_id = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
                "Juli", "Agustus", "September", "Oktober", "November", "Desember"]

    try:
        d = datetime.strptime(deadline_str.strip(), "%Y-%m-%d")
        tgl = f"{d.day} {bulan_id[d.month]} {d.year}"
        selisih = hitung_selisih_hari(deadline_str)
        if selisih is not None:
            if selisih < 0:
                tgl += f" (lewat {abs(selisih)} hari)"
            elif selisih == 0:
                tgl += " (HARI INI!)"
            elif selisih == 1:
                tgl += " (besok)"
            else:
                tgl += f" (dalam {selisih} hari)"
        return tgl
    except ValueError:
        return deadline_str
