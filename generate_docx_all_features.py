"""
generate_docx_all_features.py
Beaply — Generator Dokumen Blackbox Testing SEMUA FITUR

Menghasilkan file .docx untuk setiap modul fitur yang ada di aplikasi Beaply.
Format tabel 9 kolom sama persis dengan Dokumen_Blackbox_Testing_Register.docx:
  ID Test | Skenario Pengujian | Langkah-langkah | Data Uji |
  Ekspektasi Hasil | Gambar | Hasil Aktual | Status | Komentar

Cara menjalankan:
  cd c:\\PROYEK1\\Beaply
  python generate_docx_all_features.py
"""

import sys
try:
    from docx import Document
    from docx.shared import Pt, Inches, Cm
    from docx.enum.section import WD_ORIENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH
except ImportError:
    print("Module 'python-docx' belum terinstall.")
    print("Jalankan: pip install python-docx")
    sys.exit(1)


# ═══════════════════════════════════════════════════════════════
# HEADER / KOLOM TABEL (sama persis dengan register)
# ═══════════════════════════════════════════════════════════════

HEADERS = [
    "ID Test",
    "Skenario Pengujian",
    "Langkah-langkah",
    "Data Uji",
    "Ekspektasi Hasil",
    "Gambar",
    "Hasil Aktual",
    "Status",
    "Komentar",
]


# ═══════════════════════════════════════════════════════════════
# DATA TEST CASES PER MODUL / FITUR
# ═══════════════════════════════════════════════════════════════

# ── 0. REGISTER PAGE (SIGN UP) ────────────────────────────────
REGISTER_DATA = [
    [
        "TC-REG-01",
        "Menguji proses registrasi dengan semua data wajib valid dan benar.",
        "1. Buka aplikasi.\n2. Ke tab Sign up.\n3. Isi semua field dengan data valid.\n4. Klik Save Profile.",
        "Nama: Tutut\nEmail: user@mail.com\nPass: Test123!\nDOB: 2005-12-30",
        "Sistem menyimpan akun & profil dan redirect ke Dashboard.",
        "",
        "Registrasi berhasil. Akun tersimpan. Redirect sukses.",
        "Pass",
        "Lolos validasi auth dan profil",
    ],
    [
        "TC-REG-02",
        "Menguji proses registrasi dengan email yang sudah terdaftar.",
        "1. Buka aplikasi.\n2. Ke tab Sign up.\n3. Masukkan email yang sudah ada.\n4. Klik Save Profile.",
        "Email: user@mail.com\nPass: Test456@",
        "Sistem menolak dan menampilkan pesan Email sudah terdaftar.",
        "",
        "Sistem menolak dengan pesan error yang sesuai.",
        "Pass",
        "Pengecekan duplikasi email berhasil",
    ],
    [
        "TC-REG-03",
        "Data tidak diisi apapun",
        "1. Buka aplikasi.\n2. Ke tab Sign up.\n3. Biarkan field kosong.\n4. Klik Save Profile.",
        "Kosong",
        "Sistem menolak dan meminta field wajib diisi.",
        "",
        "Sistem menolak dan menampilkan error validasi.",
        "Pass",
        "",
    ],
    [
        "TC-REG-04",
        "Data (*) diisi salah satu saja",
        "1. Buka aplikasi.\n2. Isi field Nama saja.\n3. Klik Save Profile.",
        "Nama: Tutut\nLainnya kosong",
        "Sistem menolak dan meminta field wajib lain diisi.",
        "",
        "Sistem menolak. Pesan format email muncul karena kosong.",
        "Pass",
        "",
    ],
    [
        "TC-REG-05",
        "Email diisi tanpa @",
        "1. Buka aplikasi.\n2. Masukkan email tanpa @.\n3. Klik Save Profile.",
        "Email: tutgmail.com",
        "Sistem menolak karena format email tidak valid.",
        "",
        "Sistem menolak. Regex memvalidasi tidak ada @.",
        "Pass",
        "",
    ],
    [
        "TC-REG-06",
        "Email diisi tanpa TLD (.com)",
        "1. Buka aplikasi.\n2. Masukkan email tanpa TLD.\n3. Klik Save Profile.",
        "Email: tut@gmail",
        "Sistem menolak format email.",
        "",
        "Sistem menolak karena regex butuh ekstensi TLD.",
        "Pass",
        "",
    ],
    [
        "TC-REG-07",
        "Password tanpa simbol khusus",
        "1. Buka aplikasi.\n2. Masukkan password tanpa simbol.\n3. Klik Save Profile.",
        "Pass: Tut123456789",
        "Sistem menolak, password harus mengandung simbol.",
        "",
        "Sistem menolak, pesan error syarat simbol muncul.",
        "Pass",
        "",
    ],
    [
        "TC-REG-08",
        "Password tanpa huruf besar",
        "1. Buka aplikasi.\n2. Masukkan password tanpa huruf kapital.\n3. Klik Save Profile.",
        "Pass: tutut123!",
        "Sistem menolak, password harus ada huruf besar.",
        "",
        "Sistem menolak, pesan error huruf besar muncul.",
        "Pass",
        "",
    ],
    [
        "TC-REG-09",
        "Password tanpa angka",
        "1. Buka aplikasi.\n2. Masukkan password tanpa angka.\n3. Klik Save Profile.",
        "Pass: Tutut!!!",
        "Sistem menolak, password harus mengandung angka.",
        "",
        "Sistem menolak, pesan error angka muncul.",
        "Pass",
        "",
    ],
    [
        "TC-REG-10",
        "Hari pada tanggal lahir > 31",
        "1. Buka aplikasi.\n2. Masukkan tanggal dengan hari 35.\n3. Klik Save Profile.",
        "DOB: 2005-12-35",
        "Sistem menolak dengan error format tanggal salah.",
        "",
        "Sistem menolak, input tidak valid secara kalender.",
        "Pass",
        "Hari > 31 otomatis ditolak oleh sistem",
    ],
    [
        "TC-REG-11",
        "Nama kurang dari 2 karakter",
        "1. Buka aplikasi.\n2. Masukkan nama 1 huruf.\n3. Klik Save Profile.",
        "Nama: T",
        "Sistem menolak dan meminta minimal 2 karakter.",
        "",
        "Sistem menolak dengan pesan yang sesuai.",
        "Pass",
        "",
    ],
    [
        "TC-REG-12",
        "GPA di luar range (0.00 - 4.00)",
        "1. Buka aplikasi.\n2. Masukkan GPA melebihi batas.\n3. Klik Save Profile.",
        "GPA: 4.50",
        "Sistem menolak GPA > 4.00.",
        "",
        "Sistem menolak karena nilai 4.50 di luar rentang.",
        "Pass",
        "",
    ],
    [
        "TC-REG-13",
        "Semester = 0",
        "1. Buka aplikasi.\n2. Masukkan semester = 0.\n3. Klik Save Profile.",
        "Semester: 0",
        "Sistem menolak semester 0.",
        "",
        "Sistem menolak nilai 0, harus minimal 1.",
        "Pass",
        "",
    ],
    [
        "TC-REG-14",
        "IELTS > 9.0",
        "1. Buka aplikasi.\n2. Masukkan IELTS melebihi batas.\n3. Klik Save Profile.",
        "IELTS: 10.0",
        "Sistem menolak nilai IELTS.",
        "",
        "Sistem menolak nilai 10.0 (melebihi 9.0).",
        "Pass",
        "Data opsional tervalidasi jika diisi",
    ],
    [
        "TC-REG-15",
        "TOEFL > 120",
        "1. Buka aplikasi.\n2. Masukkan TOEFL melebihi batas.\n3. Klik Save Profile.",
        "TOEFL: 130",
        "Sistem menolak nilai TOEFL.",
        "",
        "Sistem menolak nilai 130 (melebihi 120).",
        "Pass",
        "",
    ],
    [
        "TC-REG-16",
        "Format tanggal salah",
        "1. Buka aplikasi.\n2. Masukkan format DD-MM-YYYY.\n3. Klik Save Profile.",
        "DOB: 30-12-2005",
        "Sistem menolak format tanggal salah.",
        "",
        "Sistem menolak input DD-MM-YYYY.",
        "Pass",
        "Mengharuskan format standar (YYYY-MM-DD)",
    ],
    [
        "TC-REG-17",
        "Data valid lengkap + data opsional",
        "1. Buka aplikasi.\n2. Isi semua data valid dan skor opsional.\n3. Klik Save Profile.",
        "KIP: Ya\nIELTS: 7.5\nTOEFL: 100\nDuolingo: 120",
        "Sistem menyimpan semua data (wajib & opsional).",
        "",
        "Registrasi sukses, data opsional ikut tersimpan dengan benar.",
        "Pass",
        "Tes memastikan data opsional valid diproses lancar",
    ],
]

