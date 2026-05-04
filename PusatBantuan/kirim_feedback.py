# ==============================================
# Nama Modul  : kirim_feedback
# Tipe        : Function
# Level       : L2
# Fitur       : Pusat Bantuan & Umpan Balik
# Deskripsi   : Mengirimkan data laporan dari user ke
#               database pengembang.
# Fitur Terkait: form_pelaporan
# Input       : id_user, kategori, pesan
# Output      : status_kirim (Bool)
# I.S.        : Tombol kirim ditekan.
# F.S.        : Pesan terkirim, muncul notif sukses.
# ==============================================

import json
import os
from datetime import datetime


# Path file penyimpanan feedback
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedback_data.json")


def kirim_feedback(id_user, kategori, pesan):
    """
    Function: Mengirimkan data laporan dari user ke database pengembang.

    I.S. : Tombol kirim ditekan oleh pengguna.
    F.S. : Pesan terkirim dan muncul notifikasi sukses.

    Parameter:
        id_user  (str)  : ID unik pengguna yang mengirim feedback.
        kategori (str)  : Kategori laporan (bug, saran, pertanyaan).
        pesan    (str)  : Isi pesan/laporan dari pengguna.

    Return:
        status_kirim (bool) : True jika berhasil terkirim,
                              False jika gagal.
    """

    # Validasi input
    if not id_user or not isinstance(id_user, str):
        print("  [ERROR] ID user tidak valid.")
        return False

    if not kategori or kategori not in ["bug", "saran", "pertanyaan"]:
        print("  [ERROR] Kategori harus: bug, saran, atau pertanyaan.")
        return False

    if not pesan or not isinstance(pesan, str) or len(pesan.strip()) == 0:
        print("  [ERROR] Pesan tidak boleh kosong.")
        return False

    # Membuat objek feedback
    feedback = {
        "id_user": id_user,
        "kategori": kategori,
        "pesan": pesan,
        "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Membaca data feedback yang sudah ada
    try:
        if os.path.exists(FEEDBACK_FILE):
            with open(FEEDBACK_FILE, 'r') as file:
                data_feedback = json.load(file)
                if not isinstance(data_feedback, list):
                    data_feedback = []
        else:
            data_feedback = []

        # Menambahkan feedback baru
        data_feedback.append(feedback)

        # Menyimpan ke file (simulasi kirim ke database)
        with open(FEEDBACK_FILE, 'w') as file:
            json.dump(data_feedback, file, indent=4, ensure_ascii=False)

        status_kirim = True

    except Exception as e:
        print(f"  [ERROR] Gagal mengirim feedback: {e}")
        status_kirim = False

    return status_kirim
