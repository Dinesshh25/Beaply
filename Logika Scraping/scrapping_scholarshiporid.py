"""
Beasiswa Scraper - Scraper khusus untuk scholarship.or.id
Target: cari.scholarship.or.id (subdomain platform pencari beasiswa)

Struktur website:
  - Halaman listing  : https://cari.scholarship.or.id/listings/
  - Halaman kategori : https://cari.scholarship.or.id/listing-category/<slug>/
  - Halaman detail   : https://cari.scholarship.or.id/listing/<slug-beasiswa>/

Kategori yang tersedia:
  - beasiswa-internasional
  - beasiswa-pemerintah
  - beasiswa-swasta

Catatan penting:
  - Listing dirender secara dinamis (JavaScript), perlu Selenium + WebDriverWait
  - Halaman detail berisi deskripsi panjang + link sumber resmi
  - Tidak ada pagination klasik; semua listing bisa dimuat via AJAX/scroll
    → Strategi: scroll ke bawah untuk memuat semua kartu, lalu ambil semua link
"""

import re
import time
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from normalizer import (
    extract_ipk, extract_jenjang, extract_lokasi, normalize_beasiswa
)

logging.basicConfig(
    filename='scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ─── Konstanta URL ─────────────────────────────────────────────────────────────
BASE_URL   = 'https://cari.scholarship.or.id'
LISTINGS   = f'{BASE_URL}/listings/'

CATEGORIES = {
    'internasional': f'{BASE_URL}/listing-category/beasiswa-internasional/',
    'pemerintah':    f'{BASE_URL}/listing-category/beasiswa-pemerintah/',
    'swasta':        f'{BASE_URL}/listing-category/beasiswa-swasta/',
}

DEFAULT_CATEGORIES = ['internasional', 'pemerintah', 'swasta']


# ─── Driver ───────────────────────────────────────────────────────────────────

def create_driver():
    """Buat instance Chrome driver headless."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--log-level=3")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(options=options)


# ─── Scroll Helper ────────────────────────────────────────────────────────────

def _scroll_to_bottom(driver, pause=1.5, max_scrolls=15):
    """
    Scroll halaman ke bawah secara bertahap untuk memuat konten lazy-load/AJAX.
    Berhenti jika tidak ada perubahan tinggi halaman (artinya semua konten sudah termuat).
    """
    last_height = driver.execute_script("return document.body.scrollHeight")
    scrolls = 0
    while scrolls < max_scrolls:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break  # Tidak ada konten baru, berhenti scroll
        last_height = new_height
        scrolls += 1


# ─── SCRAPE HALAMAN LISTING / KATEGORI ───────────────────────────────────────

def scrape_listings_page(driver, url, progress_callback=None):
    """
    Scrape satu halaman listing atau kategori dari cari.scholarship.or.id.

    Strategi:
      1. Buka URL → tunggu kartu listing muncul
      2. Scroll ke bawah agar semua listing ter-load (lazy/AJAX)
      3. Ambil semua elemen listing card: judul, URL, kategori, deskripsi singkat

    HTML Target (berdasarkan analisis):
      <div class="listing-item"> atau <article class="listing-item">
        <h4><a href="URL_DETAIL">JUDUL</a></h4>
        <span class="listing-category">KATEGORI</span>
        <div class="listing-content">DESKRIPSI</div>

    Returns:
        list of dict: Data dasar tiap beasiswa dari listing
    """
    results = []

    try:
        if progress_callback:
            progress_callback(f"Membuka: {url}")

        driver.get(url)

        # Tunggu sampai minimal satu kartu listing muncul
        try:
            WebDriverWait(driver, 12).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     "article, .listing-item, .post-listing, .wpbdp-listing, "
                     "h4 a[href*='/listing/'], h3 a[href*='/listing/']")
                )
            )
        except TimeoutException:
            logging.warning(f"Timeout menunggu listing di: {url}")
            if progress_callback:
                progress_callback(f"Timeout di {url}, mencoba lanjut...")

        time.sleep(2)

        # Scroll untuk memuat semua kartu (AJAX / infinite scroll)
        if progress_callback:
            progress_callback("Scrolling halaman untuk memuat semua listing...")
        _scroll_to_bottom(driver, pause=1.5, max_scrolls=15)

        # ── Strategi 1: Cari semua link yang mengarah ke /listing/ ──────
        # Ini cara paling robust karena langsung ambil semua anchor ke detail
        all_links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/listing/']")

        seen_hrefs = set()
        for link in all_links:
            href = link.get_attribute('href') or ''
            # Filter: hanya link ke halaman detail (bukan kategori, bukan listing page sendiri)
            if (href
                    and '/listing/' in href
                    and '/listing-category/' not in href
                    and '/listings/' not in href
                    and href not in seen_hrefs):
                seen_hrefs.add(href)

                nama = link.text.strip()
                if not nama:
                    # Coba ambil dari parent element
                    try:
                        parent = link.find_element(By.XPATH, '..')
                        nama = parent.text.strip() or ''
                    except Exception:
                        nama = ''

                if not nama:
                    # Ambil dari title attribute
                    nama = link.get_attribute('title') or ''

                # Ambil kategori dari elemen sekitar (sibling/parent)
                kategori_raw = []
                try:
                    container = link.find_element(By.XPATH, '../../../..')
                    cat_links  = container.find_elements(
                        By.CSS_SELECTOR, "a[href*='/listing-category/']"
                    )
                    kategori_raw = [c.text.strip() for c in cat_links if c.text.strip()]
                except Exception:
                    pass

                # Ambil deskripsi singkat dari container terdekat
                excerpt = ''
                try:
                    container = link.find_element(By.XPATH, '../../../..')
                    paragraphs = container.find_elements(By.TAG_NAME, 'p')
                    excerpt = ' '.join(p.text.strip() for p in paragraphs if p.text.strip())[:400]
                except Exception:
                    pass

                if nama:
                    entry = _build_base_entry(nama, href, kategori_raw, excerpt)
                    results.append(entry)

        if progress_callback:
            progress_callback(f"Ditemukan {len(results)} beasiswa dari {url}")

    except Exception as e:
        logging.error(f"Error scraping listing {url}: {e}")
        if progress_callback:
            progress_callback(f"Error listing: {str(e)[:100]}")

    return results


def _build_base_entry(nama, url, kategori_raw, excerpt=''):
    """
    Bangun dict dasar satu entri beasiswa dari halaman listing.
    Field detail (IPK, deadline, dll.) akan diisi saat scrape_detail_page().
    """
    combined = nama + ' ' + ' '.join(kategori_raw) + ' ' + excerpt

    return {
        'nama_beasiswa':    nama,
        'url_sumber':       url,
        'kategori_raw':     kategori_raw,
        'excerpt':          excerpt,
        'jenjang':          extract_jenjang(combined),
        'lokasi':           extract_lokasi(combined),
        # Field yang diisi dari detail page
        'penyelenggara':    '',
        'deadline_text':    '',
        'cakupan_beasiswa': '',
        'syarat_utama':     '',
        'ipk_minimal':      None,
        'jurusan':          [],
        'url_resmi':        '',   # link resmi pendaftaran dari halaman detail
        'full_text':        excerpt,
    }


# ─── SCRAPE HALAMAN DETAIL LISTING ───────────────────────────────────────────

def scrape_detail_page(driver, url, progress_callback=None):
    """
    Scrape halaman detail satu beasiswa dari cari.scholarship.or.id.

    Struktur halaman detail:
      - Judul: <h1> atau <h2>
      - Kategori: link ke /listing-category/
      - Deskripsi panjang: beberapa paragraf <p>
      - Link resmi: biasanya berupa URL pendaftaran/info di dalam konten

    Returns:
        dict atau None jika gagal
    """
    try:
        driver.get(url)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR,
                     ".wpbdp-listing-description, .listing-description, "
                     ".entry-content, .post-content, article")
                )
            )
        except TimeoutException:
            pass

        time.sleep(2)

        detail = {
            'full_text':        '',
            'penyelenggara':    '',
            'cakupan_beasiswa': '',
            'deadline_text':    '',
            'syarat_utama':     '',
            'ipk_minimal':      None,
            'jurusan':          [],
            'url_resmi':        '',
        }

        # ── Ambil konten utama deskripsi ────────────────────────────────
        content_selectors = [
            ".wpbdp-listing-description",
            ".listing-description",
            ".wpbdp-field-value",
            ".entry-content",
            ".post-content",
            "article .content",
            "article",
        ]
        full_text = ''
        for selector in content_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    full_text = '\n'.join(el.text for el in elements if el.text.strip())
                    if full_text.strip():
                        break
            except Exception:
                continue

        # Fallback: ambil semua paragraf
        if not full_text.strip():
            paragraphs = driver.find_elements(By.TAG_NAME, 'p')
            full_text = '\n'.join(p.text for p in paragraphs if p.text.strip())

        detail['full_text'] = full_text

        if not full_text.strip():
            return None

        # ── Penyelenggara ────────────────────────────────────────────────
        penyelenggara_patterns = [
            r'(?:Penyelenggara|Pemberi Beasiswa|Ditawarkan oleh|oleh)[:\s]+(.*?)(?:\n|Cakupan|Persyaratan|Syarat|Periode|Deadline|$)',
            r'(?:Kementerian|Pemerintah|Yayasan|Lembaga|Universitas|Institute)[^\n]{0,100}',
        ]
        for pattern in penyelenggara_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                detail['penyelenggara'] = match.group(0).strip()[:200] if 'Kementerian' in pattern else match.group(1).strip()[:200]
                break

        # ── Cakupan / Manfaat Beasiswa ───────────────────────────────────
        cakupan_patterns = [
            r'(?:Cakupan Beasiswa|Manfaat Beasiswa|Fasilitas|Keuntungan|Yang Didapat|Beasiswa (ini|yang) (mencakup|meliputi|diberikan))[:\s]*(.*?)(?:Persyaratan|Syarat|Cara Mendaftar|Periode|Deadline|$)',
            r'(?:meliputi|mencakup)[:\s]*(.*?)(?:Persyaratan|Syarat|$)',
        ]
        for pattern in cakupan_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE | re.DOTALL)
            if match:
                groups = match.groups()
                cakupan = groups[-1].strip() if groups else match.group(0).strip()
                detail['cakupan_beasiswa'] = cakupan[:600]
                break

        # ── Periode / Deadline ───────────────────────────────────────────
        deadline_patterns = [
            r'(?:Deadline|Batas Waktu Pendaftaran|Batas Pendaftaran|Ditutup|Pendaftaran ditutup)[:\s]*(.*?)(?:\n|Cara Mendaftar|$)',
            r'(?:Periode [Bb]easiswa|Periode [Pp]endaftaran)[:\s]*(.*?)(?:\n\n|Persyaratan|$)',
            r'(?:Dibuka hingga|Berlaku hingga|Sampai dengan)[:\s]*(.*?)(?:\n|$)',
        ]
        for pattern in deadline_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                detail['deadline_text'] = match.group(1).strip()[:200]
                break

        # ── Syarat / Persyaratan ─────────────────────────────────────────
        syarat_patterns = [
            r'(?:Persyaratan|Syarat Umum|Syarat dan Ketentuan|Kriteria Penerima|Ketentuan Umum)[:\s]*(.*?)(?:Cara Mendaftar|Deadline|Batas Waktu|Kontak|Info Lebih|$)',
        ]
        for pattern in syarat_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE | re.DOTALL)
            if match:
                detail['syarat_utama'] = match.group(1).strip()[:800]
                break

        # ── IPK Minimal ──────────────────────────────────────────────────
        detail['ipk_minimal'] = extract_ipk(full_text)

        # ── Jurusan / Prodi ──────────────────────────────────────────────
        jurusan_patterns = [
            r'(?:semua jurusan|seluruh program studi|terbuka untuk semua)',
            r'(?:jurusan|program studi|prodi|bidang studi)[:\s]*(.*?)(?:\.|,\s*IPK|\n)',
        ]
        for pattern in jurusan_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                if 'semua' in match.group(0).lower() or 'seluruh' in match.group(0).lower():
                    detail['jurusan'] = ['Semua Jurusan']
                else:
                    groups = match.groups()
                    if groups:
                        jurusan_text = groups[0].strip()
                        detail['jurusan'] = [
                            j.strip() for j in re.split(r'[,/;]', jurusan_text) if j.strip()
                        ][:10]
                break

        # ── URL Resmi Pendaftaran ────────────────────────────────────────
        # scholarship.or.id sering menyertakan link eksternal ke sumber resmi
        try:
            external_links = driver.find_elements(By.CSS_SELECTOR, "a[href^='http']")
            skip_domains = [
                'cari.scholarship.or.id', 'scholarship.or.id',
                'facebook.com', 'twitter.com', 'instagram.com',
                'linkedin.com', 'youtube.com', 'whatsapp.com'
            ]
            for link in external_links:
                href = link.get_attribute('href') or ''
                if href and not any(d in href for d in skip_domains):
                    detail['url_resmi'] = href
                    break
        except Exception:
            pass

        return detail

    except Exception as e:
        logging.error(f"Error scraping detail {url}: {e}")
        return None


# ─── FUNGSI UTAMA ORCHESTRATOR ────────────────────────────────────────────────

def jalankan_scraper_scholarshiporid(
    progress_callback=None,
    categories=None,
    scrape_details=True,
    max_entries=100,
    cancelled_check=None
):
    """
    Fungsi utama untuk menjalankan scraping dari scholarship.or.id.

    Alur kerja:
      Tahap 1 → Scrape halaman listing per kategori (internasional, pemerintah, swasta)
                 Tiap halaman di-scroll penuh untuk memuat semua kartu
      Tahap 2 → Scrape detail tiap beasiswa (opsional)
                 Ambil: deskripsi, syarat, deadline, cakupan, IPK, URL resmi
      Tahap 3 → Normalisasi data menggunakan modul normalizer
                 Tambah field 'sumber_website': 'scholarship.or.id'

    Args:
        progress_callback  : callable(str) → laporan progres ke UI/terminal
        categories         : list key dari CATEGORIES dict
                             (default: ['internasional', 'pemerintah', 'swasta'])
        scrape_details     : bool, apakah buka tiap halaman detail
        max_entries        : batas maksimum beasiswa yang diproses ke detail+normalisasi
        cancelled_check    : callable() -> bool, cek apakah dibatalkan user

    Returns:
        list of dict: Data beasiswa yang sudah dinormalisasi
    """
    if categories is None:
        categories = DEFAULT_CATEGORIES

    driver = None
    try:
        if progress_callback:
            progress_callback("Membuka browser untuk scholarship.or.id...")

        driver = create_driver()
        all_raw = []
        seen_urls = set()

        # ── TAHAP 1: Scrape semua kategori ────────────────────────────
        for cat_key in categories:
            if cancelled_check and cancelled_check():
                break

            url = CATEGORIES.get(cat_key)
            if not url:
                logging.warning(f"Kategori tidak dikenal: {cat_key}")
                continue

            if progress_callback:
                progress_callback(f"Tahap 1 - Kategori '{cat_key}': {url}")

            entries = scrape_listings_page(driver, url, progress_callback)

            new_count = 0
            for entry in entries:
                u = entry.get('url_sumber', '')
                if u and u not in seen_urls:
                    seen_urls.add(u)
                    all_raw.append(entry)
                    new_count += 1

            if progress_callback:
                progress_callback(
                    f"Kategori '{cat_key}': +{new_count} baru "
                    f"(total unik: {len(all_raw)})"
                )

        if progress_callback:
            progress_callback(
                f"Tahap 1 selesai: {len(all_raw)} beasiswa unik ditemukan."
            )

        if cancelled_check and cancelled_check():
            return []

        # Juga scrape halaman /listings/ utama untuk tangkap yang mungkin terlewat
        if progress_callback:
            progress_callback("Tahap 1b - Scraping halaman /listings/ utama...")

        main_entries = scrape_listings_page(driver, LISTINGS, progress_callback)
        for entry in main_entries:
            u = entry.get('url_sumber', '')
            if u and u not in seen_urls:
                seen_urls.add(u)
                all_raw.append(entry)

        if progress_callback:
            progress_callback(
                f"Setelah /listings/ utama: total {len(all_raw)} beasiswa unik."
            )

        # ── TAHAP 2: Scrape halaman detail ────────────────────────────
        if scrape_details:
            if progress_callback:
                progress_callback("Tahap 2: Mengambil detail tiap beasiswa...")

            to_process = all_raw[:max_entries]
            total = len(to_process)

            for idx, entry in enumerate(to_process):
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
                    # Merge: prioritas data detail jika lebih lengkap
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
                    if detail.get('url_resmi'):
                        entry['url_resmi'] = detail['url_resmi']
                    if detail.get('full_text'):
                        entry['full_text'] = detail['full_text']
                        # Perbarui jenjang & lokasi dari teks lebih lengkap
                        if not entry.get('jenjang'):
                            entry['jenjang'] = extract_jenjang(detail['full_text'])
                        if not entry.get('lokasi'):
                            entry['lokasi'] = extract_lokasi(detail['full_text'])

                time.sleep(1.5)  # Jeda sopan agar tidak membebani server

        # ── TAHAP 3: Normalisasi data ──────────────────────────────────
        if progress_callback:
            progress_callback("Tahap 3: Normalisasi data scholarship.or.id...")

        normalized = []
        for entry in all_raw[:max_entries]:
            if not entry.get('full_text') and entry.get('excerpt'):
                entry['full_text'] = entry['excerpt']

            norm = normalize_beasiswa(entry)
            norm['sumber_website'] = 'scholarship.or.id'
            # Simpan URL resmi pendaftaran jika ada
            if entry.get('url_resmi'):
                norm['url_resmi'] = entry['url_resmi']

            normalized.append(norm)

        if progress_callback:
            progress_callback(
                f"Scraping scholarship.or.id selesai! "
                f"Total: {len(normalized)} beasiswa dinormalisasi."
            )

        return normalized

    except Exception as e:
        logging.error(f"Error utama scraper scholarship.or.id: {e}")
        if progress_callback:
            progress_callback(f"Error: {str(e)}")
        return []

    finally:
        if driver:
            driver.quit()


# ─── RUN LANGSUNG (Testing) ───────────────────────────────────────────────────

if __name__ == '__main__':
    def print_progress(msg):
        print(f"[PROGRESS] {msg}")

    hasil = jalankan_scraper_scholarshiporid(
        progress_callback=print_progress,
        categories=['internasional', 'pemerintah', 'swasta'],
        scrape_details=False,    # Set True untuk data lengkap
        max_entries=10
    )

    print(f"\n=== HASIL: {len(hasil)} beasiswa ===")
    for b in hasil[:5]:
        print(f"\n  Nama         : {b.get('nama_beasiswa', '')[:80]}")
        print(f"  Penyelenggara: {b.get('penyelenggara', '-')}")
        print(f"  Jenjang      : {b.get('jenjang', [])}")
        print(f"  Deadline     : {b.get('deadline', '-')}")
        print(f"  Lokasi       : {b.get('lokasi', '-')}")
        print(f"  Kategori     : {b.get('kategori_raw', [])}")
        print(f"  URL Resmi    : {b.get('url_resmi', '-')}")
        print(f"  Sumber       : {b.get('sumber_website', '-')}")