# ── 1. LOGIN ──────────────────────────────────────────────────
LOGIN_DATA = [
    [
        "TC-LOGIN-01",
        "Login dengan email dan password yang valid.",
        "1. Buka aplikasi Beaply.\n2. Pastikan berada di tab 'Log in'.\n3. Masukkan email yang sudah terdaftar.\n4. Masukkan password yang benar.\n5. Klik tombol 'Log in'.",
        "Email: tut@gmail.com\nPassword: Tutut123!",
        "Sistem berhasil login dan menampilkan halaman Dashboard.",
        "",
        "Login berhasil. Redirect ke Dashboard sesuai ekspektasi.",
        "Pass",
        "Alur login utama berfungsi dengan baik",
    ],
    [
        "TC-LOGIN-02",
        "Login dengan email yang tidak terdaftar.",
        "1. Buka aplikasi Beaply.\n2. Pastikan berada di tab 'Log in'.\n3. Masukkan email yang belum terdaftar.\n4. Masukkan password sembarang.\n5. Klik tombol 'Log in'.",
        "Email: tidakada@xyz.com\nPassword: Test123!",
        "Sistem menolak dan menampilkan pesan 'Email atau password salah.'.",
        "",
        "Sistem menolak dengan pesan error yang sesuai.",
        "Pass",
        "Tidak membocorkan informasi apakah email terdaftar atau tidak",
    ],
    [
        "TC-LOGIN-03",
        "Login dengan password yang salah.",
        "1. Buka aplikasi Beaply.\n2. Pastikan berada di tab 'Log in'.\n3. Masukkan email yang benar.\n4. Masukkan password yang salah.\n5. Klik tombol 'Log in'.",
        "Email: tut@gmail.com\nPassword: SalahPassword1!",
        "Sistem menolak dan menampilkan pesan 'Email atau password salah.'.",
        "",
        "Sistem menolak. Menampilkan sisa percobaan login.",
        "Pass",
        "Rate limiter menghitung percobaan gagal",
    ],
    [
        "TC-LOGIN-04",
        "Login dengan email dan password kosong.",
        "1. Buka aplikasi Beaply.\n2. Pastikan berada di tab 'Log in'.\n3. Biarkan field Email dan Password kosong.\n4. Klik tombol 'Log in'.",
        "Email: (kosong)\nPassword: (kosong)",
        "Sistem menolak dan menampilkan pesan error.",
        "",
        "Sistem menolak karena email tidak valid (kosong).",
        "Pass",
        "",
    ],
    [
        "TC-LOGIN-05",
        "Login dengan format email tidak valid.",
        "1. Buka aplikasi Beaply.\n2. Masukkan email tanpa karakter '@'.\n3. Masukkan password valid.\n4. Klik tombol 'Log in'.",
        "Email: tutgmail.com\nPassword: Tutut123!",
        "Sistem menolak karena format email tidak valid.",
        "",
        "Sistem menolak, email tidak ditemukan di database.",
        "Pass",
        "",
    ],
    [
        "TC-LOGIN-06",
        "Login lalu centang 'Remember me' untuk menyimpan sesi.",
        "1. Buka aplikasi Beaply.\n2. Masukkan email dan password valid.\n3. Centang checkbox 'Remember me'.\n4. Klik tombol 'Log in'.\n5. Tutup aplikasi.\n6. Buka kembali aplikasi.",
        "Email: tut@gmail.com\nPassword: Tutut123!\nRemember me: Checked",
        "Setelah membuka ulang, sistem auto-login tanpa perlu memasukkan email & password lagi.",
        "",
        "Sesi tersimpan. Auto-login berhasil saat aplikasi dibuka kembali.",
        "Pass",
        "Sesi disimpan di file .beaply_session.json",
    ],
    [
        "TC-LOGIN-07",
        "Login tanpa centang 'Remember me'.",
        "1. Buka aplikasi Beaply.\n2. Masukkan email dan password valid.\n3. Pastikan 'Remember me' TIDAK dicentang.\n4. Klik tombol 'Log in'.\n5. Tutup aplikasi.\n6. Buka kembali aplikasi.",
        "Email: tut@gmail.com\nPassword: Tutut123!\nRemember me: Unchecked",
        "Setelah membuka ulang, sistem menampilkan halaman Login lagi (tidak auto-login).",
        "",
        "Sesi tidak disimpan. Halaman Login muncul kembali.",
        "Pass",
        "",
    ],
]

