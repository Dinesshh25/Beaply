# ==============================================
# Nama Modul  : input_jurusan
# Tipe        : Procedure
# Level       : L1
# Fitur       : Rekomendasi
# Deskripsi   : Memasukkan nama jurusan untuk filter
#               beasiswa dan analisis peluang.
# Fitur Terkait: analisis_peluang
# Input       : -
# Output      : -
# I.S.        : Buka tab Rekomendasi.
# F.S.        : Mengeluarkan filter hasil rekomendasi.
# ==============================================

from .tampilan_rekomendasi import tampilan_rekomendasi


def input_jurusan():
    """
    Procedure: Memasukkan nama jurusan untuk filter beasiswa
    dan analisis peluang.

    I.S. : Pengguna membuka tab Rekomendasi.
    F.S. : Mengeluarkan filter hasil rekomendasi beasiswa.

    Memanggil:
        tampilan_rekomendasi(profil_user) (L2 Procedure)
    """

    print("\n" + "=" * 60)
    print("         INPUT DATA REKOMENDASI BEASISWA")
    print("=" * 60)

    # Input nama jurusan
    nama_jurusan = input("\n  Masukkan nama jurusan Anda: ").strip()
    if not nama_jurusan:
        print("  [!] Nama jurusan tidak boleh kosong.")
        return

    # Input IPK
    try:
        ipk = float(input("  Masukkan IPK Anda (0.00 - 4.00): "))
        if ipk < 0 or ipk > 4:
            print("  [!] IPK harus berada dalam rentang 0.00 - 4.00.")
            return
    except ValueError:
        print("  [!] IPK harus berupa angka!")
        return

    # Input Semester
    try:
        semester = int(input("  Masukkan semester saat ini: "))
        if semester < 1 or semester > 14:
            print("  [!] Semester harus antara 1 - 14.")
            return
    except ValueError:
        print("  [!] Semester harus berupa angka bulat!")
        return

    # Input Organisasi
    org_input = input("  Apakah Anda aktif berorganisasi? (y/n): ").strip().lower()
    organisasi = org_input == 'y'

    # Input Penghasilan Orang Tua
    try:
        penghasilan_ortu = float(input("  Masukkan penghasilan orang tua (per bulan): Rp"))
        if penghasilan_ortu < 0:
            print("  [!] Penghasilan tidak boleh negatif.")
            return
    except ValueError:
        print("  [!] Penghasilan harus berupa angka!")
        return

    # Menyusun profil user
    profil_user = {
        "jurusan": nama_jurusan,
        "ipk": ipk,
        "semester": semester,
        "organisasi": organisasi,
        "penghasilan_ortu": penghasilan_ortu
    }

    # Konfirmasi data
    print("\n  --- Data Profil Anda ---")
    print(f"  Jurusan          : {nama_jurusan}")
    print(f"  IPK              : {ipk:.2f}")
    print(f"  Semester         : {semester}")
    print(f"  Aktif Organisasi : {'Ya' if organisasi else 'Tidak'}")
    print(f"  Penghasilan Ortu : Rp{penghasilan_ortu:,.0f}")
    print("  -------------------------")

    lanjut = input("\n  Lanjutkan ke rekomendasi? (y/n): ").strip().lower()
    if lanjut != 'y':
        print("  [!] Dibatalkan.")
        return

    # Memanggil tampilan_rekomendasi dengan profil user
    tampilan_rekomendasi(profil_user)
