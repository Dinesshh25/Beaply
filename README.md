# Beaply 🎓

**Beaply** adalah aplikasi *desktop* berbasis UI modern yang dirancang secara khusus untuk mempermudah mahasiswa dalam mengeksplorasi, melacak, dan mensimulasikan rekomendasi beasiswa secara terpadu. Dibangun sepenuhnya menggunakan arsitektur Python dan **CustomTkinter**, aplikasi ini menyajikan antarmuka visual (GUI) yang memukau, responsif, dinamis, dan sangat memanjakan mata.

---

## ✨ Fitur Utama (Features)

Aplikasi Beaply memiliki fungsionalitas komprehensif yang dirancang untuk mendukung perjalanan akademik kamu dari proses pendaftaran akun hingga mendapatkan rekomendasi yang presisi:

- **🔐 Autentikasi Pengguna & Profil (Authentication & Profile)**
  - Sistem *Login & Register* yang aman dan intuitif (disertai enkripsi *database* SQLite lokal).
  - Beranda profil yang interaktif.

- **📊 Dashboard Utama (Main Dashboard)**
  - Tinjauan statistik ringkas: Jumlah peluang yang tersedia, beasiswa yang di-*bookmark*, serta *Upcoming Deadlines*.
  - Menampilkan *Trending Scholarships* terbaru secara horizontal.
  - Modul *Smart Tips For You* yang akan selalu menemani dengan nasehat-nasehat jitu.

- **🔍 Eksplorasi Beasiswa (Scholarship Explorer)**
  - Fitur pencarian cerdas dari direktori beasiswa seluruh negeri.
  - Memungkinkan kamu mencari daftar beasiswa, mengatur filter (jurusan/durasi), dan menandai (*bookmark*) beasiswa incaranmu.

- **🎯 Sistem Rekomendasi Cerdas (Smart Recommendations)**
  - Menghitung probabilitas (*scoring logic*) beasiswa mana yang paling cocok dengan persentase kecocokan profil kamu (Berdasarkan IPK, Semester, Pendidikan, dll).
  - Tampilan persentase kecocokan profil (Profile Completeness) berbentuk diagram *Arc Canvas* yang nyata.

- **📅 Pelacak & Pengingat (Tracker & Reminder)**
  - Pantau jadwal atau dokumen tenggat waktu masing-masing beasiswa.
  - Sistem tidak akan membiarkanmu ketinggalan satupun kesempatan karena tertidur.

- **⚙️ Konfigurasi & Layar (Settings & Adjustability)**
  - **Dynamic Theme Mode:** Mendukung peralihan mode Gelap (*Dark*) dan Terang (*Light*) secara *Real-time*.
  - **Language Support:** Tersedia dalam dwi-bahasa (Bahasa Indonesia & English).
  - **Auto UI Scaling:** Ukuran antarmuka *(Text Size)* dapat disesuaikan (Small, Medium, Large) dan akan tersimpan secara otomatis *(Persistent memory)* ke dalam *database* setiap kali aplikasi dimulai ulang.
  - **Security:** Fitur ganti *password*, verifikasi kelayakan email, hingga penghapusan akun mandiri (*Delete Account*).

- **🆘 Pusat Bantuan (Help Center)**
  - Jelajahi FAQ (Frequently Asked Questions) bawaan aplikasi.
  - Fitur pelaporan *bugs* dan kendala untuk menjaga kenyamanan pengguna.

---

## 🛠️ Stack Teknologi (Tech Stack)

Aplikasi ini menggunakan teknologi-teknologi unggulan dan *library* andal di dalam ekosistem Python:
- **Language :** Python 3.10+
- **GUI Framework :** `customtkinter` (Pewaris moderen dari *Tkinter*)
- **Image Processing :** `Pillow` (PIL) untuk tata surya pengolahan logo simetris dan rendering antarmuka profil.
- **Database :** `sqlite3` (Internal terstruktur di `beaply.db`)