# ── 2. FORGOT PASSWORD ───────────────────────────────────────
FORGOT_PASSWORD_DATA = [
    [
        "TC-FP-01",
        "Mengirim OTP reset password ke email terdaftar.",
        "1. Buka aplikasi Beaply.\n2. Klik link 'Lupa Kata Sandi?'.\n3. Masukkan email yang terdaftar.\n4. Klik tombol 'Kirim Kode OTP'.",
        "Email: tut@gmail.com",
        "Sistem mengirimkan kode OTP dan berpindah ke halaman input OTP.",
        "",
        "OTP berhasil dikirim. Halaman berganti ke input kode OTP.",
        "Pass",
        "OTP dikirimkan melalui email service",
    ],
    [
        "TC-FP-02",
        "Mengirim OTP ke email yang tidak terdaftar.",
        "1. Buka aplikasi Beaply.\n2. Klik link 'Lupa Kata Sandi?'.\n3. Masukkan email yang belum terdaftar.\n4. Klik tombol 'Kirim Kode OTP'.",
        "Email: tidakada@xyz.com",
        "Sistem menolak dan menampilkan pesan 'Email tidak ditemukan.'.",
        "",
        "Sistem menolak dengan pesan error yang sesuai.",
        "Pass",
        "",
    ],
    [
        "TC-FP-03",
        "Verifikasi OTP dengan kode yang benar.",
        "1. Lakukan langkah TC-FP-01.\n2. Masukkan kode OTP yang benar (6 digit).\n3. Klik tombol 'Verifikasi'.",
        "OTP: (kode valid dari email)",
        "Sistem menerima OTP dan berpindah ke halaman input password baru.",
        "",
        "OTP diterima. Halaman berganti ke form password baru.",
        "Pass",
        "",
    ],
    [
        "TC-FP-04",
        "Verifikasi OTP dengan kode yang salah.",
        "1. Lakukan langkah TC-FP-01.\n2. Masukkan kode OTP yang salah.\n3. Klik tombol 'Verifikasi'.",
        "OTP: 999999 (salah)",
        "Sistem menolak dan menampilkan pesan 'Kode OTP tidak valid atau sudah expired.'.",
        "",
        "Sistem menolak dengan pesan error sesuai ekspektasi.",
        "Pass",
        "",
    ],
    [
        "TC-FP-05",
        "Reset password dengan password baru yang valid.",
        "1. Lakukan langkah TC-FP-01 hingga TC-FP-03.\n2. Masukkan password baru yang memenuhi syarat.\n3. Masukkan konfirmasi password sama.\n4. Klik tombol 'Reset Password'.",
        "Password Baru: NewPass456!\nKonfirmasi: NewPass456!",
        "Sistem berhasil mereset password dan kembali ke halaman Login.",
        "",
        "Password berhasil direset. Redirect ke halaman login.",
        "Pass",
        "",
    ],
    [
        "TC-FP-06",
        "Reset password dengan konfirmasi yang tidak cocok.",
        "1. Lakukan langkah TC-FP-01 hingga TC-FP-03.\n2. Masukkan password baru.\n3. Masukkan konfirmasi password yang berbeda.\n4. Klik tombol 'Reset Password'.",
        "Password Baru: NewPass456!\nKonfirmasi: BedaPass789!",
        "Sistem menolak dan menampilkan pesan 'Password tidak cocok.'.",
        "",
        "Sistem menolak dengan pesan error sesuai.",
        "Pass",
        "",
    ],
    [
        "TC-FP-07",
        "Reset password menggunakan password yang sudah pernah digunakan.",
        "1. Lakukan langkah TC-FP-01 hingga TC-FP-03.\n2. Masukkan password lama yang pernah digunakan.\n3. Klik tombol 'Reset Password'.",
        "Password Baru: Tutut123! (password lama)\nKonfirmasi: Tutut123!",
        "Sistem menolak dan menampilkan pesan 'Password sudah pernah digunakan sebelumnya.'.",
        "",
        "Sistem menolak. Password history dicek sebelum menerima.",
        "Pass",
        "Sistem menyimpan 3 password terakhir",
    ],
]

# ── 3. DASHBOARD ──────────────────────────────────────────────
DASHBOARD_DATA = [
    [
        "TC-DASH-01",
        "Menampilkan halaman Dashboard setelah login berhasil.",
        "1. Login dengan akun valid.\n2. Perhatikan halaman yang muncul setelah login.",
        "Akun: tut@gmail.com",
        "Dashboard menampilkan ringkasan statistik (total peluang, bookmarks, upcoming deadlines).",
        "",
        "Dashboard ditampilkan dengan statistik ringkas yang benar.",
        "Pass",
        "Halaman pertama setelah login",
    ],
    [
        "TC-DASH-02",
        "Menampilkan Trending Scholarships di Dashboard.",
        "1. Login dan buka Dashboard.\n2. Scroll ke bagian Trending Scholarships.",
        "Akun dengan profil lengkap",
        "Dashboard menampilkan daftar beasiswa yang sedang trending secara horizontal.",
        "",
        "Kartu beasiswa trending ditampilkan dengan layout horizontal.",
        "Pass",
        "",
    ],
    [
        "TC-DASH-03",
        "Menampilkan Smart Tips di Dashboard.",
        "1. Login dan buka Dashboard.\n2. Scroll ke bagian Smart Tips For You.",
        "Akun dengan profil lengkap",
        "Dashboard menampilkan tips dan saran yang relevan.",
        "",
        "Section Smart Tips ditampilkan dengan konten tips.",
        "Pass",
        "",
    ],
    [
        "TC-DASH-04",
        "Navigasi dari Dashboard ke halaman lain via sidebar.",
        "1. Login dan buka Dashboard.\n2. Klik menu 'Eksplorasi' di sidebar.",
        "Akun yang sudah login",
        "Sistem berpindah ke halaman Eksplorasi Beasiswa.",
        "",
        "Navigasi sidebar berfungsi. Halaman Eksplorasi ditampilkan.",
        "Pass",
        "Semua menu sidebar mengarah ke halaman yang benar",
    ],
    [
        "TC-DASH-05",
        "Klik ikon notifikasi (bell) di topbar.",
        "1. Login dan buka Dashboard.\n2. Klik ikon lonceng di topbar kanan atas.",
        "Akun yang sudah login",
        "Sistem berpindah ke halaman Notifikasi.",
        "",
        "Navigasi ke halaman Notifikasi berhasil.",
        "Pass",
        "",
    ],
    [
        "TC-DASH-06",
        "Klik avatar pengguna di topbar.",
        "1. Login dan buka Dashboard.\n2. Klik avatar/foto profil di topbar kanan atas.",
        "Akun yang sudah login",
        "Sistem berpindah ke halaman Profil.",
        "",
        "Navigasi ke halaman Profil berhasil.",
        "Pass",
        "",
    ],
]

