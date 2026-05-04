"""
run_all_scraping.py (dijalankan dari folder 'Logika Scraping')
Script runner utama — ketiga scraper dijalankan berurutan lalu disimpan ke DB.
"""

import sys
import os
import time

# Tambahkan folder ini ke path agar import bekerja
sys.path.insert(0, os.path.dirname(__file__))

from scrapping_indBeasiswa    import jalankan_scraper_beasiswa
from scrapping_beasiswaid     import jalankan_scraper_beasiswaid
from scrapping_scholarshiporid import jalankan_scraper_scholarshiporid
from database_beasiswa        import simpan_hasil_scraping, hitung_beasiswa, ambil_log_scraping

# ── Konfigurasi ───────────────────────────────────────────────────────────────
CONFIG = {
    'indbeasiswa': {
        'aktif'         : True,
        'scrape_details': True,
        'max_entries'   : 50,
    },
    'beasiswaid': {
        'aktif'                 : True,
        'categories'            : ['beasiswa_s1', 'beasiswa_s2', 'beasiswa_d3'],
        'scrape_details'        : True,
        'max_pages_per_category': 2,
        'max_entries'           : 50,
    },
    'scholarshiporid': {
        'aktif'         : True,
        'categories'    : ['internasional', 'pemerintah', 'swasta'],
        'scrape_details': True,
        'max_entries'   : 50,
    },
}

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def jalankan_semua():
    log("=" * 60)
    log("  MEMULAI SELURUH PROSES SCRAPING BEASISWA")
    log("=" * 60)

    total_baru = total_update = total_gagal = 0
    hasil_per_sumber = {}

    # ── 1. indbeasiswa.com ──────────────────────────────────────────
    if CONFIG['indbeasiswa']['aktif']:
        log("\n[1/3] Scraping indbeasiswa.com...")
        cfg = CONFIG['indbeasiswa']
        start = time.time()
        try:
            hasil = jalankan_scraper_beasiswa(
                progress_callback=log,
                scrape_details=cfg['scrape_details'],
                max_entries=cfg['max_entries'],
            )
            durasi = time.time() - start
            log(f"  Selesai: {len(hasil)} beasiswa ({durasi:.1f}s)")
            b, u, g = simpan_hasil_scraping(hasil, 'indbeasiswa.com', durasi, log)
            total_baru += b; total_update += u; total_gagal += g
            hasil_per_sumber['indbeasiswa.com'] = dict(total=len(hasil), baru=b, update=u, gagal=g, durasi=f"{durasi:.1f}s")
        except Exception as e:
            log(f"  ERROR: {e}")
            hasil_per_sumber['indbeasiswa.com'] = dict(error=str(e))

    # ── 2. beasiswa.id ──────────────────────────────────────────────
    if CONFIG['beasiswaid']['aktif']:
        log("\n[2/3] Scraping beasiswa.id...")
        cfg = CONFIG['beasiswaid']
        start = time.time()
        try:
            hasil = jalankan_scraper_beasiswaid(
                progress_callback=log,
                categories=cfg['categories'],
                scrape_details=cfg['scrape_details'],
                max_pages_per_category=cfg['max_pages_per_category'],
                max_entries=cfg['max_entries'],
            )
            durasi = time.time() - start
            log(f"  Selesai: {len(hasil)} beasiswa ({durasi:.1f}s)")
            b, u, g = simpan_hasil_scraping(hasil, 'beasiswa.id', durasi, log)
            total_baru += b; total_update += u; total_gagal += g
            hasil_per_sumber['beasiswa.id'] = dict(total=len(hasil), baru=b, update=u, gagal=g, durasi=f"{durasi:.1f}s")
        except Exception as e:
            log(f"  ERROR: {e}")
            hasil_per_sumber['beasiswa.id'] = dict(error=str(e))

    # ── 3. scholarship.or.id ────────────────────────────────────────
    if CONFIG['scholarshiporid']['aktif']:
        log("\n[3/3] Scraping scholarship.or.id...")
        cfg = CONFIG['scholarshiporid']
        start = time.time()
        try:
            hasil = jalankan_scraper_scholarshiporid(
                progress_callback=log,
                categories=cfg['categories'],
                scrape_details=cfg['scrape_details'],
                max_entries=cfg['max_entries'],
            )
            durasi = time.time() - start
            log(f"  Selesai: {len(hasil)} beasiswa ({durasi:.1f}s)")
            b, u, g = simpan_hasil_scraping(hasil, 'scholarship.or.id', durasi, log)
            total_baru += b; total_update += u; total_gagal += g
            hasil_per_sumber['scholarship.or.id'] = dict(total=len(hasil), baru=b, update=u, gagal=g, durasi=f"{durasi:.1f}s")
        except Exception as e:
            log(f"  ERROR: {e}")
            hasil_per_sumber['scholarship.or.id'] = dict(error=str(e))

    # ── Ringkasan ────────────────────────────────────────────────────
    log("\n" + "=" * 60)
    log("  RINGKASAN HASIL")
    log("=" * 60)
    for sumber, info in hasil_per_sumber.items():
        if 'error' in info:
            log(f"  [ERR] {sumber}: ERROR — {info['error'][:80]}")
        else:
            log(f"  [OK] {sumber}: scraped={info['total']} | baru={info['baru']} update={info['update']} gagal={info['gagal']} ({info['durasi']})")

    log(f"\n  TOTAL DB — Baru: {total_baru} | Update: {total_update} | Gagal: {total_gagal}")
    log(f"  Total beasiswa di database: {hitung_beasiswa()}")

    logs = ambil_log_scraping(limit=3)
    if logs:
        log("\n  LOG SESI TERAKHIR:")
        for l in logs:
            log(f"    [{l['dibuat_pada']}] {l['sumber_website']} baru={l['jumlah_baru']} update={l['jumlah_update']}")

    log("\n  SELESAI")
    log("=" * 60)

if __name__ == '__main__':
    jalankan_semua()
