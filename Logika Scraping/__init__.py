# Logika Scraping Package (v2.0 - Safe Update Workflow)
# Ekspor fungsi utama dari scraper, database, dan sync module

# ── Scraper ───────────────────────────────────────────────────────────────────
from .scrapping_indBeasiswa import jalankan_scraper_beasiswa                 # indbeasiswa.com
from .scrapping_beasiswaid import jalankan_scraper_beasiswaid               # beasiswa.id
from .scrapping_scholarshiporid import jalankan_scraper_scholarshiporid     # scholarship.or.id

# ── Database (Enhanced dengan Safe Update Workflow) ──────────────────────────
from .database_beasiswa import (
    # Initialization
    init_beasiswa_db,
    
    # Legacy functions (still available, but recommend using safe_update_beasiswa_batch)
    simpan_hasil_scraping,
    simpan_beasiswa_batch,
    simpan_satu_beasiswa,
    
    # NEW: Safe update dengan bookmark preservation & dedup detection
    safe_update_beasiswa_batch,
    
    # Bookmark management (NEW)
    backup_user_bookmarks,
    restore_user_bookmarks,
    
    # Audit & logging (NEW)
    record_audit_log,
    record_dedup_log,
    ambil_audit_log_scraping,
    ambil_dedup_log_scraping,
    get_scraping_stats,
    
    # Query functions
    ambil_semua_beasiswa,
    ambil_beasiswa_by_id,
    ambil_beasiswa_json,
    hitung_beasiswa,
    
    # Delete functions
    hapus_beasiswa,
    hapus_semua_by_sumber,
    
    # Logging
    catat_log_scraping,
    ambil_log_scraping,
    
    # Export
    export_beasiswa_ke_json,
)

# ── Sync Module (NEW) ─────────────────────────────────────────────────────────
from .scraping_sync import (
    ScrapingSyncManager,
    setup_sync_manager,
)

# ── Runner (NEW) ──────────────────────────────────────────────────────────────
from .run_all_scraping import jalankan_semua

__all__ = [
    # Scraper
    'jalankan_scraper_beasiswa',
    'jalankan_scraper_beasiswaid',
    'jalankan_scraper_scholarshiporid',
    
    # Database - Initialization
    'init_beasiswa_db',
    
    # Database - Save (Legacy)
    'simpan_hasil_scraping',
    'simpan_beasiswa_batch',
    'simpan_satu_beasiswa',
    
    # Database - Save (NEW - Safe Update)
    'safe_update_beasiswa_batch',
    
    # Database - Bookmark Management (NEW)
    'backup_user_bookmarks',
    'restore_user_bookmarks',
    
    # Database - Audit & Logging (NEW)
    'record_audit_log',
    'record_dedup_log',
    'ambil_audit_log_scraping',
    'ambil_dedup_log_scraping',
    'get_scraping_stats',
    
    # Database - Query
    'ambil_semua_beasiswa',
    'ambil_beasiswa_by_id',
    'ambil_beasiswa_json',
    'hitung_beasiswa',
    
    # Database - Delete
    'hapus_beasiswa',
    'hapus_semua_by_sumber',
    
    # Database - Logging & Export
    'catat_log_scraping',
    'ambil_log_scraping',
    'export_beasiswa_ke_json',
    
    # Sync Module (NEW)
    'ScrapingSyncManager',
    'setup_sync_manager',
    
    # Runner (NEW)
    'jalankan_semua',
]