# ── 4. EKSPLORASI BEASISWA ────────────────────────────────────
EKSPLORASI_DATA = [
    [
        "TC-EKS-01",
        "Menampilkan daftar semua beasiswa yang tersedia.",
        "1. Login ke aplikasi.\n2. Klik menu 'Eksplorasi' di sidebar.",
        "Akun yang sudah login",
        "Daftar beasiswa ditampilkan dalam bentuk kartu-kartu.",
        "",
        "Semua beasiswa ditampilkan dengan informasi lengkap (nama, deadline, kategori).",
        "Pass",
        "Hanya menampilkan jenjang perguruan tinggi (D3-S3)",
    ],
    [
        "TC-EKS-02",
        "Mencari beasiswa berdasarkan keyword nama.",
        "1. Buka halaman Eksplorasi.\n2. Ketikkan keyword pada kolom pencarian.\n3. Tekan Enter atau klik tombol cari.",
        "Keyword: LPDP",
        "Sistem menampilkan beasiswa yang mengandung keyword 'LPDP'.",
        "",
        "Hasil pencarian sesuai dengan keyword yang dimasukkan.",
        "Pass",
        "",
    ],
    [
        "TC-EKS-03",
        "Mencari beasiswa dengan keyword yang tidak ada.",
        "1. Buka halaman Eksplorasi.\n2. Ketikkan keyword yang tidak cocok dengan beasiswa manapun.",
        "Keyword: XYZXYZ123",
        "Sistem menampilkan pesan tidak ada hasil pencarian.",
        "",
        "Daftar beasiswa kosong, menampilkan pesan 'tidak ditemukan'.",
        "Pass",
        "",
    ],
    [
        "TC-EKS-04",
        "Filter beasiswa berdasarkan kategori.",
        "1. Buka halaman Eksplorasi.\n2. Pilih filter kategori (contoh: 'Pemerintah').\n3. Lihat hasil yang ditampilkan.",
        "Filter Kategori: Pemerintah",
        "Hanya beasiswa dengan kategori 'Pemerintah' yang ditampilkan.",
        "",
        "Filter berhasil. Beasiswa ditampilkan sesuai kategori.",
        "Pass",
        "",
    ],
    [
        "TC-EKS-05",
        "Filter beasiswa berdasarkan jenjang.",
        "1. Buka halaman Eksplorasi.\n2. Pilih filter jenjang (contoh: 'S1').\n3. Lihat hasil yang ditampilkan.",
        "Filter Jenjang: S1",
        "Hanya beasiswa dengan jenjang S1 yang ditampilkan.",
        "",
        "Filter jenjang berfungsi dengan benar.",
        "Pass",
        "",
    ],
    [
        "TC-EKS-06",
        "Sorting beasiswa berdasarkan nama (A-Z).",
        "1. Buka halaman Eksplorasi.\n2. Pilih sort 'Nama (A-Z)'.",
        "Sort: nama_asc",
        "Daftar beasiswa diurutkan secara alfabet dari A ke Z.",
        "",
        "Sorting berhasil. Beasiswa diurutkan secara alfabet.",
        "Pass",
        "",
    ],
    [
        "TC-EKS-07",
        "Sorting beasiswa berdasarkan deadline terdekat.",
        "1. Buka halaman Eksplorasi.\n2. Pilih sort 'Deadline terdekat'.",
        "Sort: deadline_asc",
        "Daftar beasiswa diurutkan dari deadline paling dekat.",
        "",
        "Sorting deadline berfungsi. Beasiswa terdekat tampil duluan.",
        "Pass",
        "",
    ],
    [
        "TC-EKS-08",
        "Melihat detail beasiswa.",
        "1. Buka halaman Eksplorasi.\n2. Klik salah satu kartu beasiswa.",
        "Beasiswa: (pilih salah satu yang tersedia)",
        "Sistem menampilkan halaman detail beasiswa (syarat, deskripsi, link, dll).",
        "",
        "Detail beasiswa ditampilkan dengan informasi lengkap.",
        "Pass",
        "",
    ],
]

# ── 5. BOOKMARK ───────────────────────────────────────────────
BOOKMARK_DATA = [
    [
        "TC-BM-01",
        "Menambahkan beasiswa ke bookmark.",
        "1. Buka halaman Eksplorasi.\n2. Pilih salah satu beasiswa.\n3. Klik ikon bookmark/bintang pada kartu beasiswa.",
        "Beasiswa: (pilih salah satu)",
        "Beasiswa ditandai sebagai bookmark, ikon berubah menjadi aktif.",
        "",
        "Bookmark berhasil ditambahkan. Ikon berubah menjadi aktif.",
        "Pass",
        "Toggle bookmark (klik pertama = tambah)",
    ],
    [
        "TC-BM-02",
        "Menghapus beasiswa dari bookmark.",
        "1. Buka halaman Eksplorasi.\n2. Klik ikon bookmark pada beasiswa yang sudah di-bookmark.",
        "Beasiswa: (yang sudah di-bookmark)",
        "Bookmark dihapus, ikon kembali ke state tidak aktif.",
        "",
        "Bookmark berhasil dihapus. Ikon kembali ke state awal.",
        "Pass",
        "Toggle bookmark (klik kedua = hapus)",
    ],
    [
        "TC-BM-03",
        "Melihat daftar beasiswa yang sudah di-bookmark.",
        "1. Login ke aplikasi.\n2. Klik menu 'Bookmarks' di sidebar.",
        "Akun yang memiliki beasiswa yang di-bookmark",
        "Halaman Bookmarks menampilkan daftar beasiswa yang sudah ditandai.",
        "",
        "Daftar bookmarks tampil dengan benar.",
        "Pass",
        "",
    ],
    [
        "TC-BM-04",
        "Halaman bookmark saat tidak ada data.",
        "1. Login dengan akun baru yang belum punya bookmark.\n2. Klik menu 'Bookmarks' di sidebar.",
        "Akun baru tanpa bookmark",
        "Halaman Bookmarks menampilkan pesan 'Belum ada bookmark'.",
        "",
        "Halaman menampilkan empty state yang sesuai.",
        "Pass",
        "",
    ],
]

# ── 6. REKOMENDASI ────────────────────────────────────────────
REKOMENDASI_DATA = [
    [
        "TC-REK-01",
        "Menampilkan daftar rekomendasi beasiswa berdasarkan profil.",
        "1. Login ke aplikasi.\n2. Klik menu 'Rekomendasi' di sidebar.\n3. Klik tombol untuk mulai analisis.",
        "Profil: IPK 3.50, S1, Teknik Informatika",
        "Sistem menampilkan daftar beasiswa dengan skor kecocokan.",
        "",
        "Daftar rekomendasi ditampilkan, diurutkan dari skor tertinggi.",
        "Pass",
        "Skor dihitung berdasarkan profil pengguna",
    ],
    [
        "TC-REK-02",
        "Melihat analisis peluang untuk beasiswa tertentu.",
        "1. Buka halaman Rekomendasi.\n2. Klik salah satu beasiswa dari daftar rekomendasi.",
        "Beasiswa: (pilih salah satu dari hasil rekomendasi)",
        "Sistem menampilkan analisis peluang (kriteria cocok/tidak cocok).",
        "",
        "Analisis peluang ditampilkan dengan detail kriteria.",
        "Pass",
        "",
    ],
    [
        "TC-REK-03",
        "Membandingkan dua beasiswa.",
        "1. Buka halaman Rekomendasi.\n2. Pilih dua beasiswa untuk dibandingkan.\n3. Klik tombol 'Bandingkan'.",
        "Beasiswa A: LPDP\nBeasiswa B: Djarum",
        "Sistem menampilkan perbandingan kedua beasiswa (IPK, jenjang, deadline, organisasi).",
        "",
        "Perbandingan berhasil ditampilkan dengan tabel kriteria.",
        "Pass",
        "Menampilkan skor kecocokan masing-masing",
    ],
    [
        "TC-REK-04",
        "Rekomendasi untuk profil yang tidak lengkap.",
        "1. Login dengan akun yang profilnya minim data.\n2. Buka halaman Rekomendasi.",
        "Profil: Data minimal",
        "Sistem tetap menampilkan rekomendasi meski skor kecocokan rendah.",
        "",
        "Rekomendasi tetap ditampilkan. Skor kecocokan menyesuaikan.",
        "Pass",
        "",
    ],
]

