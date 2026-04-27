# ==============================================
# Nama Modul  : tampilan_faq
# Tipe        : Procedure
# Level       : L1
# Fitur       : Pusat Bantuan & Umpan Balik
# Deskripsi   : Menampilkan daftar pertanyaan umum dan
#               panduan penggunaan aplikasi.
# Fitur Terkait: - (tanpa coupler)
# Input       : -
# Output      : -
# I.S.        : Klik menu Bantuan.
# F.S.        : Daftar FAQ tampil.
# ==============================================


def tampilan_faq():
    """
    Procedure: Menampilkan daftar pertanyaan umum (FAQ) dan
    panduan penggunaan aplikasi.

    I.S. : Pengguna mengklik menu Bantuan.
    F.S. : Daftar FAQ tampil di layar.
    """

    # Data FAQ statis (bisa diperluas atau diambil dari database)
    daftar_faq = [
        {
            "pertanyaan": "Bagaimana cara menambah pemasukan?",
            "jawaban": "Pilih menu '1. Tambah Pemasukan', lalu masukkan deskripsi dan jumlah pemasukan."
        },
        {
            "pertanyaan": "Bagaimana cara menambah pengeluaran?",
            "jawaban": "Pilih menu '2. Tambah Pengeluaran', lalu masukkan deskripsi dan jumlah pengeluaran."
        },
        {
            "pertanyaan": "Bagaimana cara melihat semua transaksi?",
            "jawaban": "Pilih menu '3. Tampilkan Transaksi' untuk melihat seluruh riwayat transaksi."
        },
        {
            "pertanyaan": "Bagaimana cara menghapus transaksi?",
            "jawaban": "Pilih menu '4. Hapus Transaksi', lalu masukkan nomor transaksi yang ingin dihapus."
        },
        {
            "pertanyaan": "Bagaimana cara melihat total pengeluaran?",
            "jawaban": "Pilih menu '5. Total Pengeluaran' untuk menghitung total seluruh pengeluaran."
        },
        {
            "pertanyaan": "Apakah data saya tersimpan otomatis?",
            "jawaban": "Ya, setiap perubahan transaksi otomatis tersimpan ke file data.json."
        },
        {
            "pertanyaan": "Bagaimana cara melaporkan bug atau memberi saran?",
            "jawaban": "Pilih menu 'Laporkan Masalah' pada Pusat Bantuan untuk mengirim laporan."
        }
    ]

    print("\n" + "=" * 50)
    print("         PUSAT BANTUAN - FAQ")
    print("=" * 50)

    for i, faq in enumerate(daftar_faq, 1):
        print(f"\n  Q{i}: {faq['pertanyaan']}")
        print(f"  A{i}: {faq['jawaban']}")

    print("\n" + "=" * 50)
    print("  Jika pertanyaan Anda belum terjawab,")
    print("  silakan gunakan fitur 'Laporkan Masalah'.")
    print("=" * 50)
