# ==============================================
# Nama Modul  : hitung_skor_cocok
# Tipe        : Function
# Level       : L2
# Fitur       : Rekomendasi
# Deskripsi   : Menghitung persentase kecocokan profil
#               mahasiswa dengan syarat beasiswa.
# Fitur Terkait: tampilan_rekomendasi
# Input       : profil_user, syarat_beasiswa
# Output      : persentase (Int)
# I.S.        : Sistem memproses data profil.
# F.S.        : Muncul label "Cocok X%".
# ==============================================


def hitung_skor_cocok(profil_user, syarat_beasiswa):
    """
    Function: Menghitung persentase kecocokan profil mahasiswa
    dengan syarat beasiswa.

    I.S. : Sistem memproses data profil pengguna.
    F.S. : Muncul label "Cocok X%".

    Parameter:
        profil_user (dict) : Data profil mahasiswa.
            Contoh: {
                "ipk": 3.5,
                "semester": 4,
                "jurusan": "Teknik Informatika",
                "organisasi": True,
                "penghasilan_ortu": 3000000
            }
        syarat_beasiswa (dict) : Syarat/kriteria beasiswa.
            Contoh: {
                "min_ipk": 3.0,
                "max_semester": 8,
                "jurusan": ["Teknik Informatika", "Sistem Informasi"],
                "wajib_organisasi": False,
                "max_penghasilan_ortu": 5000000
            }

    Return:
        persentase (int) : Persentase kecocokan (0-100).
    """

    total_kriteria = 0
    kriteria_terpenuhi = 0

    # Kriteria 1: IPK minimum
    total_kriteria += 1
    if "ipk" in profil_user and "min_ipk" in syarat_beasiswa:
        if profil_user["ipk"] >= syarat_beasiswa["min_ipk"]:
            kriteria_terpenuhi += 1

    # Kriteria 2: Semester maksimum
    total_kriteria += 1
    if "semester" in profil_user and "max_semester" in syarat_beasiswa:
        if profil_user["semester"] <= syarat_beasiswa["max_semester"]:
            kriteria_terpenuhi += 1

    # Kriteria 3: Jurusan sesuai
    total_kriteria += 1
    if "jurusan" in profil_user and "jurusan" in syarat_beasiswa:
        daftar_jurusan = syarat_beasiswa["jurusan"]
        if isinstance(daftar_jurusan, list):
            if profil_user["jurusan"] in daftar_jurusan:
                kriteria_terpenuhi += 1
        elif profil_user["jurusan"] == daftar_jurusan:
            kriteria_terpenuhi += 1

    # Kriteria 4: Organisasi
    total_kriteria += 1
    if "wajib_organisasi" in syarat_beasiswa:
        if not syarat_beasiswa["wajib_organisasi"]:
            # Tidak wajib organisasi, otomatis terpenuhi
            kriteria_terpenuhi += 1
        elif "organisasi" in profil_user and profil_user["organisasi"]:
            kriteria_terpenuhi += 1

    # Kriteria 5: Penghasilan orang tua
    total_kriteria += 1
    if "penghasilan_ortu" in profil_user and "max_penghasilan_ortu" in syarat_beasiswa:
        if profil_user["penghasilan_ortu"] <= syarat_beasiswa["max_penghasilan_ortu"]:
            kriteria_terpenuhi += 1

    # Hitung persentase
    if total_kriteria == 0:
        persentase = 0
    else:
        persentase = int((kriteria_terpenuhi / total_kriteria) * 100)

    return persentase

# ==============================================
# Nama Modul  : analisis_peluang
# Tipe        : Function
# Level       : L2
# Fitur       : Rekomendasi
# Deskripsi   : Merekomendasikan cara meningkatkan peluang
#               (misal: saran portofolio, dll).
# Fitur Terkait: -
# Input       : data_profil, target_beasiswa
# Output      : saran (String)
# I.S.        : Peluang dihitung rendah.
# F.S.        : Tips peningkatan peluang tampil.
# ==============================================


