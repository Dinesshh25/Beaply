"""
auth.py
Beaply - Logika Bisnis Sistem Autentikasi & Keamanan

Nama Fitur: Sistem Autentikasi dan Keamanan

Modul sesuai Detailing Modul:
  No  Nama Modul            Tipe        Penanggung Jawab
  ──  ────────────────────  ──────────  ─────────────────
   1  tampilan_auth         Procedure   Gebby Rizki Aditya
   2  registrasi_pengguna   Function    Gebby Rizki Aditya
   3  login_pengguna        Function    Gebby Rizki Aditya
   4  lupa_sandi            Procedure   Gebby Rizki Aditya
   5  verifikasi_otp        Function    Gebby Rizki Aditya
   6  reset_password        Function    Gebby Rizki Aditya
   7  buat_sesi             Function    Gebby Rizki Aditya
   8  logout_pengguna       Function    Gebby Rizki Aditya
   9  validasi_input        Function    Gebby Rizki Aditya
  10  hash_password         Function    Gebby Rizki Aditya

Catatan:
  - tampilan_auth diimplementasikan di main.py (class HalamanAuth)
  - hash_password diimplementasikan di auth_utils.py
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
# MODUL 1: tampilan_auth (Procedure)
# ════════════════════════════════════════════════════════════
#
# Tipe      : Procedure (tidak mengembalikan nilai)
# Deskripsi : Menampilkan antarmuka halaman autentikasi utama:
#             form login, form registrasi, dan tautan "Lupa Kata Sandi".
# Fitur Terkait: registrasi_pengguna, login_pengguna, lupa_sandi
# Input     : -
# Output    : -
# I.S.      : Pengguna belum terautentikasi.
# F.S.      : Form autentikasi ditampilkan dan siap menerima input.
#
# IMPLEMENTASI: di main.py → class HalamanAuth
#   - _build_login_form()    → form login (email + password)
#   - _build_register_form() → form registrasi
#   - _go_lupa_sandi()       → navigasi ke halaman lupa sandi
# ════════════════════════════════════════════════════════════


# ════════════════════════════════════════════════════════════
# MODUL 2: registrasi_pengguna (Function)
# ════════════════════════════════════════════════════════════

def registrasi_pengguna(email: str, password: str, confirm_password: str,
                        nama_lengkap: str) -> dict:
    """
    Mendaftarkan pengguna baru ke dalam sistem.

    Tipe        : Function
    Fitur Terkait: validasi_input, hash_password, kirim_email_verifikasi

    Input:
        - email (String)            : alamat email pengguna
        - password (String)         : kata sandi
        - confirm_password (String) : konfirmasi kata sandi
        - nama_lengkap (String)     : nama lengkap pengguna

    Output:
        - status_registrasi (Object: {success: Boolean, user_id: String,
                                      message: String})

    I.S. : Email belum terdaftar di database.
    F.S. : Akun pengguna tersimpan di DB dengan status 'active',
           email verifikasi terkirim.
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

    # Hash password (memanggil modul 10: hash_password)
    pwd_hash = hash_password(password)

    # Simpan ke DB
    ok, msg, user_id = create_user(email, pwd_hash, nama_lengkap, status="active")
    if not ok:
        return {"success": False, "user_id": "", "message": msg}

    # Simpan ke password history
    add_password_history(user_id, pwd_hash)

    return {"success": True, "user_id": user_id, "message": "Registrasi berhasil! Silakan login."}


# ════════════════════════════════════════════════════════════
# MODUL 3: login_pengguna (Function)
# ════════════════════════════════════════════════════════════

def login_pengguna(email: str, password: str) -> dict:
    """
    Mengautentikasi pengguna menggunakan email dan kata sandi.

    Tipe        : Function
    Fitur Terkait: validasi_input, verifikasi_password, buat_sesi, rate_limiter

    Input:
        - email (String)    : alamat email pengguna
        - password (String) : kata sandi

    Output:
        - auth_response (Object: {success: Boolean, access_token: String,
          refresh_token: String, user_profile: Object, message: String})

    I.S. : Pengguna memiliki akun terdaftar dan terverifikasi.
    F.S. : Sesi aktif dibuat, token dikirim ke klien,
           timestamp login terakhir diperbarui.
    """
    email = email.lower().strip()

    # Rate limiting (maks. 5 percobaan gagal per 15 menit)
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

    # Cek status akun (aktif/terblokir/unverified)
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
        # Update failed attempts di DB
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

    # Login berhasil! Buat sesi (memanggil modul 7: buat_sesi)
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
# MODUL 4: lupa_sandi (Procedure)
# ════════════════════════════════════════════════════════════

