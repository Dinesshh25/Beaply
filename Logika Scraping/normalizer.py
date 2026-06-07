"""
normalizer.py
Modul utilitas untuk mem-parsing dan menormalisasi data beasiswa mentah
hasil scraping dari berbagai sumber website.
"""

import re
from datetime import datetime

# ─── Mapping bulan Indonesia ──────────────────────────────────────────────────
BULAN_ID = {
    'januari': 1, 'february': 2, 'februari': 2, 'maret': 3,
    'april': 4, 'mei': 5, 'juni': 6, 'juli': 7, 'agustus': 8,
    'september': 9, 'oktober': 10, 'november': 11, 'desember': 12,
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'jun': 6,
    'jul': 7, 'agu': 8, 'ags': 8, 'sep': 9, 'okt': 10, 'nov': 11, 'des': 12,
}

# ─── Filter tahun: hanya 2026 ke atas ─────────────────────────────────────────

def is_year_2026_or_later(entry: dict) -> bool:
    """
    Cek apakah beasiswa ini relevan untuk tahun 2026 ke atas.
    Mengecek dari:
      1. Path URL (cari folder tahun seperti /2025/ atau /2024/)
      2. Field deadline (format YYYY-MM-DD atau teks)
      3. Field deadline_text (cari angka tahun)
      4. Nama beasiswa (cari angka tahun seperti '2026', '2027')
      5. Full text (cari angka tahun)
    Jika tidak ada info tahun sama sekali, loloskan (asumsi relevan).
    Jika ada info tahun < 2026, tolak.
    """
    MIN_YEAR = 2026

    # 1. Cek URL untuk folder tahun lama (e.g. /2025/ atau /2024/)
    url = entry.get('url_sumber') or entry.get('url') or ''
    if url:
        m_url = re.search(r'/20(\d{2})/', url)
        if m_url:
            year_val = int("20" + m_url.group(1))
            if year_val < MIN_YEAR:
                return False

    # 2. Cek deadline terformat (YYYY-MM-DD)
    deadline = entry.get('deadline') or entry.get('deadline_text') or ''
    if deadline:
        dt = parse_tanggal_indonesia(str(deadline))
        if dt and dt.year < MIN_YEAR:
            return False
        if dt and dt.year >= MIN_YEAR:
            return True

    # 3. Cek teks untuk angka tahun
    combined_text = ' '.join(filter(None, [
        str(entry.get('nama_beasiswa', '')),
        str(entry.get('deadline_text', '')),
        str(entry.get('full_text', '')),
    ]))

    years_found = re.findall(r'\b(20\d{2})\b', combined_text)
    if years_found:
        years_int = [int(y) for y in years_found]
        max_year = max(years_int)
        if max_year < MIN_YEAR:
            return False
        return True

    # Tidak ada informasi tahun sama sekali → loloskan (asumsi relevan)
    return True


# ─── Kata kunci jenjang ───────────────────────────────────────────────────────
JENJANG_PATTERNS = {
    'S1':  [r'\bS[-\s]?1\b', r'\bSarjana\b', r'\bUndergraduate\b', r'\bBachelor\b',
            r'\bD4\b', r'\bDiploma[-\s]?4\b', r'\bbeasiswa[-\s]sarjana\b'],
    'S2':  [r'\bS[-\s]?2\b', r'\bMagister\b', r'\bMaster\b', r'\bPostgraduate\b',
            r'\bM\.?S\b', r'\bM\.?A\b', r'\bbeasiswa[-\s]magister\b'],
    'S3':  [r'\bS[-\s]?3\b', r'\bDoktor\b', r'\bPhD\b', r'\bDoctoral\b', r'\bDoktoral\b'],
    'D3':  [r'\bD[-\s]?3\b', r'\bDiploma[-\s]?3\b', r'\bAhli[-\s]Madya\b'],
    'D4':  [r'\bD[-\s]?4\b', r'\bDiploma[-\s]?4\b', r'\bSarjana[-\s]Terapan\b'],
    'D2':  [r'\bD[-\s]?2\b', r'\bDiploma[-\s]?2\b'],
    'SMA': [r'\bSMA\b', r'\bSMK\b', r'\bMA\b', r'\bSederajat\b', r'\bHigh[-\s]School\b'],
}

# Jenjang yang termasuk kategori mahasiswa (perguruan tinggi)
JENJANG_MAHASISWA = {'D2', 'D3', 'D4', 'S1', 'S2', 'S3'}

# Jenjang yang BUKAN mahasiswa (SMA/SMK ke bawah)
JENJANG_NON_MAHASISWA = {'SMA'}


