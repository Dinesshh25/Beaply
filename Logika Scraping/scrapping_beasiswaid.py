"""
Beasiswa Scraper - Scraper khusus untuk beasiswa.id
Mengambil data beasiswa dari halaman kategori/listing dan halaman detail artikel.

Struktur beasiswa.id:
- Halaman listing: /category/beasiswa/ → berisi kartu artikel (judul + excerpt + kategori)
- Pagination: /category/beasiswa/page/2/, page/3/, dst.
- Halaman detail: /2026/nama-beasiswa/ → artikel lengkap dengan syarat, deadline, dll.
"""

import re
import time
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from normalizer import (
    parse_tanggal_indonesia, extract_deadlines, extract_ipk,
    extract_toefl, extract_ielts,
    extract_jenjang, extract_lokasi, normalize_beasiswa,
    is_mahasiswa_only, is_year_2026_or_later
)

logging.basicConfig(filename='scraper.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# ─── URL Sumber beasiswa.id ───────────────────────────────────────────────────
SOURCES_BEASISWAID = {
    'semua_beasiswa':   'https://beasiswa.id/category/beasiswa/',
    'beasiswa_s1':      'https://beasiswa.id/category/beasiswa/beasiswa-sarjana/',
    'beasiswa_s2':      'https://beasiswa.id/category/beasiswa/beasiswa-magister/',
    'beasiswa_s3':      'https://beasiswa.id/category/beasiswa/beasiswa-doktor/',
    'beasiswa_d3':      'https://beasiswa.id/category/beasiswa/beasiswa-diploma/',
    'beasiswa_luar_negeri': 'https://beasiswa.id/category/beasiswa/beasiswa-luar-negeri/',
    'beasiswa_dalam_negeri': 'https://beasiswa.id/category/beasiswa/beasiswa-dalam-negeri/',
}

# Kategori yang ingin di-scrape (bisa dikombinasikan)
DEFAULT_CATEGORIES = ['beasiswa_s1', 'beasiswa_s2', 'beasiswa_d3']


def create_driver():
    """Buat instance Chrome driver headless."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(options=chrome_options)


# ─── SCRAPE HALAMAN LISTING / KATEGORI ───────────────────────────────────────

def scrape_category_page(driver, base_url, max_pages=5, progress_callback=None):
    """
    Scrape satu halaman kategori beasiswa.id (dengan dukungan pagination).

    Struktur HTML yang ditarget:
      <article class="...">
        <h2 class="..."><a href="URL_DETAIL">JUDUL</a></h2>
        <div class="entry-categories">..kategori..</div>
        <div class="entry-summary"><p>EXCERPT</p></div>
      </article>

    Args:
        driver       : Selenium WebDriver
        base_url     : URL kategori awal (misal: https://beasiswa.id/category/beasiswa/beasiswa-sarjana/)
        max_pages    : Maksimum halaman yang di-scrape
        progress_callback : callable(str) untuk laporan progres

    Returns:
        list of dict: Data dasar tiap beasiswa (judul, url, excerpt, kategori)
    """
    results = []

    for page_num in range(1, max_pages + 1):
        # Bangun URL paginasi
        if page_num == 1:
            url = base_url
        else:
            # beasiswa.id pakai pola: /category/xxx/page/N/
            url = base_url.rstrip('/') + f'/page/{page_num}/'

        if progress_callback:
            progress_callback(f"Membuka halaman {page_num}: {url}")

        try:
            driver.get(url)
            # Tunggu sampai konten artikel muncul
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "article, .post, main"))
            )
            time.sleep(2)
        except Exception as e:
            logging.warning(f"Halaman {page_num} tidak termuat: {e}")
            break

        # Cek apakah halaman valid (bukan 404/empty)
        articles = driver.find_elements(By.CSS_SELECTOR, "article")
        if not articles:
            if progress_callback:
                progress_callback(f"Halaman {page_num} kosong, berhenti pagination.")
            break

        if progress_callback:
            progress_callback(f"Halaman {page_num}: ditemukan {len(articles)} artikel.")

        for article in articles:
            entry = _parse_card_article(article)
            if entry and entry.get('url_sumber'):
                results.append(entry)

    return results


def _parse_card_article(article_element):
    """
    Parse satu elemen <article> dari halaman listing beasiswa.id.

    Return dict fields:
        - nama_beasiswa  : Judul artikel
        - url_sumber     : Link ke halaman detail
        - excerpt        : Cuplikan teks dari listing
        - kategori_raw   : List kategori/tag dari website (misal: ['Beasiswa S1', 'Beasiswa Luar Negeri'])
        - jenjang        : List jenjang terdeteksi dari judul/kategori
        - lokasi         : Lokasi yang terdeteksi dari judul
    """
    entry = {
        'nama_beasiswa': '',
        'url_sumber':    '',
        'excerpt':       '',
        'kategori_raw':  [],
        'jenjang':       [],
        'lokasi':        '',
        # Field-field ini akan diisi saat scrape detail
        'penyelenggara':     '',
        'deadline_text':     '',
        'cakupan_beasiswa':  '',
        'syarat_utama':      '',
        'ipk_minimal':       None,
        'jurusan':           [],
        'full_text':         '',
    }

    # ── Judul & URL ──────────────────────────────────────────────────
    try:
        # beasiswa.id memakai <h2> atau <h3> dengan <a> di dalamnya
        judul_el = article_element.find_element(
            By.CSS_SELECTOR, "h2 a, h3 a, .entry-title a"
        )
        entry['nama_beasiswa'] = judul_el.text.strip()
        entry['url_sumber']    = judul_el.get_attribute('href') or ''
    except Exception:
        # Fallback: coba ambil semua link
        try:
            links = article_element.find_elements(By.TAG_NAME, 'a')
            for link in links:
                href = link.get_attribute('href') or ''
                if 'beasiswa.id' in href and '/category/' not in href and '/tag/' not in href:
                    entry['url_sumber']    = href
                    entry['nama_beasiswa'] = link.text.strip() or entry['nama_beasiswa']
                    break
        except Exception:
            pass

    if not entry['nama_beasiswa'] or not entry['url_sumber']:
        return None

    # ── Excerpt / Ringkasan ───────────────────────────────────────────
    try:
        excerpt_el = article_element.find_element(
            By.CSS_SELECTOR, ".entry-summary, .entry-content, p"
        )
        entry['excerpt'] = excerpt_el.text.strip()[:500]
    except Exception:
        pass

    # ── Kategori/Tag dari website ─────────────────────────────────────
    try:
        cat_elements = article_element.find_elements(
            By.CSS_SELECTOR, ".entry-categories a, .cat-links a, .tags-links a"
        )
        entry['kategori_raw'] = [c.text.strip() for c in cat_elements if c.text.strip()]
    except Exception:
        pass

    # ── Ekstraksi awal dari judul + kategori ─────────────────────────
    combined_text = entry['nama_beasiswa'] + ' ' + ' '.join(entry['kategori_raw'])
    entry['jenjang'] = extract_jenjang(combined_text)
    entry['lokasi']  = extract_lokasi(combined_text)

    return entry


# ─── SCRAPE HALAMAN DETAIL ARTIKEL ───────────────────────────────────────────

def scrape_detail_page(driver, url, progress_callback=None):
    """
    Scrape halaman detail artikel beasiswa di beasiswa.id.

    Halaman detail beasiswa.id biasanya berisi:
    - Judul lengkap
    - Isi artikel dengan seksi: Penyelenggara, Cakupan/Manfaat, Syarat, Deadline, Cara Mendaftar

    Returns:
        dict atau None jika gagal
    """
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "article, .entry-content, .post-content"))
        )
        time.sleep(2)

        detail = {
            'full_text':        '',
            'penyelenggara':    '',
            'cakupan_beasiswa': '',
            'deadline_text':    '',
            'syarat_utama':     '',
            'ipk_minimal':      None,
            'jurusan':          [],
        }

        # ── Ambil teks konten utama ───────────────────────────────────
        try:
            content_el = driver.find_element(
                By.CSS_SELECTOR,
                "article .entry-content, .entry-content, .post-content, article"
            )
            detail['full_text'] = content_el.text
        except Exception:
            paragraphs = driver.find_elements(By.TAG_NAME, 'p')
            detail['full_text'] = '\n'.join(p.text for p in paragraphs)

        full_text = detail['full_text']
        if not full_text:
            return None

        # ── Penyelenggara ─────────────────────────────────────────────
        penyelenggara_match = re.search(
            r'(?:Penyelenggara|Pemberi Beasiswa|Lembaga)[:\s]+(.*?)(?:\n|Cakupan|Manfaat|Persyaratan|Syarat|Deadline|$)',
            full_text, re.IGNORECASE
        )
        if penyelenggara_match:
            detail['penyelenggara'] = penyelenggara_match.group(1).strip()[:200]

        # ── Cakupan / Manfaat Beasiswa ────────────────────────────────
        cakupan_patterns = [
            r'(?:Cakupan Beasiswa|Manfaat Beasiswa|Fasilitas Beasiswa|Keuntungan|Cakupan)[:\s]*(.*?)(?:Persyaratan|Syarat|Cara Mendaftar|Deadline|Batas Waktu|$)',
            r'(?:Beasiswa ini mencakup|Penerima akan mendapatkan)[:\s]*(.*?)(?:\n\n|Persyaratan|$)',
        ]
        for pattern in cakupan_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE | re.DOTALL)
            if match:
                detail['cakupan_beasiswa'] = match.group(1).strip()[:500]
                break

        # ── Deadline / Batas Waktu ────────────────────────────────────
        deadline_patterns = [
            r'(?:Deadline|Batas Waktu Pendaftaran|Batas Pendaftaran|Pendaftaran ditutup)[:\s]*(.*?)(?:\n|Cara Mendaftar|Info|$)',
            r'(?:Jadwal Pendaftaran|Periode Pendaftaran)[:\s]*(.*?)(?:\n\n|Persyaratan|$)',
            r'(?:Dibuka hingga|Open until)[:\s]*(.*?)(?:\n|$)',
        ]
        for pattern in deadline_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                detail['deadline_text'] = match.group(1).strip()[:200]
                break

        # ── Syarat / Persyaratan ──────────────────────────────────────
        syarat_patterns = [
            r'(?:Persyaratan|Syarat Umum|Syarat Pendaftaran|Kriteria Penerima|Ketentuan)[:\s]*(.*?)(?:Cara Mendaftar|Deadline|Batas|Kontak|Info|$)',
        ]
        for pattern in syarat_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE | re.DOTALL)
            if match:
                detail['syarat_utama'] = match.group(1).strip()[:800]
                break

        # ── IPK Minimal ───────────────────────────────────────────────
        detail['ipk_minimal'] = extract_ipk(full_text)

        # ── Jurusan / Prodi ───────────────────────────────────────────
        jurusan_patterns = [
            r'(?:jurusan|program studi|prodi|bidang studi)[:\s]*(.*?)(?:\.|,\s*IPK|\n)',
            r'(?:semua jurusan|seluruh prodi|terbuka untuk semua)',
        ]
        for pattern in jurusan_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                if 'semua' in match.group(0).lower() or 'seluruh' in match.group(0).lower():
                    detail['jurusan'] = ['Semua Jurusan']
                else:
                    jurusan_text = match.group(1).strip()
                    detail['jurusan'] = [j.strip() for j in re.split(r'[,/;]', jurusan_text) if j.strip()][:10]
                break

        return detail

    except Exception as e:
        logging.error(f"Error scraping detail {url}: {e}")
        return None


# ─── FUNGSI UTAMA ORCHESTRATOR ────────────────────────────────────────────────

def jalankan_scraper_beasiswaid(
    progress_callback=None,
    categories=None,
    scrape_details=True,
    max_pages_per_category=3,
    max_entries=100,
    cancelled_check=None
):
    """
    Fungsi utama untuk menjalankan scraping dari beasiswa.id.

    Strategi scraping:
      1. Iterasi tiap kategori yang dipilih (S1, S2, D3, dll.)
      2. Scrape halaman listing per kategori (dengan pagination)
      3. Deduplikasi berdasarkan URL
      4. Scrape halaman detail tiap beasiswa (opsional)
      5. Normalisasi data menggunakan modul normalizer

    Args:
        progress_callback        : callable(str) untuk kirim pesan progres ke UI
        categories               : list key dari SOURCES_BEASISWAID (default: S1, S2, D3)
        scrape_details           : bool, apakah buka halaman detail
        max_pages_per_category   : maks halaman per kategori
        max_entries              : maks total beasiswa yang diproses ke detail+normalisasi
        cancelled_check          : callable() -> bool, cek apakah proses dibatalkan user

    Returns:
        list of dict: Data beasiswa yang sudah dinormalisasi, siap disimpan ke DB
    """
    if categories is None:
        categories = DEFAULT_CATEGORIES

    driver = None
    try:
        if progress_callback:
            progress_callback("Membuka browser untuk beasiswa.id...")

        driver = create_driver()
        all_raw_entries = []
        seen_urls = set()  # Untuk deduplikasi

        # ── TAHAP 1: Scrape semua kategori yang dipilih ───────────────
        for cat_key in categories:
            if cancelled_check and cancelled_check():
                break

            base_url = SOURCES_BEASISWAID.get(cat_key)
            if not base_url:
                logging.warning(f"Kategori tidak dikenal: {cat_key}")
                continue

            if progress_callback:
                progress_callback(f"Tahap 1 - Scraping kategori: {cat_key} ({base_url})")

            entries = scrape_category_page(
                driver,
                base_url,
                max_pages=max_pages_per_category,
                progress_callback=progress_callback
            )

            # Deduplikasi
            new_count = 0
            for entry in entries:
                url = entry.get('url_sumber', '')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_raw_entries.append(entry)
                    new_count += 1

            if progress_callback:
                progress_callback(
                    f"Kategori '{cat_key}': {new_count} beasiswa baru "
                    f"(total unik: {len(all_raw_entries)})"
                )

        if progress_callback:
            progress_callback(f"Tahap 1 selesai: {len(all_raw_entries)} beasiswa unik ditemukan.")

        if cancelled_check and cancelled_check():
            return []

        # ── Filter: hanya beasiswa untuk mahasiswa (D3/D4/S1/S2/S3) ──
        # Beasiswa khusus SMA/SMK sederajat ke bawah akan dibuang
        filtered = []
        removed_count = 0
        for entry in all_raw_entries:
            jenjang = entry.get('jenjang', [])
            # Gabungkan teks untuk pengecekan lebih akurat
            combined_text = (
                entry.get('nama_beasiswa', '') + ' ' +
                ' '.join(entry.get('kategori_raw', [])) + ' ' +
                entry.get('excerpt', '')
            )
            if is_mahasiswa_only(jenjang, combined_text):
                filtered.append(entry)
            else:
                removed_count += 1
                if progress_callback:
                    progress_callback(
                        f"  ⛔ Dibuang (SMA/SMK): {entry.get('nama_beasiswa', '')[:60]}"
                    )

        if progress_callback:
            progress_callback(
                f"Setelah filter mahasiswa: {len(filtered)} beasiswa lolos, "
                f"{removed_count} dibuang (SMA/SMK)."
            )

        # Filter tahun: hanya 2026 ke atas
        filtered_year = []
        removed_year = 0
        for entry in filtered:
            if is_year_2026_or_later(entry):
                filtered_year.append(entry)
            else:
                removed_year += 1
                if progress_callback:
                    progress_callback(
                        f"  ⛔ Dibuang (< 2026): {entry.get('nama_beasiswa', '')[:60]}"
                    )
        filtered = filtered_year
        if progress_callback:
            progress_callback(
                f"Setelah filter tahun ≥ 2026: {len(filtered)} beasiswa lolos, "
                f"{removed_year} dibuang (tahun lama)."
            )

        # ── TAHAP 2: Scrape detail per URL ────────────────────────────────
        if scrape_details:
            if progress_callback:
                progress_callback("Tahap 2: Mengambil detail tiap beasiswa...")

            entries_to_process = filtered[:max_entries]
            total = len(entries_to_process)

            for idx, entry in enumerate(entries_to_process):
                if cancelled_check and cancelled_check():
                    break

                url = entry.get('url_sumber', '')
                if not url:
                    continue

                if progress_callback:
                    progress_callback(
                        f"Detail [{idx + 1}/{total}]: "
                        f"{entry.get('nama_beasiswa', '')[:55]}..."
                    )

                detail = scrape_detail_page(driver, url, progress_callback)
                if detail:
                    # Merge data detail ke entry, prioritas data detail jika lebih lengkap
                    if detail.get('penyelenggara') and not entry.get('penyelenggara'):
                        entry['penyelenggara'] = detail['penyelenggara']
                    if detail.get('cakupan_beasiswa') and not entry.get('cakupan_beasiswa'):
                        entry['cakupan_beasiswa'] = detail['cakupan_beasiswa']
                    if detail.get('deadline_text') and not entry.get('deadline_text'):
                        entry['deadline_text'] = detail['deadline_text']
                    if detail.get('syarat_utama') and not entry.get('syarat_utama'):
                        entry['syarat_utama'] = detail['syarat_utama']
                    if detail.get('ipk_minimal') and not entry.get('ipk_minimal'):
                        entry['ipk_minimal'] = detail['ipk_minimal']
                    if detail.get('jurusan') and not entry.get('jurusan'):
                        entry['jurusan'] = detail['jurusan']
                    if detail.get('full_text'):
                        entry['full_text'] = detail['full_text']
                        # Update jenjang & lokasi dari full_text yang lebih lengkap
                        if not entry.get('jenjang'):
                            entry['jenjang'] = extract_jenjang(detail['full_text'])
                        if not entry.get('lokasi'):
                            entry['lokasi'] = extract_lokasi(detail['full_text'])

                time.sleep(1.5)  # Jeda sopan agar tidak membebani server

        # ── TAHAP 3: Normalisasi data ─────────────────────────────────
        if progress_callback:
            progress_callback("Tahap 3: Normalisasi data beasiswa.id...")

        normalized = []
        for entry in filtered[:max_entries]:
            # Tambah field full_text dari excerpt jika detail tidak di-scrape
            if not entry.get('full_text') and entry.get('excerpt'):
                entry['full_text'] = entry['excerpt']

            norm = normalize_beasiswa(entry)

            # Tandai sumber
            norm['sumber_website'] = 'beasiswa.id'

            normalized.append(norm)

        # Filter akhir setelah normalisasi (Tahun, Jenjang Mahasiswa, dan TOEFL/IELTS)
        final_normalized = []
        removed_year = 0
        removed_level = 0
        removed_lang = 0
        
        for norm in normalized:
            # 1. Cek tahun
            if not is_year_2026_or_later(norm):
                removed_year += 1
                if progress_callback:
                    progress_callback(f"  ⛔ Dibuang akhir (< 2026): {norm.get('nama_beasiswa', '')[:60]}")
                continue
            
            # 2. Cek PT (Mahasiswa)
            jenjang = norm.get('jenjang', [])
            full_text = norm.get('nama_beasiswa', '') + ' ' + norm.get('full_text', '')
            if not is_mahasiswa_only(jenjang, full_text):
                removed_level += 1
                if progress_callback:
                    progress_callback(f"  ⛔ Dibuang akhir (SMA/SMK): {norm.get('nama_beasiswa', '')[:60]}")
                continue
            
            # 3. Cek TOEFL/IELTS
            if (norm.get('syarat_toefl', 0) > 0) or (norm.get('syarat_ielts', 0.0) > 0.0):
                final_normalized.append(norm)
            else:
                removed_lang += 1
                if progress_callback:
                    progress_callback(f"  ⛔ Dibuang akhir (Tanpa TOEFL/IELTS): {norm.get('nama_beasiswa', '')[:60]}")
        
        normalized = final_normalized

        if progress_callback:
            if removed_year > 0 or removed_level > 0 or removed_lang > 0:
                progress_callback(
                    f"Filter akhir: {len(normalized)} beasiswa lolos. Dibuang: "
                    f"{removed_year} tahun lama, {removed_level} non-PT, {removed_lang} tanpa TOEFL/IELTS."
                )
            progress_callback(
                f"Scraping beasiswa.id selesai! "
                f"Total: {len(normalized)} beasiswa dinormalisasi."
            )

        return normalized

    except Exception as e:
        logging.error(f"Error utama scraper beasiswa.id: {e}")
        if progress_callback:
            progress_callback(f"Error beasiswa.id: {str(e)}")
        return []

    finally:
        if driver:
            driver.quit()


# ─── RUN LANGSUNG (Testing) ───────────────────────────────────────────────────

if __name__ == '__main__':
    def print_progress(msg):
        print(f"[PROGRESS] {msg}")

    hasil = jalankan_scraper_beasiswaid(
        progress_callback=print_progress,
        categories=['beasiswa_s1', 'beasiswa_s2'],
        scrape_details=False,       # Set True untuk scrape detail lengkap
        max_pages_per_category=2,   # 2 halaman per kategori
        max_entries=10
    )

    print(f"\n=== HASIL: {len(hasil)} beasiswa ===")
    for b in hasil[:5]:
        print(f"\n  Nama        : {b.get('nama_beasiswa', '')[:80]}")
        print(f"  Penyelenggara: {b.get('penyelenggara', '-')}")
        print(f"  Jenjang     : {b.get('jenjang', [])}")
        print(f"  Deadline    : {b.get('deadline', '-')}")
        print(f"  Lokasi      : {b.get('lokasi', '-')}")
        print(f"  Sumber      : {b.get('sumber_website', '-')}")
        print(f"  URL         : {b.get('url_sumber', '-')}")