def lupa_sandi(email: str) -> dict:
    """
    Menginisiasi alur pemulihan kata sandi.
    Pengguna memasukkan email, sistem memverifikasi email terdaftar,
    lalu mengirim OTP (6 digit, berlaku 10 menit) ke email pengguna.

    Tipe        : Procedure
    Fitur Terkait: kirim_otp, validasi_email

    Input:
        - email (String) : alamat email pengguna

    Output:
        - status (Object: {success: Boolean, method: String,
                           message: String})

    I.S. : Pengguna memiliki akun terdaftar.
    F.S. : OTP/link reset terkirim ke email, record pemulihan tersimpan
           di DB dengan timestamp expiry.
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

    # Generate OTP 6 digit
    otp = generate_otp(6)
    otp_hash = hash_password(otp)

    # Simpan ke DB (berlaku 10 menit)
    create_password_reset(user["id"], "otp", otp_hash, expires_minutes=10)

    # Kirim email OTP
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
# MODUL 5: verifikasi_otp (Function)
# ════════════════════════════════════════════════════════════

def verifikasi_otp(email: str, otp_code: str) -> dict:
    """
    Memverifikasi kode OTP yang dimasukkan pengguna.
    Mencocokkan OTP dengan yang disimpan di database,
    memeriksa masa berlaku, dan menghitung percobaan gagal
    (maks. 3 kali sebelum OTP di-invalidasi).

    Tipe        : Function
    Fitur Terkait: lupa_sandi, reset_password

    Input:
        - email (String)    : alamat email pengguna
        - otp_code (String) : kode OTP 6 digit

    Output:
        - (Object: {valid: Boolean, reset_token: String,
                    attempts_remaining: Integer, message: String})

    I.S. : OTP telah dikirim dan belum kedaluwarsa.
    F.S. : Jika valid, reset_token sementara dihasilkan
           untuk proses reset password.
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
        # Tambah counter percobaan (maks 3 kali)
        new_count = increment_reset_attempts(reset_req["id"])
        remaining = max(0, 3 - new_count)
        msg = f"Kode OTP salah. Sisa percobaan: {remaining}."
        if remaining == 0:
            msg = "Kode OTP di-invalidasi.\nSilakan minta kode baru."
        return {
            "valid": False, "reset_token": "",
            "attempts_remaining": remaining, "message": msg,
        }

    # OTP valid! Generate reset token sementara
    reset_token = generate_token()

    return {
        "valid": True,
        "reset_token": reset_token,
        "attempts_remaining": -1,
        "message": "Kode OTP valid! Silakan buat kata sandi baru.",
    }


# ════════════════════════════════════════════════════════════
# MODUL 6: reset_password (Function)
# ════════════════════════════════════════════════════════════

def reset_password(email: str, new_password: str,
                   confirm_new_password: str) -> dict:
    """
    Mengatur kata sandi baru setelah verifikasi OTP/link berhasil.
    Memvalidasi kekuatan kata sandi baru dan memastikan tidak sama
    dengan 3 kata sandi terakhir. Kata sandi di-hash dan diperbarui
    di database.

    Tipe        : Function
    Fitur Terkait: verifikasi_otp, hash_password, validasi_input

    Input:
        - reset_token (String)          : token dari verifikasi OTP
        - new_password (String)         : kata sandi baru
        - confirm_new_password (String) : konfirmasi kata sandi baru

    Output:
        - status (Object: {success: Boolean, message: String})

    I.S. : Reset token valid dan belum kedaluwarsa.
    F.S. : Kata sandi diperbarui, semua sesi aktif dihapus
           (force re-login), reset token di-invalidasi.
    """
    email = email.lower().strip()
    user = get_user_by_email(email)
    if not user:
        return {"success": False, "message": "Akun tidak ditemukan."}

    # Validasi kekuatan password baru
    valid, errors = validate_password_strength(new_password)
    if not valid:
        return {"success": False, "message": "Password baru lemah:\n• " + "\n• ".join(errors)}

    # Cocokkan password
    if new_password != confirm_new_password:
        return {"success": False, "message": "Konfirmasi kata sandi tidak cocok."}

    # Cek riwayat 3 password terakhir
    history = get_password_history(user["id"], limit=3)
    if check_password_history(new_password, history):
        return {
            "success": False,
            "message": "Kata sandi baru tidak boleh sama dengan\n3 kata sandi terakhir.",
        }

    # Hash & simpan (memanggil modul 10: hash_password)
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
# MODUL 7: buat_sesi (Function)
# ════════════════════════════════════════════════════════════

