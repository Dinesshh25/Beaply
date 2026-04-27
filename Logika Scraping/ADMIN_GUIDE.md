# Panduan Admin - Safe Scraping Workflow

## Overview

Modul "Logika Scraping" Beaply telah diperbarui dengan **Safe Update Workflow** yang komprehensif untuk admin. Workflow ini dirancang untuk:

✅ **Prevent Duplikasi** - Deteksi & skip data duplikat dengan hash matching & URL checking  
✅ **Preserve Bookmark** - Backup & restore bookmark user secara otomatis  
✅ **Audit Trail** - Log lengkap untuk compliance & review  
✅ **Data Integrity** - Checksum verification & transaction-based updates  
✅ **Sync Distribution** - Automatic package generation untuk distribusi ke user apps  
✅ **Database Recovery** - Backup sebelum update untuk disaster recovery  

---

## Workflow Lengkap

### Step 1: Database Backup
Sebelum scraping, sistem otomatis mem-backup database admin ke folder `db_backups/`.

```
💾 Backup database admin...
✓ Backup berhasil: c:\Beaply\db_backups\beaply_backup_20260427_140000.db
```

**Tujuan**: Jika terjadi error, Anda bisa restore dari backup.

### Step 2: Scraping dari 3 Website
Sistem scrape beasiswa dari:
- **indbeasiswa.com**
- **beasiswa.id**
- **scholarship.or.id**

### Step 3: Deduplication Detection
Sistem deteksi duplikat menggunakan 3 metode:

1. **URL Matching** - Jika `url_sumber` sudah ada → UPDATE existing
2. **Hash Matching** - Jika content hash sama → SKIP (exact duplicate)
3. **New Entry** - Data baru → INSERT

**Contoh Log**:
```
🔍 Deteksi duplikat...
  ✓ URL-match: 5 beasiswa di-update (ada perubahan info)
  ✓ Hash-match: 3 beasiswa di-skip (konten sama, URL berbeda)
  ✓ New entry: 42 beasiswa baru di-insert
```

### Step 4: Bookmark Preservation (CRITICAL!)
Sebelum update database:

1. **Backup semua bookmark user** ke memory
   ```
   📌 Backup semua bookmark user...
   ✓ Backup selesai: 150 beasiswa dengan 2500 total bookmarks
   ```

2. **Update database** dengan safe transaction
   ```
   🔒 Update database...
   ✓ Update selesai: 42 baru, 5 update, 3 skip, 0 error
   ```

3. **Restore semua bookmark user** dari backup
   ```
   📌 Restore bookmark user...
   ✓ Restore selesai: 2500 bookmark di-restore, 0 gagal
   ```

**Mengapa ini penting?**
- User yang sudah mem-bookmark beasiswa tidak akan kehilangan data bookmark-nya
- Bookmark di-preserve bahkan jika ID beasiswa berubah (dari merge/dedup)
- Jika bookmark referrer beasiswa hilang, sistem otomatis re-link-nya

### Step 5: Audit Logging
Setiap event di-log untuk compliance & review:

```
🔐 AUDIT EVENTS:
  [2026-04-27 14:00:00] SCRAPE_START: SUCCESS - Admin user1 memulai scraping
  [2026-04-27 14:05:00] BACKUP_BOOKMARK: SUCCESS - Backup 2500 bookmark user
  [2026-04-27 14:10:00] UPDATE_DATA: SUCCESS - 42 baru, 5 update, 3 skip
  [2026-04-27 14:15:00] RESTORE_BOOKMARK: SUCCESS - Restore 2500 bookmark
  [2026-04-27 14:20:00] SCRAPE_END: SUCCESS - Scraping selesai
```

### Step 6: Sync Package Generation
Sistem otomatis generate sync packages untuk distribusi ke user apps:

```
📦 GENERATE SYNC PACKAGES:
  [indbeasiswa.com] Package generated: sync_package_20260427_140000.json
  [beasiswa.id] Package generated: sync_package_20260427_140001.json
  [scholarship.or.id] Package generated: sync_package_20260427_140002.json
```

