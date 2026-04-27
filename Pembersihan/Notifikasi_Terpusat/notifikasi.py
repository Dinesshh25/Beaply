"""
notifikasi.py
Beaply - Logika Bisnis Manajemen Notifikasi Terpusat

Modul sesuai spesifikasi:
  1. tampilan_laci_notif       — Data riwayat notifikasi grouped by date
  2. ambil_riwayat             — Ambil data notifikasi user
  3. tandai_dibaca             — Mark notif as read
  4. tampilan_kontrol_notif    — Data preferensi toggle
  5. ubah_preferensi_notif     — Simpan perubahan toggle
  6. buat_notifikasi_deadline  — Auto-generate notif deadline
  7. buat_notifikasi_status    — Notif saat status tracker berubah
"""

from .notifikasi_database import (
    tambah_notifikasi,
    ambil_riwayat_notif,
    tandai_dibaca as db_tandai_dibaca,
    tandai_semua_dibaca as db_tandai_semua_dibaca,
    hapus_notifikasi as db_hapus_notifikasi,
    hapus_semua_notifikasi as db_hapus_semua,
    hitung_belum_dibaca as db_hitung_belum_dibaca,
    ambil_preferensi_notif,
    simpan_preferensi_notif,
)
from .notifikasi_utils import (
    format_waktu_relatif,
    group_by_tanggal,
    ikon_tipe,
    warna_tipe,
    label_tipe,
)


# ════════════════════════════════════════════════════════════
# 1. TAMPILAN LACI NOTIFIKASI
# ════════════════════════════════════════════════════════════

def tampilan_laci_notif(profil_id: int, bhs: str = "id") -> dict:
    """
    Siapkan data untuk render laci notifikasi.

    Return: {
        notifikasi_grouped: list of {tanggal, items},
        total: int,
        belum_dibaca: int,
    }
    """
    semua = ambil_riwayat_notif(profil_id)
    grouped = group_by_tanggal(semua, bhs)
    belum = db_hitung_belum_dibaca(profil_id)

    # Tambahkan info format ke setiap notif
    for g in grouped:
        for n in g["items"]:
            n["waktu_relatif"] = format_waktu_relatif(n.get("dibuat_pada", ""), bhs)
            n["ikon"] = ikon_tipe(n.get("tipe", "info"))
            n["warna"] = warna_tipe(n.get("tipe", "info"))

    return {
        "notifikasi_grouped": grouped,
        "total": len(semua),
        "belum_dibaca": belum,
    }


# ════════════════════════════════════════════════════════════
# 2. AMBIL RIWAYAT
# ════════════════════════════════════════════════════════════

def ambil_riwayat(profil_id: int, filter_baca: int = None) -> list:
    """
    Mengambil data notifikasi terbaru dari basis data.

    Args:
        profil_id: ID profil pengguna
        filter_baca: None=semua, 0=belum dibaca, 1=sudah dibaca

    Return: data_notif (list[dict])
    """
    return ambil_riwayat_notif(profil_id, filter_baca)


# ════════════════════════════════════════════════════════════
# 3. TANDAI DIBACA
# ════════════════════════════════════════════════════════════

def tandai_dibaca(notif_id: int) -> bool:
    """
    Mengubah status notifikasi dari unread → read.
    Return: status_baca (Bool)
    """
    return db_tandai_dibaca(notif_id)


def tandai_semua_dibaca(profil_id: int) -> tuple:
    """Tandai semua notifikasi sebagai dibaca."""
    return db_tandai_semua_dibaca(profil_id)


# ════════════════════════════════════════════════════════════
# 4. TAMPILAN KONTROL NOTIFIKASI
# ════════════════════════════════════════════════════════════

def tampilan_kontrol_notif(profil_id: int) -> dict:
    """
    Siapkan data preferensi toggle notifikasi.

    Return: dict dengan semua toggle status
    """
    return ambil_preferensi_notif(profil_id)


# ════════════════════════════════════════════════════════════
# 5. UBAH PREFERENSI NOTIFIKASI
# ════════════════════════════════════════════════════════════

