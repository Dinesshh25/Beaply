"""
models/database.py
Beaply - Koneksi Database TERPUSAT (Satu-satunya titik akses DB)

Semua modul lain harus menggunakan get_connection() atau get_db() dari sini.
"""

import sqlite3
import os
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Path database — relatif terhadap root proyek
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "beaply.db")


def get_connection() -> sqlite3.Connection:
    """
    Buka koneksi ke database SQLite.
    row_factory memungkinkan akses kolom via nama (row["kolom"]).
    WAL mode meningkatkan performa concurrent read.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


@contextmanager
def get_db():
    """
    Context manager untuk koneksi DB — auto commit & close.
    Gunakan ini untuk operasi write agar tidak pernah lupa menutup koneksi.

    Contoh:
        with get_db() as conn:
            conn.execute("INSERT INTO ...")
        # conn sudah di-commit dan di-close otomatis

        with get_db() as conn:
            rows = conn.execute("SELECT ...").fetchall()
    """
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception as exc:
        conn.rollback()
        logger.error("DB transaction rolled back: %s", exc, exc_info=True)
        raise
    finally:
        conn.close()


def init_all_tables():
    """
    Inisialisasi semua tabel yang dibutuhkan aplikasi.
    Dipanggil sekali saat aplikasi pertama kali dijalankan.
    """
    from models.profil_model import init_profil_db
    from models.auth_model import init_auth_db
    from models.beasiswa_model import init_beasiswa_db
    from models.tracker_model import init_tracker_db
    from models.notifikasi_model import init_notifikasi_db

    init_profil_db()
    init_auth_db()
    init_beasiswa_db()
    init_tracker_db()
    init_notifikasi_db()