**Isi Package**:
- Metadata (timestamp, total beasiswa, checksum, dll)
- Semua data beasiswa dalam format JSON
- Integrity checksum untuk verification

### Step 7: Manifest Creation & Verification
Untuk setiap package, sistem buat manifest yang bisa di-track:

```
📋 SYNC MANIFEST:
  - Package ID: 20260427_140000
  - Total beasiswa: 150
  - Checksum: a1b2c3d4e5f6...
  - Destinations: (akan di-populate saat sync)
  - Status: READY_FOR_DISTRIBUTION
```

---

## File-File Baru

### 1. **database_beasiswa.py** (Enhanced)
Tambahan tabel & function:

**Tabel Baru:**
- `user_bookmarks` - Preservasi bookmark user
- `scraping_audit_log` - Audit trail lengkap
- `scraping_dedup_log` - Log deduplication

**Function Baru:**
```python
# Main safe update function
safe_update_beasiswa_batch(
    entries,
    sumber_website,
    admin_user='admin',
    progress_callback=None,
    skip_bookmark_preservation=False
) -> (baru, update, gagal, dedup_stats)

# Bookmark management
backup_user_bookmarks(progress_callback=None) -> dict
restore_user_bookmarks(backup_data, progress_callback=None) -> (restored, failed)

# Audit & logging
record_audit_log(...) -> audit_log_id
record_dedup_log(...) -> dedup_log_id

# Query functions
ambil_audit_log_scraping(sumber_website=None, event_type=None, ...) -> list[dict]
ambil_dedup_log_scraping(sumber_website=None, status_duplikasi=None, ...) -> list[dict]
get_scraping_stats(sesi_scraping_id=None) -> dict
```

### 2. **scraping_sync.py** (Baru)
Module untuk sync data ke user applications.

**Class:**
```python
ScrapingSyncManager(admin_db_path, sync_output_dir, backup_dir)
  - backup_admin_database() -> (sukses, path)
  - generate_sync_package(sumber_website=None) -> (sukses, path)
  - create_sync_manifest(package_path) -> (sukses, path)
  - verify_sync_package_integrity(package_path) -> (valid, message)
  - record_sync_event(...) -> bool
  - get_sync_statistics() -> dict
```

### 3. **run_all_scraping.py** (Updated)
Runner script dengan safe workflow terintegrasi.

**Function:**
```python
jalankan_semua(auto_sync: bool = True)
  - Backup database
  - Scrape semua sumber
  - Safe update dengan dedup & bookmark preservation
  - Generate sync packages
  - Create manifests
```

---

## Cara Menggunakan

### Option 1: Run dari Terminal/Command Line

```bash
cd c:\Beaply Main\Beaply\Logika Scraping
python run_all_scraping.py
```

**Output**: Full logs dengan all steps

### Option 2: Run dengan Custom Settings

Edit `run_all_scraping.py` section CONFIG:

```python
CONFIG = {
    'indbeasiswa': {
        'aktif'         : True,  # Enable/disable
        'scrape_details': True,  # Scrape full details?
        'max_entries'   : 50,    # Max entries to scrape
    },
    # ... dll
}
```

### Option 3: Run dari Python Script

```python
from Logika_Scraping.run_all_scraping import jalankan_semua

# Run scraping
jalankan_semua(auto_sync=True)
```

### Option 4: Programmatic Usage

```python
from Logika_Scraping.database_beasiswa import safe_update_beasiswa_batch
from Logika_Scraping.scraping_sync import setup_sync_manager

# Do custom scraping
hasil = my_custom_scraper()

# Safe update
baru, update, gagal, dedup = safe_update_beasiswa_batch(
    entries=hasil,
    sumber_website='custom_source',
    admin_user='admin',
    progress_callback=print
)

# Generate sync package
manager = setup_sync_manager('c:/Beaply/beaply.db')
ok, package_path = manager.generate_sync_package(
    sumber_website='custom_source'
)
```

---

## Monitoring & Review

### View Audit Logs

```python
from Logika_Scraping.database_beasiswa import ambil_audit_log_scraping

# Get all audit logs for last session
logs = ambil_audit_log_scraping(limit=100)

for log in logs:
    print(f"{log['dibuat_pada']} | {log['event_type']} | {log['status']}")
    print(f"  {log['deskripsi']}")
```

