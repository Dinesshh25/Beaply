"""
Beasiswa Scraper - Scraper khusus untuk indbeasiswa.com
Mengambil data beasiswa dari halaman listing dan detail.
"""

import re
import time
import logging
from urllib.parse import urlparse
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from normalizer import (
    parse_tanggal_indonesia, extract_deadlines, extract_ipk,
    extract_jenjang, extract_lokasi, normalize_beasiswa
)

logging.basicConfig(filename='scraper.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# URL sumber utama
SOURCES = {
    'indbeasiswa_listing': 'https://indbeasiswa.com/daftar-beasiswa-2026-beasiswa-2027/',
    'indbeasiswa_s1': 'https://indbeasiswa.com/beasiswa-s1/',
    'indbeasiswa_s2': 'https://indbeasiswa.com/beasiswa-s2/',
}


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


def scrape_listing_page(driver, url, progress_callback=None):
    """
    Scrape halaman listing utama daftar beasiswa 2026-2027.
    Return: list of dict dengan field dasar dari listing.
    """
    if progress_callback:
        progress_callback("Mengakses halaman listing beasiswa...")

    driver.get(url)
    time.sleep(3)

    beasiswa_list = []

    try:
        # Ambil seluruh konten artikel
        content_area = driver.find_element(By.CSS_SELECTOR, "article, .entry-content, .post-content, .td-post-content")
        paragraphs = content_area.find_elements(By.TAG_NAME, "p")

        if progress_callback:
            progress_callback(f"Menemukan {len(paragraphs)} paragraf, mulai parsing...")

        current_entry = None

        for p in paragraphs:
            text = p.text.strip()
            if not text or len(text) < 20:
                continue

            # Setiap entri beasiswa dimulai dengan nama beasiswa
            # Pattern: teks berisi "Beasiswa" atau "Program" diikuti info
            if ('easiswa' in text or 'rogram' in text or 'FULL' in text or
                'GRATIS' in text.upper() or 'Kuliah' in text) and \
               ('Deadline' in text or 'deadline' in text or
                'Info' in text or 'Pendaftaran' in text or
                'Bentuk Beasiswa' in text or 'Cakupan' in text or
                'Penyelenggara' in text):

                # Parse entry
                entry = _parse_listing_entry(text, p, driver)
                if entry and entry.get('nama_beasiswa'):
                    beasiswa_list.append(entry)

                    if progress_callback:
                        progress_callback(
                            f"Ditemukan: {entry['nama_beasiswa'][:60]}..."
                        )

    except Exception as e:
        logging.error(f"Error scraping listing: {e}")
        if progress_callback:
            progress_callback(f"Error pada listing: {str(e)[:100]}")

    if progress_callback:
        progress_callback(f"Total {len(beasiswa_list)} beasiswa ditemukan dari listing.")

    return beasiswa_list


def _parse_listing_entry(text, element, driver):
    """
    Parse satu entri beasiswa dari teks paragraf di halaman listing.
    """
    entry = {
        'nama_beasiswa': '',
        'penyelenggara': '',
        'jenjang': [],
        'jurusan': [],
        'ipk_minimal': None,
        'lokasi': '',
        'deadline_text': '',
        'cakupan_beasiswa': '',
        'syarat_utama': '',
        'url_sumber': '',
        'full_text': text,
    }

    lines = text.split('\n')
    full_text = text

    # Extract nama beasiswa (biasanya di awal, sebelum keyword Penyelenggara/Bentuk/Cakupan/Deadline)
    nama_match = re.match(
        r'^(.*?)(?:Penyelenggara|Bentuk Beasiswa|Cakupan|Deadline|Batas Waktu|Jadwal|Info)',
        full_text, re.IGNORECASE | re.DOTALL
    )
    if nama_match:
        entry['nama_beasiswa'] = nama_match.group(1).strip()
    else:
        # Ambil kalimat pertama sebagai nama
        first_line = lines[0] if lines else text[:200]
        entry['nama_beasiswa'] = first_line.strip()

    # Clean up nama
    entry['nama_beasiswa'] = re.sub(r'\s+', ' ', entry['nama_beasiswa']).strip()
    if len(entry['nama_beasiswa']) > 200:
        entry['nama_beasiswa'] = entry['nama_beasiswa'][:200]

    # Extract penyelenggara
    penyelenggara_match = re.search(
        r'Penyelenggara:\s*(.*?)(?:Bentuk|Cakupan|Deadline|Batas|Info|Jadwal|$)',
        full_text, re.IGNORECASE | re.DOTALL
    )
    if penyelenggara_match:
        entry['penyelenggara'] = penyelenggara_match.group(1).strip()

    # Extract cakupan/bentuk beasiswa
    cakupan_match = re.search(
        r'(?:Bentuk Beasiswa|Cakupan Beasiswa|Cakupan|Bentuk Bantuan|Keuntungan):\s*(.*?)(?:Deadline|Batas|Info|Jadwal|Pendaftaran|$)',
        full_text, re.IGNORECASE | re.DOTALL
    )
    if cakupan_match:
        entry['cakupan_beasiswa'] = cakupan_match.group(1).strip()

    # Extract deadline
    deadline_match = re.search(
        r'(?:Deadline|Batas Waktu Pendaftaran|Deaadline):\s*(.*?)(?:Info|$)',
        full_text, re.IGNORECASE | re.DOTALL
    )
    if deadline_match:
        entry['deadline_text'] = deadline_match.group(1).strip()
    else:
        # Try jadwal pendaftaran
        jadwal_match = re.search(
            r'(?:Jadwal Pendaftaran|Pendaftaran)[:\s]*(.*?)(?:Info|$)',
            full_text, re.IGNORECASE | re.DOTALL
        )
        if jadwal_match:
            entry['deadline_text'] = jadwal_match.group(1).strip()

    # Extract URL sumber
    try:
        links = element.find_elements(By.TAG_NAME, 'a')
        for link in links:
            href = link.get_attribute('href')
            if href and 'indbeasiswa.com' in href:
                entry['url_sumber'] = href
                break
    except Exception:
        pass

    # Use normalizer to extract structured fields
    entry['jenjang'] = extract_jenjang(full_text)
    entry['lokasi'] = extract_lokasi(entry['nama_beasiswa'] + ' ' + entry.get('penyelenggara', '') + ' ' + full_text)
    entry['ipk_minimal'] = extract_ipk(full_text)

    return entry


def scrape_detail_page(driver, url, progress_callback=None):
    """
    Scrape halaman detail beasiswa untuk informasi tambahan.
    """
    try:
        driver.get(url)
        time.sleep(2)

        detail = {
            'full_text': '',
            'ipk_minimal': None,
            'jurusan': [],
            'syarat_utama': '',
        }

        # Ambil konten utama
        try:
            content = driver.find_element(
                By.CSS_SELECTOR,
                "article, .entry-content, .post-content, .td-post-content"
            )
            detail['full_text'] = content.text
        except Exception:
            paragraphs = driver.find_elements(By.TAG_NAME, 'p')
            detail['full_text'] = '\n'.join(p.text for p in paragraphs)

        full_text = detail['full_text']

        # Extract IPK
        detail['ipk_minimal'] = extract_ipk(full_text)

        # Extract jurusan dari teks
        jurusan_patterns = [
            r'(?:jurusan|program studi|prodi|fakultas|bidang studi)[:\s]*(.*?)(?:\.|,\s*IPK|\n)',
            r'(?:untuk jurusan|terbuka untuk)[:\s]*(.*?)(?:\.|$)',
        ]
        for pattern in jurusan_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                jurusan_text = match.group(1).strip()
                jurusan_list = [j.strip() for j in re.split(r'[,/;]', jurusan_text) if j.strip()]
                detail['jurusan'] = jurusan_list[:10]  # Max 10 jurusan
                break

        # Extract syarat
        syarat_patterns = [
            r'(?:Syarat|Persyaratan|Ketentuan|Kriteria)[:\s]*(.*?)(?:Cara Mendaftar|Info|Pendaftaran|Deadline|$)',
        ]
        for pattern in syarat_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE | re.DOTALL)
            if match:
                syarat = match.group(1).strip()
                detail['syarat_utama'] = syarat[:500]
                break

        return detail

    except Exception as e:
        logging.error(f"Error scraping detail {url}: {e}")
        return None


