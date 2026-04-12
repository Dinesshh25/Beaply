"""
notifikasi_database.py
Beaply - Manajemen tabel & CRUD SQLite untuk Manajemen Notifikasi Terpusat

Tabel:
  - notifikasi             : Data notifikasi pengguna
  - preferensi_notifikasi  : Pengaturan toggle notifikasi
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

def init_notifikasi_db():
    """Buat tabel notifikasi dan preferensi_notifikasi kalau belum ada."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS notifikasi (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            profil_id       INTEGER NOT NULL,
            judul           TEXT    NOT NULL,
            pesan           TEXT    NOT NULL,
            tipe            TEXT    NOT NULL DEFAULT 'info'
                            CHECK(tipe IN ('info','deadline','status','sistem')),
            sudah_dibaca    INTEGER DEFAULT 0,
            dibuat_pada     TEXT    DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (profil_id) REFERENCES profil(id) ON DELETE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS preferensi_notifikasi (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            profil_id       INTEGER NOT NULL UNIQUE,
            push_notif      INTEGER DEFAULT 1,
            email_notif     INTEGER DEFAULT 0,
            notif_deadline  INTEGER DEFAULT 1,
            notif_status    INTEGER DEFAULT 1,
            notif_sistem    INTEGER DEFAULT 1,
            FOREIGN KEY (profil_id) REFERENCES profil(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


# ════════════════════════════════════════════════════════════
# CRUD — NOTIFIKASI
# ════════════════════════════════════════════════════════════

def tambah_notifikasi(profil_id: int, judul: str, pesan: str,
                      tipe: str = "info") -> tuple:
    """
    Insert notifikasi baru.
    Return: (sukses, pesan, notif_id)
    """
    valid_tipe = ("info", "deadline", "status", "sistem")
    if tipe not in valid_tipe:
        tipe = "info"
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO notifikasi (profil_id, judul, pesan, tipe)
            VALUES (?, ?, ?, ?)
        """, (profil_id, judul.strip(), pesan.strip(), tipe))
        nid = cur.lastrowid
        conn.commit()
        conn.close()
        return True, "Notifikasi dibuat.", nid
    except Exception as e:
        return False, str(e), -1


def ambil_riwayat_notif(profil_id: int, filter_baca: int = None,
                        limit: int = 50) -> list:
    """
    Ambil riwayat notifikasi.
    filter_baca: None=semua, 0=belum dibaca, 1=sudah dibaca
    """
    conn = get_connection()
    cur = conn.cursor()

    query = "SELECT * FROM notifikasi WHERE profil_id = ?"
    params = [profil_id]

    if filter_baca is not None:
        query += " AND sudah_dibaca = ?"
        params.append(filter_baca)

    query += " ORDER BY dibuat_pada DESC LIMIT ?"
    params.append(limit)

    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def tandai_dibaca(notif_id: int) -> bool:
    """
    Ubah status notifikasi dari unread → read.
    Return: status_baca (True jika berhasil)
    """
    try:
        conn = get_connection()
        conn.execute("""
            UPDATE notifikasi SET sudah_dibaca = 1 WHERE id = ?
        """, (notif_id,))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def tandai_semua_dibaca(profil_id: int) -> tuple:
    """Tandai semua notifikasi sebagai dibaca."""
    try:
        conn = get_connection()
        conn.execute("""
            UPDATE notifikasi SET sudah_dibaca = 1
            WHERE profil_id = ? AND sudah_dibaca = 0
        """, (profil_id,))
        conn.commit()
        conn.close()
        return True, "Semua notifikasi ditandai dibaca."
    except Exception as e:
        return False, str(e)


def hapus_notifikasi(notif_id: int) -> tuple:
    """Hapus satu notifikasi."""
    try:
        conn = get_connection()
        conn.execute("DELETE FROM notifikasi WHERE id = ?", (notif_id,))
        conn.commit()
        conn.close()
        return True, "Notifikasi dihapus."
    except Exception as e:
        return False, str(e)


def hapus_semua_notifikasi(profil_id: int) -> tuple:
    """Hapus semua notifikasi milik profil."""
    try:
        conn = get_connection()
        conn.execute("DELETE FROM notifikasi WHERE profil_id = ?",
                     (profil_id,))
        conn.commit()
        conn.close()
        return True, "Semua notifikasi dihapus."
    except Exception as e:
        return False, str(e)


def hitung_belum_dibaca(profil_id: int) -> int:
    """Hitung jumlah notifikasi belum dibaca."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) as cnt FROM notifikasi
        WHERE profil_id = ? AND sudah_dibaca = 0
    """, (profil_id,))
    row = cur.fetchone()
    conn.close()
    return row["cnt"] if row else 0


# ════════════════════════════════════════════════════════════
# CRUD — PREFERENSI NOTIFIKASI
# ════════════════════════════════════════════════════════════

def ambil_preferensi_notif(profil_id: int) -> dict:
    """Ambil preferensi notifikasi. Return default jika belum ada."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM preferensi_notifikasi WHERE profil_id = ?",
                (profil_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return dict(row)
    return {
        "push_notif": 1,
        "email_notif": 0,
        "notif_deadline": 1,
        "notif_status": 1,
        "notif_sistem": 1,
    }


def simpan_preferensi_notif(profil_id: int, prefs: dict) -> tuple:
    """Upsert preferensi notifikasi."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO preferensi_notifikasi
                (profil_id, push_notif, email_notif,
                 notif_deadline, notif_status, notif_sistem)
            VALUES (:profil_id, :push_notif, :email_notif,
                    :notif_deadline, :notif_status, :notif_sistem)
            ON CONFLICT(profil_id) DO UPDATE SET
                push_notif     = excluded.push_notif,
                email_notif    = excluded.email_notif,
                notif_deadline = excluded.notif_deadline,
                notif_status   = excluded.notif_status,
                notif_sistem   = excluded.notif_sistem
        """, {"profil_id": profil_id, **prefs})
        conn.commit()
        conn.close()
        return True, "Preferensi notifikasi tersimpan."
    except Exception as e:
        return False, str(e)