### View Dedup Logs

```python
from Logika_Scraping.database_beasiswa import ambil_dedup_log_scraping

# Get dedup logs for a source
logs = ambil_dedup_log_scraping(sumber_website='indbeasiswa.com')

for log in logs:
    print(f"Status: {log['status_duplikasi']} | Action: {log['action_taken']}")
    print(f"  {log['nama_beasiswa']}")
```

### View Scraping Stats

```python
from Logika_Scraping.database_beasiswa import get_scraping_stats

# Get stats for latest scraping session
stats = get_scraping_stats()  # None = latest sesi

print(f"Session ID: {stats['sesi_id']}")
print(f"Dedup stats: {stats['dedup_stats']}")
print(f"Audit stats: {stats['audit_stats']}")
```

### View Sync Statistics

```python
from Logika_Scraping.scraping_sync import setup_sync_manager

manager = setup_sync_manager('c:/Beaply/beaply.db')
stats = manager.get_sync_statistics()

print(f"Total packages: {stats['total_packages']}")
print(f"Total synced: {stats['total_synced']}")
print(f"Total failed: {stats['total_failed']}")
```

---

## Database Structure

### Tabel: `user_bookmarks`
Menyimpan bookmark user untuk preservasi saat update.

```sql
CREATE TABLE user_bookmarks (
    id INTEGER PRIMARY KEY,
    beasiswa_id INTEGER NOT NULL,        -- reference ke beasiswa table
    user_id TEXT NOT NULL,               -- username/user_id
    url_sumber_beasiswa TEXT NOT NULL,   -- backup url (untuk recovery)
    nama_beasiswa TEXT NOT NULL,         -- backup nama
    ditambahkan_pada TEXT,               -- timestamp
    UNIQUE(beasiswa_id, user_id)
);
```

### Tabel: `scraping_audit_log`
Full audit trail untuk compliance.

```sql
CREATE TABLE scraping_audit_log (
    id INTEGER PRIMARY KEY,
    sesi_scraping_id INTEGER,              -- reference ke scraping_log
    sumber_website TEXT NOT NULL,
    event_type TEXT NOT NULL,              -- SCRAPE_START, BACKUP_BOOKMARK, etc.
    status TEXT NOT NULL,                  -- SUCCESS, WARNING, ERROR
    deskripsi TEXT,                        -- detail event
    data_detail TEXT,                      -- JSON detail
    admin_user TEXT,                       -- admin username
    dibuat_pada TEXT
);
```

**Event Types:**
- `SCRAPE_START` - Scraping dimulai
- `BACKUP_BOOKMARK` - Bookmark di-backup
- `DEDUP_CHECK` - Dedup detection selesai
- `UPDATE_DATA` - Database update selesai
- `RESTORE_BOOKMARK` - Bookmark di-restore
- `SCRAPE_END` - Scraping selesai

### Tabel: `scraping_dedup_log`
Log untuk setiap dedup detection.

```sql
CREATE TABLE scraping_dedup_log (
    id INTEGER PRIMARY KEY,
    sesi_scraping_id INTEGER,
    sumber_website TEXT NOT NULL,
    status_duplikasi TEXT NOT NULL,     -- EXACT_DUPLICATE, HASH_MATCH, URL_MATCH, NEW
    beasiswa_id_new INTEGER,
    beasiswa_id_existing INTEGER,
    nama_beasiswa TEXT,
    url_sumber_baru TEXT,
    url_sumber_existing TEXT,
    hash_baru TEXT,
    hash_existing TEXT,
    similarity_score REAL,
    action_taken TEXT,                  -- SKIP, UPDATE, INSERT
    dibuat_pada TEXT
);
```

---

## Best Practices

### 1. **Regular Backups**
- System otomatis backup sebelum setiap scraping
- Tapi, backup database offline juga (external drive/cloud) untuk disaster recovery
- Retention: Keep backups untuk minimal 3 bulan

