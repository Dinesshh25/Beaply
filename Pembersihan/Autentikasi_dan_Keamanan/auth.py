"""
auth.py
Beaply - Logika Bisnis Sistem Autentikasi & Keamanan

Modul sesuai spesifikasi:
  1. registrasi_pengguna     — Registrasi akun baru
  2. login_pengguna          — Login dengan email & password
  3. sso_google              — SSO via Google (stub)
  4. sso_apple               — SSO via Apple (stub)
  5. lupa_sandi              — Inisiasi reset password (OTP)
  6. verifikasi_otp          — Verifikasi kode OTP
  7. reset_password          — Set password baru
  8. buat_sesi               — Buat session token
  9. refresh_token_fn        — Refresh session
  10. logout_pengguna        — Logout (single / all devices)
  11. validasi_input         — Wrapper validasi email + password
  12. get_current_user       — Ambil user dari session aktif
"""

from .auth_database import (
    init_auth_db,
    create_user,
    get_user_by_email,
    get_user_by_id,
    update_user_status,
    update_login_attempts,
    update_last_login,
    update_user_password,
    create_session,
    get_session,
    invalidate_session,
    invalidate_all_sessions,
    get_active_sessions,
    create_password_reset,
    get_password_reset,
    use_password_reset,
    increment_reset_attempts,
    add_password_history,
    get_password_history,
    link_sso_account,
)
from .auth_utils import (
    hash_password,
    verify_password,
    validate_password_strength,
    check_password_history,
    validate_email_format,
    sanitize_input,
    generate_otp,
    generate_token,
    generate_session_token,
    RateLimiter,
)
from .email_service import email_service


# ════════════════════════════════════════════════════════════
# INISIALISASI
# ════════════════════════════════════════════════════════════

# Rate limiter global (5 percobaan per 15 menit, lockout 30 menit)
rate_limiter = RateLimiter(max_attempts=5, window_seconds=900, lockout_seconds=1800)

# Sesi aktif saat ini (untuk desktop app, cukup 1 sesi per waktu)
_current_session = {
    "session_id": None,
    "user_id": None,
    "token": None,
}


def init_auth():
    """Inisialisasi tabel autentikasi."""
    init_auth_db()


# ════════════════════════════════════════════════════════════
# 1. REGISTRASI PENGGUNA
# ════════════════════════════════════════════════════════════

def registrasi_pengguna(email: str, password: str, confirm_password: str,
                        nama_lengkap: str) -> dict:
    """
    Mendaftarkan pengguna baru ke dalam sistem.

    Validasi:
      - Format email
      - Kekuatan password (min 8 char, upper/lower/digit/symbol)
      - Password == confirm_password
      - Email belum terdaftar

    Return: {success: bool, user_id: str, message: str}
    """
    # Sanitasi input
    email = sanitize_input(email).lower().strip()
    nama_lengkap = sanitize_input(nama_lengkap).strip()

    # Validasi email
    if not validate_email_format(email):
        return {"success": False, "user_id": "", "message": "Format email tidak valid."}

    # Validasi nama
    if not nama_lengkap or len(nama_lengkap) < 2:
        return {"success": False, "user_id": "", "message": "Nama lengkap minimal 2 karakter."}

    # Validasi kekuatan password
    valid, errors = validate_password_strength(password)
    if not valid:
        return {"success": False, "user_id": "", "message": "Password lemah:\n• " + "\n• ".join(errors)}

    # Cocokkan password
    if password != confirm_password:
        return {"success": False, "user_id": "", "message": "Konfirmasi kata sandi tidak cocok."}

    # Cek duplikasi email
    if get_user_by_email(email):
        return {"success": False, "user_id": "", "message": "Email sudah terdaftar."}

    # Hash password
    pwd_hash = hash_password(password)

    # Simpan ke DB (langsung active karena desktop app — tidak perlu email verification)
    ok, msg, user_id = create_user(email, pwd_hash, nama_lengkap, status="active")
    if not ok:
        return {"success": False, "user_id": "", "message": msg}

    # Simpan ke password history
    add_password_history(user_id, pwd_hash)

    return {"success": True, "user_id": user_id, "message": "Registrasi berhasil! Silakan login."}


# ════════════════════════════════════════════════════════════
# 2. LOGIN PENGGUNA
# ════════════════════════════════════════════════════════════

