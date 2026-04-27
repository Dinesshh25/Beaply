"""
models/rekomendasi_model.py
Beaply - Model: Rekomendasi Beasiswa

Data & algoritma pencocokan beasiswa dengan profil user.
Dipindahkan dari: models/feedback_model.py (tidak relevan secara semantik).
"""

from models.database import get_connection


# ════════════════════════════════════════════════════════════
# DATA BEASISWA REKOMENDASI
# ════════════════════════════════════════════════════════════

DAFTAR_BEASISWA_REKOMENDASI = [
    {
        "nama": "Beasiswa Unggulan Kemendikbud",
        "min_ipk": 3.25, "max_semester": 6,
        "jurusan": ["Teknik Informatika", "Sistem Informasi", "Ilmu Komputer",
                    "Teknik Elektro", "Matematika"],
        "wajib_organisasi": True,
        "max_penghasilan_ortu": 6_000_000,
    },
    {
        "nama": "Beasiswa Bank Indonesia",
        "min_ipk": 3.0, "max_semester": 8,
        "jurusan": ["Teknik Informatika", "Sistem Informasi",
                    "Ekonomi", "Manajemen", "Akuntansi"],
        "wajib_organisasi": False,
        "max_penghasilan_ortu": 5_000_000,
    },
    {
        "nama": "Beasiswa Djarum Foundation",
        "min_ipk": 3.2, "max_semester": 4,
        "jurusan": ["Teknik Informatika", "Sistem Informasi",
                    "Teknik Elektro", "Teknik Mesin", "Arsitektur"],
        "wajib_organisasi": True,
        "max_penghasilan_ortu": 8_000_000,
    },
    {
        "nama": "Beasiswa KIP Kuliah",
        "min_ipk": 2.75, "max_semester": 8,
        "jurusan": ["Teknik Informatika", "Sistem Informasi", "Ilmu Komputer",
                    "Ekonomi", "Hukum", "Kedokteran", "Farmasi"],
        "wajib_organisasi": False,
        "max_penghasilan_ortu": 4_000_000,
    },
    {
        "nama": "Beasiswa LPDP",
        "min_ipk": 3.5, "max_semester": 8,
        "jurusan": ["Teknik Informatika", "Sistem Informasi", "Ilmu Komputer",
                    "Teknik Elektro", "Fisika", "Matematika", "Biologi"],
        "wajib_organisasi": True,
        "max_penghasilan_ortu": 10_000_000,
    },
]


# ════════════════════════════════════════════════════════════
# ALGORITMA MATCHING
# ════════════════════════════════════════════════════════════

def hitung_skor_cocok(profil_user: dict, syarat_beasiswa: dict) -> int:
    """
    Menghitung persentase kecocokan profil mahasiswa dengan syarat beasiswa.
    Return: skor 0–100.
    """
    total = 0
    terpenuhi = 0

    # IPK
    total += 1
    if profil_user.get("ipk", 0) >= syarat_beasiswa.get("min_ipk", 0):
        terpenuhi += 1

    # Semester
    total += 1
    if profil_user.get("semester", 1) <= syarat_beasiswa.get("max_semester", 8):
        terpenuhi += 1

    # Jurusan
    total += 1
    daftar_jurusan = syarat_beasiswa.get("jurusan", [])
    if isinstance(daftar_jurusan, list):
        if profil_user.get("jurusan", "") in daftar_jurusan:
            terpenuhi += 1
    elif profil_user.get("jurusan") == daftar_jurusan:
        terpenuhi += 1

    # Organisasi
    total += 1
    if not syarat_beasiswa.get("wajib_organisasi", False):
        terpenuhi += 1
    elif profil_user.get("organisasi", False):
        terpenuhi += 1

    # Penghasilan orang tua
    total += 1
    if profil_user.get("penghasilan_ortu", 0) <= syarat_beasiswa.get("max_penghasilan_ortu", 999_999_999):
        terpenuhi += 1

    return int((terpenuhi / total) * 100) if total > 0 else 0


def analisis_peluang(data_profil: dict, target_beasiswa: dict) -> str:
    """
    Merekomendasikan cara meningkatkan peluang mendapatkan beasiswa.
    Return: teks analisis yang siap ditampilkan di GUI.
    """
    saran = []

    ipk = data_profil.get("ipk", 0)
    min_ipk = target_beasiswa.get("min_ipk", 0)
    if ipk < min_ipk:
        saran.append(
            f"- IPK Anda ({ipk:.2f}) masih di bawah syarat minimum ({min_ipk:.2f}). "
            f"Tingkatkan IPK minimal {min_ipk - ipk:.2f} poin."
        )

    semester = data_profil.get("semester", 1)
    max_sem = target_beasiswa.get("max_semester", 8)
    if semester > max_sem:
        saran.append(
            f"- Semester Anda ({semester}) melebihi batas maksimum ({max_sem}). "
            f"Pertimbangkan beasiswa lain."
        )

    jurusan = data_profil.get("jurusan", "")
    daftar = target_beasiswa.get("jurusan", [])
    if isinstance(daftar, list) and jurusan not in daftar:
        saran.append(f"- Jurusan Anda ({jurusan}) tidak termasuk dalam daftar yang diterima.")

    if target_beasiswa.get("wajib_organisasi") and not data_profil.get("organisasi"):
        saran.append("- Beasiswa ini mewajibkan pengalaman organisasi.")

    if not saran:
        return (
            "Selamat! Profil Anda memenuhi semua syarat beasiswa ini. "
            "Pastikan kelengkapan dokumen dan persiapkan diri untuk seleksi."
        )

    header = "Saran untuk meningkatkan peluang Anda:\n"
    return header + "\n".join(saran) + "\n\nTips: Perkuat portofolio dengan sertifikasi atau proyek."


def ambil_profil_untuk_rekomendasi(profil_id: int) -> dict:
    """
    Ambil data profil dalam format yang dibutuhkan algoritma rekomendasi.
    Menggunakan data dari DB, bukan nilai hardcoded.
    """
    from models.database import get_connection
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM profil WHERE id = ?", (profil_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return {}
    profil = dict(row)
    return {
        "jurusan":          profil.get("jurusan", ""),
        "ipk":              profil.get("ip", 0.0) or 0.0,
        "semester":         profil.get("semester", 1) or 1,
        # Default: belum ada kolom organisasi & penghasilan di DB,
        # fallback ke nilai konservatif sampai kolom ditambahkan
        "organisasi":       profil.get("aktif_organisasi", False),
        "penghasilan_ortu": profil.get("penghasilan_ortu", 5_000_000),
    }
