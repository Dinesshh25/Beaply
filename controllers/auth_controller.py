"""
controllers/auth_controller.py
Beaply - Controller: Autentikasi

Mediator antara View (gui_auth.py) dan Model (auth_model + auth_utils).
"""

from models.auth_model import (
    create_user, get_user_by_email, get_user_by_id,
    verify_user_email, update_user_password,
    create_session, validate_session, invalidate_session,
    invalidate_all_sessions,
    create_password_reset, validate_otp,
    record_login, add_password_history, get_password_history,
)
from models.auth_utils import (
    hash_password, verify_password,
    validate_password_strength, get_password_strength_level,
    check_password_history,
    validate_email_format, sanitize_input,
    generate_otp, generate_session_token,
    RateLimiter,
)
from models.email_service import email_service

import logging
logger = logging.getLogger(__name__)

# Rate limiter singleton
_rate_limiter = RateLimiter()


def register(nama: str, email: str, password: str,
             confirm_password: str) -> tuple[bool, str, int]:
    """
    Registrasi user baru.
    Return: (sukses, pesan, user_id)
    """
    nama = sanitize_input(nama)
    email = sanitize_input(email).lower()

    if not nama or len(nama) < 2:
        return False, "Nama minimal 2 karakter.", -1

    if not validate_email_format(email):
        return False, "Format email tidak valid.", -1

    valid, errors = validate_password_strength(password)
    if not valid:
        return False, "\n".join(errors), -1

    if password != confirm_password:
        return False, "Konfirmasi password tidak cocok.", -1

    existing = get_user_by_email(email)
    if existing:
        return False, "Email sudah terdaftar.", -1

    pw_hash = hash_password(password)
    verification_code = generate_otp()

    ok, msg, uid = create_user(email, pw_hash, nama, verification_code)
    if ok:
        add_password_history(uid, pw_hash)
        email_service.send_verification_email(email, verification_code)

    return ok, msg, uid


def login(email: str, password: str) -> tuple[bool, str, dict | None]:
    """
    Login user.
    Return: (sukses, pesan, session_data)
    """
    email = sanitize_input(email).lower()

    allowed, remaining, lockout = _rate_limiter.check(email, "login")
    if not allowed:
        return False, f"Terlalu banyak percobaan. Coba lagi setelah {lockout}.", None

    user = get_user_by_email(email)
    if not user:
        _rate_limiter.record_attempt(email, "login")
        return False, "Email atau password salah.", None

    if not verify_password(password, user["password_hash"]):
        _rate_limiter.record_attempt(email, "login")
        record_login(user["id"], "failed")
        return False, f"Email atau password salah. ({remaining - 1} percobaan tersisa)", None

    _rate_limiter.reset(email, "login")
    record_login(user["id"], "success")

    session_token = generate_session_token()
    create_session(user["id"], session_token)

    return True, "Login berhasil.", {
        "user_id": user["id"],
        "email": user["email"],
        "nama": user["nama_lengkap"],
        "session_token": session_token,
    }


def logout(session_token: str) -> bool:
    """Logout user."""
    try:
        return invalidate_session(session_token)
    except Exception as e:
        logger.error("logout gagal (token=%s...): %s", session_token[:8], e)
        return False


def forgot_password(email: str) -> tuple[bool, str]:
    """Kirim OTP untuk reset password."""
    email = sanitize_input(email).lower()
    user = get_user_by_email(email)
    if not user:
        return False, "Email tidak ditemukan."

    otp = generate_otp()
    create_password_reset(user["id"], otp)
    ok, msg = email_service.send_otp(email, otp)

    return True, msg


def verify_reset_otp(email: str, otp_code: str) -> tuple[bool, str]:
    """Verifikasi OTP reset password."""
    user = get_user_by_email(email.strip().lower())
    if not user:
        return False, "Email tidak ditemukan."
    valid = validate_otp(user["id"], otp_code)
    if not valid:
        return False, "Kode OTP tidak valid atau sudah expired."
    return True, "OTP valid."


def reset_password(email: str, new_password: str,
                   confirm_password: str) -> tuple[bool, str]:
    """Reset password setelah OTP terverifikasi."""
    if new_password != confirm_password:
        return False, "Konfirmasi password tidak cocok."

    valid, errors = validate_password_strength(new_password)
    if not valid:
        return False, "\n".join(errors)

    user = get_user_by_email(email.strip().lower())
    if not user:
        return False, "User tidak ditemukan."

    history = get_password_history(user["id"])
    if check_password_history(new_password, history):
        return False, "Password sudah pernah digunakan sebelumnya."

    pw_hash = hash_password(new_password)
    ok, msg = update_user_password(user["id"], pw_hash)
    if ok:
        add_password_history(user["id"], pw_hash)
        invalidate_all_sessions(user["id"])

    return ok, msg


def change_password(user_id: int, old_password: str,
                    new_password: str, confirm: str) -> tuple[bool, str]:
    """Ubah password dari settings."""
    user = get_user_by_id(user_id)
    if not user:
        return False, "User tidak ditemukan."
    if not verify_password(old_password, user["password_hash"]):
        return False, "Password lama salah."
    if new_password != confirm:
        return False, "Konfirmasi password tidak cocok."
    valid, errors = validate_password_strength(new_password)
    if not valid:
        return False, "\n".join(errors)
    history = get_password_history(user_id)
    if check_password_history(new_password, history):
        return False, "Password sudah pernah digunakan."
    pw_hash = hash_password(new_password)
    ok, msg = update_user_password(user_id, pw_hash)
    if ok:
        add_password_history(user_id, pw_hash)
    return ok, msg


def get_strength_level(password: str) -> tuple:
    """Untuk indikator visual kekuatan password."""
    return get_password_strength_level(password)


# ════════════════════════════════════════════════════════════
# SESSION STATE MANAGEMENT
# ════════════════════════════════════════════════════════════

_CURRENT_USER = None
_CURRENT_SESSION_TOKEN = None


def set_current_user(user_profile: dict | None):
    """Simpan user yang sedang login ke state global."""
    global _CURRENT_USER, _CURRENT_SESSION_TOKEN
    _CURRENT_USER = user_profile
    _CURRENT_SESSION_TOKEN = (
        user_profile.get("session_token") if user_profile else None
    )


def get_current_user() -> dict | None:
    return _CURRENT_USER


def get_current_session() -> str | None:
    return _CURRENT_SESSION_TOKEN


def is_authenticated() -> bool:
    return _CURRENT_USER is not None


def logout_pengguna(session_token: str) -> bool:
    """Logout dan hapus session dari DB."""
    return logout(session_token)


def init_auth():
    """Inisialisasi tabel auth database."""
    from models.auth_model import init_auth_db
    init_auth_db()

