"""
run_all_scraping.py (dijalankan dari folder 'Logika Scraping')
Script runner utama — kedua scraper dijalankan berurutan lalu disimpan ke DB dengan safe update workflow.

Safe Update Workflow:
1. Backup admin database
2. Scrape semua sumber data
3. Deteksi & prevent duplikat
4. Backup user bookmarks
5. Update database dengan safe transaction
6. Restore user bookmarks
7. Catat audit log lengkap
8. Generate & verify sync packages
9. Create manifest untuk distribusi ke user apps

Feature:
- Bookmark preservation saat update
- Deduplication dengan content hash & URL matching
- Full audit trail untuk compliance
- Automatic sync package generation
- Database backup untuk disaster recovery
"""

import sys
import os
import time

# Tambahkan folder ini ke path agar import bekerja
sys.path.insert(0, os.path.dirname(__file__))

from scrapping_indBeasiswa    import jalankan_scraper_beasiswa
from scrapping_beasiswaid     import jalankan_scraper_beasiswaid
from database_beasiswa        import (
    safe_update_beasiswa_batch,
    hitung_beasiswa,
    ambil_log_scraping,
    ambil_audit_log_scraping,
    get_scraping_stats
)
from scraping_sync import setup_sync_manager

# ── Konfigurasi ───────────────────────────────────────────────────────────────
CONFIG = {
    'indbeasiswa': {
        'aktif'         : True,
        'scrape_details': False,
        'max_entries'   : 150,
    },
    'beasiswaid': {
        'aktif'                 : True,
        'categories'            : ['beasiswa_s1', 'beasiswa_s2', 'beasiswa_s3'],
        'scrape_details'        : False,
        'max_pages_per_category': 10,
        'max_entries'           : 150,
    },
}

