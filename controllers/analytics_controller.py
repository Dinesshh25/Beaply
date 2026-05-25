"""
controllers/analytics_controller.py
Beaply – Analytics Controller

Analisis data beasiswa untuk menghasilkan insight bermakna:
  - Distribusi deadline per bulan
  - Distribusi per hari dalam bulan
  - Distribusi per jenjang
  - Distribusi per region (DN vs LN)
  - Insight & FAQ otomatis dari pola data
"""

import datetime
from collections import Counter
from models.beasiswa_model import ambil_semua_beasiswa


# ────────────────────────────────────────────────────────────
# HELPERS
# ────────────────────────────────────────────────────────────

BULAN = ["", "Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
         "Jul", "Ags", "Sep", "Okt", "Nov", "Des"]

BULAN_FULL = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
              "Juli", "Agustus", "September", "Oktober", "November", "Desember"]


def _parse_date(s):
    """Safely parse YYYY-MM-DD string → date or None."""
    if not s:
        return None
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        return None


# ────────────────────────────────────────────────────────────
# CORE ANALYSIS
# ────────────────────────────────────────────────────────────

def get_analytics_data() -> dict:
    """
    Hasilkan semua data analitik dari database beasiswa.
    Return dict dengan kunci:
      - deadline_by_month   : list[(label, count)]  — 12 bulan
      - deadline_by_day     : list[(label, count)]  — hari 1-31
      - by_jenjang          : list[(label, count)]
      - by_region           : list[(label, count)]
      - by_tipe             : list[(label, count)]
      - total               : int
      - with_deadline       : int
      - peak_month          : dict {month, label, count}
      - peak_day            : dict {day, count}
      - insights            : list[dict]  ← FAQ / Insight cards
    """
    all_bea = ambil_semua_beasiswa()
    total = len(all_bea)

    months_c  = Counter({m: 0 for m in range(1, 13)})
    days_c    = Counter({d: 0 for d in range(1, 32)})
    jenjang_c = Counter()
    region_c  = Counter()
    tipe_c    = Counter()
    with_dl   = 0

    for bea in all_bea:
        # deadline
        dl = _parse_date(bea.get("deadline"))
        if dl:
            with_dl += 1
            months_c[dl.month] += 1
            days_c[dl.day] += 1

        # jenjang (stored as "S1, S2" string in DB)
        jenjang_raw = bea.get("jenjang", "") or ""
        for j in [x.strip() for x in jenjang_raw.split(",") if x.strip()]:
            jenjang_c[j] += 1

        # region / kategori dari DB (pemerintah / swasta / internasional)
        kat = bea.get("kategori", "swasta")
        if kat == "internasional":
            region_c["Luar Negeri"] += 1
        else:
            region_c["Dalam Negeri"] += 1

        # pendanaan as tipe proxy
        pendanaan = bea.get("pendanaan", "") or ""
        if pendanaan:
            tipe_c[pendanaan] += 1
        else:
            tipe_c["Tidak Diketahui"] += 1

    # Build series lists
    deadline_by_month = [(BULAN[m], months_c[m]) for m in range(1, 13)]
    deadline_by_day   = [(str(d), days_c[d]) for d in range(1, 32)]
    by_jenjang        = sorted(jenjang_c.items(), key=lambda x: -x[1])
    by_region         = sorted(region_c.items(), key=lambda x: -x[1])
    by_tipe           = sorted(tipe_c.items(), key=lambda x: -x[1])[:6]

    # Peak analysis
    peak_month_num  = max(months_c, key=months_c.get) if months_c else 1
    peak_month_cnt  = months_c[peak_month_num]
    peak_day_num    = max(days_c, key=days_c.get) if days_c else 1
    peak_day_cnt    = days_c[peak_day_num]

    peak_month = {"month": peak_month_num,
                  "label": BULAN_FULL[peak_month_num],
                  "count": peak_month_cnt}
    peak_day   = {"day": peak_day_num, "count": peak_day_cnt}

    insights = _build_insights(
        total, with_dl, peak_month, peak_day,
        by_jenjang, by_region, by_tipe, deadline_by_month
    )

    return {
        "deadline_by_month": deadline_by_month,
        "deadline_by_day":   deadline_by_day,
        "by_jenjang":        by_jenjang,
        "by_region":         by_region,
        "by_tipe":           by_tipe,
        "total":             total,
        "with_deadline":     with_dl,
        "peak_month":        peak_month,
        "peak_day":          peak_day,
        "insights":          insights,
    }


# ────────────────────────────────────────────────────────────
# INSIGHT / FAQ BUILDER
# ────────────────────────────────────────────────────────────