def jalankan_scraper_beasiswa(progress_callback=None, scrape_details=True,
                               max_entries=100, cancelled_check=None):
    """
    Fungsi utama untuk menjalankan scraping beasiswa.

    Args:
        progress_callback: callable(str) untuk mengirim pesan progress
        scrape_details: bool, apakah scrape halaman detail
        max_entries: int, maks jumlah beasiswa yang diambil
        cancelled_check: callable() -> bool, cek apakah dibatalkan

    Returns:
        list of dict: Data beasiswa yang sudah dinormalisasi
    """
    driver = None
    try:
        if progress_callback:
            progress_callback("Membuka browser...")

        driver = create_driver()
        all_entries = []

        # Tahap 1: Scrape halaman listing utama
        if progress_callback:
            progress_callback("Tahap 1: Scraping halaman listing...")

        listing_data = scrape_listing_page(
            driver,
            SOURCES['indbeasiswa_listing'],
            progress_callback
        )
        all_entries.extend(listing_data)

        if cancelled_check and cancelled_check():
            return []

        if progress_callback:
            progress_callback(f"Tahap 1 selesai: {len(all_entries)} beasiswa ditemukan.")

        # Filter hanya S1 dan S2
        filtered = []
        for entry in all_entries:
            jenjang = entry.get('jenjang', [])
            if any(j in ['S1', 'S2', 'D3', 'D4'] for j in jenjang) or not jenjang:
                filtered.append(entry)

        if progress_callback:
            progress_callback(f"Setelah filter S1/S2: {len(filtered)} beasiswa.")

        # Tahap 2: Scrape detail (opsional)
        if scrape_details:
            if progress_callback:
                progress_callback("Tahap 2: Mengambil detail per beasiswa...")

            entries_to_detail = filtered[:max_entries]
            for idx, entry in enumerate(entries_to_detail):
                if cancelled_check and cancelled_check():
                    break

                url = entry.get('url_sumber', '')
                if not url:
                    continue

                if progress_callback:
                    progress_callback(
                        f"Detail {idx + 1}/{len(entries_to_detail)}: "
                        f"{entry.get('nama_beasiswa', '')[:50]}..."
                    )

                detail = scrape_detail_page(driver, url)
                if detail:
                    # Merge detail ke entry
                    if detail.get('ipk_minimal') and not entry.get('ipk_minimal'):
                        entry['ipk_minimal'] = detail['ipk_minimal']
                    if detail.get('jurusan') and entry.get('jurusan', []) == []:
                        entry['jurusan'] = detail['jurusan']
                    if detail.get('syarat_utama') and not entry.get('syarat_utama'):
                        entry['syarat_utama'] = detail['syarat_utama']
                    if detail.get('full_text'):
                        entry['full_text'] = detail['full_text']

                time.sleep(1)  # Respect rate limit

        # Tahap 3: Normalize semua data
        if progress_callback:
            progress_callback("Tahap 3: Normalisasi data...")

        normalized = []
        for entry in filtered[:max_entries]:
            norm = normalize_beasiswa(entry)
            normalized.append(norm)

        if progress_callback:
            progress_callback(f"Scraping selesai! Total: {len(normalized)} beasiswa.")

        return normalized

    except Exception as e:
        logging.error(f"Error utama scraper: {e}")
        if progress_callback:
            progress_callback(f"Error: {str(e)}")
        return []

    finally:
        if driver:
            driver.quit()


if __name__ == '__main__':
    def print_progress(msg):
        print(f"[PROGRESS] {msg}")

    hasil = jalankan_scraper_beasiswa(
        progress_callback=print_progress,
        scrape_details=False,
        max_entries=5
    )

    print(f"\n=== HASIL: {len(hasil)} beasiswa ===")
    for b in hasil[:5]:
        print(f"\n  Nama: {b['nama_beasiswa'][:80]}")
        print(f"  Penyelenggara: {b['penyelenggara']}")
        print(f"  Jenjang: {b['jenjang']}")
        print(f"  Deadline: {b['deadline']}")
        print(f"  Lokasi: {b['lokasi']}")
        print(f"  Tipe: {b['tipe_beasiswa']}")