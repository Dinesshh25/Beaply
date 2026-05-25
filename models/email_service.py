"""
email_service.py
Beaply - Layanan Pengiriman Email (OTP, Reset Link, Verifikasi)

Mendukung dua mode:
  - DEV_MODE = True  → OTP/link ditampilkan di console (untuk testing)
  - DEV_MODE = False → email dikirim melalui SMTP
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# ════════════════════════════════════════════════════════════
# KONFIGURASI SMTP
# Isi kredensial ini untuk menggunakan pengiriman email asli.
# ════════════════════════════════════════════════════════════

SMTP_HOST = ""          # contoh: "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = ""          # contoh: "beaply.app@gmail.com"
SMTP_PASS = ""          # contoh: app password dari Google
SENDER_NAME = "Beaply"
SENDER_EMAIL = ""       # contoh: "beaply.app@gmail.com"

# Jika True, OTP dan link akan ditampilkan di console / dialog
# Berguna untuk testing tanpa set up SMTP
DEV_MODE = True


class EmailService:
    """Layanan pengiriman email untuk autentikasi Beaply."""

    def __init__(self):
        self.dev_mode = DEV_MODE
        self._last_otp = None       # untuk diakses GUI saat DEV_MODE
        self._last_link = None

    @property
    def last_otp(self):
        """Ambil OTP terakhir yang dikirim (hanya untuk DEV_MODE)."""
        return self._last_otp

    @property
    def last_link(self):
        """Ambil link reset terakhir (hanya untuk DEV_MODE)."""
        return self._last_link

    def send_otp(self, email: str, otp_code: str) -> tuple:
        """
        Kirim kode OTP ke email pengguna.
        Return: (sukses: bool, pesan: str)
        """
        self._last_otp = otp_code

        if self.dev_mode:
            print(f"[DEV] OTP untuk {email}: {otp_code}")
            return True, f"[DEV MODE] OTP: {otp_code}"

        subject = "Beaply — Kode Verifikasi OTP Anda"
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <div style="max-width: 500px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563EB;">🎓 Beaply</h2>
                <p>Hai,</p>
                <p>Kode OTP Anda untuk reset kata sandi:</p>
                <div style="background: #F3F4F6; padding: 20px; text-align: center;
                            border-radius: 8px; margin: 20px 0;">
                    <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px;
                                 color: #1F2937;">{otp_code}</span>
                </div>
                <p style="color: #6B7280; font-size: 14px;">
                    Kode ini berlaku selama <strong>10 menit</strong>.<br>
                    Jika Anda tidak meminta kode ini, abaikan email ini.
                </p>
                <hr style="border: none; border-top: 1px solid #E5E7EB; margin: 20px 0;">
                <p style="color: #9CA3AF; font-size: 12px;">
                    © Beaply — Insight Beasiswa untuk Mahasiswa
                </p>
            </div>
        </body>
        </html>
        """
        return self._send_email(email, subject, body)

    def send_reset_link(self, email: str, reset_url: str) -> tuple:
        """
        Kirim tautan reset kata sandi ke email.
        Return: (sukses: bool, pesan: str)
        """
        self._last_link = reset_url

        if self.dev_mode:
            print(f"[DEV] Reset link untuk {email}: {reset_url}")
            return True, f"[DEV MODE] Link: {reset_url}"

        subject = "Beaply — Reset Kata Sandi"
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <div style="max-width: 500px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563EB;">🎓 Beaply</h2>
                <p>Hai,</p>
                <p>Anda meminta untuk mereset kata sandi. Klik tombol di bawah:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}"
                       style="background: #2563EB; color: white; padding: 12px 32px;
                              text-decoration: none; border-radius: 8px; font-weight: bold;">
                        Reset Kata Sandi
                    </a>
                </div>
                <p style="color: #6B7280; font-size: 14px;">
                    Tautan ini berlaku selama <strong>1 jam</strong>.<br>
                    Jika Anda tidak meminta reset, abaikan email ini.
                </p>
            </div>
        </body>
        </html>
        """
        return self._send_email(email, subject, body)

    def send_verification_email(self, email: str, verification_code: str) -> tuple:
        """
        Kirim email verifikasi akun.
        Return: (sukses: bool, pesan: str)
        """
        if self.dev_mode:
            print(f"[DEV] Kode verifikasi untuk {email}: {verification_code}")
            return True, f"[DEV MODE] Kode: {verification_code}"

        subject = "Beaply — Verifikasi Email Anda"
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <div style="max-width: 500px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563EB;">🎓 Beaply</h2>
                <p>Hai,</p>
                <p>Terima kasih telah mendaftar di Beaply!</p>
                <p>Kode verifikasi Anda:</p>
                <div style="background: #F3F4F6; padding: 20px; text-align: center;
                            border-radius: 8px; margin: 20px 0;">
                    <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px;
                                 color: #1F2937;">{verification_code}</span>
                </div>
            </div>
        </body>
        </html>
        """
        return self._send_email(email, subject, body)

    def _send_email(self, to_email: str, subject: str, html_body: str) -> tuple:
        """
        Kirim email via SMTP.
        Return: (sukses: bool, pesan: str)
        """
        if not SMTP_HOST or not SMTP_USER or not SMTP_PASS:
            return False, "Konfigurasi SMTP belum diisi. Aktifkan DEV_MODE untuk testing."

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
            msg["To"] = to_email
            msg.attach(MIMEText(html_body, "html"))

            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.sendmail(SENDER_EMAIL, to_email, msg.as_string())

            return True, "Email berhasil dikirim."
        except Exception as e:
            return False, f"Gagal mengirim email: {str(e)}"


# Singleton instance
email_service = EmailService()
