"""
auth_utils.py
Beaply - Utilitas Keamanan Autentikasi

Modul:
  - hash_password / verify_password  (bcrypt, salt factor 12)
  - validate_password_strength       (min 8 char, upper/lower/digit/symbol)
  - check_password_history           (3 password terakhir)
  - validate_email_format            (regex)
  - sanitize_input                   (cegah injection)
  - generate_otp / generate_token    (OTP 6 digit, UUID token)
  - RateLimiter                      (sliding window, 5/15min, lockout 30min)
"""

import re
import uuid
import random
import string
import time
from datetime import datetime, timedelta

import bcrypt


# ════════════════════════════════════════════════════════════
# PASSWORD HASHING (bcrypt, salt factor 12)
# ════════════════════════════════════════════════════════════

def hash_password(plain_password: str) -> str:
    """
    Hash kata sandi menggunakan bcrypt dengan salt factor 12.
    Return: hash string yang aman untuk disimpan.
    """
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifikasi kata sandi plaintext terhadap hash bcrypt.
    Return: True jika cocok.
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


# ════════════════════════════════════════════════════════════
# VALIDASI KEKUATAN PASSWORD
# ════════════════════════════════════════════════════════════

def validate_password_strength(password: str) -> tuple:
    """
    Validasi kekuatan kata sandi.
    Syarat:
      - Minimal 8 karakter
      - Mengandung huruf besar
      - Mengandung huruf kecil
      - Mengandung angka
      - Mengandung simbol
    Return: (valid: bool, errors: list[str])
    """
    errors = []

    if len(password) < 8:
        errors.append("Minimal 8 karakter.")
    if not re.search(r"[A-Z]", password):
        errors.append("Harus mengandung huruf besar (A-Z).")
    if not re.search(r"[a-z]", password):
        errors.append("Harus mengandung huruf kecil (a-z).")
    if not re.search(r"\d", password):
        errors.append("Harus mengandung angka (0-9).")
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?`~]", password):
        errors.append("Harus mengandung simbol (!@#$%^&*...).")

    return (len(errors) == 0), errors


def get_password_strength_level(password: str) -> tuple:
    """
    Hitung level kekuatan password untuk indikator visual.
    Return: (level: int 0-4, label: str, color: str)
    """
    if not password:
        return 0, "", "#555555"

    score = 0
    if len(password) >= 8:
        score += 1
    if re.search(r"[A-Z]", password) and re.search(r"[a-z]", password):
        score += 1
    if re.search(r"\d", password):
        score += 1
    if re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?`~]", password):
        score += 1

    levels = {
        0: ("Sangat Lemah", "#FF3B30"),
        1: ("Lemah", "#FF9500"),
        2: ("Cukup", "#FFCC00"),
        3: ("Kuat", "#34C759"),
        4: ("Sangat Kuat", "#00C7BE"),
    }
    label, color = levels.get(score, levels[0])
    return score, label, color


def check_password_history(plain_password: str, history_hashes: list) -> bool:
    """
    Cek apakah password baru sama dengan salah satu dari riwayat.
    Return: True jika password sudah pernah digunakan (TIDAK BOLEH).
    """
    for h in history_hashes:
        if verify_password(plain_password, h):
            return True  # cocok = sudah pernah dipakai
    return False


# ════════════════════════════════════════════════════════════
# VALIDASI INPUT
# ════════════════════════════════════════════════════════════

def validate_email_format(email: str) -> bool:
    """Validasi format email menggunakan regex."""
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email.strip()))


def sanitize_input(text: str) -> str:
    """
    Sanitasi input untuk mencegah SQL Injection dan XSS.
    Untuk desktop app dengan parameterized queries, ini adalah
    lapisan perlindungan tambahan.
    """
    if not text:
        return ""
    # Hilangkan karakter kontrol
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    # Escape karakter HTML untuk mencegah XSS
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace('"', "&quot;")
    text = text.replace("'", "&#x27;")
    return text.strip()


# ════════════════════════════════════════════════════════════
# GENERATOR: OTP & TOKEN
# ════════════════════════════════════════════════════════════

def generate_otp(length: int = 6) -> str:
    """Generate kode OTP numerik acak (default 6 digit)."""
    return "".join(random.choices(string.digits, k=length))


def generate_token() -> str:
    """Generate token acak berbasis UUID4 (64 karakter hex)."""
    return uuid.uuid4().hex + uuid.uuid4().hex


def generate_session_token() -> str:
    """Generate token sesi unik."""
    return str(uuid.uuid4())


# ════════════════════════════════════════════════════════════
# RATE LIMITER (Sliding Window Counter)
# ════════════════════════════════════════════════════════════

class RateLimiter:
    """
    Rate limiter berbasis sliding window counter (in-memory).

    Konfigurasi default:
      - max_attempts: 5 percobaan
      - window_seconds: 900 (15 menit)
      - lockout_seconds: 1800 (30 menit)
    """

    def __init__(self, max_attempts: int = 5, window_seconds: int = 900,
                 lockout_seconds: int = 1800):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.lockout_seconds = lockout_seconds
        # {identifier: [timestamp, timestamp, ...]}
        self._attempts: dict[str, list[float]] = {}
        # {identifier: lockout_end_timestamp}
        self._lockouts: dict[str, float] = {}

    def check(self, identifier: str, action_type: str = "login") -> tuple:
        """
        Cek apakah identifier boleh melanjutkan aksi.
        Return: (allowed: bool, remaining_attempts: int, lockout_until: str|None)
        """
        key = f"{identifier}:{action_type}"
        now = time.time()

        # Cek lockout
        if key in self._lockouts:
            if now < self._lockouts[key]:
                lockout_dt = datetime.fromtimestamp(self._lockouts[key])
                return False, 0, lockout_dt.strftime("%H:%M:%S")
            else:
                # Lockout selesai
                del self._lockouts[key]
                self._attempts.pop(key, None)

        # Bersihkan percobaan di luar window
        if key in self._attempts:
            cutoff = now - self.window_seconds
            self._attempts[key] = [t for t in self._attempts[key] if t > cutoff]

        attempts = self._attempts.get(key, [])
        remaining = self.max_attempts - len(attempts)

        if remaining <= 0:
            # Lockout!
            lockout_end = now + self.lockout_seconds
            self._lockouts[key] = lockout_end
            self._attempts.pop(key, None)
            lockout_dt = datetime.fromtimestamp(lockout_end)
            return False, 0, lockout_dt.strftime("%H:%M:%S")

        return True, remaining, None

    def record_attempt(self, identifier: str, action_type: str = "login"):
        """Catat satu percobaan gagal."""
        key = f"{identifier}:{action_type}"
        now = time.time()
        if key not in self._attempts:
            self._attempts[key] = []
        self._attempts[key].append(now)

    def reset(self, identifier: str, action_type: str = "login"):
        """Reset counter (biasanya setelah login berhasil)."""
        key = f"{identifier}:{action_type}"
        self._attempts.pop(key, None)
        self._lockouts.pop(key, None)
