"""
models/auth_model.py
Beaply - Model: Autentikasi & Keamanan

CRUD SQLite untuk tabel users, sessions, password_resets, login_history.
Digabungkan dari: Autentikasi_dan_Keamanan/auth_database.py
"""

import sqlite3
import os
from datetime import datetime, timedelta

from models.database import get_connection


# ════════════════════════════════════════════════════════════
# INISIALISASI TABEL
# ════════════════════════════════════════════════════════════

def init_auth_db():
    """Buat tabel autentikasi jika belum ada."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id                      TEXT    PRIMARY KEY,
            email                   TEXT    NOT NULL UNIQUE,
            password_hash           TEXT,
            nama_lengkap            TEXT    NOT NULL,
            status                  TEXT    NOT NULL DEFAULT 'unverified',
            google_id               TEXT    DEFAULT NULL,
            apple_id                TEXT    DEFAULT NULL,
            auth_provider           TEXT    NOT NULL DEFAULT 'local',
            last_login_at           TEXT    DEFAULT NULL,
            failed_login_attempts   INTEGER DEFAULT 0,
            lockout_until           TEXT    DEFAULT NULL,
            created_at              TEXT    DEFAULT (datetime('now','localtime')),
            updated_at              TEXT    DEFAULT (datetime('now','localtime'))
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       INTEGER NOT NULL,
            session_token TEXT    NOT NULL UNIQUE,
            created_at    TEXT    DEFAULT (datetime('now','localtime')),
            expires_at    TEXT    NOT NULL,
            is_active     INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS password_resets (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            otp_code    TEXT    NOT NULL,
            created_at  TEXT    DEFAULT (datetime('now','localtime')),
            expires_at  TEXT    NOT NULL,
            is_used     INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS login_history (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            login_at   TEXT    DEFAULT (datetime('now','localtime')),
            ip_address TEXT    DEFAULT '',
            status     TEXT    DEFAULT 'success',
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS password_history (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id       INTEGER NOT NULL,
            password_hash TEXT    NOT NULL,
            changed_at    TEXT    DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


# ════════════════════════════════════════════════════════════
# CRUD — USERS
# ════════════════════════════════════════════════════════════

def create_user(email: str, password_hash: str, nama: str,
                verification_code: str = None) -> tuple[bool, str, int]:
    """Insert user baru. Return: (sukses, pesan, user_id)"""
    import uuid
    try:
        conn = get_connection()
        cur = conn.cursor()
        user_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO users (id, email, password_hash, nama_lengkap, status, auth_provider)
            VALUES (?, ?, ?, ?, 'unverified', 'local')
        """, (user_id, email.strip().lower(), password_hash, nama.strip()))
        conn.commit()
        conn.close()
        return True, "User berhasil dibuat.", user_id
    except sqlite3.IntegrityError:
        return False, "Email sudah terdaftar.", -1
    except Exception as e:
        return False, str(e), -1


def get_user_by_email(email: str) -> dict | None:
    """Ambil user berdasarkan email."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id: int) -> dict | None:
    """Ambil user berdasarkan ID."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def verify_user_email(user_id: int) -> bool:
    """Tandai user sebagai verified."""
    try:
        conn = get_connection()
        conn.execute("""
            UPDATE users SET status = 'verified',
            updated_at = datetime('now','localtime')
            WHERE id = ?
        """, (user_id,))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def update_user_password(user_id: int, new_password_hash: str) -> tuple[bool, str]:
    """Update password user."""
    try:
        conn = get_connection()
        conn.execute("""
            UPDATE users SET password_hash = ?,
            updated_at = datetime('now','localtime')
            WHERE id = ?
        """, (new_password_hash, user_id))
        conn.commit()
        conn.close()
        return True, "Password diperbarui."
    except Exception as e:
        return False, str(e)


# ════════════════════════════════════════════════════════════
# CRUD — SESSIONS
# ════════════════════════════════════════════════════════════