def ubah_preferensi_notif(profil_id: int, jenis_notif: str,
                          status_toggle: bool) -> bool:
    """
    Menerima dan menyimpan perubahan toggle notifikasi.

    Args:
        profil_id: ID profil
        jenis_notif: 'push_notif', 'email_notif', 'notif_deadline',
                      'notif_status', 'notif_sistem'
        status_toggle: True/False

    Return: status_simpan (Bool)
    """
    valid_jenis = ('push_notif', 'email_notif', 'notif_deadline',
                   'notif_status', 'notif_sistem')
    if jenis_notif not in valid_jenis:
        return False

    # Ambil preferensi saat ini, update field yang diminta
    prefs = ambil_preferensi_notif(profil_id)
    prefs[jenis_notif] = int(status_toggle)

    # Hapus field yang bukan untuk simpan
    save_data = {
        "push_notif": prefs.get("push_notif", 1),
        "email_notif": prefs.get("email_notif", 0),
        "notif_deadline": prefs.get("notif_deadline", 1),
        "notif_status": prefs.get("notif_status", 1),
        "notif_sistem": prefs.get("notif_sistem", 1),
    }

    ok, msg = simpan_preferensi_notif(profil_id, save_data)
    return ok


def simpan_semua_preferensi(profil_id: int, prefs: dict) -> tuple:
    """Simpan semua preferensi sekaligus."""
    save_data = {
        "push_notif": int(prefs.get("push_notif", 1)),
        "email_notif": int(prefs.get("email_notif", 0)),
        "notif_deadline": int(prefs.get("notif_deadline", 1)),
        "notif_status": int(prefs.get("notif_status", 1)),
        "notif_sistem": int(prefs.get("notif_sistem", 1)),
    }
    return simpan_preferensi_notif(profil_id, save_data)


# ════════════════════════════════════════════════════════════
# 6. BUAT NOTIFIKASI DEADLINE (auto-generate)
# ════════════════════════════════════════════════════════════

def buat_notifikasi_deadline(profil_id: int, nama_beasiswa: str,
                             hari_tersisa: int) -> tuple:
    """
    Auto-generate notifikasi deadline.

    Return: (sukses, pesan, notif_id)
    """
    # Cek preferensi
    prefs = ambil_preferensi_notif(profil_id)
    if not prefs.get("notif_deadline", 1):
        return False, "Notifikasi deadline dinonaktifkan.", -1

    if hari_tersisa <= 0:
        judul = f"⚠️ Deadline {nama_beasiswa} HARI INI!"
        pesan = f"Deadline pendaftaran {nama_beasiswa} adalah hari ini. Segera selesaikan!"
    elif hari_tersisa <= 3:
        judul = f"⏰ {hari_tersisa} hari lagi: {nama_beasiswa}"
        pesan = f"Deadline {nama_beasiswa} tinggal {hari_tersisa} hari lagi. Jangan sampai terlewat!"
    elif hari_tersisa <= 7:
        judul = f"📅 Reminder: {nama_beasiswa}"
        pesan = f"Deadline {nama_beasiswa} dalam {hari_tersisa} hari. Pastikan dokumen sudah siap."
    else:
        judul = f"📋 Deadline mendatang: {nama_beasiswa}"
        pesan = f"Deadline {nama_beasiswa} dalam {hari_tersisa} hari."

    return tambah_notifikasi(profil_id, judul, pesan, "deadline")


# ════════════════════════════════════════════════════════════
# 7. BUAT NOTIFIKASI STATUS (saat status tracker berubah)
# ════════════════════════════════════════════════════════════

def buat_notifikasi_status(profil_id: int, nama_beasiswa: str,
                           status_baru: str) -> tuple:
    """
    Buat notifikasi saat status tracker berubah.

    Return: (sukses, pesan, notif_id)
    """
    prefs = ambil_preferensi_notif(profil_id)
    if not prefs.get("notif_status", 1):
        return False, "Notifikasi status dinonaktifkan.", -1

    status_label = {
        "belum_mulai":   "Belum Mulai",
        "sedang_proses": "Sedang Proses",
        "terkirim":      "Terkirim",
        "diterima":      "Diterima ✅",
        "ditolak":       "Ditolak ❌",
    }

    label = status_label.get(status_baru, status_baru)
    judul = f"📋 Status diperbarui: {nama_beasiswa}"
    pesan = f"Status pendaftaran {nama_beasiswa} berubah menjadi: {label}"

    return tambah_notifikasi(profil_id, judul, pesan, "status")


# ════════════════════════════════════════════════════════════
# HELPER: Hitung badge
# ════════════════════════════════════════════════════════════

def hitung_belum_dibaca(profil_id: int) -> int:
    """Hitung jumlah notifikasi belum dibaca (untuk badge)."""
    return db_hitung_belum_dibaca(profil_id)


def hapus_notifikasi(notif_id: int) -> tuple:
    """Hapus satu notifikasi."""
    return db_hapus_notifikasi(notif_id)


def hapus_semua(profil_id: int) -> tuple:
    """Hapus semua notifikasi."""
    return db_hapus_semua(profil_id)
