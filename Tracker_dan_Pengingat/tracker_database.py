"""
tracker_database.py
Beaply - Manajemen tabel & CRUD SQLite untuk Tracker & Pengingat

Tabel:
  - tracker_beasiswa  : Data pelacakan pendaftaran beasiswa
  - pengingat         : Pengingat deadline beasiswa
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "beaply.db")


def get_connection():
    """Buka koneksi ke database SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ════════════════════════════════════════════════════════════
# INISIALISASI TABEL
# ════════════════════════════════════════════════════════════

def init_tracker_db():
    """Buat tabel tracker_beasiswa dan pengingat kalau belum ada."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tracker_beasiswa (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            profil_id       INTEGER NOT NULL,
            nama_beasiswa   TEXT    NOT NULL,
            status          TEXT    NOT NULL DEFAULT 'belum_mulai'
                            CHECK(status IN (
                                'belum_mulai','sedang_proses',
                                'terkirim','diterima','ditolak'
                            )),
            deadline        TEXT,
            catatan         TEXT    DEFAULT '',
            dibookmark      INTEGER DEFAULT 0,
            dibuat_pada     TEXT    DEFAULT (datetime('now','localtime')),
            diupdate_pada   TEXT    DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (profil_id) REFERENCES profil(id) ON DELETE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS pengingat (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            tracker_id      INTEGER NOT NULL,
            waktu_pengingat TEXT    NOT NULL,
            sudah_tampil    INTEGER DEFAULT 0,
            dibuat_pada     TEXT    DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (tracker_id) REFERENCES tracker_beasiswa(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


# ════════════════════════════════════════════════════════════
# CRUD — TRACKER BEASISWA
# ════════════════════════════════════════════════════════════

def tambah_tracker(profil_id: int, nama_beasiswa: str,
                   deadline: str = None, catatan: str = "") -> tuple:
    """
    Insert tracker beasiswa baru.
    Return: (sukses, pesan, tracker_id)
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO tracker_beasiswa
                (profil_id, nama_beasiswa, deadline, catatan)
            VALUES (?, ?, ?, ?)
        """, (profil_id, nama_beasiswa.strip(), deadline, catatan.strip()))
        tid = cur.lastrowid
        conn.commit()
        conn.close()
        return True, "Tracker berhasil ditambahkan.", tid
    except Exception as e:
        return False, str(e), -1


def ambil_semua_tracker(profil_id: int) -> list:
    """Ambil semua tracker milik profil, urut deadline terdekat."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM tracker_beasiswa
        WHERE profil_id = ?
        ORDER BY
            CASE WHEN deadline IS NULL THEN 1 ELSE 0 END,
            deadline ASC,
            dibuat_pada DESC
    """, (profil_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def ambil_tracker_by_id(tracker_id: int) -> dict | None:
    """Ambil satu tracker berdasarkan ID."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tracker_beasiswa WHERE id = ?", (tracker_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def update_status_tracker(tracker_id: int, status: str) -> tuple:
    """Update status tracker. Return: (sukses, pesan)"""
    valid = ('belum_mulai', 'sedang_proses', 'terkirim', 'diterima', 'ditolak')
    if status not in valid:
        return False, f"Status harus salah satu dari: {', '.join(valid)}"
    try:
        conn = get_connection()
        conn.execute("""
            UPDATE tracker_beasiswa
            SET status = ?, diupdate_pada = datetime('now','localtime')
            WHERE id = ?
        """, (status, tracker_id))
        conn.commit()
        conn.close()
        return True, "Status diperbarui."
    except Exception as e:
        return False, str(e)


def update_tracker(tracker_id: int, nama_beasiswa: str,
                   deadline: str, catatan: str) -> tuple:
    """Update data tracker. Return: (sukses, pesan)"""
    try:
        conn = get_connection()
        conn.execute("""
            UPDATE tracker_beasiswa
            SET nama_beasiswa = ?, deadline = ?, catatan = ?,
                diupdate_pada = datetime('now','localtime')
            WHERE id = ?
        """, (nama_beasiswa.strip(), deadline, catatan.strip(), tracker_id))
        conn.commit()
        conn.close()
        return True, "Tracker diperbarui."
    except Exception as e:
        return False, str(e)


def hapus_tracker(tracker_id: int) -> tuple:
    """Hapus tracker (dan pengingat via CASCADE). Return: (sukses, pesan)"""
    try:
        conn = get_connection()
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("DELETE FROM tracker_beasiswa WHERE id = ?", (tracker_id,))
        conn.commit()
        conn.close()
        return True, "Tracker dihapus."
    except Exception as e:
        return False, str(e)


def update_bookmark_tracker(tracker_id: int, status: int) -> tuple:
    """Toggle bookmark status. Return: (sukses, pesan)"""
    try:
        conn = get_connection()
        conn.execute("""
            UPDATE tracker_beasiswa
            SET dibookmark = ?, diupdate_pada = datetime('now','localtime')
            WHERE id = ?
        """, (status, tracker_id))
        conn.commit()
        conn.close()
        return True, "Bookmark diperbarui."
    except Exception as e:
        return False, str(e)


def ambil_tracker_by_bulan(profil_id: int, bulan: int, tahun: int) -> list:
    """Ambil tracker yang deadline-nya di bulan & tahun tertentu (untuk kalender)."""
    conn = get_connection()
    cur = conn.cursor()
    pattern = f"{tahun:04d}-{bulan:02d}-%"
    cur.execute("""
        SELECT * FROM tracker_beasiswa
        WHERE profil_id = ? AND deadline LIKE ?
        ORDER BY deadline ASC
    """, (profil_id, pattern))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def hitung_statistik_tracker(profil_id: int) -> dict:
    """Hitung jumlah tracker per status."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN status = 'belum_mulai' THEN 1 ELSE 0 END) as belum_mulai,
            SUM(CASE WHEN status = 'sedang_proses' THEN 1 ELSE 0 END) as sedang_proses,
            SUM(CASE WHEN status = 'terkirim' THEN 1 ELSE 0 END) as terkirim,
            SUM(CASE WHEN status = 'diterima' THEN 1 ELSE 0 END) as diterima,
            SUM(CASE WHEN status = 'ditolak' THEN 1 ELSE 0 END) as ditolak,
            SUM(CASE WHEN dibookmark = 1 THEN 1 ELSE 0 END) as bookmark
        FROM tracker_beasiswa
        WHERE profil_id = ?
    """, (profil_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return dict(row)
    return {"total": 0, "belum_mulai": 0, "sedang_proses": 0,
            "terkirim": 0, "diterima": 0, "ditolak": 0, "bookmark": 0}


# ════════════════════════════════════════════════════════════
# CRUD — PENGINGAT
# ════════════════════════════════════════════════════════════

def tambah_pengingat(tracker_id: int, waktu_pengingat: str) -> tuple:
    """
    Tambah pengingat untuk tracker.
    Return: (sukses, pesan, pengingat_id)
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO pengingat (tracker_id, waktu_pengingat)
            VALUES (?, ?)
        """, (tracker_id, waktu_pengingat))
        pid = cur.lastrowid
        conn.commit()
        conn.close()
        return True, "Pengingat ditambahkan.", pid
    except Exception as e:
        return False, str(e), -1


def ambil_pengingat_aktif(profil_id: int) -> list:
    """Ambil semua pengingat aktif (belum tampil) milik profil."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.*, t.nama_beasiswa, t.deadline
        FROM pengingat p
        JOIN tracker_beasiswa t ON p.tracker_id = t.id
        WHERE t.profil_id = ? AND p.sudah_tampil = 0
              AND p.waktu_pengingat <= datetime('now','localtime')
        ORDER BY p.waktu_pengingat ASC
    """, (profil_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def tandai_pengingat_tampil(pengingat_id: int):
    """Tandai pengingat sudah ditampilkan."""
    conn = get_connection()
    conn.execute("UPDATE pengingat SET sudah_tampil = 1 WHERE id = ?",
                 (pengingat_id,))
    conn.commit()
    conn.close()
