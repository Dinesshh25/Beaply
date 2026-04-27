# ==============================================
# Modul Khusus: Rekomendasi
# ==============================================
# Modul ini menyediakan fitur rekomendasi beasiswa
# berdasarkan profil dan jurusan mahasiswa.
#
# Sub-modul:
#   L1 - input_jurusan          (Procedure) : Input nama jurusan untuk filter
#   L1 - tampilan_rekomendasi   (Procedure) : Menampilkan daftar rekomendasi
#   L2 - hitung_skor_cocok      (Function)  : Menghitung persentase kecocokan
#   L2 - analisis_peluang       (Function)  : Memberikan saran peningkatan peluang
# ==============================================

from .input_jurusan import input_jurusan
from .tampilan_rekomendasi import tampilan_rekomendasi
from .hitung_skor_cocok import hitung_skor_cocok
from .analisis_peluang import analisis_peluang