# Admin configuration
ADMIN_USER = os.environ.get('BEAPLY_ADMIN_USER', 'admin')
ADMIN_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'beaply.db'
)

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def jalankan_semua(auto_sync: bool = True):
    """
    Jalankan seluruh proses scraping dengan safe update workflow.

    Args:
        auto_sync: jika True, automatic generate sync packages setelah scraping
    """
    log("=" * 70)
    log("  🔄 MEMULAI PROSES SCRAPING BEASISWA DENGAN SAFE UPDATE WORKFLOW")
    log("=" * 70)

    hasil_per_sumber = {}
    all_hasil = []

    # ── STEP 0: Backup Database ────────────────────────────────────────
    log("\n[PREP] Backup database admin...")
    sync_manager = setup_sync_manager(ADMIN_DB_PATH)
    ok, backup_path = sync_manager.backup_admin_database(log)
    if not ok:
        log(f"⚠️  Warning: backup gagal - {backup_path}")
    else:
        log(f"✓ Backup berhasil: {backup_path}")

    # ── STEP 1: indbeasiswa.com ────────────────────────────────────────
    if CONFIG['indbeasiswa']['aktif']:
        log("\n[1/2] Scraping indbeasiswa.com...")
        cfg = CONFIG['indbeasiswa']
        start = time.time()
        try:
            hasil = jalankan_scraper_beasiswa(
                progress_callback=log,
                scrape_details=cfg['scrape_details'],
                max_entries=cfg['max_entries'],
            )
            durasi = time.time() - start
            log(f"  ✓ Selesai: {len(hasil)} beasiswa ({durasi:.1f}s)")
            all_hasil.extend(hasil)
            hasil_per_sumber['indbeasiswa.com'] = dict(total=len(hasil), durasi=f"{durasi:.1f}s")
        except Exception as e:
            log(f"  ❌ ERROR: {e}")
            hasil_per_sumber['indbeasiswa.com'] = dict(error=str(e), total=0)

    # ── STEP 2: beasiswa.id ────────────────────────────────────────────
    if CONFIG['beasiswaid']['aktif']:
        log("\n[2/2] Scraping beasiswa.id...")
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
            log(f"  ✓ Selesai: {len(hasil)} beasiswa ({durasi:.1f}s)")
            all_hasil.extend(hasil)
            hasil_per_sumber['beasiswa.id'] = dict(total=len(hasil), durasi=f"{durasi:.1f}s")
        except Exception as e:
            log(f"  ❌ ERROR: {e}")
            hasil_per_sumber['beasiswa.id'] = dict(error=str(e), total=0)

    # ── STEP 3: Safe Update Database dengan Bookmark Preservation ──────
    log("\n" + "=" * 70)
    log("  🔒 SAFE UPDATE DATABASE DENGAN BOOKMARK PRESERVATION")
    log("=" * 70)

    total_baru = 0
    total_update = 0
    total_gagal = 0
    dedup_stats_all = {}

    if all_hasil:
        # Update per sumber untuk better tracking
        for sumber, info in hasil_per_sumber.items():
            if info.get('error'):
                continue

            # Filter hasil untuk sumber ini
            hasil_sumber = [h for h in all_hasil if h.get('sumber_website') == sumber]
            if not hasil_sumber:
                continue

            log(f"\n  Processing {sumber}...")
            b, u, g, dedup = safe_update_beasiswa_batch(
                entries=hasil_sumber,
                sumber_website=sumber,
                admin_user=ADMIN_USER,
                progress_callback=log
            )

            total_baru += b
            total_update += u
            total_gagal += g
            dedup_stats_all[sumber] = dedup

            hasil_per_sumber[sumber]['baru'] = b
            hasil_per_sumber[sumber]['update'] = u
            hasil_per_sumber[sumber]['gagal'] = g
    else:
        log("⚠️  Tidak ada data untuk di-update")

    # ── STEP 5: Ringkasan & Stats ──────────────────────────────────────
    log("\n" + "=" * 70)
    log("  📊 RINGKASAN HASIL SCRAPING & UPDATE")
    log("=" * 70)

    for sumber, info in hasil_per_sumber.items():
        if 'error' in info:
            log(f"  ❌ [{sumber}]: ERROR — {info['error'][:80]}")
        else:
            log(f"  ✓ [{sumber}]")
            log(f"     Scraped: {info['total']} | Baru: {info.get('baru', 0)} | Update: {info.get('update', 0)} | Gagal: {info.get('gagal', 0)} | Durasi: {info['durasi']}")
            if sumber in dedup_stats_all:
                dedup = dedup_stats_all[sumber]
                log(f"     Dedup: URL-match={dedup.get('url_match', 0)}, Hash-match={dedup.get('hash_match', 0)}, New={dedup.get('new_entry', 0)}")

    log(f"\n  📈 TOTAL DATABASE UPDATE:")
    log(f"     Baru: {total_baru} | Update: {total_update} | Gagal: {total_gagal}")
    log(f"     Total beasiswa di database: {hitung_beasiswa()}")

    # Show audit logs
    logs = ambil_log_scraping(limit=3)
    if logs:
        log("\n  📋 LOG SESI SCRAPING TERAKHIR:")
        for l in logs:
            log(f"     [{l['dibuat_pada']}] {l['sumber_website']} baru={l['jumlah_baru']} update={l['jumlah_update']} gagal={l['jumlah_gagal']}")

    # Show audit events
    audit_logs = ambil_audit_log_scraping(limit=10)
    if audit_logs:
        log("\n  🔐 AUDIT EVENTS TERBARU:")
        for a in audit_logs:
            log(f"     [{a['dibuat_pada']}] {a['event_type']}: {a['status']} - {a['deskripsi'][:60]}")

    # ── STEP 6: Generate Sync Packages ─────────────────────────────────
    if auto_sync:
        log("\n" + "=" * 70)
        log("  📦 GENERATE SYNC PACKAGES UNTUK DISTRIBUSI KE USER APPS")
        log("=" * 70)

        # Backup database sebelum sync
        log("\n  💾 Backup database sebelum sync...")
        ok, msg = sync_manager.backup_admin_database(log)

        # Generate sync package untuk masing-masing sumber
        for sumber in ['indbeasiswa.com', 'beasiswa.id']:
            if sumber not in hasil_per_sumber or 'error' in hasil_per_sumber[sumber]:
                continue

            log(f"\n  📦 Generate package untuk {sumber}...")
            ok, package_path = sync_manager.generate_sync_package(
                sumber_website=sumber,
                progress_callback=log
            )

            if ok:
                # Verify integrity
                log(f"\n  🔍 Verify package integrity...")
                ok_verify, msg_verify = sync_manager.verify_sync_package_integrity(
                    package_path,
                    log
                )

                if ok_verify:
                    # Create manifest
                    log(f"\n  📋 Create sync manifest...")
                    ok_manifest, manifest_path = sync_manager.create_sync_manifest(
                        package_path,
                        sync_destinations=[],  # Will be populated when syncing to user apps
                        progress_callback=log
                    )

                    if ok_manifest:
                        log(f"  ✓ Manifest created: {manifest_path}")
            else:
                log(f"  ⚠️  Failed to generate package: {package_path}")

        # Show sync statistics
        log("\n  📊 SYNC STATISTICS:")
        stats = sync_manager.get_sync_statistics(log)
        log(f"     Total packages: {stats.get('total_packages', 0)}")
        log(f"     Total synced: {stats.get('total_synced', 0)}")
        log(f"     Total failed: {stats.get('total_failed', 0)}")

    # ── Final Summary ──────────────────────────────────────────────────
    log("\n" + "=" * 70)
    log("  ✅ SCRAPING PROCESS SELESAI!")
    log("=" * 70)
    log(f"  Admin User: {ADMIN_USER}")
    log(f"  Database: {ADMIN_DB_PATH}")
    log(f"  Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    log("=" * 70 + "\n")

if __name__ == '__main__':
    jalankan_semua(auto_sync=True)