def create_session(user_id: int, session_token: str,
                   expires_hours: int = 24) -> tuple[bool, str]:
    """Buat sesi baru."""
    try:
        expires = (datetime.now() + timedelta(hours=expires_hours)).strftime(
            "%Y-%m-%d %H:%M:%S")
        conn = get_connection()
        conn.execute("""
            INSERT INTO sessions (user_id, session_token, expires_at)
            VALUES (?, ?, ?)
        """, (user_id, session_token, expires))
        conn.commit()
        conn.close()
        return True, "Sesi dibuat."
    except Exception as e:
        return False, str(e)


def validate_session(session_token: str) -> dict | None:
    """Validasi sesi aktif. Return user data jika valid."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT s.*, u.email, u.nama_lengkap
        FROM sessions s
        JOIN users u ON s.user_id = u.id
        WHERE s.session_token = ? AND s.is_active = 1
              AND s.expires_at > datetime('now','localtime')
    """, (session_token,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def invalidate_session(session_token: str) -> bool:
    """Nonaktifkan sesi."""
    try:
        conn = get_connection()
        conn.execute(
            "UPDATE sessions SET is_active = 0 WHERE session_token = ?",
            (session_token,))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def invalidate_all_sessions(user_id: int) -> bool:
    """Nonaktifkan semua sesi user."""
    try:
        conn = get_connection()
        conn.execute(
            "UPDATE sessions SET is_active = 0 WHERE user_id = ?",
            (user_id,))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


# ════════════════════════════════════════════════════════════
# CRUD — PASSWORD RESETS
# ════════════════════════════════════════════════════════════

def create_password_reset(user_id: int, otp_code: str,
                          expires_minutes: int = 10) -> tuple[bool, str]:
    """Buat OTP reset password."""
    try:
        expires = (datetime.now() + timedelta(minutes=expires_minutes)).strftime(
            "%Y-%m-%d %H:%M:%S")
        conn = get_connection()
        conn.execute("""
            INSERT INTO password_resets (user_id, otp_code, expires_at)
            VALUES (?, ?, ?)
        """, (user_id, otp_code, expires))
        conn.commit()
        conn.close()
        return True, "OTP dibuat."
    except Exception as e:
        return False, str(e)


def validate_otp(user_id: int, otp_code: str) -> bool:
    """Validasi OTP reset password."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id FROM password_resets
        WHERE user_id = ? AND otp_code = ? AND is_used = 0
              AND expires_at > datetime('now','localtime')
        ORDER BY created_at DESC LIMIT 1
    """, (user_id, otp_code))
    row = cur.fetchone()
    if row:
        conn.execute("UPDATE password_resets SET is_used = 1 WHERE id = ?",
                      (row["id"],))
        conn.commit()
    conn.close()
    return row is not None


# ════════════════════════════════════════════════════════════
# CRUD — LOGIN HISTORY
# ════════════════════════════════════════════════════════════

def record_login(user_id: int, status: str = "success",
                 ip_address: str = "") -> None:
    """Catat riwayat login."""
    try:
        conn = get_connection()
        conn.execute("""
            INSERT INTO login_history (user_id, status, ip_address)
            VALUES (?, ?, ?)
        """, (user_id, status, ip_address))
        conn.commit()
        conn.close()
    except Exception:
        pass


# ════════════════════════════════════════════════════════════
# CRUD — PASSWORD HISTORY
# ════════════════════════════════════════════════════════════

def add_password_history(user_id: int, password_hash: str) -> None:
    """Tambah ke riwayat password."""
    try:
        conn = get_connection()
        conn.execute("""
            INSERT INTO password_history (user_id, password_hash)
            VALUES (?, ?)
        """, (user_id, password_hash))
        conn.commit()
        conn.close()
    except Exception:
        pass


def get_password_history(user_id: int, limit: int = 3) -> list[str]:
    """Ambil N password hash terakhir."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT password_hash FROM password_history
        WHERE user_id = ?
        ORDER BY changed_at DESC LIMIT ?
    """, (user_id, limit))
    rows = cur.fetchall()
    conn.close()
    return [r["password_hash"] for r in rows]
