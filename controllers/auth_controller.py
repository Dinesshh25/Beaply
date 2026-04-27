import uuid
import random
import string
from model import auth_model

def generate_otp(length=6):
    return "".join(random.choices(string.digits, k=length))

class AuthController:
    def __init__(self, main_controller):
        self.main_controller = main_controller
        self.view = None
        self.lupa_sandi_view = None

    def mount_views(self, auth_view_cls, lupa_sandi_view_cls):
        self.auth_view_cls = auth_view_cls
        self.lupa_sandi_view_cls = lupa_sandi_view_cls

    def tampilkan_auth(self):
        """Merender HalamanAuth di container uatama."""
        self.view = self.auth_view_cls(self.main_controller.get_container(), self)
        self.main_controller.show_view(self.view)

    def tampilkan_lupa_sandi(self):
        """Merender HalamanLupaSandi di container utama."""
        self.lupa_sandi_view = self.lupa_sandi_view_cls(self.main_controller.get_container(), self)
        self.main_controller.show_view(self.lupa_sandi_view)

    def proses_login(self, email, password):
        email_clean = email.lower().strip()
        user = auth_model.get_user_by_email(email_clean)
        
        if not user:
            self.view.tampilkan_error_login("Email atau kata sandi salah.")
            return

        if not auth_model.verify_password(password, user["password_hash"]):
            auth_model.update_login_attempts(user["id"], user["failed_login_attempts"] + 1)
            self.view.tampilkan_error_login("Email atau kata sandi salah.")
            return
            
        # Success
        auth_model.update_last_login(user["id"])
        
        # Beritahu main_controller tentang succesful login and kirim user profile.
        # Simulasi user_profile dictionary
        user_profile = {
            "id": user["id"],
            "email": user["email"],
            "nama_lengkap": user["nama_lengkap"]
        }
        self.main_controller.on_login_success(user_profile)

    def proses_register(self, nama, email, pwd, confirm):
        email_clean = email.lower().strip()
        if not auth_model.validate_email_format(email_clean):
            self.view.tampilkan_error_register("Format email tidak valid.")
            return
        if pwd != confirm:
            self.view.tampilkan_error_register("Konfirmasi kata sandi tidak cocok.")
            return
            
        valid, errors = auth_model.validate_password_strength(pwd)
        if not valid:
            self.view.tampilkan_error_register("Password lemah: " + ", ".join(errors))
            return
            
        user = auth_model.get_user_by_email(email_clean)
        if user:
            self.view.tampilkan_error_register("Email sudah terdaftar.")
            return
            
        hashed_pwd = auth_model.hash_password(pwd)
        ok, msg, user_id = auth_model.create_user(email_clean, hashed_pwd, nama)
        if ok:
            self.view.tampilkan_pesan_sukses("Akun berhasi didaftarkan! Silakan login.")
        else:
            self.view.tampilkan_error_register("Terjadi kesalahan sistem: " + msg)

    def proses_permintaan_otp(self, email):
        email_clean = email.lower().strip()
        user = auth_model.get_user_by_email(email_clean)
        if not user:
            self.lupa_sandi_view.tampilkan_error_lupa("Email tidak ditemukan.")
            return
            
        otp = generate_otp(6)
        otp_hash = auth_model.hash_password(otp)
        auth_model.create_password_reset(user["id"], "otp", otp_hash)
        
        # Secara lokal pass plaintext otp ke UI untuk bypass email provider
        self.lupa_sandi_view.lanjut_ke_step2(otp)

    def proses_verifikasi_otp(self, email, otp):
        user = auth_model.get_user_by_email(email.lower().strip())
        if not user:
            self.lupa_sandi_view.tampilkan_error_otp("Terjadi kesalahan sesi email.")
            return
            
        req = auth_model.get_password_reset(user["id"])
        if not req:
            self.lupa_sandi_view.tampilkan_error_otp("Kode OTP kedaluwarsa atau tidak valid.")
            return
            
        if not auth_model.verify_password(otp, req["token_hash"]):
            auth_model.increment_reset_attempts(req["id"])
            self.lupa_sandi_view.tampilkan_error_otp("Kode OTP salah.")
            return
            
        # Berhasil diverifikasi
        reset_token = uuid.uuid4().hex
        self.lupa_sandi_view.lanjut_ke_step3(reset_token)

    def proses_reset_password(self, email, pwd, confirm):
        if pwd != confirm:
            self.lupa_sandi_view.tampilkan_error_reset("Konfirmasi kata sandi tidak cocok.")
            return
            
        valid, errors = auth_model.validate_password_strength(pwd)
        if not valid:
            self.lupa_sandi_view.tampilkan_error_reset("Password lemah: " + ", ".join(errors))
            return
            
        user = auth_model.get_user_by_email(email.lower().strip())
        new_hash = auth_model.hash_password(pwd)
        auth_model.update_user_password(user["id"], new_hash)
        
        req = auth_model.get_password_reset(user["id"])
        if req:
            auth_model.use_password_reset(req["id"])
            
        self.lupa_sandi_view.tampilkan_pesan_sukses("Password berhasil diubah, silahkan login.")
