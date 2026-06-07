"""
test_register_blackbox.py
Beaply — Blackbox Testing: Register Page (Sign Up)

Mencakup skenario pengujian berdasarkan sheet referensi:
  TC-REG-01  : Data wajib lengkap & valid → registrasi berhasil
  TC-REG-02  : Semua field kosong → tolak
  TC-REG-03  : Hanya satu field diisi → tolak
  TC-REG-04  : Field (*) diisi semua, email tanpa @(...).com bagian domain → tolak
  TC-REG-05  : Field (*) diisi semua, email hanya pakai @(...) tanpa TLD → tolak
  TC-REG-06  : Password tanpa simbol khusus → tolak
  TC-REG-07  : Password tanpa huruf besar → tolak
  TC-REG-08  : Password tanpa angka → tolak
  TC-REG-09  : Tanggal lahir hari melebihi 31 → tolak
  TC-REG-10  : Email sudah terdaftar → tolak
  TC-REG-11  : Nama < 2 karakter → tolak
  TC-REG-12  : GPA di luar range (0.00-4.00) → tolak
  TC-REG-13  : Semester 0 atau negatif → tolak
  TC-REG-14  : IELTS score di luar range (0.0-9.0) → tolak
  TC-REG-15  : TOEFL score di luar range (0-120) → tolak
  TC-REG-16  : Tanggal lahir format salah → tolak
  TC-REG-17  : Data valid + field opsional terisi → registrasi berhasil

Cara menjalankan:
  cd c:\\PROYEK1\\Beaply
  .venv\\Scripts\\python.exe -m pytest test_register_blackbox.py -v
  atau:
  .venv\\Scripts\\python.exe test_register_blackbox.py
"""

import sys
import os
import sqlite3
import unittest

# ── Pastikan root proyek ada di sys.path ────────────────────
_root = os.path.abspath(os.path.dirname(__file__))
if _root not in sys.path:
    sys.path.insert(0, _root)

# ── Inisialisasi database sebelum import controller ──────────
from database import init_db
init_db()

from controllers.auth_controller import init_auth, register as _register
init_auth()

from controllers.profil_controller import (
    input_data_wajib, input_data_spesifik, simpan_profil,
)
from models.auth_model import get_user_by_email
from models.database import get_connection


# ════════════════════════════════════════════════════════════
# HELPER
# ════════════════════════════════════════════════════════════

def _hapus_user_by_email(email: str):
    """Hapus user test dari DB agar bisa dipakai ulang."""
    try:
        conn = get_connection()
        conn.execute("DELETE FROM users WHERE email = ?", (email.lower(),))
        conn.commit()
        conn.close()
    except Exception:
        pass


def _data_wajib_valid(**overrides) -> dict:
    """Kembalikan dict data wajib yang valid; field bisa di-override."""
    base = {
        "nama":           "Tutut Puspitasari",
        "tanggal_lahir":  "2005-12-30",
        "email":          "tutut.valid@gmail.com",
        "jurusan":        "Teknik Informatika",
        "kampus":         "Universitas Padjadjaran",
        "semester":       "4",
        "ip":             "3.50",
        "jenjang":        "S1",
        "jenis_kelamin":  "Perempuan",
        "aktif_organisasi": False,
    }
    base.update(overrides)
    return base


def _make_spesifik(status_kip=False, skor_ielts="", skor_toefl="",
                   skor_duolingo="", skor_sat="", skor_act="",
                   skor_gre="", skor_gmat="", skor_hsk="", level_jlpt=""):
    """Buat dict data spesifik; semua opsional kecuali status_kip."""
    return input_data_spesifik(
        status_kip, skor_ielts, skor_toefl, skor_duolingo,
        skor_sat, skor_act, skor_gre, skor_gmat, skor_hsk, level_jlpt,
    )


