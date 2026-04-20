"""
auth_database.py
Beaply - Manajemen tabel & CRUD SQLite untuk Sistem Autentikasi

Tabel:
  - users           : Data akun pengguna
  - sessions        : Sesi aktif pengguna
  - password_resets  : Permintaan reset kata sandi (OTP / link)
  - password_history : Riwayat 3 kata sandi terakhir
"""

import sqlite3
import uuid
import json
from datetime import datetime, timedelta

# Gunakan database yang sama dengan database.py (di folder parent)
import os
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

def init_auth_db():
    """Buat semua tabel autentikasi kalau belum ada."""
    conn = get_connection()
    cur = conn.cursor()

    # ── Tabel users ──────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id                    TEXT PRIMARY KEY,
            email                 TEXT NOT NULL UNIQUE COLLATE NOCASE,
            password_hash         TEXT,
            nama_lengkap          TEXT NOT NULL,
            status                TEXT NOT NULL DEFAULT 'unverified'
                                       CHECK(status IN ('unverified','active','suspended','deleted')),
            google_id             TEXT DEFAULT NULL,
            apple_id              TEXT DEFAULT NULL,
            auth_provider         TEXT NOT NULL DEFAULT 'local'
                                       CHECK(auth_provider IN ('local','google','apple','mixed')),
            last_login_at         TEXT DEFAULT NULL,
            failed_login_attempts INTEGER DEFAULT 0,
            lockout_until         TEXT DEFAULT NULL,
            created_at            TEXT DEFAULT (datetime('now','localtime')),
            updated_at            TEXT DEFAULT (datetime('now','localtime'))
        )
    """)

    # ── Tabel sessions ───────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id                TEXT PRIMARY KEY,
            user_id           TEXT NOT NULL,
            token_hash        TEXT NOT NULL,
            device_info       TEXT DEFAULT '{}',
            ip_address        TEXT DEFAULT '127.0.0.1',
            is_active         INTEGER DEFAULT 1,
            created_at        TEXT DEFAULT (datetime('now','localtime')),
            expires_at        TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # ── Tabel password_resets ────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS password_resets (
            id          TEXT PRIMARY KEY,
            user_id     TEXT NOT NULL,
            method      TEXT NOT NULL CHECK(method IN ('otp','link')),
            token_hash  TEXT NOT NULL,
            attempts    INTEGER DEFAULT 0,
            is_used     INTEGER DEFAULT 0,
            expires_at  TEXT NOT NULL,
            created_at  TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # ── Tabel password_history ───────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS password_history (
            id              TEXT PRIMARY KEY,
            user_id         TEXT NOT NULL,
            password_hash   TEXT NOT NULL,
            created_at      TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


# ════════════════════════════════════════════════════════════
# CRUD — USERS
# ════════════════════════════════════════════════════════════

def create_user(email: str, password_hash: str, nama_lengkap: str,
                status: str = "active", auth_provider: str = "local") -> tuple:
    """
    Insert user baru.
    Return: (sukses: bool, pesan: str, user_id: str)
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        user_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO users (id, email, password_hash, nama_lengkap, status, auth_provider)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, email.lower().strip(), password_hash, nama_lengkap.strip(),
              status, auth_provider))
        conn.commit()
        conn.close()
        return True, "Akun berhasil dibuat.", user_id
    except sqlite3.IntegrityError:
        return False, "Email sudah terdaftar.", ""
    except Exception as e:
        return False, str(e), ""


def get_user_by_email(email: str) -> dict | None:
    """Ambil user berdasarkan email."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ? COLLATE NOCASE", (email.lower().strip(),))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id: str) -> dict | None:
    """Ambil user berdasarkan ID."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def update_user_status(user_id: str, status: str) -> tuple:
    """Update status akun. Return: (sukses, pesan)"""
    try:
        conn = get_connection()
        conn.execute("""
            UPDATE users SET status = ?, updated_at = datetime('now','localtime')
            WHERE id = ?
        """, (status, user_id))
        conn.commit()
        conn.close()
        return True, "Status diperbarui."
    except Exception as e:
        return False, str(e)


def update_login_attempts(user_id: str, count: int, lockout_until: str = None):
    """Update jumlah percobaan login gagal dan waktu lockout."""
    conn = get_connection()
    conn.execute("""
        UPDATE users
        SET failed_login_attempts = ?, lockout_until = ?,
            updated_at = datetime('now','localtime')
        WHERE id = ?
    """, (count, lockout_until, user_id))
    conn.commit()
    conn.close()


def update_last_login(user_id: str):
    """Catat timestamp login terakhir."""
    conn = get_connection()
    conn.execute("""
        UPDATE users
        SET last_login_at = datetime('now','localtime'),
            failed_login_attempts = 0,
            lockout_until = NULL,
            updated_at = datetime('now','localtime')
        WHERE id = ?
    """, (user_id,))
    conn.commit()
    conn.close()


def update_user_password(user_id: str, new_hash: str):
    """Update hash password user."""
    conn = get_connection()
    conn.execute("""
        UPDATE users
        SET password_hash = ?, updated_at = datetime('now','localtime')
        WHERE id = ?
    """, (new_hash, user_id))
    conn.commit()
    conn.close()



