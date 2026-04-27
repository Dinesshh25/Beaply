# ==============================================
# Nama Modul  : form_pelaporan
# Tipe        : Procedure
# Level       : L1
# Fitur       : Pusat Bantuan & Umpan Balik
# Deskripsi   : Antarmuka untuk mengirimkan pesan,
#               laporan bug, atau saran fitur.
# Fitur Terkait: kirim_feedback
# Input       : -
# Output      : -
# I.S.        : Klik "Laporkan Masalah".
# F.S.        : Form input terbuka.
# ==============================================

from .kirim_feedback import kirim_feedback


def form_pelaporan():
    """
    Procedure: Antarmuka untuk mengirimkan pesan, laporan bug,
    atau saran fitur dari pengguna.

    I.S. : Pengguna mengklik "Laporkan Masalah".
    F.S. : Form input terbuka, pengguna dapat mengisi dan mengirim laporan.

    Memanggil:
        kirim_feedback(id_user, kategori, pesan) -> status_kirim (Bool)
    """

    print("\n" + "=" * 50)
    print("       FORM PELAPORAN & UMPAN BALIK")
    print("=" * 50)

    # Input ID User
    id_user = input("\n  Masukkan ID User Anda: ").strip()
    if not id_user:
        print("  [!] ID User tidak boleh kosong.")
        return

    # Input Kategori
    print("\n  Pilih Kategori Laporan:")
    print("  1. Bug (Laporan kesalahan/error)")
    print("  2. Saran (Saran fitur/perbaikan)")
    print("  3. Pertanyaan (Pertanyaan umum)")

    pilihan_kategori = input("  Pilih (1/2/3): ").strip()

    kategori_map = {
        "1": "bug",
        "2": "saran",
        "3": "pertanyaan"
    }

    kategori = kategori_map.get(pilihan_kategori)
    if not kategori:
        print("  [!] Pilihan kategori tidak valid.")
        return

    # Input Pesan
    pesan = input("\n  Tulis pesan/laporan Anda:\n  > ").strip()
    if not pesan:
        print("  [!] Pesan tidak boleh kosong.")
        return

    # Konfirmasi sebelum mengirim
    print("\n  --- Ringkasan Laporan ---")
    print(f"  ID User   : {id_user}")
    print(f"  Kategori  : {kategori}")
    print(f"  Pesan     : {pesan}")
    print("  --------------------------")

    konfirmasi = input("\n  Kirim laporan ini? (y/n): ").strip().lower()
    if konfirmasi != 'y':
        print("  [!] Pengiriman dibatalkan.")
        return

    # Memanggil function kirim_feedback (L2)
    status_kirim = kirim_feedback(id_user, kategori, pesan)

    if status_kirim:
        print("\n  [✓] Laporan berhasil terkirim!")
        print("  Terima kasih atas umpan balik Anda.")
    else:
        print("\n  [✗] Gagal mengirim laporan.")
        print("  Silakan coba lagi nanti.")

    print("=" * 50)