def is_mahasiswa_only(jenjang_list: list[str], teks: str = '') -> bool:
    """
    Cek apakah beasiswa ini STRICTLY untuk mahasiswa (perguruan tinggi).
    Jika mengandung kata SMA, SMK, SMP, atau SD di jenjang atau teks, LANGSUNG TOLAK.
    """
    # 1. Pengecekan ketat teks (biasanya gabungan nama beasiswa + excerpt)
    teks_lower = teks.lower()
    if 'sma ' in teks_lower or 'smk ' in teks_lower or 'smp ' in teks_lower or 'sd ' in teks_lower:
        return False
    if 'sma/' in teks_lower or 'smk/' in teks_lower or 'smp/' in teks_lower:
        return False
        
    # 2. Pengecekan jenjang_list
    if jenjang_list:
        # Jika ada SMA/SMK di list jenjang, langsung tolak
        if any(j in JENJANG_NON_MAHASISWA for j in jenjang_list):
            return False
            
        # Jika ada minimal satu jenjang mahasiswa, loloskan
        if any(j in JENJANG_MAHASISWA for j in jenjang_list):
            return True
            
        return False

    # 3. Jenjang kosong → cek dari teks (ekstraksi jenjang)
    if teks:
        detected = extract_jenjang(teks)
        if detected:
            # Rekursif dengan jenjang yang terdeteksi, tapi teks dikosongkan agar tidak infinite loop
            return is_mahasiswa_only(detected, '')

    # Tidak ada info jenjang sama sekali, tapi sudah lolos filter teks (tidak ada kata SMA)
    return True


# ─── Kata kunci lokasi ────────────────────────────────────────────────────────
LOKASI_KEYWORDS = {
    'Luar Negeri': [
        'luar negeri', 'internasional', 'overseas', 'abroad',
        'jepang', 'japan', 'australia', 'inggris', 'uk', 'united kingdom',
        'amerika', 'usa', 'united states', 'belanda', 'netherlands',
        'jerman', 'germany', 'perancis', 'france', 'korea', 'china', 'tiongkok',
        'eropa', 'europe', 'asia', 'arab saudi', 'turki', 'turkey',
        'singapura', 'singapore', 'malaysia', 'kanada', 'canada',
        'new zealand', 'selandia baru', 'rusia', 'russia',
    ],
    'Dalam Negeri': [
        'indonesia', 'dalam negeri', 'domestic', 'nasional',
        'jakarta', 'bandung', 'surabaya', 'yogyakarta', 'semarang',
        'medan', 'makassar', 'palembang', 'depok', 'bogor',
    ],
}

# ─── Fungsi Parsing Tanggal ───────────────────────────────────────────────────

