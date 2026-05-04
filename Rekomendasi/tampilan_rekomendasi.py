# ==============================================
# Nama Modul  : tampilan_rekomendasi
# Tipe        : Procedure
# Level       : L1 (memanggil L2)
# Fitur       : Rekomendasi
# Deskripsi   : Menampilkan daftar beasiswa terpilih
#               berdasarkan skor tertinggi.
# Fitur Terkait: hitung_skor_cocok
# Input       : -
# Output      : -
# I.S.        : Buka tab Rekomendasi.
# F.S.        : List rekomendasi tampil.
# ==============================================

from .hitung_skor_cocok import hitung_skor_cocok
from .analisis_peluang import analisis_peluang


# Data beasiswa contoh (bisa diperluas atau diambil dari database/scraping)
DAFTAR_BEASISWA = [
    {
        "nama": "Beasiswa Unggulan Kemendikbud",
        "min_ipk": 3.25,
        "max_semester": 6,
        "jurusan": ["Teknik Informatika", "Sistem Informasi", "Ilmu Komputer",
                    "Teknik Elektro", "Matematika"],
        "wajib_organisasi": True,
        "max_penghasilan_ortu": 6000000
    },
    {
        "nama": "Beasiswa Bank Indonesia",
        "min_ipk": 3.0,
        "max_semester": 8,
        "jurusan": ["Teknik Informatika", "Sistem Informasi", "Ekonomi",
                    "Manajemen", "Akuntansi"],
        "wajib_organisasi": False,
        "max_penghasilan_ortu": 5000000
    },
    {
        "nama": "Beasiswa Djarum Foundation",
        "min_ipk": 3.2,
        "max_semester": 4,
        "jurusan": ["Teknik Informatika", "Sistem Informasi", "Teknik Elektro",
                    "Teknik Mesin", "Arsitektur"],
        "wajib_organisasi": True,
        "max_penghasilan_ortu": 8000000
    },
    {
        "nama": "Beasiswa KIP Kuliah",
        "min_ipk": 2.75,
        "max_semester": 8,
        "jurusan": ["Teknik Informatika", "Sistem Informasi", "Ilmu Komputer",
                    "Ekonomi", "Hukum", "Kedokteran", "Farmasi"],
        "wajib_organisasi": False,
        "max_penghasilan_ortu": 4000000
    },
    {
        "nama": "Beasiswa LPDP",
        "min_ipk": 3.5,
        "max_semester": 8,
        "jurusan": ["Teknik Informatika", "Sistem Informasi", "Ilmu Komputer",
                    "Teknik Elektro", "Fisika", "Matematika", "Biologi"],
        "wajib_organisasi": True,
        "max_penghasilan_ortu": 10000000
    }
]


def tampilan_rekomendasi(profil_user):
    """
    Procedure: Menampilkan daftar beasiswa terpilih berdasarkan
    skor kecocokan tertinggi.

    I.S. : Pengguna membuka tab Rekomendasi.
    F.S. : List rekomendasi tampil di layar.

    Memanggil:
        hitung_skor_cocok(profil_user, syarat_beasiswa) -> persentase (Int)
        analisis_peluang(data_profil, target_beasiswa) -> saran (String)

    Parameter:
        profil_user (dict) : Data profil mahasiswa.
    """

    print("\n" + "=" * 60)
    print("          REKOMENDASI BEASISWA")
    print("=" * 60)
    print(f"  Profil: {profil_user.get('jurusan', '-')} | "
          f"IPK: {profil_user.get('ipk', '-')} | "
          f"Semester: {profil_user.get('semester', '-')}")
    print("-" * 60)

    # Hitung skor kecocokan untuk setiap beasiswa
    hasil_rekomendasi = []
    for beasiswa in DAFTAR_BEASISWA:
        skor = hitung_skor_cocok(profil_user, beasiswa)
        hasil_rekomendasi.append({
            "beasiswa": beasiswa,
            "skor": skor
        })

    # Urutkan berdasarkan skor tertinggi
    hasil_rekomendasi.sort(key=lambda x: x["skor"], reverse=True)

    # Tampilkan hasil
    for i, item in enumerate(hasil_rekomendasi, 1):
        beasiswa = item["beasiswa"]
        skor = item["skor"]

        # Label warna berdasarkan skor
        if skor >= 80:
            label = "★ SANGAT COCOK"
        elif skor >= 60:
            label = "● COCOK"
        elif skor >= 40:
            label = "◐ CUKUP COCOK"
        else:
            label = "○ KURANG COCOK"

        print(f"\n  {i}. {beasiswa['nama']}")
        print(f"     Cocok {skor}% - {label}")
        print(f"     Min IPK: {beasiswa['min_ipk']} | "
              f"Max Semester: {beasiswa['max_semester']} | "
              f"Organisasi: {'Wajib' if beasiswa['wajib_organisasi'] else 'Tidak Wajib'}")

    # Tampilkan analisis peluang untuk beasiswa teratas
    print("\n" + "=" * 60)
    print("  ANALISIS PELUANG - Beasiswa Teratas")
    print("=" * 60)

    top_beasiswa = hasil_rekomendasi[0]["beasiswa"]
    saran = analisis_peluang(profil_user, top_beasiswa)
    print(f"\n  Beasiswa: {top_beasiswa['nama']}")
    print(f"  Skor Kecocokan: {hasil_rekomendasi[0]['skor']}%\n")
    print(f"  {saran}")

    print("\n" + "=" * 60)
