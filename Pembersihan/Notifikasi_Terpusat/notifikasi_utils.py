"""
notifikasi_utils.py
Beaply - Utilitas untuk Manajemen Notifikasi Terpusat

Modul:
  - format_waktu_relatif    — "2 jam lalu", "Kemarin", dll.
  - group_by_tanggal        — Kelompokkan notifikasi per tanggal
  - ikon_tipe_notif         — Ikon emoji berdasarkan tipe
"""

from datetime import datetime, timedelta


# ════════════════════════════════════════════════════════════
# FORMAT WAKTU RELATIF
# ════════════════════════════════════════════════════════════

def format_waktu_relatif(waktu_str: str, bhs: str = "id") -> str:
    """
    Format waktu menjadi relatif: '2 jam lalu', 'Kemarin', dll.

    Args:
        waktu_str: datetime string (YYYY-MM-DD HH:MM:SS)
        bhs: bahasa (id/en)
    """
    try:
        waktu = datetime.strptime(waktu_str, "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        try:
            waktu = datetime.strptime(waktu_str, "%Y-%m-%d")
        except (ValueError, TypeError):
            return waktu_str

    now = datetime.now()
    delta = now - waktu

    if bhs == "en":
        if delta.total_seconds() < 60:
            return "Just now"
        elif delta.total_seconds() < 3600:
            menit = int(delta.total_seconds() / 60)
            return f"{menit} min ago"
        elif delta.total_seconds() < 86400:
            jam = int(delta.total_seconds() / 3600)
            return f"{jam} hour{'s' if jam > 1 else ''} ago"
        elif delta.days == 1:
            return "Yesterday"
        elif delta.days < 7:
            return f"{delta.days} days ago"
        else:
            return waktu.strftime("%d %b %Y")
    else:
        if delta.total_seconds() < 60:
            return "Baru saja"
        elif delta.total_seconds() < 3600:
            menit = int(delta.total_seconds() / 60)
            return f"{menit} menit lalu"
        elif delta.total_seconds() < 86400:
            jam = int(delta.total_seconds() / 3600)
            return f"{jam} jam lalu"
        elif delta.days == 1:
            return "Kemarin"
        elif delta.days < 7:
            return f"{delta.days} hari lalu"
        else:
            bulan_id = ["", "Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
                        "Jul", "Ags", "Sep", "Okt", "Nov", "Des"]
            return f"{waktu.day} {bulan_id[waktu.month]} {waktu.year}"


# ════════════════════════════════════════════════════════════
# GROUP BY TANGGAL
# ════════════════════════════════════════════════════════════

def group_by_tanggal(notifikasi_list: list, bhs: str = "id") -> list:
    """
    Kelompokkan notifikasi berdasarkan tanggal.

    Return: [
        {"tanggal": "Hari Ini", "items": [...]},
        {"tanggal": "Kemarin", "items": [...]},
        {"tanggal": "12 Apr 2026", "items": [...]},
    ]
    """
    if not notifikasi_list:
        return []

    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    groups = {}
    for n in notifikasi_list:
        waktu_str = n.get("dibuat_pada", "")
        try:
            tgl = datetime.strptime(waktu_str, "%Y-%m-%d %H:%M:%S").date()
        except (ValueError, TypeError):
            tgl = today

        if tgl == today:
            label = "Hari Ini" if bhs == "id" else "Today"
        elif tgl == yesterday:
            label = "Kemarin" if bhs == "id" else "Yesterday"
        else:
            bulan = ["", "Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
                     "Jul", "Ags", "Sep", "Okt", "Nov", "Des"]
            label = f"{tgl.day} {bulan[tgl.month]} {tgl.year}"

        if label not in groups:
            groups[label] = []
        groups[label].append(n)

    return [{"tanggal": k, "items": v} for k, v in groups.items()]


# ════════════════════════════════════════════════════════════
# IKON & WARNA TIPE NOTIFIKASI
# ════════════════════════════════════════════════════════════

TIPE_IKON = {
    "info":     "ℹ️",
    "deadline": "⏰",
    "status":   "📋",
    "sistem":   "🔔",
}

TIPE_WARNA = {
    "info":     "#3B82F6",
    "deadline": "#EAB308",
    "status":   "#10B981",
    "sistem":   "#8B5CF6",
}

TIPE_LABEL = {
    "id": {"info": "Informasi", "deadline": "Deadline", "status": "Status",
           "sistem": "Sistem"},
    "en": {"info": "Information", "deadline": "Deadline", "status": "Status",
           "sistem": "System"},
}


def ikon_tipe(tipe: str) -> str:
    """Ambil ikon emoji untuk tipe notifikasi."""
    return TIPE_IKON.get(tipe, "🔔")


def warna_tipe(tipe: str) -> str:
    """Ambil warna hex untuk tipe notifikasi."""
    return TIPE_WARNA.get(tipe, "#6B7280")


def label_tipe(tipe: str, bhs: str = "id") -> str:
    """Ambil label tipe notifikasi."""
    return TIPE_LABEL.get(bhs, TIPE_LABEL["id"]).get(tipe, tipe)
