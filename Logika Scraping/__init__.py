# Logika Scraping Package
# Ekspor fungsi utama dari scraper dan modul database

# ── Scraper ───────────────────────────────────────────────────────────────────
from .scrapping import jalankan_scraper_beasiswa                            # indbeasiswa.com
from .scrapping_beasiswaid import jalankan_scraper_beasiswaid               # beasiswa.id
from .scrapping_scholarshiporid import jalankan_scraper_scholarshiporid     # scholarship.or.id

# ── Database ──────────────────────────────────────────────────────────────────
from .database_beasiswa import (
    init_beasiswa_db,           # inisialisasi tabel (auto dipanggil saat import)
    simpan_hasil_scraping,      # ← fungsi utama: simpan list hasil scraper ke DB + log
    simpan_beasiswa_batch,      # simpan banyak sekaligus
    simpan_satu_beasiswa,       # simpan satu entry
    ambil_semua_beasiswa,       # query dengan filter
    ambil_beasiswa_by_id,       # ambil by ID
    ambil_beasiswa_json,        # ambil data_json lengkap
    hitung_beasiswa,            # COUNT beasiswa
    hapus_beasiswa,             # hapus by ID
    hapus_semua_by_sumber,      # hapus semua dari satu website
    catat_log_scraping,         # catat sesi scraping ke log
    ambil_log_scraping,         # ambil riwayat log
    export_beasiswa_ke_json,    # export ke file JSON
)

__all__ = [
    # Scraper
    'jalankan_scraper_beasiswa',
    'jalankan_scraper_beasiswaid',
    'jalankan_scraper_scholarshiporid',
    # Database
    'init_beasiswa_db',
    'simpan_hasil_scraping',
    'simpan_beasiswa_batch',
    'simpan_satu_beasiswa',
    'ambil_semua_beasiswa',
    'ambil_beasiswa_by_id',
    'ambil_beasiswa_json',
    'hitung_beasiswa',
    'hapus_beasiswa',
    'hapus_semua_by_sumber',
    'catat_log_scraping',
    'ambil_log_scraping',
    'export_beasiswa_ke_json',
]