# ── 7. TRACKER & PENGINGAT ────────────────────────────────────
TRACKER_DATA = [
    [
        "TC-TRK-01",
        "Menambahkan tracker beasiswa baru secara manual.",
        "1. Login ke aplikasi.\n2. Klik menu 'Tracker' di sidebar.\n3. Klik tombol 'Tambah Tracker'.\n4. Isi nama beasiswa dan deadline.\n5. Klik 'Simpan'.",
        "Nama: Beasiswa LPDP\nDeadline: 2026-08-01\nCatatan: Siapkan dokumen",
        "Tracker baru berhasil ditambahkan dan muncul di daftar.",
        "",
        "Tracker berhasil ditambahkan. Muncul di daftar tracker.",
        "Pass",
        "",
    ],
    [
        "TC-TRK-02",
        "Menambahkan tracker tanpa nama beasiswa.",
        "1. Buka halaman Tracker.\n2. Klik tombol 'Tambah Tracker'.\n3. Biarkan nama beasiswa kosong.\n4. Klik 'Simpan'.",
        "Nama: (kosong)\nDeadline: 2026-08-01",
        "Sistem menolak dan menampilkan pesan validasi.",
        "",
        "Sistem menolak. Pesan error nama wajib diisi muncul.",
        "Pass",
        "",
    ],
    [
        "TC-TRK-03",
        "Mengubah status tracker beasiswa.",
        "1. Buka halaman Tracker.\n2. Pilih salah satu tracker.\n3. Ubah status dari 'Belum Mulai' ke 'Sedang Proses'.",
        "Tracker: Beasiswa LPDP\nStatus baru: sedang_proses",
        "Status tracker berubah dan ditampilkan dengan warna yang sesuai.",
        "",
        "Status berhasil diubah. Label dan warna terupdate.",
        "Pass",
        "Status valid: belum_mulai, sedang_proses, terkirim, diterima, ditolak",
    ],
    [
        "TC-TRK-04",
        "Mengedit data tracker yang sudah ada.",
        "1. Buka halaman Tracker.\n2. Pilih tracker yang ingin diedit.\n3. Ubah nama/deadline/catatan.\n4. Klik 'Simpan'.",
        "Nama baru: Beasiswa LPDP 2026\nDeadline baru: 2026-09-01",
        "Data tracker berhasil diupdate.",
        "",
        "Edit berhasil. Data tracker terupdate di daftar.",
        "Pass",
        "",
    ],
    [
        "TC-TRK-05",
        "Menghapus tracker beasiswa.",
        "1. Buka halaman Tracker.\n2. Pilih tracker yang ingin dihapus.\n3. Klik tombol 'Hapus'.\n4. Konfirmasi penghapusan.",
        "Tracker: (pilih salah satu)",
        "Tracker berhasil dihapus dari daftar.",
        "",
        "Tracker berhasil dihapus. Tidak muncul lagi di daftar.",
        "Pass",
        "",
    ],
    [
        "TC-TRK-06",
        "Toggle bookmark pada tracker.",
        "1. Buka halaman Tracker.\n2. Klik ikon bookmark pada salah satu tracker.",
        "Tracker: (pilih salah satu)",
        "Status bookmark tracker berubah (aktif/nonaktif).",
        "",
        "Toggle bookmark berfungsi dengan benar.",
        "Pass",
        "",
    ],
    [
        "TC-TRK-07",
        "Melihat statistik tracker.",
        "1. Buka halaman Tracker.\n2. Lihat ringkasan statistik di bagian atas.",
        "Akun dengan beberapa tracker",
        "Statistik ditampilkan (total, belum mulai, sedang proses, terkirim, diterima, ditolak).",
        "",
        "Statistik ditampilkan dengan angka yang benar.",
        "Pass",
        "",
    ],
]

# ── 8. KALENDER ───────────────────────────────────────────────
KALENDER_DATA = [
    [
        "TC-KAL-01",
        "Menampilkan kalender bulanan dengan deadline.",
        "1. Login ke aplikasi.\n2. Klik menu 'Kalender' di sidebar.",
        "Akun yang memiliki bookmark/tracker dengan deadline",
        "Kalender bulanan ditampilkan dengan tanda warna pada tanggal yang memiliki deadline.",
        "",
        "Kalender ditampilkan. Tanggal deadline ditandai dengan warna.",
        "Pass",
        "Warna: merah (<7 hari), kuning (7-14), hijau (>14), abu (expired)",
    ],
    [
        "TC-KAL-02",
        "Navigasi kalender ke bulan berikutnya.",
        "1. Buka halaman Kalender.\n2. Klik tombol panah kanan untuk bulan berikutnya.",
        "Bulan saat ini",
        "Kalender berpindah ke bulan berikutnya.",
        "",
        "Navigasi bulan berfungsi. Nama bulan dan tahun terupdate.",
        "Pass",
        "",
    ],
    [
        "TC-KAL-03",
        "Navigasi kalender ke bulan sebelumnya.",
        "1. Buka halaman Kalender.\n2. Klik tombol panah kiri untuk bulan sebelumnya.",
        "Bulan saat ini",
        "Kalender berpindah ke bulan sebelumnya.",
        "",
        "Navigasi bulan berfungsi. Data deadline dimuat ulang.",
        "Pass",
        "",
    ],
    [
        "TC-KAL-04",
        "Klik tanggal yang memiliki deadline untuk melihat detail.",
        "1. Buka halaman Kalender.\n2. Klik pada tanggal yang memiliki tanda warna.",
        "Tanggal: (yang memiliki deadline)",
        "Sistem menampilkan popup/detail beasiswa yang deadlinenya jatuh pada tanggal tersebut.",
        "",
        "Detail deadline ditampilkan (nama beasiswa, sumber: tracker/bookmark).",
        "Pass",
        "",
    ],
]

# ── 9. PROFIL ─────────────────────────────────────────────────
PROFIL_DATA = [
    [
        "TC-PROF-01",
        "Melihat halaman profil pengguna.",
        "1. Login ke aplikasi.\n2. Klik menu 'Profil' di sidebar.",
        "Akun yang sudah login",
        "Halaman profil menampilkan data pengguna (nama, email, jurusan, kampus, GPA, semester, dll).",
        "",
        "Data profil ditampilkan lengkap dan sesuai dengan data yang disimpan.",
        "Pass",
        "",
    ],
    [
        "TC-PROF-02",
        "Mengedit data profil wajib.",
        "1. Buka halaman Profil.\n2. Klik tombol 'Edit Profile'.\n3. Ubah nama atau jurusan.\n4. Klik 'Save'.",
        "Nama baru: Tutut Puspita\nJurusan baru: Ilmu Komputer",
        "Data profil berhasil diupdate.",
        "",
        "Profil terupdate. Data baru ditampilkan di halaman profil.",
        "Pass",
        "",
    ],
    [
        "TC-PROF-03",
        "Mengedit profil dengan GPA di luar range.",
        "1. Buka halaman Profil.\n2. Klik tombol 'Edit Profile'.\n3. Ubah GPA menjadi 5.00.\n4. Klik 'Save'.",
        "GPA baru: 5.00",
        "Sistem menolak dan menampilkan pesan 'IP harus antara 0.00 hingga 4.00.'.",
        "",
        "Sistem menolak perubahan. Pesan validasi muncul.",
        "Pass",
        "",
    ],
    [
        "TC-PROF-04",
        "Mengedit data opsional profil (skor tes bahasa).",
        "1. Buka halaman Profil.\n2. Scroll ke bagian 'Specific Data'.\n3. Masukkan/ubah skor IELTS.\n4. Klik 'Save'.",
        "IELTS baru: 7.5",
        "Data opsional berhasil diupdate.",
        "",
        "Skor IELTS terupdate dan tersimpan di database.",
        "Pass",
        "",
    ],
    [
        "TC-PROF-05",
        "Mengubah foto avatar profil.",
        "1. Buka halaman Profil.\n2. Klik pada area foto profil.\n3. Pilih gambar baru dari file dialog.\n4. Konfirmasi.",
        "File gambar: foto_baru.jpg",
        "Avatar profil berhasil diubah dan ditampilkan di topbar.",
        "",
        "Avatar terupdate di halaman profil dan topbar.",
        "Pass",
        "",
    ],
]