def analisis_peluang(data_profil, target_beasiswa):
    """
    Function: Merekomendasikan cara meningkatkan peluang
    mendapatkan beasiswa.

    I.S. : Peluang dihitung rendah oleh sistem.
    F.S. : Tips peningkatan peluang tampil di layar.

    Parameter:
        data_profil (dict) : Data profil mahasiswa.
            Contoh: {
                "ipk": 2.8,
                "semester": 4,
                "jurusan": "Teknik Informatika",
                "organisasi": False,
                "penghasilan_ortu": 3000000
            }
        target_beasiswa (dict) : Syarat beasiswa yang ditargetkan.
            Contoh: {
                "nama": "Beasiswa Unggulan",
                "min_ipk": 3.5,
                "max_semester": 6,
                "jurusan": ["Teknik Informatika"],
                "wajib_organisasi": True,
                "max_penghasilan_ortu": 5000000
            }

    Return:
        saran (str) : String berisi saran-saran untuk
                      meningkatkan peluang mendapatkan beasiswa.
    """

    daftar_saran = []

    # Analisis IPK
    if "ipk" in data_profil and "min_ipk" in target_beasiswa:
        if data_profil["ipk"] < target_beasiswa["min_ipk"]:
            selisih = target_beasiswa["min_ipk"] - data_profil["ipk"]
            daftar_saran.append(
                f"- IPK Anda ({data_profil['ipk']:.2f}) masih di bawah "
                f"syarat minimum ({target_beasiswa['min_ipk']:.2f}). "
                f"Tingkatkan IPK minimal {selisih:.2f} poin. "
                f"Tips: Fokus pada mata kuliah dengan bobot SKS tinggi "
                f"dan manfaatkan jam konsultasi dosen."
            )

    # Analisis Semester
    if "semester" in data_profil and "max_semester" in target_beasiswa:
        if data_profil["semester"] > target_beasiswa["max_semester"]:
            daftar_saran.append(
                f"- Semester Anda ({data_profil['semester']}) melebihi "
                f"batas maksimum ({target_beasiswa['max_semester']}). "
                f"Pertimbangkan beasiswa lain yang menerima semester "
                f"lebih tinggi."
            )

    # Analisis Jurusan
    if "jurusan" in data_profil and "jurusan" in target_beasiswa:
        daftar_jurusan = target_beasiswa["jurusan"]
        if isinstance(daftar_jurusan, list):
            if data_profil["jurusan"] not in daftar_jurusan:
                daftar_saran.append(
                    f"- Jurusan Anda ({data_profil['jurusan']}) tidak "
                    f"termasuk dalam daftar jurusan yang diterima. "
                    f"Cari beasiswa yang sesuai dengan jurusan Anda."
                )

    # Analisis Organisasi
    if "wajib_organisasi" in target_beasiswa:
        if target_beasiswa["wajib_organisasi"]:
            if "organisasi" not in data_profil or not data_profil["organisasi"]:
                daftar_saran.append(
                    "- Beasiswa ini mewajibkan pengalaman organisasi. "
                    "Bergabunglah dengan organisasi kemahasiswaan, "
                    "UKM, atau komunitas kampus untuk memperkuat "
                    "profil Anda."
                )

    # Analisis Penghasilan Orang Tua
    if "penghasilan_ortu" in data_profil and "max_penghasilan_ortu" in target_beasiswa:
        if data_profil["penghasilan_ortu"] > target_beasiswa["max_penghasilan_ortu"]:
            daftar_saran.append(
                f"- Penghasilan orang tua Anda "
                f"(Rp{data_profil['penghasilan_ortu']:,.0f}) melebihi "
                f"batas maksimum (Rp{target_beasiswa['max_penghasilan_ortu']:,.0f}). "
                f"Pertimbangkan beasiswa prestasi non-ekonomi."
            )

    # Saran umum jika profil sudah cukup baik
    if not daftar_saran:
        saran = (
            "Selamat! Profil Anda sudah memenuhi semua syarat beasiswa ini. "
            "Pastikan kelengkapan dokumen dan persiapkan diri untuk seleksi."
        )
    else:
        header = "Saran untuk meningkatkan peluang Anda:\n"
        saran = header + "\n".join(daftar_saran)
        saran += (
            "\n\nTips tambahan: Perkuat portofolio dengan sertifikasi, "
            "proyek, atau pengalaman magang yang relevan."
        )

    return saran

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
