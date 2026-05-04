"""
controllers/tracker_controller.py
Beaply - Controller: Tracker & Pengingat

Mediator antara View (gui_tracker) dan Model (tracker_model).
"""

import calendar
from datetime import datetime, timedelta

from models.tracker_model import (
    tambah_tracker, ambil_semua_tracker, ambil_tracker_by_id,
    update_status_tracker, update_tracker, hapus_tracker,
    update_bookmark_tracker, ambil_tracker_by_bulan,
    hitung_statistik_tracker, tambah_pengingat,
    ambil_pengingat_aktif, tandai_pengingat_tampil,
    validasi_tracker_input, logika_warna_tanggal,
    hitung_selisih_hari, format_status, warna_status,
    format_deadline_display, STATUS_LIST,
)


# ════════════════════════════════════════════════════════════
# 1. TAMPILAN KALENDER
# ════════════════════════════════════════════════════════════

def tampilan_kalender(profil_id: int, bulan: int = None,
                      tahun: int = None) -> dict:
    """
    Siapkan data untuk render kalender grid bulanan.
    """
    now = datetime.now()
    if bulan is None:
        bulan = now.month
    if tahun is None:
        tahun = now.year

    nama_bulan_id = [
        "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ]

    hari_pertama, total_hari = calendar.monthrange(tahun, bulan)
    tracker_list = ambil_tracker_by_bulan(profil_id, bulan, tahun)

    tgl_warna = {}
    tgl_tracker = {}
    for t in tracker_list:
        if t["deadline"]:
            try:
                d = datetime.strptime(t["deadline"], "%Y-%m-%d")
                day = d.day
                warna = logika_warna_tanggal(t["deadline"], bool(t["dibookmark"]))
                if day not in tgl_warna or _prioritas_warna(warna) > _prioritas_warna(tgl_warna[day]):
                    tgl_warna[day] = warna
                if day not in tgl_tracker:
                    tgl_tracker[day] = []
                tgl_tracker[day].append(t)
            except ValueError:
                pass

    return {
        "bulan": bulan,
        "tahun": tahun,
        "nama_bulan": nama_bulan_id[bulan],
        "hari_pertama": hari_pertama,
        "total_hari": total_hari,
        "tanggal_hari_ini": now.strftime("%Y-%m-%d"),
        "tracker_di_bulan": tracker_list,
        "tanggal_warna": tgl_warna,
        "tanggal_tracker": tgl_tracker,
    }


def _prioritas_warna(hex_color: str) -> int:
    """Semakin tinggi semakin mendesak."""
    prio = {
        "#991B1B": 5, "#EF4444": 4, "#EAB308": 3,
        "#3B82F6": 2, "#22C55E": 1, "#6B7280": 0,
    }
    return prio.get(hex_color, 0)


# ════════════════════════════════════════════════════════════
# 2. TAMBAH PENANDA MANUAL
# ════════════════════════════════════════════════════════════

def tambah_penanda_manual(profil_id: int, nama_beasiswa: str,
                          deadline: str = "", catatan: str = "") -> tuple:
    """Validasi lalu tambah tracker baru."""
    ok, msg = validasi_tracker_input(nama_beasiswa, deadline)
    if not ok:
        return False, msg, -1
    dl = deadline.strip() if deadline and deadline.strip() else None
    return tambah_tracker(profil_id, nama_beasiswa, dl, catatan)


# ════════════════════════════════════════════════════════════
# 3. KELOLA STATUS & DATA
# ════════════════════════════════════════════════════════════

def ubah_status(tracker_id: int, status_baru: str) -> tuple:
    """Update status tracker."""
    if status_baru not in STATUS_LIST:
        return False, f"Status tidak valid: {status_baru}"
    return update_status_tracker(tracker_id, status_baru)


def ubah_tracker(tracker_id: int, nama: str, deadline: str,
                 catatan: str) -> tuple:
    """Validasi & update data tracker."""
    ok, msg = validasi_tracker_input(nama, deadline)
    if not ok:
        return False, msg
    dl = deadline.strip() if deadline and deadline.strip() else None
    return update_tracker(tracker_id, nama, dl, catatan)


def toggle_bookmark(tracker_id: int) -> tuple:
    """Toggle bookmark on/off."""
    t = ambil_tracker_by_id(tracker_id)
    if not t:
        return False, "Tracker tidak ditemukan."
    new_val = 0 if t["dibookmark"] else 1
    return update_bookmark_tracker(tracker_id, new_val)


def get_semua_tracker(profil_id: int) -> list:
    """Ambil semua tracker user."""
    return ambil_semua_tracker(profil_id)


def get_tracker_by_id(tracker_id: int) -> dict | None:
    """Ambil detail tracker."""
    return ambil_tracker_by_id(tracker_id)


def hapus(tracker_id: int) -> tuple:
    """Hapus tracker."""
    return hapus_tracker(tracker_id)


# ════════════════════════════════════════════════════════════
# 4. HITUNG STATISTIK
# ════════════════════════════════════════════════════════════

def hitung_statistik(profil_id: int) -> dict:
    """Ambil ringkasan statistik tracker."""
    stats = hitung_statistik_tracker(profil_id)
    semua = ambil_semua_tracker(profil_id)
    deadline_terdekat = None
    for t in semua:
        if t["deadline"] and t["status"] not in ("diterima", "ditolak"):
            selisih = hitung_selisih_hari(t["deadline"])
            if selisih is not None and selisih >= 0:
                deadline_terdekat = t
                break
    stats["deadline_terdekat"] = deadline_terdekat
    return stats


# ════════════════════════════════════════════════════════════
# 5. KELOLA PENGINGAT
# ════════════════════════════════════════════════════════════

def buat_pengingat_otomatis(tracker_id: int) -> tuple:
    """Buat pengingat otomatis: H-7, H-3, H-1 dari deadline."""
    t = ambil_tracker_by_id(tracker_id)
    if not t or not t["deadline"]:
        return False, "Tracker tidak ditemukan atau tidak punya deadline."
    selisih = hitung_selisih_hari(t["deadline"])
    if selisih is None or selisih < 0:
        return False, "Deadline sudah lewat."
    dl = datetime.strptime(t["deadline"], "%Y-%m-%d")
    pengingat_hari = []
    if selisih >= 7:
        pengingat_hari.append(7)
    if selisih >= 3:
        pengingat_hari.append(3)
    if selisih >= 1:
        pengingat_hari.append(1)
    for h in pengingat_hari:
        waktu = (dl - timedelta(days=h)).strftime("%Y-%m-%d 08:00:00")
        tambah_pengingat(tracker_id, waktu)
    return True, f"{len(pengingat_hari)} pengingat dibuat."


def cek_pengingat(profil_id: int) -> list:
    """Cek dan ambil pengingat yang sudah waktunya ditampilkan."""
    aktif = ambil_pengingat_aktif(profil_id)
    for p in aktif:
        tandai_pengingat_tampil(p["id"])
    return aktif


# Re-export format helpers for views
def fmt_status(status: str, bhs: str = "id") -> str:
    return format_status(status, bhs)


def clr_status(status: str) -> str:
    return warna_status(status)


def fmt_deadline(deadline_str: str) -> str:
    return format_deadline_display(deadline_str)