def _do_full_register(nama, email, password,
                      tanggal_lahir="2005-12-30",
                      jurusan="Teknik Informatika",
                      kampus="Universitas Padjadjaran",
                      semester="4",
                      ip="3.50",
                      jenjang="S1",
                      jenis_kelamin="Perempuan",
                      aktif_organisasi=False,
                      **spesifik_overrides):
    """
    Simulasi alur lengkap registrasi:
      1. auth_controller.register  (buat user)
      2. profil_controller.simpan_profil  (buat profil)
    Return: (ok: bool, msg: str, uid, pid)
    """
    ok, msg, uid = _register(nama, email, password, password)
    if not ok:
        return False, msg, None, None

    dw = input_data_wajib(
        nama, tanggal_lahir, email, jurusan, kampus,
        semester, ip, jenjang, jenis_kelamin, aktif_organisasi,
    )
    ds = _make_spesifik(**spesifik_overrides)
    ok2, msg2, pid = simpan_profil(dw, ds, user_id=uid)
    if not ok2:
        return False, msg2, uid, None
    return True, "Registrasi berhasil.", uid, pid


# ════════════════════════════════════════════════════════════
# TEST CLASS
# ════════════════════════════════════════════════════════════

class TestRegisterPage(unittest.TestCase):
    """
    Blackbox tests untuk alur registrasi (Sign Up) Beaply.
    Setiap test case berdiri sendiri; cleanup dilakukan di setUp/tearDown.
    """

    # ── email unik per test agar tidak konflik ───────────────
    VALID_EMAIL = "tc.reg.01@beaplytest.com"
    DUP_EMAIL   = "tc.reg.10.dup@beaplytest.com"

    @classmethod
    def setUpClass(cls):
        """Bersihkan email test sebelum suite dimulai."""
        for em in [cls.VALID_EMAIL, cls.DUP_EMAIL]:
            _hapus_user_by_email(em)

    @classmethod
    def tearDownClass(cls):
        """Bersihkan email test setelah suite selesai."""
        for em in [cls.VALID_EMAIL, cls.DUP_EMAIL]:
            _hapus_user_by_email(em)

    def _cleanup(self, *emails):
        for e in emails:
            _hapus_user_by_email(e)

    # ────────────────────────────────────────────────────────
    # TC-REG-01 : Data wajib lengkap & valid → berhasil
    # ────────────────────────────────────────────────────────
    def test_01_register_data_valid_berhasil(self):
        """TC-REG-01 | Semua data wajib valid → registrasi berhasil."""
        email = self.VALID_EMAIL
        self._cleanup(email)

        ok, msg, uid, pid = _do_full_register(
            nama="Tutut Puspitasari",
            email=email,
            password="Tutut123!",
        )
        print(f"\n[TC-REG-01] ok={ok}, msg={msg}")
        self.assertTrue(ok, f"Seharusnya berhasil, tapi: {msg}")
        self.assertIsNotNone(uid)
        self.assertIsNotNone(pid)

        # Cleanup
        self._cleanup(email)

    # ────────────────────────────────────────────────────────
    # TC-REG-02 : Semua field kosong → tolak
    # ────────────────────────────────────────────────────────
    def test_02_semua_field_kosong_ditolak(self):
        """TC-REG-02 | Tidak ada field yang diisi → gagal validasi."""
        ok, msg, uid = _register("", "", "", "")
        print(f"\n[TC-REG-02] ok={ok}, msg={msg}")
        self.assertFalse(ok, "Harus gagal jika semua field kosong.")

    # ────────────────────────────────────────────────────────
    # TC-REG-03 : Hanya satu field diisi (nama saja)
    # ────────────────────────────────────────────────────────
    def test_03_hanya_satu_field_diisi_ditolak(self):
        """TC-REG-03 | Hanya nama diisi, email & password kosong → gagal."""
        ok, msg, uid = _register("Tutut", "", "", "")
        print(f"\n[TC-REG-03] ok={ok}, msg={msg}")
        self.assertFalse(ok, "Harus gagal jika email & password kosong.")

    # ────────────────────────────────────────────────────────
    # TC-REG-04 : Email tanpa karakter '@'
    # ────────────────────────────────────────────────────────
    def test_04_email_tanpa_at_ditolak(self):
        """TC-REG-04 | Email tanpa '@' → format tidak valid."""
        ok, msg, uid = _register("Tutut", "tutgmail.com", "Tutut123!", "Tutut123!")
        print(f"\n[TC-REG-04] ok={ok}, msg={msg}")
        self.assertFalse(ok)
        self.assertIn("email", msg.lower(), f"Pesan error tidak menyebut 'email': {msg}")

    # ────────────────────────────────────────────────────────
    # TC-REG-05 : Email hanya pakai @(...) tanpa TLD
    # ────────────────────────────────────────────────────────
    def test_05_email_tanpa_tld_ditolak(self):
        """TC-REG-05 | Email seperti 'tut@gmail' (tanpa .com) → format tidak valid."""
        ok, msg, uid = _register("Tutut", "tut@gmail", "Tutut123!", "Tutut123!")
        print(f"\n[TC-REG-05] ok={ok}, msg={msg}")
        self.assertFalse(ok)
        self.assertIn("email", msg.lower(), f"Pesan error tidak menyebut 'email': {msg}")

    # ────────────────────────────────────────────────────────
    # TC-REG-06 : Password tanpa simbol khusus
    # ────────────────────────────────────────────────────────
    def test_06_password_tanpa_simbol_ditolak(self):
        """TC-REG-06 | Password 'Tut123456789' (tanpa simbol) → gagal."""
        ok, msg, uid = _register("Tutut", "tut06@test.com", "Tut123456789", "Tut123456789")
        print(f"\n[TC-REG-06] ok={ok}, msg={msg}")
        self.assertFalse(ok)
        # Pastikan pesan error menyinggung simbol
        self.assertTrue(
            "simbol" in msg.lower() or "symbol" in msg.lower() or "!" in msg,
            f"Pesan error seharusnya menyebut simbol: {msg}"
        )

    # ────────────────────────────────────────────────────────
    # TC-REG-07 : Password tanpa huruf besar
    # ────────────────────────────────────────────────────────
    def test_07_password_tanpa_huruf_besar_ditolak(self):
        """TC-REG-07 | Password 'tutut123!' (tanpa huruf besar) → gagal."""
        ok, msg, uid = _register("Tutut", "tut07@test.com", "tutut123!", "tutut123!")
        print(f"\n[TC-REG-07] ok={ok}, msg={msg}")
        self.assertFalse(ok)
        self.assertTrue(
            "besar" in msg.lower() or "upper" in msg.lower() or "A-Z" in msg,
            f"Pesan error seharusnya menyebut huruf besar: {msg}"
        )

    # ────────────────────────────────────────────────────────
    # TC-REG-08 : Password tanpa angka
    # ────────────────────────────────────────────────────────
    def test_08_password_tanpa_angka_ditolak(self):
        """TC-REG-08 | Password 'Tutut!!!' (tanpa angka) → gagal."""
        ok, msg, uid = _register("Tutut", "tut08@test.com", "Tutut!!!", "Tutut!!!")
        print(f"\n[TC-REG-08] ok={ok}, msg={msg}")
        self.assertFalse(ok)
        self.assertTrue(
            "angka" in msg.lower() or "digit" in msg.lower() or "0-9" in msg,
            f"Pesan error seharusnya menyebut angka: {msg}"
        )

    # ────────────────────────────────────────────────────────
    # TC-REG-09 : Tanggal lahir hari > 31
    # ────────────────────────────────────────────────────────
    def test_09_tanggal_hari_melebihi_31_ditolak(self):
        """TC-REG-09 | Tanggal lahir '2005-12-35' (hari > 31) → gagal profil."""
        email = "tut09@test.com"
        self._cleanup(email)

        # Register user dulu (hanya auth)
        ok_auth, msg_auth, uid = _register("Tutut", email, "Tutut123!", "Tutut123!")
        self.assertTrue(ok_auth, f"Register auth gagal: {msg_auth}")

        # Coba simpan profil dengan tanggal invalid
        dw = input_data_wajib(
            "Tutut", "2005-12-35", email,
            "Teknik Informatika", "Unpad", "4", "3.50", "S1", "Perempuan"
        )
        ds = _make_spesifik()
        ok_p, msg_p, pid = simpan_profil(dw, ds, user_id=uid)
        print(f"\n[TC-REG-09] ok={ok_p}, msg={msg_p}")
        self.assertFalse(ok_p, "Seharusnya gagal karena tanggal lahir tidak valid.")
        self.assertTrue(
            "tanggal" in msg_p.lower() or "date" in msg_p.lower() or "format" in msg_p.lower(),
            f"Pesan harus menyebut tanggal/format: {msg_p}"
        )
        self._cleanup(email)

    # ────────────────────────────────────────────────────────
    # TC-REG-10 : Email sudah terdaftar → tolak
    # ────────────────────────────────────────────────────────
    def test_10_email_sudah_terdaftar_ditolak(self):
        """TC-REG-10 | Email yang sudah digunakan → 'Email sudah terdaftar'."""
        email = self.DUP_EMAIL
        self._cleanup(email)

        # Daftar pertama — harus berhasil
        ok1, msg1, uid1 = _register("Tutut", email, "Tutut123!", "Tutut123!")
        self.assertTrue(ok1, f"Pendaftaran pertama gagal: {msg1}")

        # Daftar kedua dengan email yang sama — harus gagal
        ok2, msg2, uid2 = _register("Tutut Dua", email, "Tutut456@", "Tutut456@")
        print(f"\n[TC-REG-10] ok={ok2}, msg={msg2}")
        self.assertFalse(ok2, "Seharusnya gagal karena email sudah terdaftar.")
        self.assertIn("terdaftar", msg2.lower(),
                      f"Pesan harus menyebut 'terdaftar': {msg2}")
        self._cleanup(email)

    # ────────────────────────────────────────────────────────
    # TC-REG-11 : Nama < 2 karakter → tolak
    # ────────────────────────────────────────────────────────
    def test_11_nama_terlalu_pendek_ditolak(self):
        """TC-REG-11 | Nama 1 karakter → gagal validasi nama."""
        ok, msg, uid = _register("T", "tut11@test.com", "Tutut123!", "Tutut123!")
        print(f"\n[TC-REG-11] ok={ok}, msg={msg}")
        self.assertFalse(ok)
        self.assertTrue(
            "nama" in msg.lower() or "karakter" in msg.lower(),
            f"Pesan harus menyebut nama/karakter: {msg}"
        )

    # ────────────────────────────────────────────────────────
    # TC-REG-12 : GPA di luar range (> 4.00)
    # ────────────────────────────────────────────────────────
    def test_12_gpa_di_luar_range_ditolak(self):
        """TC-REG-12 | GPA = 4.50 (> 4.00) → gagal validasi profil."""
        email = "tut12@test.com"
        self._cleanup(email)

        ok_auth, msg_auth, uid = _register("Tutut", email, "Tutut123!", "Tutut123!")
        self.assertTrue(ok_auth, f"Auth gagal: {msg_auth}")

        dw = input_data_wajib(
            "Tutut", "2005-12-30", email,
            "Teknik Informatika", "Unpad", "4", "4.50", "S1", "Perempuan"
        )
        ds = _make_spesifik()
        ok_p, msg_p, pid = simpan_profil(dw, ds, user_id=uid)
        print(f"\n[TC-REG-12] ok={ok_p}, msg={msg_p}")
        self.assertFalse(ok_p, "Seharusnya gagal karena GPA > 4.00.")
        self.assertTrue(
            "ip" in msg_p.lower() or "gpa" in msg_p.lower() or "4.00" in msg_p,
            f"Pesan harus menyebut IP/GPA: {msg_p}"
        )
        self._cleanup(email)

    # ────────────────────────────────────────────────────────
    # TC-REG-13 : Semester 0 atau negatif
    # ────────────────────────────────────────────────────────
    def test_13_semester_nol_ditolak(self):
        """TC-REG-13 | Semester = 0 → gagal validasi profil."""
        email = "tut13@test.com"
        self._cleanup(email)

        ok_auth, msg_auth, uid = _register("Tutut", email, "Tutut123!", "Tutut123!")
        self.assertTrue(ok_auth, f"Auth gagal: {msg_auth}")

        dw = input_data_wajib(
            "Tutut", "2005-12-30", email,
            "Teknik Informatika", "Unpad", "0", "3.50", "S1", "Perempuan"
        )
        ds = _make_spesifik()
        ok_p, msg_p, pid = simpan_profil(dw, ds, user_id=uid)
        print(f"\n[TC-REG-13] ok={ok_p}, msg={msg_p}")
        self.assertFalse(ok_p, "Seharusnya gagal karena semester = 0.")
        self.assertTrue(
            "semester" in msg_p.lower(),
            f"Pesan harus menyebut semester: {msg_p}"
        )
        self._cleanup(email)

    # ────────────────────────────────────────────────────────
    # TC-REG-14 : IELTS score di luar range (0.0-9.0)
    # ────────────────────────────────────────────────────────
    def test_14_ielts_out_of_range_ditolak(self):
        """TC-REG-14 | IELTS = 10.0 (> 9.0) → gagal validasi profil."""
        email = "tut14@test.com"
        self._cleanup(email)

        ok_auth, msg_auth, uid = _register("Tutut", email, "Tutut123!", "Tutut123!")
        self.assertTrue(ok_auth, f"Auth gagal: {msg_auth}")

        dw = input_data_wajib(
            "Tutut", "2005-12-30", email,
            "Teknik Informatika", "Unpad", "4", "3.50", "S1", "Perempuan"
        )
        ds = _make_spesifik(skor_ielts="10.0")
        ok_p, msg_p, pid = simpan_profil(dw, ds, user_id=uid)
        print(f"\n[TC-REG-14] ok={ok_p}, msg={msg_p}")
        self.assertFalse(ok_p, "Seharusnya gagal karena IELTS > 9.0.")
        self.assertTrue(
            "ielts" in msg_p.lower() or "0–9" in msg_p or "0.0" in msg_p,
            f"Pesan harus menyebut IELTS: {msg_p}"
        )
        self._cleanup(email)

    # ────────────────────────────────────────────────────────
    # TC-REG-15 : TOEFL score di luar range (0-120)
    # ────────────────────────────────────────────────────────
    def test_15_toefl_out_of_range_ditolak(self):
        """TC-REG-15 | TOEFL iBT = 130 (> 120) → gagal validasi profil."""
        email = "tut15@test.com"
        self._cleanup(email)

        ok_auth, msg_auth, uid = _register("Tutut", email, "Tutut123!", "Tutut123!")
        self.assertTrue(ok_auth, f"Auth gagal: {msg_auth}")

        dw = input_data_wajib(
            "Tutut", "2005-12-30", email,
            "Teknik Informatika", "Unpad", "4", "3.50", "S1", "Perempuan"
        )
        ds = _make_spesifik(skor_toefl="130")
        ok_p, msg_p, pid = simpan_profil(dw, ds, user_id=uid)
        print(f"\n[TC-REG-15] ok={ok_p}, msg={msg_p}")
        self.assertFalse(ok_p, "Seharusnya gagal karena TOEFL > 120.")
        self.assertTrue(
            "toefl" in msg_p.lower() or "120" in msg_p,
            f"Pesan harus menyebut TOEFL: {msg_p}"
        )
        self._cleanup(email)

    # ────────────────────────────────────────────────────────
    # TC-REG-16 : Tanggal lahir format salah (bukan YYYY-MM-DD)
    # ────────────────────────────────────────────────────────
    def test_16_tanggal_format_salah_ditolak(self):
        """TC-REG-16 | Tanggal '30-12-2005' (format salah) → gagal validasi profil."""
        email = "tut16@test.com"
        self._cleanup(email)

        ok_auth, msg_auth, uid = _register("Tutut", email, "Tutut123!", "Tutut123!")
        self.assertTrue(ok_auth, f"Auth gagal: {msg_auth}")

        dw = input_data_wajib(
            "Tutut", "30-12-2005", email,
            "Teknik Informatika", "Unpad", "4", "3.50", "S1", "Perempuan"
        )
        ds = _make_spesifik()
        ok_p, msg_p, pid = simpan_profil(dw, ds, user_id=uid)
        print(f"\n[TC-REG-16] ok={ok_p}, msg={msg_p}")
        self.assertFalse(ok_p, "Seharusnya gagal karena format tanggal salah.")
        self.assertTrue(
            "tanggal" in msg_p.lower() or "format" in msg_p.lower() or "yyyy" in msg_p.lower(),
            f"Pesan harus menyebut format tanggal: {msg_p}"
        )
        self._cleanup(email)

    # ────────────────────────────────────────────────────────
    # TC-REG-17 : Data valid + field opsional terisi → berhasil
    # ────────────────────────────────────────────────────────
    def test_17_data_valid_dengan_data_opsional_berhasil(self):
        """TC-REG-17 | Data valid + IELTS 7.5, TOEFL 100, KIP checked → berhasil."""
        email = "tut17@test.com"
        self._cleanup(email)

        ok, msg, uid, pid = _do_full_register(
            nama="Tutut Lengkap",
            email=email,
            password="Tutut123!",
            status_kip=True,
            skor_ielts="7.5",
            skor_toefl="100",
            skor_duolingo="120",
        )
        print(f"\n[TC-REG-17] ok={ok}, msg={msg}")
        self.assertTrue(ok, f"Seharusnya berhasil dengan data opsional: {msg}")
        self.assertIsNotNone(pid)
        self._cleanup(email)