def _build_insights(total, with_dl, peak_month, peak_day,
                    by_jenjang, by_region, by_tipe, monthly_series) -> list:
    """
    Buat daftar insight / FAQ card secara otomatis dari pola data.
    Setiap insight: {icon, title, body, tag}
    """
    insights = []
    pm = peak_month
    pd = peak_day

    # ── Insight 1: Peak Month ──
    if pm["count"] > 0:
        # Find second highest month for context
        monthly_sorted = sorted(
            enumerate(monthly_series, 1),
            key=lambda x: -x[1][1]
        )
        top2 = monthly_sorted[:2]
        body_parts = [
            f"Bulan {pm['label']} adalah puncak deadline beasiswa "
            f"dengan {pm['count']} beasiswa berakhir di bulan ini."
        ]
        if len(top2) >= 2:
            m2_num, (m2_lbl, m2_cnt) = top2[1]
            body_parts.append(
                f"Bulan {m2_lbl} menyusul dengan {m2_cnt} beasiswa. "
                "Ini karena banyak penyelenggara menyesuaikan siklus "
                "akademik semester ganjil & genap."
            )
        insights.append({
            "icon": "📅",
            "title": f"Mengapa banyak deadline di bulan {pm['label']}?",
            "body": " ".join(body_parts),
            "tag": "Deadline Trend",
        })

    # ── Insight 2: Peak Day of Month ──
    if pd["count"] > 0:
        day_explanations = {
            1:  "Tanggal 1 adalah awal bulan — banyak penyelenggara "
                "memilihnya sebagai batas akhir karena mudah diingat dan "
                "selaras dengan siklus anggaran bulanan.",
            15: "Tanggal 15 (pertengahan bulan) sering dipilih agar "
                "memberi ruang persiapan bagi calon pendaftar.",
            28: "Tanggal 28 dipilih karena konsisten berlaku di semua bulan, "
                "termasuk Februari.",
            30: "Tanggal 30/31 menandai akhir bulan — batas alami "
                "siklus administrasi.",
            31: "Tanggal 31 sering muncul sebagai batas akhir periode "
                "pelaporan keuangan penyelenggara.",
        }
        explanation = day_explanations.get(
            pd["day"],
            f"Tanggal {pd['day']} dipilih penyelenggara untuk kemudahan "
            "perencanaan dan konsistensi jadwal internal mereka."
        )
        insights.append({
            "icon": "🔢",
            "title": f"Kenapa banyak beasiswa berdeadline tanggal {pd['day']}?",
            "body": f"{pd['count']} beasiswa berakhir di tanggal {pd['day']}. {explanation}",
            "tag": "Pola Tanggal",
        })

    # ── Insight 3: Region Distribution ──
    if by_region:
        total_r = sum(c for _, c in by_region)
        ln_count = dict(by_region).get("Luar Negeri", 0)
        dn_count = dict(by_region).get("Dalam Negeri", 0)
        ln_pct = int(ln_count / total_r * 100) if total_r else 0
        insights.append({
            "icon": "🌍",
            "title": "Lebih banyak beasiswa luar negeri atau dalam negeri?",
            "body": (
                f"{ln_pct}% beasiswa yang tersedia adalah beasiswa luar negeri "
                f"({ln_count} dari {total_r}). Beasiswa internasional mendominasi "
                "karena banyak universitas dan pemerintah asing aktif merekrut "
                "pelajar Indonesia melalui program beasiswa kompetitif."
            ),
            "tag": "Distribusi Region",
        })

    # ── Insight 4: Jenjang ──
    if by_jenjang:
        top_j, top_j_cnt = by_jenjang[0]
        insights.append({
            "icon": "🎓",
            "title": f"Jenjang {top_j} paling banyak tersedia — mengapa?",
            "body": (
                f"Terdapat {top_j_cnt} slot beasiswa untuk jenjang {top_j} — "
                "terbanyak dibandingkan jenjang lain. Ini mencerminkan tingginya "
                "permintaan pendidikan tingkat pertama dan komitmen banyak "
                "penyelenggara untuk mendukung mahasiswa baru."
            ),
            "tag": "Distribusi Jenjang",
        })

    # ── Insight 5: Timing tip ──
    today = datetime.date.today()
    early_months = {1, 2, 3}  # Jan-Mar typically high
    if today.month in early_months:
        tip = (
            "Kamu berada di periode paling aktif pendaftaran beasiswa! "
            "Januari–Maret adalah waktu terbanyak deadline muncul. "
            "Segera lengkapi dokumen dan daftar sekarang."
        )
    elif today.month in {10, 11, 12}:
        tip = (
            "Akhir tahun bukan musim sepi! Banyak beasiswa membuka "
            "pendaftaran di Q4 untuk siklus tahun depan. Persiapkan "
            "dokumen mulai dari sekarang."
        )
    else:
        tip = (
            "Pastikan kamu memantau beasiswa setiap minggu. "
            "Rata-rata beasiswa menutup pendaftaran 30 hari setelah dibuka — "
            "jangan sampai ketinggalan!"
        )
    insights.append({
        "icon": "💡",
        "title": "Kapan waktu terbaik mendaftar beasiswa?",
        "body": tip,
        "tag": "Tips Strategis",
    })

    # ── Insight 6: Coverage ──
    no_dl = total - with_dl
    if no_dl > 0:
        insights.append({
            "icon": "⏳",
            "title": f"Ada {no_dl} beasiswa tanpa deadline — apa artinya?",
            "body": (
                f"{no_dl} beasiswa tidak mencantumkan deadline. Ini bisa berarti "
                "pendaftaran berlangsung sepanjang tahun (rolling admission), "
                "atau informasi belum diperbarui. Kunjungi situs resmi "
                "penyelenggara untuk memastikan."
            ),
            "tag": "Info Penting",
        })

    return insights