def parse_tanggal_indonesia(teks: str) -> datetime | None:
    """
    Parse teks tanggal bahasa Indonesia menjadi objek datetime.
    Contoh input: '31 Maret 2026', 'March 2026', '2026-03-31'
    """
    if not teks:
        return None

    teks = teks.strip().lower()

    # Format: YYYY-MM-DD
    m = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', teks)
    if m:
        try:
            return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            pass

    # Format: DD Bulan YYYY atau DD/MM/YYYY
    m = re.search(r'(\d{1,2})\s+([a-zA-Z]+)\s+(\d{4})', teks)
    if m:
        day  = int(m.group(1))
        mon  = BULAN_ID.get(m.group(2).lower()[:3])
        year = int(m.group(3))
        if mon:
            try:
                return datetime(year, mon, day)
            except ValueError:
                pass

    # Format: Bulan YYYY (tanpa hari) → pakai hari 1
    m = re.search(r'([a-zA-Z]+)\s+(\d{4})', teks)
    if m:
        mon  = BULAN_ID.get(m.group(1).lower()[:3])
        year = int(m.group(2))
        if mon:
            try:
                return datetime(year, mon, 1)
            except ValueError:
                pass

    # Format: DD/MM/YYYY
    m = re.search(r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})', teks)
    if m:
        try:
            return datetime(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            pass

    return None


def extract_deadlines(teks: str) -> str | None:
    """
    Coba parse deadline dari teks bebas.
    Return string 'YYYY-MM-DD' jika berhasil, atau teks asli (dipotong) jika gagal.
    """
    if not teks:
        return None
    dt = parse_tanggal_indonesia(teks)
    if dt:
        return dt.strftime('%Y-%m-%d')
    # Kembalikan teks mentah maks 150 karakter
    return teks.strip()[:150] if teks.strip() else None


# ─── Fungsi Ekstraksi ─────────────────────────────────────────────────────────

def extract_ipk(teks: str) -> float | None:
    """
    Ekstrak nilai IPK minimal dari teks.
    Contoh: 'IPK minimal 3.00', 'GPA min 3.5', 'IP ≥ 2.75'
    """
    if not teks:
        return None
    patterns = [
        r'[Ii][Pp][Kk]\s*(?:minimal?|minimum|min\.?|≥|>=|di\s*atas)?\s*:?\s*(\d+[.,]\d+)',
        r'[Gg][Pp][Aa]\s*(?:of\s*)?(?:at\s*least|minimum|min\.?|\d+\.?\d*)\s*:?\s*(\d+[.,]\d+)',
        r'[Ii][Pp]\s*(?:minimal?|min\.?)?\s*(?:≥|>=)\s*(\d+[.,]\d+)',
        r'nilai\s*(?:IP|IPK)\s*(?:minimal?|minimum)?\s*:?\s*(\d+[.,]\d+)',
    ]
    for pattern in patterns:
        m = re.search(pattern, teks, re.IGNORECASE)
        if m:
            try:
                return float(m.group(1).replace(',', '.'))
            except ValueError:
                pass
    return None


def extract_toefl(teks: str) -> int:
    """
    Ekstrak skor minimal TOEFL dari teks.
    Contoh: 'TOEFL 500', 'TOEFL iBT 80', 'TOEFL ITP minimal 550'
    """
    if not teks:
        return 0
    patterns = [
        r'toefl\s*(?:itp|pbt|ibt)?\s*(?:minimal?|minimum|score|skor|of|≥|>=)?\s*:?\s*(\d{3})',
        r'(\d{3})\s*(?:score|skor|points)?\s*(?:minimal?|minimum)?\s*toefl',
        r'toefl\s*ibt\s*(?:minimal?|minimum|score|skor|of|≥|>=)?\s*:?\s*([5-9]\d|1[0-1]\d)',
    ]
    for pattern in patterns:
        m = re.search(pattern, teks, re.IGNORECASE)
        if m:
            try:
                score = int(m.group(1))
                if 400 <= score <= 677:
                    return score
                elif 45 <= score <= 120:
                    return score
            except ValueError:
                pass
    return 0


def extract_ielts(teks: str) -> float:
    """
    Ekstrak skor minimal IELTS dari teks.
    Contoh: 'IELTS 6.5', 'IELTS minimal 6.0', 'IELTS ≥ 7.0'
    """
    if not teks:
        return 0.0
    patterns = [
        r'ielts\s*(?:minimal?|minimum|score|skor|of|≥|>=)?\s*:?\s*(\d[.,]\d)',
        r'(\d[.,]\d)\s*(?:score|skor|points)?\s*(?:minimal?|minimum)?\s*ielts',
        r'ielts\s*(?:minimal?|minimum|score|skor|of|≥|>=)?\s*:?\s*(\d)',
    ]
    for pattern in patterns:
        m = re.search(pattern, teks, re.IGNORECASE)
        if m:
            try:
                val = float(m.group(1).replace(',', '.'))
                if 4.0 <= val <= 9.0:
                    return val
            except ValueError:
                pass
    return 0.0


def extract_jenjang(teks: str) -> list[str]:
    """
    Ekstrak jenjang pendidikan dari teks.
    Return list string unik, mis: ['S1', 'S2']
    """
    if not teks:
        return []
    found = []
    for jenjang, patterns in JENJANG_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, teks, re.IGNORECASE):
                found.append(jenjang)
                break
    return list(dict.fromkeys(found))  # deduplikasi jaga urutan


def extract_lokasi(teks: str) -> str:
    """
    Tentukan lokasi beasiswa: 'Luar Negeri', 'Dalam Negeri', atau ''
    Berdasarkan kata kunci yang ditemukan dalam teks.
    """
    if not teks:
        return ''
    teks_lower = teks.lower()
    for lokasi, keywords in LOKASI_KEYWORDS.items():
        for kw in keywords:
            if kw in teks_lower:
                return lokasi
    return ''


def extract_tipe_beasiswa(teks: str, lokasi: str = '') -> str:
    """
    Tentukan tipe beasiswa: 'Luar Negeri' atau 'Dalam Negeri'.
    Jika lokasi sudah diketahui, gunakan nilai itu. Kalau tidak, analisis teks.
    """
    if lokasi in ('Luar Negeri', 'Dalam Negeri'):
        return lokasi
    return extract_lokasi(teks)


# ─── Normalisasi Utama ────────────────────────────────────────────────────────

