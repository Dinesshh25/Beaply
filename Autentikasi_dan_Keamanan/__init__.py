"""
Autentikasi_dan_Keamanan
Beaply - Package Sistem Autentikasi & Keamanan

Modul:
  - auth             : Logika bisnis autentikasi (login, register, OTP, dll.)
  - auth_database    : Tabel & CRUD SQLite untuk autentikasi
  - auth_utils       : Utilitas keamanan (bcrypt, validasi, rate limiter)
  - email_service    : Layanan pengiriman email (DEV mode / SMTP)

Detailing Modul (10 fungsi):
  1. tampilan_auth      → main.py (HalamanAuth)
  2. registrasi_pengguna
  3. login_pengguna
  4. lupa_sandi
  5. verifikasi_otp
  6. reset_password
  7. buat_sesi
  8. logout_pengguna
  9. validasi_input
 10. hash_password      → auth_utils.py
"""

from .auth import (
    init_auth,
    registrasi_pengguna,
    login_pengguna,
    lupa_sandi,
    verifikasi_otp,
    reset_password,
    logout_pengguna,
    get_current_user,
    get_current_session,
    is_authenticated,
)

from .auth_utils import (
    get_password_strength_level,
    validate_email_format,
    validate_password_strength,
    hash_password,
    verify_password,
)