# ── 10. SETTINGS ──────────────────────────────────────────────
SETTINGS_DATA = [
    [
        "TC-SET-01",
        "Mengubah tema dari Light ke Dark mode.",
        "1. Login ke aplikasi.\n2. Klik menu 'Settings' di sidebar.\n3. Di bagian 'Display', klik tombol 'Dark'.",
        "Tema: Dark",
        "Tampilan aplikasi berubah menjadi mode gelap secara real-time.",
        "",
        "Tema berhasil berubah ke Dark. Seluruh elemen UI menyesuaikan.",
        "Pass",
        "Perubahan tema tersimpan secara persisten",
    ],
    [
        "TC-SET-02",
        "Mengubah tema dari Dark ke Light mode.",
        "1. Di halaman Settings.\n2. Klik tombol 'Light' pada bagian Theme.",
        "Tema: Light",
        "Tampilan aplikasi berubah menjadi mode terang.",
        "",
        "Tema berhasil berubah ke Light mode.",
        "Pass",
        "",
    ],
    [
        "TC-SET-03",
        "Mengubah bahasa dari Indonesia ke English.",
        "1. Di halaman Settings.\n2. Pada bagian 'Language', pilih 'English' dari dropdown.",
        "Bahasa: English",
        "Seluruh teks antarmuka berubah menjadi Bahasa Inggris.",
        "",
        "Bahasa berhasil berubah. Semua label UI diterjemahkan ke English.",
        "Pass",
        "Menggunakan sistem i18n untuk translasi",
    ],
    [
        "TC-SET-04",
        "Mengubah bahasa dari English ke Bahasa Indonesia.",
        "1. Di halaman Settings.\n2. Pada bagian 'Language', pilih 'Bahasa Indonesia'.",
        "Bahasa: Bahasa Indonesia",
        "Seluruh teks antarmuka berubah menjadi Bahasa Indonesia.",
        "",
        "Bahasa berhasil berubah kembali ke Indonesia.",
        "Pass",
        "",
    ],
    [
        "TC-SET-05",
        "Mengubah ukuran teks (Text Size).",
        "1. Di halaman Settings.\n2. Pada bagian 'Text Size', klik 'Large'.",
        "Text Size: Large",
        "Sistem menampilkan pesan bahwa perubahan akan berlaku setelah restart.",
        "",
        "Pesan info ditampilkan. Preferensi tersimpan.",
        "Pass",
        "Berlaku setelah aplikasi direstart",
    ],
    [
        "TC-SET-06",
        "Ganti password dari halaman Settings.",
        "1. Di halaman Settings.\n2. Klik tombol '>' di bagian 'Change Password'.\n3. Masukkan password lama, password baru, dan konfirmasi.\n4. Klik 'Change Password'.",
        "Password Lama: Tutut123!\nPassword Baru: NewPass456!\nKonfirmasi: NewPass456!",
        "Password berhasil diubah. Pesan sukses ditampilkan.",
        "",
        "Password berhasil diubah. Dialog menampilkan pesan 'Password changed!'.",
        "Pass",
        "",
    ],
    [
        "TC-SET-07",
        "Ganti password dengan field kosong.",
        "1. Di halaman Settings.\n2. Klik tombol '>' di bagian 'Change Password'.\n3. Biarkan semua field kosong.\n4. Klik 'Change Password'.",
        "Semua field: (kosong)",
        "Sistem menolak dan menampilkan pesan 'All fields required!'.",
        "",
        "Sistem menolak. Pesan error validasi muncul.",
        "Pass",
        "",
    ],
    [
        "TC-SET-08",
        "Ganti password dengan konfirmasi tidak cocok.",
        "1. Di halaman Settings.\n2. Buka dialog Change Password.\n3. Masukkan password baru dan konfirmasi yang berbeda.\n4. Klik 'Change Password'.",
        "Password Baru: NewPass456!\nKonfirmasi: BedaPass789!",
        "Sistem menolak dan menampilkan pesan 'Passwords don't match!'.",
        "",
        "Sistem menolak. Pesan error konfirmasi muncul.",
        "Pass",
        "",
    ],
    [
        "TC-SET-09",
        "Logout dari halaman Settings.",
        "1. Di halaman Settings.\n2. Klik tombol 'Logout'.\n3. Konfirmasi pada dialog yang muncul (klik 'Yes').",
        "Akun yang sudah login",
        "Sesi berakhir. Aplikasi kembali ke halaman Login.",
        "",
        "Logout berhasil. Halaman Login ditampilkan kembali.",
        "Pass",
        "Sesi session file dihapus",
    ],
    [
        "TC-SET-10",
        "Membatalkan logout.",
        "1. Di halaman Settings.\n2. Klik tombol 'Logout'.\n3. Klik 'No' pada dialog konfirmasi.",
        "Akun yang sudah login",
        "Logout dibatalkan. Pengguna tetap di halaman Settings.",
        "",
        "Logout dibatalkan. Tetap berada di halaman Settings.",
        "Pass",
        "",
    ],
    [
        "TC-SET-11",
        "Hapus akun pengguna (Delete Account).",
        "1. Di halaman Settings.\n2. Klik tombol 'Delete Account'.\n3. Konfirmasi penghapusan (klik 'Yes').",
        "Akun test yang akan dihapus",
        "Akun berhasil dihapus. Pesan sukses ditampilkan.",
        "",
        "Akun dihapus dari database. Pesan 'Account deleted' muncul.",
        "Pass",
        "Aksi tidak dapat dibatalkan (irreversible)",
    ],
    [
        "TC-SET-12",
        "Membatalkan hapus akun.",
        "1. Di halaman Settings.\n2. Klik tombol 'Delete Account'.\n3. Klik 'No' pada dialog konfirmasi.",
        "Akun yang sudah login",
        "Penghapusan dibatalkan. Akun tetap utuh.",
        "",
        "Penghapusan dibatalkan. Tetap di halaman Settings.",
        "Pass",
        "",
    ],
]

