"""
models/feedback_model.py
Beaply - Model: Feedback & Bantuan

Menyimpan feedback pengguna ke file JSON.
Dipindahkan dari: PusatBantuan/kirim_feedback.py
"""

import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FEEDBACK_FILE = os.path.join(BASE_DIR, "data", "feedback_data.json")


def kirim_feedback(id_user, kategori, pesan):
    """
    Mengirimkan data laporan dari user ke penyimpanan.
    Return: status_kirim (bool)
    """
    if not id_user or not isinstance(id_user, (str, int)):
        return False
    if not pesan or not isinstance(pesan, str) or len(pesan.strip()) == 0:
        return False

    feedback = {
        "id_user": str(id_user),
        "kategori": kategori,
        "pesan": pesan,
        "waktu": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        if os.path.exists(FEEDBACK_FILE):
            with open(FEEDBACK_FILE, 'r', encoding='utf-8') as file:
                data_feedback = json.load(file)
                if not isinstance(data_feedback, list):
                    data_feedback = []
        else:
            data_feedback = []

        data_feedback.append(feedback)

        os.makedirs(os.path.dirname(FEEDBACK_FILE), exist_ok=True)
        with open(FEEDBACK_FILE, 'w', encoding='utf-8') as file:
            json.dump(data_feedback, file, indent=4, ensure_ascii=False)

        return True
    except Exception as e:
        print(f"  [ERROR] Gagal mengirim feedback: {e}")
        return False


# FAQ data — dipindahkan dari tampilan_faq.py
DAFTAR_FAQ = [
    {
        "pertanyaan": "Bagaimana cara profil saya dinilai?",
        "jawaban": "Sistem menghitung persentase kecocokan berdasarkan IPK, semester aktif, dan syarat dari penyedia beasiswa."
    },
    {
        "pertanyaan": "Apa itu Smart Tips?",
        "jawaban": "Smart Tips adalah saran otomatis yang dihasilkan dari profil Anda untuk meningkatkan peluang melamar beasiswa."
    },
    {
        "pertanyaan": "Apakah saya harus mengisi skor TOEFL/IELTS?",
        "jawaban": "Tidak wajib jika beasiswa yang Anda inisiasi tidak memintanya. Tapi sangat disarankan untuk memperbesar peluang."
    },
    {
        "pertanyaan": "Apakah progres saya tersimpan otomatis?",
        "jawaban": "Ya, selama Anda sudah menyimpan profil di awal, data akan terus diperbarui dan tersimpan."
    },
    {
        "pertanyaan": "Bagaimana cara kerja fitur Rekomendasi?",
        "jawaban": "Fitur rekomendasi mencocokkan profil Anda dengan database beasiswa dan memberikan skor kecocokan untuk setiap beasiswa."
    },
    {
        "pertanyaan": "Apa itu Beaply Pro?",
        "jawaban": "Beaply Pro adalah fitur premium yang membuka akses semua skor rekomendasi beasiswa dan fitur-fitur advanced lainnya."
    },
]



# ════════════════════════════════════════════════════════════
# CATATAN: Data & algoritma rekomendasi beasiswa telah dipindah ke
# models/rekomendasi_model.py untuk pemisahan tanggung jawab yang tepat.
# ════════════════════════════════════════════════════════════

