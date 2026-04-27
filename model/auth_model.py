import sqlite3
import uuid
import re
import json
import bcrypt
from datetime import datetime, timedelta
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Pembersihan", "beaply.db")

def _get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# ════════════════════════════════════════════════════════════
# INISIALISASI
# ════════════════════════════════════════════════════════════

def init_auth_db():
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id                    TEXT PRIMARY KEY,
            email                 TEXT NOT NULL UNIQUE COLLATE NOCASE,
            password_hash         TEXT,
            nama_lengkap          TEXT NOT NULL,
            status                TEXT NOT NULL DEFAULT 'active',
            last_login_at         TEXT DEFAULT NULL,
            failed_login_attempts INTEGER DEFAULT 0,
            lockout_until         TEXT DEFAULT NULL,
            created_at            TEXT DEFAULT (datetime('now','localtime')),
            updated_at            TEXT DEFAULT (datetime('now','localtime'))
        )
    """)
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
    conn.commit()
    conn.close()

# ════════════════════════════════════════════════════════════
# UTILITAS KEAMANAN
# ════════════════════════════════════════════════════════════

def hash_password(plain_password: str) -> str:
    salt = bcrypt.gensalt(rounds=10) # 10 rounds to be slightly faster for local app
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False

def validate_password_strength(password: str) -> tuple:
    errors = []
    if len(password) < 8: errors.append("Minimal 8 karakter.")
    if not re.search(r"[A-Z]", password): errors.append("Harus mengandung huruf besar.")
    if not re.search(r"[a-z]", password): errors.append("Harus mengandung huruf kecil.")
    if not re.search(r"\d", password): errors.append("Harus mengandung angka.")
    return len(errors) == 0, errors

def validate_email_format(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email.strip()))

# ════════════════════════════════════════════════════════════
# CRUD USER
# ════════════════════════════════════════════════════════════

def create_user(email: str, password_hash: str, nama_lengkap: str) -> tuple:
    try:
        conn = _get_connection()
        cur = conn.cursor()
        user_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO users (id, email, password_hash, nama_lengkap, status)
            VALUES (?, ?, ?, ?, 'active')
        """, (user_id, email.lower().strip(), password_hash, nama_lengkap.strip()))
        conn.commit()
        conn.close()
        return True, "Akun berhasil dibuat.", user_id
    except sqlite3.IntegrityError:
        return False, "Email sudah terdaftar.", ""
    except Exception as e:
        return False, str(e), ""

def get_user_by_email(email: str) -> dict | None:
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ? COLLATE NOCASE", (email.lower().strip(),))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_by_id(user_id: str) -> dict | None:
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

def update_login_attempts(user_id: str, count: int, lockout_until: str = None):
    conn = _get_connection()
    conn.execute("""
        UPDATE users SET failed_login_attempts = ?, lockout_until = ?, updated_at = datetime('now','localtime')
        WHERE id = ?
    """, (count, lockout_until, user_id))
    conn.commit()
    conn.close()

def update_last_login(user_id: str):
    conn = _get_connection()
    conn.execute("""
        UPDATE users SET last_login_at = datetime('now','localtime'), failed_login_attempts = 0, lockout_until = NULL, updated_at = datetime('now','localtime')
        WHERE id = ?
    """, (user_id,))
    conn.commit()
    conn.close()

def update_user_password(user_id: str, new_hash: str):
    conn = _get_connection()
    conn.execute("UPDATE users SET password_hash = ?, updated_at = datetime('now','localtime') WHERE id = ?", (new_hash, user_id))
    conn.commit()
    conn.close()

# ════════════════════════════════════════════════════════════
# LUPA SANDI (OTP LOKAL)
# ════════════════════════════════════════════════════════════

def create_password_reset(user_id: str, method: str, token_hash: str, expires_minutes: int = 10) -> str:
    reset_id = str(uuid.uuid4())
    expires_at = (datetime.now() + timedelta(minutes=expires_minutes)).strftime("%Y-%m-%d %H:%M:%S")
    conn = _get_connection()
    conn.execute("UPDATE password_resets SET is_used = 1 WHERE user_id = ? AND is_used = 0", (user_id,))
    conn.execute("INSERT INTO password_resets (id, user_id, method, token_hash, expires_at) VALUES (?, ?, ?, ?, ?)", (reset_id, user_id, method, token_hash, expires_at))
    conn.commit()
    conn.close()
    return reset_id

def get_password_reset(user_id: str) -> dict | None:
    conn = _get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM password_resets WHERE user_id = ? AND is_used = 0 ORDER BY created_at DESC LIMIT 1", (user_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        d = dict(row)
        exp = datetime.strptime(d["expires_at"], "%Y-%m-%d %H:%M:%S")
        if datetime.now() > exp: return None
        return d
    return None

def use_password_reset(reset_id: str):
    conn = _get_connection()
    conn.execute("UPDATE password_resets SET is_used = 1 WHERE id = ?", (reset_id,))
    conn.commit()
    conn.close()

def increment_reset_attempts(reset_id: str) -> int:
    conn = _get_connection()
    conn.execute("UPDATE password_resets SET attempts = attempts + 1 WHERE id = ?", (reset_id,))
    cur = conn.cursor()
    cur.execute("SELECT attempts FROM password_resets WHERE id = ?", (reset_id,))
    count = cur.fetchone()["attempts"]
    if count >= 3: conn.execute("UPDATE password_resets SET is_used = 1 WHERE id = ?", (reset_id,))
    conn.commit()
    conn.close()
    return count