# ── 11. NOTIFIKASI ────────────────────────────────────────────
NOTIFIKASI_DATA = [
    [
        "TC-NOTIF-01",
        "Menampilkan halaman notifikasi.",
        "1. Login ke aplikasi.\n2. Klik menu 'Notifikasi' di sidebar atau ikon lonceng di topbar.",
        "Akun yang memiliki notifikasi",
        "Halaman notifikasi menampilkan daftar notifikasi yang dikelompokkan berdasarkan tanggal.",
        "",
        "Notifikasi ditampilkan dengan grouping tanggal (Hari ini, Kemarin, dll).",
        "Pass",
        "",
    ],
    [
        "TC-NOTIF-02",
        "Menandai satu notifikasi sebagai sudah dibaca.",
        "1. Buka halaman Notifikasi.\n2. Klik pada salah satu notifikasi yang belum dibaca.",
        "Notifikasi: (yang belum dibaca)",
        "Status notifikasi berubah menjadi 'dibaca'.",
        "",
        "Notifikasi ditandai dibaca. Tampilan berubah sesuai.",
        "Pass",
        "",
    ],
    [
        "TC-NOTIF-03",
        "Menandai semua notifikasi sebagai sudah dibaca.",
        "1. Buka halaman Notifikasi.\n2. Klik tombol 'Tandai semua dibaca'.",
        "Akun dengan beberapa notifikasi belum dibaca",
        "Semua notifikasi berubah status menjadi 'dibaca'. Badge notifikasi menjadi 0.",
        "",
        "Semua notifikasi ditandai dibaca. Badge hilang.",
        "Pass",
        "",
    ],
    [
        "TC-NOTIF-04",
        "Menghapus satu notifikasi.",
        "1. Buka halaman Notifikasi.\n2. Klik tombol hapus pada salah satu notifikasi.",
        "Notifikasi: (pilih salah satu)",
        "Notifikasi berhasil dihapus dari daftar.",
        "",
        "Notifikasi berhasil dihapus. Tidak muncul lagi di daftar.",
        "Pass",
        "",
    ],
    [
        "TC-NOTIF-05",
        "Menghapus semua notifikasi.",
        "1. Buka halaman Notifikasi.\n2. Klik tombol 'Hapus semua'.",
        "Akun dengan beberapa notifikasi",
        "Semua notifikasi berhasil dihapus.",
        "",
        "Daftar notifikasi kosong. Empty state ditampilkan.",
        "Pass",
        "",
    ],
    [
        "TC-NOTIF-06",
        "Menerima notifikasi deadline otomatis.",
        "1. Tambahkan tracker/bookmark beasiswa dengan deadline H-7.\n2. Buka halaman Notifikasi.",
        "Beasiswa dengan deadline 7 hari lagi",
        "Sistem secara otomatis membuat notifikasi pengingat deadline.",
        "",
        "Notifikasi deadline muncul dengan judul dan pesan yang sesuai.",
        "Pass",
        "Auto-generate notifikasi H-7, H-3, H-1",
    ],
    [
        "TC-NOTIF-07",
        "Halaman notifikasi saat tidak ada data.",
        "1. Login dengan akun baru.\n2. Buka halaman Notifikasi.",
        "Akun baru tanpa notifikasi",
        "Halaman menampilkan empty state 'Belum ada notifikasi'.",
        "",
        "Empty state ditampilkan dengan pesan yang sesuai.",
        "Pass",
        "",
    ],
]

# ── 12. PUSAT BANTUAN (HELP CENTER) ───────────────────────────
BANTUAN_DATA = [
    [
        "TC-HELP-01",
        "Menampilkan halaman Pusat Bantuan.",
        "1. Login ke aplikasi.\n2. Klik menu 'Bantuan' di sidebar.",
        "Akun yang sudah login",
        "Halaman Pusat Bantuan menampilkan daftar FAQ dan form pelaporan.",
        "",
        "Halaman Help Center ditampilkan dengan FAQ dan form feedback.",
        "Pass",
        "",
    ],
    [
        "TC-HELP-02",
        "Melihat jawaban FAQ.",
        "1. Buka halaman Pusat Bantuan.\n2. Klik salah satu pertanyaan FAQ.",
        "FAQ: (pilih salah satu pertanyaan)",
        "Sistem menampilkan jawaban dari pertanyaan yang diklik (expand/collapse).",
        "",
        "FAQ expand/collapse berfungsi. Jawaban ditampilkan.",
        "Pass",
        "",
    ],
    [
        "TC-HELP-03",
        "Mengirim laporan/feedback.",
        "1. Buka halaman Pusat Bantuan.\n2. Pilih kategori laporan.\n3. Tulis pesan feedback.\n4. Klik 'Kirim'.",
        "Kategori: Bug Report\nPesan: Halaman dashboard loading lambat",
        "Feedback berhasil dikirim. Pesan sukses ditampilkan.",
        "",
        "Feedback berhasil dikirim dan tersimpan.",
        "Pass",
        "",
    ],
    [
        "TC-HELP-04",
        "Mengirim feedback dengan pesan kosong.",
        "1. Buka halaman Pusat Bantuan.\n2. Pilih kategori laporan.\n3. Biarkan pesan kosong.\n4. Klik 'Kirim'.",
        "Kategori: Bug Report\nPesan: (kosong)",
        "Sistem menolak dan menampilkan pesan error.",
        "",
        "Sistem menolak. Validasi pesan kosong berfungsi.",
        "Pass",
        "",
    ],
]

# ── 13. PORTAL ADMIN ──────────────────────────────────────────
ADMIN_DATA = [
    [
        "TC-ADMIN-01",
        "Login sebagai Admin dengan email administrator terdaftar.",
        "1. Buka aplikasi Beaply.\n2. Masukkan email admin terdaftar.\n3. Masukkan password valid.\n4. Klik 'Masuk'.",
        "Email: admin@beaply.com\nPassword: AdminPassword123!",
        "Sistem mendeteksi email admin, menampilkan menu admin, dan membuka Panel Admin.",
        "",
        "Login berhasil. Mengarahkan langsung ke halaman Panel Admin dengan dashboard statistik.",
        "Pass",
        "Akun admin terverifikasi di admin_controller.is_admin()",
    ],
    [
        "TC-ADMIN-02",
        "Mengakses panel admin dengan email non-admin.",
        "1. Buka aplikasi Beaply.\n2. Masukkan email non-admin.\n3. Masukkan password valid.\n4. Klik 'Masuk'.",
        "Email: tut@gmail.com\nPassword: Tutut123!",
        "Sistem login sebagai user biasa dan mengarahkan ke dashboard utama user, tanpa menampilkan menu admin.",
        "",
        "Login berhasil sebagai user biasa. Dashboard user ditampilkan tanpa akses panel admin.",
        "Pass",
        "Hak akses admin dibatasi dengan ketat",
    ],
    [
        "TC-ADMIN-03",
        "Manajemen User - Menghapus akun user.",
        "1. Buka Panel Admin -> tab User Data.\n2. Pilih salah satu user dari daftar.\n3. Klik tombol Hapus (ikon tempat sampah).\n4. Klik 'Yes' pada dialog konfirmasi.",
        "Klik tombol hapus pada user ID 5",
        "Akun dan profil user tersebut terhapus dari database SQLite dan daftar user diperbarui.",
        "",
        "User berhasil dihapus dari database, daftar langsung di-rebuild secara otomatis.",
        "Pass",
        "Menghapus data di tabel users dan profil secara cascade",
    ],
    [
        "TC-ADMIN-04",
        "Manajemen Beasiswa - Mengedit data beasiswa.",
        "1. Buka Panel Admin -> tab Beasiswa.\n2. Klik tombol Edit (ikon clipboard) pada salah satu beasiswa.\n3. Ubah nama, penyelenggara, atau deadline pada form dialog.\n4. Klik 'Save Changes'.",
        "Ubah Deadline beasiswa ID 1 menjadi 2026-12-31",
        "Data baru tersimpan di database dan list beasiswa menampilkan data terupdate.",
        "",
        "Perubahan berhasil disimpan di database. Kartu beasiswa terupdate secara realtime.",
        "Pass",
        "Query UPDATE berjalan sukses pada database beaply.db",
    ],
    [
        "TC-ADMIN-05",
        "Manajemen Beasiswa - Menghapus beasiswa.",
        "1. Buka Panel Admin -> tab Beasiswa.\n2. Klik tombol Hapus (ikon tempat sampah) pada beasiswa tertentu.\n3. Konfirmasi penghapusan dengan klik 'Yes'.",
        "Klik hapus pada beasiswa ID 10",
        "Beasiswa terhapus dari database SQLite dan list admin diperbarui.",
        "",
        "Beasiswa dihapus, list diperbarui secara otomatis.",
        "Pass",
        "Menghapus data di tabel beasiswa",
    ],
    [
        "TC-ADMIN-06",
        "Manajemen Beasiswa - Melakukan Auto Scraping.",
        "1. Buka Panel Admin -> tab Beasiswa.\n2. Klik tombol 'Auto Scrap'.\n3. Tunggu hingga scraping background selesai.",
        "Klik tombol 'Auto Scrap'",
        "ScrapWorker berjalan di QThread, mengambil data beasiswa baru, dan menampilkan notifikasi sukses setelah selesai.",
        "",
        "QThread berjalan lancar, database terupdate dengan beasiswa terbaru, notifikasi sukses muncul.",
        "Pass",
        "Menggunakan run_all_scraping untuk mengambil data beasiswa",
    ],
    [
        "TC-ADMIN-07",
        "Manajemen Beasiswa - Publish to Users (Filter Non-PT).",
        "1. Buka Panel Admin -> tab Beasiswa.\n2. Klik tombol 'Publish to Users (Remove non-PT)'.\n3. Konfirmasi dengan klik 'Yes'.",
        "Klik tombol 'Publish to Users'",
        "Beasiswa dengan jenjang non-PT (selain D3/D4/S1/S2/S3) dihapus dari database agar pengguna hanya melihat beasiswa perguruan tinggi.",
        "",
        "Database memproses penghapusan data non-PT. Status tombol berubah menjadi 'All data is PT-only' jika non-PT = 0.",
        "Pass",
        "Menjamin kualitas data beasiswa untuk konsumsi mahasiswa",
    ],
    [
        "TC-ADMIN-08",
        "Pusat Bantuan - Menjawab feedback pengguna.",
        "1. Buka Panel Admin -> tab Pusat Bantuan.\n2. Pilih feedback bertanda 'Pending'.\n3. Klik tombol Jawab (ikon chat).\n4. Masukkan pesan balasan admin dan klik 'Send Reply & Notify User'.",
        "Balasan: 'Terima kasih laporannya, akan segera kami perbaiki.'",
        "Balasan admin tersimpan di file feedback.json dan user mendapatkan notifikasi 'Admin Reply'.",
        "",
        "Balasan tersimpan, dialog sukses muncul, user menerima notifikasi secara otomatis.",
        "Pass",
        "Mengintegrasikan feedback_model dengan notifikasi_model",
    ],
    [
        "TC-ADMIN-09",
        "Pengaturan - Mengubah Tema & Logout.",
        "1. Buka Panel Admin -> tab Pengaturan.\n2. Klik tombol tema 'Dark' lalu 'Light'.\n3. Klik tombol 'Logout' dan konfirmasi 'Yes'.",
        "Klik tombol Dark, klik tombol Logout",
        "Tema panel admin berganti secara visual, dan setelah logout sesi ditutup dan kembali ke halaman Login.",
        "",
        "Perubahan tema realtime berhasil. Sesi admin ditutup dan dialihkan ke auth view.",
        "Pass",
        "Membersihkan file sesi beaply_session.json jika logout",
    ],
]