# ════════════════════════════════════════════════════════════
# CRUD — SESSIONS
# ════════════════════════════════════════════════════════════

def create_session(user_id: str, token_hash: str,
                   device_info: dict = None, ip_address: str = "127.0.0.1",
                   expires_days: int = 7) -> tuple:
    """
    Buat sesi baru.
    Return: (session_id, token_hash, expires_at)
    """
    session_id = str(uuid.uuid4())
    expires_at = (datetime.now() + timedelta(days=expires_days)).strftime("%Y-%m-%d %H:%M:%S")
    device_json = json.dumps(device_info or {"platform": "desktop", "os": "windows"})

    conn = get_connection()
    conn.execute("""
        INSERT INTO sessions (id, user_id, token_hash, device_info, ip_address, expires_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (session_id, user_id, token_hash, device_json, ip_address, expires_at))
    conn.commit()
    conn.close()
    return session_id, token_hash, expires_at


def get_session(session_id: str) -> dict | None:
    """Ambil sesi berdasarkan ID."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM sessions WHERE id = ? AND is_active = 1", (session_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        d = dict(row)
        # Cek expiry
        exp = datetime.strptime(d["expires_at"], "%Y-%m-%d %H:%M:%S")
        if datetime.now() > exp:
            invalidate_session(session_id)
            return None
        return d
    return None


def invalidate_session(session_id: str):
    """Nonaktifkan satu sesi."""
    conn = get_connection()
    conn.execute("UPDATE sessions SET is_active = 0 WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()


def invalidate_all_sessions(user_id: str):
    """Nonaktifkan semua sesi milik user."""
    conn = get_connection()
    conn.execute("UPDATE sessions SET is_active = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def get_active_sessions(user_id: str) -> list:
    """Ambil semua sesi aktif milik user."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM sessions
        WHERE user_id = ? AND is_active = 1
        ORDER BY created_at DESC
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ════════════════════════════════════════════════════════════
# CRUD — PASSWORD RESETS
# ════════════════════════════════════════════════════════════

def create_password_reset(user_id: str, method: str, token_hash: str,
                          expires_minutes: int = 10) -> str:
    """
    Buat record reset kata sandi.
    Return: reset_id
    """
    reset_id = str(uuid.uuid4())
    expires_at = (datetime.now() + timedelta(minutes=expires_minutes)).strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    # Invalidasi request lama yang masih aktif
    conn.execute("""
        UPDATE password_resets SET is_used = 1
        WHERE user_id = ? AND is_used = 0
    """, (user_id,))
    conn.execute("""
        INSERT INTO password_resets (id, user_id, method, token_hash, expires_at)
        VALUES (?, ?, ?, ?, ?)
    """, (reset_id, user_id, method, token_hash, expires_at))
    conn.commit()
    conn.close()
    return reset_id


def get_password_reset(user_id: str) -> dict | None:
    """Ambil reset request aktif terbaru milik user."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM password_resets
        WHERE user_id = ? AND is_used = 0
        ORDER BY created_at DESC LIMIT 1
    """, (user_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        d = dict(row)
        exp = datetime.strptime(d["expires_at"], "%Y-%m-%d %H:%M:%S")
        if datetime.now() > exp:
            return None  # kedaluwarsa
        return d
    return None


def use_password_reset(reset_id: str):
    """Tandai reset request sudah digunakan."""
    conn = get_connection()
    conn.execute("UPDATE password_resets SET is_used = 1 WHERE id = ?", (reset_id,))
    conn.commit()
    conn.close()


def increment_reset_attempts(reset_id: str) -> int:
    """Tambah counter percobaan. Return: jumlah baru."""
    conn = get_connection()
    conn.execute("UPDATE password_resets SET attempts = attempts + 1 WHERE id = ?", (reset_id,))
    cur = conn.cursor()
    cur.execute("SELECT attempts FROM password_resets WHERE id = ?", (reset_id,))
    row = cur.fetchone()
    count = row["attempts"] if row else 0
    # Invalidasi jika sudah 3 kali gagal
    if count >= 3:
        conn.execute("UPDATE password_resets SET is_used = 1 WHERE id = ?", (reset_id,))
    conn.commit()
    conn.close()
    return count


# ════════════════════════════════════════════════════════════
# CRUD — PASSWORD HISTORY
# ════════════════════════════════════════════════════════════

def add_password_history(user_id: str, password_hash: str):
    """Simpan hash password ke riwayat."""
    conn = get_connection()
    entry_id = str(uuid.uuid4())
    conn.execute("""
        INSERT INTO password_history (id, user_id, password_hash)
        VALUES (?, ?, ?)
    """, (entry_id, user_id, password_hash))
    conn.commit()
    conn.close()


def get_password_history(user_id: str, limit: int = 3) -> list:
    """Ambil N password hash terakhir milik user."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT password_hash FROM password_history
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (user_id, limit))
    rows = cur.fetchall()
    conn.close()
    return [r["password_hash"] for r in rows]