---

## 📂 Struktur Modul & Arsitektur (Modular Architecture)

Setelah melalui proses *refactoring*, aplikasi Beaply dirancang secara modular. Setiap subsistem atau fitur ditempatkan di dalam direktorinya masing-masing agar kode lebih bersih, terisolasi, dan mudah berkolaborasi. 

Berikut adalah rincian direktori/modul pada *codebase* Beaply saat ini:

1. **`main.py`**
   - Berfungsi sebagai **kerangka dasar (bootstrapper)** yang hanya memuat *class* inisialisasi aplikasi (`BeaplyApp`) untuk menjalankan GUI dan merutekan transisi *login/register* dan otorisasi tahap pertama.
   
2. **`gui_dashboard.py`**
   - Merupakan **Jembatan Terminal (HUB)** yang menampung susunan `LayoutDenganSidebar` serta *Dashboard Utama*. Dari modul inilah layar navigasi dialihkan ke berbagai halaman fitur lainnya.
   
3. **`ui_utils.py` & `database.py`**
   - Modul utilitas *backend* dan *Design System*. Berisi token warna desain, fungsi translasi (i18n), serta interkoneksi utama terhadap `beaply.db` via SQLite.

4. **`Autentikasi_dan_Keamanan/`**
   - Menangani segala urusan keamanan pengguna (algoritma kriptografi, verifikasi sandi, evaluasi kekuatan kata sandi, OTP, *Login*, *Register*). Memiliki UI spesifik seperti `gui_auth.py`.
   
5. **`Profile_dan_Setting/`**
   - Sistem *CRUD* Manajemen Profil: Berisi fungsionalitas pembuatan profil awal mahasiswa, halaman setelan (*Settings*), mode *Theme*, penagaturan bahasa antarmuka, hingga logika UI *Scale*. Punya dependensi ke UI modular seperti `gui_profile.py` dan `gui_settings.py`.

6. **`Tracker_dan_Pengingat/`**
   - Mengelola fungsionalitas kalender pendaftaran beasiswa dan sistem status tahapan seleksi (*Tracker*). 
   
7. **`Eksplorasi_dan_Navigasi/`**
   - Mewadahi antarmuka perpustakaan eksplorasi direktori beasiswa. Dari sini pengguna dapat memberikan bintang (*bookmark*), menyortir abjad, atau mencari beasiswa ideal.

8. **`Rekomendasi/`**
   - Berisi komponen *Smart Logic* atau algoritma penentu kecocokan (Matching system) berdasarkan perhitungan *scoring* yang direpresentasikan oleh *Profile Completeness*.

9. **`Notifikasi_Terpusat/`**
   - Menyediakan fitur notifikasi kotak masuk *(Inbox)*. Memberi alert kepada pengguna perihal status seleksi beasiswa maupun *deadline* pendaftaran yang jatuh tempo dalam < 7 hari.
   
10. **`PusatBantuan/`**
    - Menyediakan antarmuka FAQ (Frequently Asked Questions) dan formulir pengaduan (Support) lokal langsung dari dalam program ekosistem.

---

## 🚀 Cara Menjalankan Aplikasi (How to Run)

1. **Persiapan *Environment*:**
   Pastikan kamu telah menginstall modul utama yang dibutuhkan melalui repositori `requirements.txt`:
   ```bash
   pip install customtkinter Pillow
   ```
2. **Jalankan Aplikasi Utama:**
   Aplikasi Beaply berjalan terpusat dan tersinkronisasi lewat satu eksekutor inti yaitu `main.py`:
   ```bash
   python main.py
   ```
3. **Mulai Bersenang-senang!** Buat akun baru, atau masuk ke akun yang sudah ada untuk mulai memburu beasiswa masa depanmu!

---

*Thank you for utilizing Beaply! Empowering your education with ease and elegance.* 🚀