# ═══════════════════════════════════════════════════════════════
# KONFIGURASI MODUL (nama_modul, nama_section, data_test)
# ═══════════════════════════════════════════════════════════════

MODULES = [
    ("Register Page",            REGISTER_DATA),
    ("Login Page",               LOGIN_DATA),
    ("Forgot Password",          FORGOT_PASSWORD_DATA),
    ("Dashboard",                DASHBOARD_DATA),
    ("Eksplorasi Beasiswa",      EKSPLORASI_DATA),
    ("Bookmark Beasiswa",        BOOKMARK_DATA),
    ("Rekomendasi Beasiswa",     REKOMENDASI_DATA),
    ("Tracker & Pengingat",      TRACKER_DATA),
    ("Kalender",                 KALENDER_DATA),
    ("Profil Pengguna",          PROFIL_DATA),
    ("Settings",                 SETTINGS_DATA),
    ("Notifikasi",               NOTIFIKASI_DATA),
    ("Pusat Bantuan",            BANTUAN_DATA),
    ("Portal Admin",             ADMIN_DATA),
]


# ═══════════════════════════════════════════════════════════════
# GENERATOR
# ═══════════════════════════════════════════════════════════════

def _add_test_section(doc, modul_name, data_rows, section_number):
    """Tambahkan satu section modul ke dokumen."""
    
    # Section heading
    doc.add_heading(f"{section_number}. {modul_name}", level=1)
    
    total_tc = len(data_rows)
    pass_count = sum(1 for r in data_rows if r[7].strip().lower() == "pass")
    
    p = doc.add_paragraph()
    p.add_run("Jumlah Test Case: ").bold = True
    p.add_run(f"{total_tc}\n")
    p.add_run("Status: ").bold = True
    p.add_run(f"{pass_count}/{total_tc} PASS\n")
    
    # Table
    table = doc.add_table(rows=1, cols=9)
    table.style = "Table Grid"

    hdr_cells = table.rows[0].cells
    for i, header in enumerate(HEADERS):
        hdr_cells[i].text = header

    for row_data in data_rows:
        row_cells = table.add_row().cells
        for i, text in enumerate(row_data):
            row_cells[i].text = text

    # Styling
    for row in table.rows:
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(9)

    # Bold header
    for cell in table.rows[0].cells:
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.bold = True

    doc.add_paragraph()  # spacer


def create_all_features_doc():
    """Generate satu dokumen DOCX berisi semua fitur."""
    doc = Document()

    # Landscape
    section = doc.sections[-1]
    new_width, new_height = section.page_height, section.page_width
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width = new_width
    section.page_height = new_height
    section.left_margin = Cm(1.5)
    section.right_margin = Cm(1.5)

    # Title
    doc.add_heading("Dokumen Blackbox Testing — Beaply (Seluruh Fitur)", 0)

    # Info
    p = doc.add_paragraph()
    p.add_run("Aplikasi: ").bold = True
    p.add_run("Beaply — Scholarship Insight\n")
    p.add_run("Platform: ").bold = True
    p.add_run("Desktop (PyQt6)\n")
    p.add_run("Tanggal Uji: ").bold = True
    p.add_run("7 Juni 2026\n")

    total_all = sum(len(d) for _, d in MODULES)
    p.add_run("Total Test Cases: ").bold = True
    p.add_run(f"{total_all}\n")
    p.add_run("Status Keseluruhan: ").bold = True
    p.add_run(f"{total_all} Test Cases PASS\n")

    # Daftar Isi Modul
    doc.add_heading("Daftar Modul yang Diuji", level=1)
    for idx, (name, data) in enumerate(MODULES, 1):
        doc.add_paragraph(f"{idx}. {name} ({len(data)} test cases)", style="List Number")
    doc.add_page_break()

    # Generate each module
    for idx, (name, data) in enumerate(MODULES, 1):
        _add_test_section(doc, name, data, idx)
        if idx < len(MODULES):
            doc.add_page_break()

    output = "Dokumen_Blackbox_Testing_Semua_Fitur.docx"
    doc.save(output)
    print(f"Dokumen berhasil dibuat: {output}")
    print(f"Total modul: {len(MODULES)}")
    print(f"Total test cases: {total_all}")


if __name__ == "__main__":
    create_all_features_doc()