def normalize_beasiswa(entry: dict) -> dict:
    """
    Normalisasi satu entri beasiswa mentah dari scraper menjadi format standar.

    Input  : dict mentah dari scraper (field bisa tidak lengkap / tidak konsisten)
    Output : dict terstandar siap disimpan ke database

    Field output yang dijamin ada (meski nilai None / [] / ''):
        nama_beasiswa, penyelenggara, jenjang, jurusan, lokasi, tipe_beasiswa,
        deadline, deadline_text, cakupan_beasiswa, syarat_utama, ipk_minimal,
        url_sumber, url_resmi, sumber_website, kategori_raw, full_text
    """
    # Salin agar tidak mutasi dict asli
    norm = dict(entry)

    # ── Nama beasiswa ─────────────────────────────────────────────────
    nama = str(norm.get('nama_beasiswa') or '').strip()
    # Bersihkan whitespace ganda
    nama = re.sub(r'\s+', ' ', nama)
    norm['nama_beasiswa'] = nama[:500]

    # ── Penyelenggara ─────────────────────────────────────────────────
    norm['penyelenggara'] = str(norm.get('penyelenggara') or '').strip()[:300]

    # ── Jenjang ───────────────────────────────────────────────────────
    jenjang = norm.get('jenjang', [])
    if isinstance(jenjang, str):
        jenjang = [jenjang] if jenjang else []
    # Jika belum ada, coba ekstrak dari nama + full_text
    if not jenjang:
        gabung = nama + ' ' + str(norm.get('full_text', ''))
        jenjang = extract_jenjang(gabung)
    norm['jenjang'] = jenjang

    # ── Jurusan ───────────────────────────────────────────────────────
    jurusan = norm.get('jurusan', [])
    if isinstance(jurusan, str):
        jurusan = [jurusan] if jurusan else []
    norm['jurusan'] = jurusan

    # ── Lokasi & Tipe ─────────────────────────────────────────────────
    lokasi = str(norm.get('lokasi') or '').strip()
    if not lokasi:
        gabung = nama + ' ' + str(norm.get('penyelenggara', '')) + ' ' + str(norm.get('full_text', ''))
        lokasi = extract_lokasi(gabung)
    norm['lokasi']        = lokasi
    norm['tipe_beasiswa'] = extract_tipe_beasiswa('', lokasi)

    # ── Deadline ──────────────────────────────────────────────────────
    deadline_text = str(norm.get('deadline_text') or '').strip()
    # Coba parse ke format YYYY-MM-DD
    deadline_terformat = extract_deadlines(deadline_text)
    norm['deadline']      = deadline_terformat
    norm['deadline_text'] = deadline_text[:300]

    # ── Cakupan & Syarat ─────────────────────────────────────────────
    norm['cakupan_beasiswa'] = str(norm.get('cakupan_beasiswa') or '').strip()[:1000]
    norm['syarat_utama']     = str(norm.get('syarat_utama')     or '').strip()[:2000]

    # ── IPK Minimal ───────────────────────────────────────────────────
    ipk = norm.get('ipk_minimal')
    if ipk is None:
        # Coba ekstrak dari full_text
        ipk = extract_ipk(str(norm.get('full_text', '')))
    try:
        norm['ipk_minimal'] = float(ipk) if ipk is not None else None
    except (ValueError, TypeError):
        norm['ipk_minimal'] = None

    # ── TOEFL & IELTS ─────────────────────────────────────────────────
    toefl = norm.get('syarat_toefl')
    if toefl is None or toefl == 0:
        toefl = extract_toefl(str(norm.get('full_text', '')) + " " + str(norm.get('syarat_utama', '')))
    try:
        norm['syarat_toefl'] = int(toefl) if toefl else 0
    except (ValueError, TypeError):
        norm['syarat_toefl'] = 0

    ielts = norm.get('syarat_ielts')
    if ielts is None or ielts == 0.0:
        ielts = extract_ielts(str(norm.get('full_text', '')) + " " + str(norm.get('syarat_utama', '')))
    try:
        norm['syarat_ielts'] = float(ielts) if ielts else 0.0
    except (ValueError, TypeError):
        norm['syarat_ielts'] = 0.0

    # ── URL ───────────────────────────────────────────────────────────
    norm['url_sumber']   = str(norm.get('url_sumber')  or '').strip()
    norm['url_resmi']    = str(norm.get('url_resmi')   or '').strip()
    norm['sumber_website'] = str(norm.get('sumber_website') or '').strip()

    # ── Kategori raw ──────────────────────────────────────────────────
    kat = norm.get('kategori_raw', [])
    if isinstance(kat, str):
        kat = [kat] if kat else []
    norm['kategori_raw'] = kat

    # ── Full text ─────────────────────────────────────────────────────
    norm['full_text'] = str(norm.get('full_text') or norm.get('excerpt') or '').strip()

    return norm