### 2. **Monitor Bookmarks**
- Regularly check `user_bookmarks` table untuk ensure data integrity
- Jika ada orphaned bookmarks, cleanup & notify users

### 3. **Review Audit Logs**
- Monthly review audit logs untuk compliance
- Check untuk anomalies: terlalu banyak duplikat, error rate tinggi, dll
- Keep logs untuk audit trail (legally required di beberapa jurisdiksi)

### 4. **Test Before Production**
- Jika ada changes ke scraper logic, test di development dulu
- Check dedup detection accuracy
- Verify bookmark preservation works correctly

### 5. **Sync Schedule**
- Recommend scraping every 2 months (per requirement)
- Can scrape individual sources on different schedules
- Always run auto_sync=True untuk distribute updates ke user apps

### 6. **Monitor Dedup Metrics**
- Track dedup statistics untuk assess data quality
- Tinggi hash_match = possible duplicate scraping sources
- Tinggi url_match = frequent updates (beasiswa info berubah often)

---

## Troubleshooting

### Problem: "Bookmark corruption detected"
**Solution:**
1. Stop scraping
2. Restore dari backup: `beaply_backup_*.db`
3. Check `user_bookmarks` table untuk orphaned records
4. Run recovery: `safe_update_beasiswa_batch(..., skip_bookmark_preservation=False)`

### Problem: "Too many duplicates detected"
**Solution:**
1. Check `scraping_dedup_log` untuk patterns
2. Adjust scraper logic jika ada issue dengan URL normalization
3. Consider deduping existing data dengan `content_hash`

### Problem: "Sync package verification failed"
**Solution:**
1. Regenerate package: `manager.generate_sync_package()`
2. Verify integrity: `manager.verify_sync_package_integrity()`
3. Check for data corruption in database

### Problem: "Admin scraping too slow"
**Solution:**
1. Check scraper performance di individual scrapers
2. Reduce `max_entries` atau `max_pages_per_category` di CONFIG
3. Consider parallel scraping (if supported)

---

## Configuration Reference

### Environment Variables
```bash
# Set admin username for audit logs
set BEAPLY_ADMIN_USER=admin_name

# Custom database path (if different from default)
set BEAPLY_DB_PATH=c:\custom\path\beaply.db
```

### File Locations
```
Logika Scraping/
├── run_all_scraping.py          # Main runner
├── database_beasiswa.py         # Enhanced DB module
├── scraping_sync.py             # Sync module
├── scrapping_indBeasiswa.py     # Scraper 1
├── scrapping_beasiswaid.py      # Scraper 2
├── scrapping_scholarshiporid.py # Scraper 3
├── normalizer.py                # Data normalizer
├── ADMIN_GUIDE.md              # This file
└── db_backups/                  # Database backups (auto-created)
    └── beaply_backup_*.db       # Backup snapshots

Project Root/
├── beaply.db                    # Main database
├── sync_packages/               # Sync packages (auto-created)
│   ├── sync_package_*.json      # Package files
│   ├── manifest_*.json          # Manifest files
│   └── sync_logs/               # Sync event logs
└── db_backups/                  # Database backups
    └── beaply_backup_*.db       # Backup snapshots
```

---

## Support & Documentation

- **Bookmark Preservation Logic**: See `safe_update_beasiswa_batch()` in `database_beasiswa.py`
- **Deduplication Algorithm**: See `safe_update_beasiswa_batch()` dedup logic
- **Sync Distribution**: See `ScrapingSyncManager` in `scraping_sync.py`
- **Audit Trail**: Query `scraping_audit_log` table
- **Database Schema**: See `init_beasiswa_db()` in `database_beasiswa.py`

---

## Version History

### v2.0 (2026-04-27) - Safe Update Workflow Release
- ✅ Bookmark preservation
- ✅ Deduplication with hash & URL matching
- ✅ Full audit trail
- ✅ Sync package generation
- ✅ Database backup & recovery
- ✅ Transaction-based updates

### v1.0 (Previous)
- Basic scraping from 3 sources
- Simple database storage

---

**Last Updated**: 2026-04-27  
**Maintained By**: Beaply Development Team  
**For Support**: Contact admin@beaply.dev