def login_pengguna(email: str, password: str) -> dict:
    """
    Mengautentikasi pengguna menggunakan email dan kata sandi.

    Return: {
        success: bool,
        session_id: str,
        token: str,
        user_profile: dict,
        message: str
    }
    """
    email = email.lower().strip()

    # Rate limiting
    allowed, remaining, lockout = rate_limiter.check(email, "login")
    if not allowed:
        return {
            "success": False, "session_id": "", "token": "",
            "user_profile": None,
            "message": f"Terlalu banyak percobaan login.\nCoba lagi setelah {lockout}.",
        }

    # Cek user ada
    user = get_user_by_email(email)
    if not user:
        rate_limiter.record_attempt(email, "login")
        return {
            "success": False, "session_id": "", "token": "",
            "user_profile": None,
            "message": "Email atau kata sandi salah.",
        }

    # Cek status akun
    if user["status"] == "suspended":
        return {
            "success": False, "session_id": "", "token": "",
            "user_profile": None,
            "message": "Akun Anda ditangguhkan. Hubungi admin.",
        }
    if user["status"] == "deleted":
        return {
            "success": False, "session_id": "", "token": "",
            "user_profile": None,
            "message": "Akun tidak ditemukan.",
        }

    # Verifikasi password
    if not user["password_hash"] or not verify_password(password, user["password_hash"]):
        rate_limiter.record_attempt(email, "login")
        # Update failed attempts di DB juga
        new_count = user["failed_login_attempts"] + 1
        lockout_until = None
        if new_count >= 5:
            from datetime import datetime, timedelta
            lockout_until = (datetime.now() + timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
        update_login_attempts(user["id"], new_count, lockout_until)
        return {
            "success": False, "session_id": "", "token": "",
            "user_profile": None,
            "message": "Email atau kata sandi salah.",
        }

    # Berhasil! Buat sesi
    session_result = buat_sesi(user["id"])

    # Update login info
    update_last_login(user["id"])
    rate_limiter.reset(email, "login")

    return {
        "success": True,
        "session_id": session_result["session_id"],
        "token": session_result["token"],
        "user_profile": {
            "id": user["id"],
            "email": user["email"],
            "nama_lengkap": user["nama_lengkap"],
            "status": user["status"],
            "auth_provider": user["auth_provider"],
        },
        "message": "Login berhasil!",
    }


# ════════════════════════════════════════════════════════════
# 3. SSO GOOGLE (Stub)
# ════════════════════════════════════════════════════════════

def sso_google(google_auth_code: str = "") -> dict:
    """
    [STUB] Autentikasi melalui Google OAuth 2.0.

    Implementasi penuh memerlukan:
      1. Redirect ke Google OAuth consent page
      2. Terima authorization code dari callback
      3. Tukar code → access token via Google API
      4. Ambil profil pengguna dari Google API
      5. Buat/hubungkan akun → buat sesi

    Untuk implementasi penuh, diperlukan:
      - Google OAuth Client ID & Secret
      - Backend server dengan redirect URI
      - Library: google-auth, google-auth-oauthlib

    Return: {success: bool, message: str, ...}
    """
    return {
        "success": False,
        "message": "SSO Google belum dikonfigurasi.\nFitur ini memerlukan backend server terpisah.",
        "is_new_user": False,
    }


# ════════════════════════════════════════════════════════════
# 4. SSO APPLE (Stub)
# ════════════════════════════════════════════════════════════

def sso_apple(apple_identity_token: str = "", authorization_code: str = "") -> dict:
    """
    [STUB] Autentikasi melalui Apple Sign-In.

    Implementasi penuh memerlukan:
      1. Apple Developer Account
      2. Service ID & Private Key
      3. Verifikasi identity token via Apple API
      4. Decode profil dari JWT token
      5. Buat/hubungkan akun → buat sesi

    Mendukung fitur "Hide My Email" dari Apple.

    Return: {success: bool, message: str, ...}
    """
    return {
        "success": False,
        "message": "SSO Apple belum dikonfigurasi.\nFitur ini memerlukan backend server terpisah.",
        "is_new_user": False,
    }


# ════════════════════════════════════════════════════════════
# 5. LUPA SANDI
# ════════════════════════════════════════════════════════════

def lupa_sandi(email: str) -> dict:
    """
    Inisiasi alur pemulihan kata sandi.
    Generate OTP 6 digit → simpan → kirim ke email.

    Return: {success: bool, method: str, message: str, otp: str (DEV only)}
    """
    email = email.lower().strip()

    # Rate limit pengiriman OTP
    allowed, remaining, lockout = rate_limiter.check(email, "otp_send")
    if not allowed:
        return {
            "success": False, "method": "",
            "message": f"Terlalu banyak permintaan. Coba lagi setelah {lockout}.",
        }

    # Validasi email
    if not validate_email_format(email):
        return {"success": False, "method": "", "message": "Format email tidak valid."}

    # Cek email terdaftar
    user = get_user_by_email(email)
    if not user:
        # Pesan generik untuk mencegah email enumeration
        return {
            "success": True, "method": "otp",
            "message": "Jika email terdaftar, kode OTP akan dikirim.",
        }

    # Generate OTP
    otp = generate_otp(6)
    otp_hash = hash_password(otp)

    # Simpan ke DB (berlaku 10 menit)
    create_password_reset(user["id"], "otp", otp_hash, expires_minutes=10)

    # Kirim email
    ok, msg = email_service.send_otp(email, otp)
    rate_limiter.record_attempt(email, "otp_send")

    result = {
        "success": True, "method": "otp",
        "message": "Kode OTP telah dikirim ke email Anda.\nKode berlaku selama 10 menit.",
    }

    # Untuk DEV_MODE, sertakan OTP di response
    if email_service.dev_mode:
        result["otp_dev"] = otp

    return result


# ════════════════════════════════════════════════════════════
# 6. VERIFIKASI OTP
# ════════════════════════════════════════════════════════════

def verifikasi_otp(email: str, otp_code: str) -> dict:
    """
    Verifikasi kode OTP yang dimasukkan pengguna.

    Return: {
        valid: bool,
        reset_token: str (jika valid),
        attempts_remaining: int,
        message: str
    }
    """
    email = email.lower().strip()
    user = get_user_by_email(email)

    if not user:
        return {
            "valid": False, "reset_token": "",
            "attempts_remaining": 0, "message": "Email tidak ditemukan.",
        }

    # Ambil reset request aktif
    reset_req = get_password_reset(user["id"])
    if not reset_req:
        return {
            "valid": False, "reset_token": "",
            "attempts_remaining": 0,
            "message": "Kode OTP kedaluwarsa atau belum diminta.\nSilakan minta ulang.",
        }

    # Cek OTP
    if not verify_password(otp_code, reset_req["token_hash"]):
        # Tambah counter percobaan
        new_count = increment_reset_attempts(reset_req["id"])
        remaining = max(0, 3 - new_count)
        msg = f"Kode OTP salah. Sisa percobaan: {remaining}."
        if remaining == 0:
            msg = "Kode OTP di-invalidasi.\nSilakan minta kode baru."
        return {
            "valid": False, "reset_token": "",
            "attempts_remaining": remaining, "message": msg,
        }

    # OTP valid! Generate reset token
    reset_token = generate_token()

    return {
        "valid": True,
        "reset_token": reset_token,
        "attempts_remaining": -1,
        "message": "Kode OTP valid! Silakan buat kata sandi baru.",
    }


# ════════════════════════════════════════════════════════════
# 7. RESET PASSWORD
# ════════════════════════════════════════════════════════════

def reset_password(email: str, new_password: str,
                   confirm_new_password: str) -> dict:
    """
    Atur kata sandi baru setelah verifikasi OTP berhasil.

    Validasi:
      - Kekuatan password baru
      - Password baru != 3 password terakhir
      - new_password == confirm_new_password

    Return: {success: bool, message: str}
    """
    email = email.lower().strip()
    user = get_user_by_email(email)
    if not user:
        return {"success": False, "message": "Akun tidak ditemukan."}

    # Validasi kekuatan
    valid, errors = validate_password_strength(new_password)
    if not valid:
        return {"success": False, "message": "Password baru lemah:\n• " + "\n• ".join(errors)}

    # Cocokkan
    if new_password != confirm_new_password:
        return {"success": False, "message": "Konfirmasi kata sandi tidak cocok."}

    # Cek riwayat password
    history = get_password_history(user["id"], limit=3)
    if check_password_history(new_password, history):
        return {
            "success": False,
            "message": "Kata sandi baru tidak boleh sama dengan\n3 kata sandi terakhir.",
        }

    # Hash & simpan
    new_hash = hash_password(new_password)
    update_user_password(user["id"], new_hash)
    add_password_history(user["id"], new_hash)

    # Invalidasi semua sesi aktif (force re-login)
    invalidate_all_sessions(user["id"])

    # Invalidasi semua reset request
    reset_req = get_password_reset(user["id"])
    if reset_req:
        use_password_reset(reset_req["id"])

    # Reset current session
    global _current_session
    _current_session = {"session_id": None, "user_id": None, "token": None}

    return {"success": True, "message": "Kata sandi berhasil diperbarui!\nSilakan login kembali."}


# ════════════════════════════════════════════════════════════
# 8. BUAT SESI
# ════════════════════════════════════════════════════════════

def buat_sesi(user_id: str, device_info: dict = None,
              ip_address: str = "127.0.0.1") -> dict:
    """
    Membuat sesi pengguna yang aman.

    Return: {session_id: str, token: str, expires_at: str}
    """
    token = generate_session_token()
    token_hash = hash_password(token)

    session_id, _, expires_at = create_session(
        user_id, token_hash, device_info, ip_address, expires_days=7
    )

    # Set current session
    global _current_session
    _current_session = {
        "session_id": session_id,
        "user_id": user_id,
        "token": token,
    }

    return {
        "session_id": session_id,
        "token": token,
        "expires_at": expires_at,
    }


# ════════════════════════════════════════════════════════════
# 9. REFRESH TOKEN
# ════════════════════════════════════════════════════════════

def refresh_token_fn(session_id: str) -> dict:
    """
    Perbarui session yang kedaluwarsa.
    Implementasi token rotation: session lama di-invalidasi.

    Return: {success: bool, session_id: str, token: str, expires_at: str, message: str}
    """
    old_session = get_session(session_id)
    if not old_session:
        return {
            "success": False, "session_id": "", "token": "",
            "expires_at": "", "message": "Sesi tidak valid atau kedaluwarsa.",
        }

    # Invalidasi sesi lama
    invalidate_session(session_id)

    # Buat sesi baru
    new_session = buat_sesi(old_session["user_id"])

    return {
        "success": True,
        "session_id": new_session["session_id"],
        "token": new_session["token"],
        "expires_at": new_session["expires_at"],
        "message": "Sesi diperbarui.",
    }


# ════════════════════════════════════════════════════════════
# 10. LOGOUT PENGGUNA
# ════════════════════════════════════════════════════════════

def logout_pengguna(logout_all_devices: bool = False) -> dict:
    """
    Mengakhiri sesi pengguna.

    Args:
      logout_all_devices: True → logout dari semua perangkat

    Return: {success: bool, message: str}
    """
    global _current_session

    if not _current_session["session_id"]:
        return {"success": True, "message": "Sudah logout."}

    user_id = _current_session["user_id"]

    if logout_all_devices:
        invalidate_all_sessions(user_id)
    else:
        invalidate_session(_current_session["session_id"])

    _current_session = {"session_id": None, "user_id": None, "token": None}

    return {"success": True, "message": "Logout berhasil."}


# ════════════════════════════════════════════════════════════
# 11. VALIDASI INPUT (Wrapper)
# ════════════════════════════════════════════════════════════

def validasi_input(field_name: str, field_value: str,
                   validation_rules: dict = None) -> dict:
    """
    Melakukan validasi terhadap input pengguna.

    Return: {valid: bool, errors: list[str]}
    """
    errors = []
    value = sanitize_input(field_value)

    if field_name == "email":
        if not value:
            errors.append("Email tidak boleh kosong.")
        elif not validate_email_format(value):
            errors.append("Format email tidak valid.")

    elif field_name == "password":
        valid, pwd_errors = validate_password_strength(value)
        if not valid:
            errors.extend(pwd_errors)

    elif field_name == "nama_lengkap":
        if not value or len(value) < 2:
            errors.append("Nama lengkap minimal 2 karakter.")

    elif field_name == "otp":
        if not value or len(value) != 6 or not value.isdigit():
            errors.append("Kode OTP harus 6 digit angka.")

    return {"valid": len(errors) == 0, "errors": errors}


# ════════════════════════════════════════════════════════════
# 12. GET CURRENT USER
# ════════════════════════════════════════════════════════════

def get_current_user() -> dict | None:
    """
    Ambil data user yang sedang login berdasarkan session aktif.
    Return: dict user atau None.
    """
    if not _current_session["user_id"]:
        return None
    return get_user_by_id(_current_session["user_id"])


def get_current_session() -> dict:
    """Ambil info session aktif."""
    return _current_session.copy()


def is_authenticated() -> bool:
    """Cek apakah ada user yang sedang login."""
    return _current_session["user_id"] is not None
