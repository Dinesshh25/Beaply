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