def buat_sesi(user_id: str, device_info: dict = None,
              ip_address: str = "127.0.0.1") -> dict:
    """
    Membuat sesi pengguna yang aman. Menghasilkan access token
    (berlaku 15 menit) dan refresh token (berlaku 7 hari).
    Menyimpan informasi sesi (device, IP, timestamp) di database.

    Tipe        : Function
    Fitur Terkait: login_pengguna

    Input:
        - user_id (String)      : ID pengguna
        - device_info (Object)  : informasi device (optional)
        - ip_address (String)   : alamat IP (optional)

    Output:
        - session (Object: {access_token: String, refresh_token: String,
          expires_in: Integer, session_id: String})

    I.S. : Pengguna berhasil diautentikasi.
    F.S. : Sesi aktif tersimpan, token dihasilkan dan dikirim ke klien.
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
# MODUL 8: logout_pengguna (Function)
# ════════════════════════════════════════════════════════════

def logout_pengguna(logout_all_devices: bool = False) -> dict:
    """
    Mengakhiri sesi pengguna. Menghapus/menginvalidasi access token
    dan refresh token, membersihkan data sesi dari server dan klien.
    Mendukung logout dari satu perangkat atau semua perangkat.

    Tipe        : Function
    Fitur Terkait: buat_sesi

    Input:
        - session_id (String)           : ID sesi aktif
        - logout_all_devices (Boolean)  : True → logout semua perangkat

    Output:
        - status (Object: {success: Boolean, message: String})

    I.S. : Pengguna memiliki sesi aktif.
    F.S. : Token diinvalidasi, data sesi dihapus,
           pengguna diarahkan ke halaman login.
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
# MODUL 9: validasi_input (Function)
# ════════════════════════════════════════════════════════════

def validasi_input(field_name: str, field_value: str,
                   validation_rules: dict = None) -> dict:
    """
    Melakukan validasi terhadap semua input pengguna pada form
    autentikasi. Termasuk validasi format email (regex), kekuatan
    password, sanitasi input untuk mencegah SQL Injection dan XSS.

    Tipe        : Function
    Fitur Terkait: registrasi_pengguna, login_pengguna, reset_password

    Input:
        - field_name (String)           : nama field (email/password/nama/otp)
        - field_value (String)          : nilai yang diinput pengguna
        - validation_rules (Object)     : aturan validasi tambahan (optional)

    Output:
        - validation_result (Object: {valid: Boolean,
                                      errors: Array<String>})

    I.S. : Input pengguna diterima dari form.
    F.S. : Hasil validasi dikembalikan dengan detail error jika ada.
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
# MODUL 10: hash_password (Function)
# ════════════════════════════════════════════════════════════
#
# Tipe        : Function
# Deskripsi   : Melakukan hashing kata sandi menggunakan algoritma
#               bcrypt dengan salt factor 12. Digunakan saat registrasi
#               dan reset kata sandi.
# Fitur Terkait: registrasi_pengguna, reset_password
#
# Input:
#     - plain_password (String) : kata sandi dalam bentuk plaintext
#
# Output:
#     - hashed_password (String) : kata sandi dalam bentuk hash bcrypt
#                                  yang aman untuk disimpan.
#
# I.S. : Kata sandi dalam bentuk plaintext.
# F.S. : Kata sandi dalam bentuk hash bcrypt yang aman untuk disimpan.
#
# IMPLEMENTASI: di auth_utils.py → def hash_password()
# ════════════════════════════════════════════════════════════


# ════════════════════════════════════════════════════════════
# HELPER: get_current_user & is_authenticated
# ════════════════════════════════════════════════════════════

def get_current_user() -> dict | None:
    """Ambil data user yang sedang login berdasarkan session aktif."""
    if not _current_session["user_id"]:
        return None
    return get_user_by_id(_current_session["user_id"])


def get_current_session() -> dict:
    """Ambil info session aktif."""
    return _current_session.copy()


def is_authenticated() -> bool:
    """Cek apakah ada user yang sedang login."""
    return _current_session["user_id"] is not None
