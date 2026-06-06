"""
models/rekomendasi_model.py
Beaply - Model: Rekomendasi Beasiswa

Data & algoritma pencocokan beasiswa dengan profil user.
Sekarang menggunakan data beasiswa dari database (bukan hardcoded).
"""

from models.database import get_connection


# ════════════════════════════════════════════════════════════
# DATA BEASISWA REKOMENDASI — DARI DATABASE
# ════════════════════════════════════════════════════════════

def _load_beasiswa_dari_db() -> list:
    """
    Ambil semua beasiswa dari DB dan konversi ke format rekomendasi.
    Setiap item punya field asli DB + field mapping untuk algoritma.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM beasiswa
        ORDER BY CASE WHEN deadline IS NULL THEN 1 ELSE 0 END, deadline ASC
    """)
    rows = cur.fetchall()
    conn.close()

    result = []
    for row in rows:
        bea = dict(row)
        # Tambahkan field mapping yang dipakai algoritma
        bea["min_ipk"] = bea.get("syarat_ipk", 0) or 0
        bea["max_semester"] = 8  # default, karena DB tidak punya field ini
        bea["jurusan"] = ["Semua Jurusan"]  # default open
        bea["wajib_organisasi"] = False  # default
        bea["max_penghasilan_ortu"] = 999_999_999  # default (tidak membatasi)
        # TOEFL / IELTS dari DB
        bea["min_toefl"] = bea.get("syarat_toefl", 0) or 0
        bea["min_ielts"] = bea.get("syarat_ielts", 0) or 0
        result.append(bea)
    return result


# Cache agar tidak query DB berulang kali dalam satu session
_cached_beasiswa = None


def get_daftar_beasiswa_rekomendasi() -> list:
    """Ambil daftar beasiswa untuk rekomendasi (cached per session)."""
    global _cached_beasiswa
    if _cached_beasiswa is None:
        _cached_beasiswa = _load_beasiswa_dari_db()
    return _cached_beasiswa


def refresh_cache():
    """Reset cache (dipanggil setelah scraping/update data)."""
    global _cached_beasiswa
    _cached_beasiswa = None


# Backward compat: controller sudah diupdate untuk memanggil
# get_daftar_beasiswa_rekomendasi() secara langsung.


# ════════════════════════════════════════════════════════════
# ALGORITMA MATCHING (DITINGKATKAN)
# ════════════════════════════════════════════════════════════

def hitung_skor_cocok(profil_user: dict, syarat_beasiswa: dict) -> int:
    """
    Menghitung persentase kecocokan profil mahasiswa dengan syarat beasiswa.
    Menggunakan weighted scoring untuk hasil yang lebih bervariasi.

    Bobot:
      - IPK kecocokan       : 25 poin (gradual, bukan binary)
      - Jenjang              : 20 poin
      - Deadline aktif       : 15 poin
      - Organisasi bonus     : 10 poin
      - TOEFL/IELTS          : 10 poin
      - Penghasilan ortu     : 10 poin
      - Kategori preference  : 10 poin
    Total max = 100.
    """
    from datetime import datetime
    skor = 0

    ipk_user = profil_user.get("ipk", 0) or 0
    min_ipk = syarat_beasiswa.get("min_ipk", 0) or 0

    # ── 1. IPK (25 poin) ──────────────────────────────────
    if min_ipk > 0:
        if ipk_user >= min_ipk:
            # Full score + bonus jika jauh di atas syarat
            skor += 25
        else:
            # Partial: seberapa dekat IPK user ke syarat
            ratio = ipk_user / min_ipk if min_ipk > 0 else 0
            skor += int(25 * ratio)
    else:
        # Beasiswa tanpa syarat IPK → berikan skor moderat
        # (lebih rendah dari yang punya syarat IPK dan lolos)
        if ipk_user >= 3.0:
            skor += 20
        elif ipk_user >= 2.5:
            skor += 15
        else:
            skor += 10

    # ── 2. Jenjang (20 poin) ──────────────────────────────
    jenjang_bea = syarat_beasiswa.get("jenjang", "")
    jenjang_user = profil_user.get("jenjang", "S1") or "S1"
    if jenjang_bea:
        if jenjang_user.upper() in jenjang_bea.upper():
            skor += 20
        else:
            skor += 0  # Jenjang tidak cocok → 0 poin
    else:
        skor += 10  # Tidak ada info jenjang → netral

    # ── 3. Deadline aktif (15 poin) ───────────────────────
    deadline = syarat_beasiswa.get("deadline", "")
    if deadline:
        try:
            dl_date = datetime.strptime(deadline, "%Y-%m-%d").date()
            days = (dl_date - datetime.now().date()).days
            if days < 0:
                skor += 0   # Sudah expired
            elif days <= 7:
                skor += 15  # Sangat urgent → prioritas tinggi
            elif days <= 30:
                skor += 12
            elif days <= 90:
                skor += 10
            else:
                skor += 8
        except (ValueError, TypeError):
            skor += 5
    else:
        skor += 5  # Tanpa deadline → skor netral

    # ── 4. Organisasi bonus (10 poin) ─────────────────────
    punya_org = bool(profil_user.get("organisasi") or profil_user.get("aktif_organisasi"))
    wajib_org = syarat_beasiswa.get("wajib_organisasi", False)
    if wajib_org:
        skor += 10 if punya_org else 0
    else:
        # Tidak wajib, tapi punya organisasi tetap bonus
        skor += 8 if punya_org else 5

    # ── 5. TOEFL / IELTS (10 poin) ────────────────────────
    min_toefl = syarat_beasiswa.get("min_toefl", 0) or syarat_beasiswa.get("syarat_toefl", 0) or 0
    min_ielts = syarat_beasiswa.get("min_ielts", 0) or syarat_beasiswa.get("syarat_ielts", 0) or 0
    skor_toefl_user = profil_user.get("skor_toefl", 0) or 0
    skor_ielts_user = profil_user.get("skor_ielts", 0) or 0

    if min_toefl > 0 or min_ielts > 0:
        lang_score = 0
        if min_toefl > 0:
            lang_score = 10 if skor_toefl_user >= min_toefl else int(10 * skor_toefl_user / min_toefl) if min_toefl > 0 else 0
        elif min_ielts > 0:
            lang_score = 10 if skor_ielts_user >= min_ielts else int(10 * skor_ielts_user / min_ielts) if min_ielts > 0 else 0
        skor += lang_score
    else:
        # Tidak ada syarat bahasa → bonus jika punya skor
        if skor_toefl_user > 0 or skor_ielts_user > 0:
            skor += 8
        else:
            skor += 5

    # ── 6. Penghasilan ortu (10 poin) ─────────────────────
    penghasilan = profil_user.get("penghasilan_ortu", 0) or 0
    max_penghasilan = syarat_beasiswa.get("max_penghasilan_ortu", 999_999_999)
    if max_penghasilan < 999_999_999:
        # Beasiswa punya batas penghasilan
        skor += 10 if penghasilan <= max_penghasilan else 0
    else:
        skor += 7  # Tidak ada batas → skor netral

    # ── 7. Kategori (10 poin) ─────────────────────────────
    # Jika user punya status KIP → prioritaskan beasiswa pemerintah
    kategori = syarat_beasiswa.get("kategori", "")
    status_kip = profil_user.get("status_kip", False)
    if status_kip and kategori == "pemerintah":
        skor += 10
    elif kategori == "internasional" and (skor_toefl_user > 0 or skor_ielts_user > 0):
        skor += 10
    else:
        skor += 5

    return min(skor, 100)