# ════════════════════════════════════════════════════════════
# RUNNER MANUAL (python test_register_blackbox.py)
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import time
    # Ensure stdout/stderr handles UTF-8 on Windows to print emojis safely
    if sys.platform.startswith("win"):
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

    print("=" * 70)
    print("  BEAPLY — BLACKBOX TEST: REGISTER PAGE")
    print("=" * 70)

    loader  = unittest.TestLoader()
    suite   = loader.loadTestsFromTestCase(TestRegisterPage)
    runner  = unittest.TextTestRunner(verbosity=2)

    start = time.time()
    result = runner.run(suite)
    elapsed = time.time() - start

    print("\n" + "=" * 70)
    print(f"  Selesai dalam {elapsed:.2f} detik")
    print(f"  Tests run  : {result.testsRun}")
    print(f"  Errors     : {len(result.errors)}")
    print(f"  Failures   : {len(result.failures)}")
    print(f"  Skipped    : {len(result.skipped)}")

    if result.wasSuccessful():
        print("  STATUS     : ✅  SEMUA LULUS")
    else:
        print("  STATUS     : ❌  ADA KEGAGALAN")
        print("\n  Detail kegagalan:")
        for test, tb in result.failures + result.errors:
            print(f"  — {test}: {tb.splitlines()[-1]}")

    print("=" * 70)
    sys.exit(0 if result.wasSuccessful() else 1)