def analisis_peluang(data_profil: dict, target_beasiswa: dict) -> str:
    """
    Merekomendasikan cara meningkatkan peluang mendapatkan beasiswa.
    Return: teks analisis yang siap ditampilkan di GUI.
    """
    saran = []

    ipk = data_profil.get("ipk", 0)
    min_ipk = target_beasiswa.get("min_ipk", 0)
    if min_ipk > 0 and ipk < min_ipk:
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

    # Jenjang
    jenjang_bea = target_beasiswa.get("jenjang", "")
    jenjang_user = data_profil.get("jenjang", "S1")
    if jenjang_bea and jenjang_user.upper() not in jenjang_bea.upper():
        saran.append(f"- Jenjang Anda ({jenjang_user}) tidak sesuai dengan beasiswa ini ({jenjang_bea}).")

    jurusan = data_profil.get("jurusan", "")
    daftar = target_beasiswa.get("jurusan", [])
    if isinstance(daftar, list) and daftar:
        semua_jurusan = any(j.strip().lower() == "semua jurusan" for j in daftar)
        if not semua_jurusan and jurusan.lower() not in [j.lower() for j in daftar]:
            saran.append(f"- Jurusan Anda ({jurusan}) tidak termasuk dalam daftar yang diterima.")

    wajib_org = target_beasiswa.get("wajib_organisasi", False)
    punya_org = bool(data_profil.get("organisasi") or data_profil.get("aktif_organisasi"))
    if wajib_org and not punya_org:
        saran.append("- Beasiswa ini mewajibkan pengalaman organisasi.")

    # TOEFL
    min_toefl = target_beasiswa.get("min_toefl", 0) or target_beasiswa.get("syarat_toefl", 0) or 0
    if min_toefl > 0:
        user_toefl = data_profil.get("skor_toefl", 0) or 0
        if user_toefl < min_toefl:
            saran.append(f"- Skor TOEFL Anda ({user_toefl}) di bawah minimum ({min_toefl}).")

    # IELTS
    min_ielts = target_beasiswa.get("min_ielts", 0) or target_beasiswa.get("syarat_ielts", 0) or 0
    if min_ielts > 0:
        user_ielts = data_profil.get("skor_ielts", 0) or 0
        if user_ielts < min_ielts:
            saran.append(f"- Skor IELTS Anda ({user_ielts}) di bawah minimum ({min_ielts}).")

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
    Menggunakan data dari DB — termasuk field baru penghasilan_ortu.
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
        "jurusan":           profil.get("jurusan", ""),
        "ipk":               profil.get("ip", 0.0) or 0.0,
        "semester":          profil.get("semester", 1) or 1,
        "jenjang":           profil.get("jenjang", "S1") or "S1",
        # aktif_organisasi: 1 = ya, 0 = tidak
        "organisasi":        bool(profil.get("aktif_organisasi", 0)),
        "aktif_organisasi":  bool(profil.get("aktif_organisasi", 0)),
        # Skor bahasa dari profil
        "skor_toefl":        profil.get("skor_toefl", 0) or 0,
        "skor_ielts":        profil.get("skor_ielts", 0) or 0.0,
        # Penghasilan orang tua — dari DB, fallback 0 (dianggap belum diisi)
        "penghasilan_ortu":  profil.get("penghasilan_ortu", 0) or 0,
        # Status KIP
        "status_kip":        bool(profil.get("status_kip", 0)),
    }

