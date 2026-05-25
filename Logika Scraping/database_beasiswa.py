"""
database_beasiswa.py
Modul database untuk menyimpan hasil scraping beasiswa ke SQLite (beaply.db).

Desain:
  - Tabel `beasiswa`             → data pokok setiap beasiswa (kolom terstruktur + JSON raw)
  - Tabel `scraping_log`         → riwayat setiap sesi scraping (kapan, dari mana, berapa data)
  - Tabel `user_bookmarks`       → preservasi bookmark user saat update data
  - Tabel `scraping_audit_log`   → audit trail lengkap untuk compliance & admin review
  - Tabel `scraping_dedup_log`   → logging untuk detection & prevention duplikasi

Strategi penyimpanan:
  - Field terstruktur (nama, penyelenggara, jenjang, deadline, dst.) disimpan sebagai
    kolom relasional agar bisa di-query/filter langsung dari GUI.
  - Field array (jenjang, jurusan, kategori_raw) disimpan sebagai JSON string.
  - Seluruh dict hasil scraping juga disimpan di kolom `data_json` sebagai cadangan
    lengkap agar tidak ada informasi yang hilang.
  - Mekanisme UPSERT berdasarkan `url_sumber` → data yang sama tidak duplikat,
    tapi diupdate jika ada versi lebih baru.
  - Content hash untuk deteksi duplikat & data integrity check.
  - Bookmark user di-backup sebelum update, dan di-restore setelah update selesai.
"""

import json
import logging
import os
import sqlite3
import hashlib
from datetime import datetime

# ─── Path ke database yang sama dengan beaply.db ─────────────────────────────
# Sesuaikan path ini jika lokasi beaply.db berbeda
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "beaply.db"
)

logger = logging.getLogger(__name__)


# ─── Koneksi ──────────────────────────────────────────────────────────────────

def get_connection() -> sqlite3.Connection:
    """Buka koneksi ke beaply.db dengan row_factory dict-like."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")   # lebih aman untuk concurrent write
    return conn


# ─── Inisialisasi Tabel ───────────────────────────────────────────────────────

def init_beasiswa_db():
    """
    Buat tabel `beasiswa`, `scraping_log`, `user_bookmarks`, `scraping_audit_log`,
    dan `scraping_dedup_log` jika belum ada.
    Aman dipanggil berulang kali (idempotent).
    """
    conn = get_connection()
    cur  = conn.cursor()

    # ── Tabel utama beasiswa ──────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS beasiswa (
            id                INTEGER  PRIMARY KEY AUTOINCREMENT,

            -- Identitas & sumber
            nama              TEXT     NOT NULL,
            url               TEXT     UNIQUE,          -- key deduplikasi
            url_resmi         TEXT     DEFAULT NULL,    -- link pendaftaran resmi
            sumber_website    TEXT     DEFAULT NULL,    -- 'indbeasiswa.com' | 'beasiswa.id' | 'scholarship.or.id'

            -- Informasi pokok (kolom relasional, mudah di-query)
            penyelenggara     TEXT     DEFAULT NULL,
            jenjang           TEXT     DEFAULT NULL,    -- JSON array, mis: '["S1","S2"]'
            jurusan           TEXT     DEFAULT NULL,    -- JSON array, mis: '["Teknik","Informatika"]'
            lokasi            TEXT     DEFAULT NULL,    -- negara/kota
            tipe_beasiswa     TEXT     DEFAULT NULL,    -- 'Dalam Negeri' | 'Luar Negeri'
            deadline          TEXT     DEFAULT NULL,    -- tanggal terformat YYYY-MM-DD atau teks
            deadline_text     TEXT     DEFAULT NULL,    -- teks asli deadline

            -- Detail
            cakupan_beasiswa  TEXT     DEFAULT NULL,
            syarat_utama      TEXT     DEFAULT NULL,
            ipk_minimal       REAL     DEFAULT NULL,
            kategori_raw      TEXT     DEFAULT NULL,    -- JSON array dari website

            -- Deduplication & integrity
            content_hash      TEXT     DEFAULT NULL,    -- SHA256 hash dari content untuk detect duplikasi
            
            -- Data lengkap (JSON blob) — cadangan agar tidak ada info yang hilang
            data_json         TEXT     NOT NULL,

            -- Metadata
            dibuat_pada       TEXT     DEFAULT (datetime('now','localtime')),
            diupdate_pada     TEXT     DEFAULT (datetime('now','localtime'))
        )
    """)

    # ── Tabel log sesi scraping ───────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS scraping_log (
            id              INTEGER  PRIMARY KEY AUTOINCREMENT,
            sumber_website  TEXT     NOT NULL,          -- website yang di-scrape
            jumlah_baru     INTEGER  DEFAULT 0,         -- berhasil INSERT baru
            jumlah_update   INTEGER  DEFAULT 0,         -- berhasil UPDATE (data lama)
            jumlah_gagal    INTEGER  DEFAULT 0,         -- gagal disimpan
            durasi_detik    REAL     DEFAULT NULL,      -- durasi scraping
            keterangan      TEXT     DEFAULT NULL,      -- pesan tambahan / error summary
            dibuat_pada     TEXT     DEFAULT (datetime('now','localtime'))
        )
    """)

    # ── Tabel Bookmark User (preservasi saat update admin) ─────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user_bookmarks (
            id                  INTEGER  PRIMARY KEY AUTOINCREMENT,
            beasiswa_id         INTEGER  NOT NULL,      -- reference ke tabel beasiswa
            user_id             TEXT     NOT NULL,      -- username/user_id dari aplikasi user
            url_sumber_beasiswa TEXT     NOT NULL,      -- backup url_sumber untuk recovery
            nama_beasiswa       TEXT     NOT NULL,      -- backup nama untuk reference
            ditambahkan_pada    TEXT     DEFAULT (datetime('now','localtime')),
            UNIQUE(beasiswa_id, user_id),
            FOREIGN KEY(beasiswa_id) REFERENCES beasiswa(id) ON DELETE CASCADE
        )
    """)

    # ── Tabel Audit Log Scraping (compliance & admin review) ──────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS scraping_audit_log (
            id                      INTEGER  PRIMARY KEY AUTOINCREMENT,
            sesi_scraping_id        INTEGER  DEFAULT NULL,   -- reference ke scraping_log
            sumber_website          TEXT     NOT NULL,
            event_type              TEXT     NOT NULL,       -- 'SCRAPE_START', 'BACKUP_BOOKMARK', 'DEDUP_CHECK', 'UPDATE_DATA', 'RESTORE_BOOKMARK', 'SCRAPE_END'
            status                  TEXT     NOT NULL,       -- 'SUCCESS', 'WARNING', 'ERROR'
            deskripsi               TEXT     DEFAULT NULL,   -- detail event
            data_detail             TEXT     DEFAULT NULL,   -- JSON detail event (misalnya: duplikat count, affected rows)
            admin_user              TEXT     DEFAULT NULL,   -- admin username yang melakukan scraping
            dibuat_pada             TEXT     DEFAULT (datetime('now','localtime'))
        )
    """)

    # ── Tabel Deduplication Log (tracking & prevention duplikasi) ──────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS scraping_dedup_log (
            id                      INTEGER  PRIMARY KEY AUTOINCREMENT,
            sesi_scraping_id        INTEGER  DEFAULT NULL,   -- reference ke scraping_log
            sumber_website          TEXT     NOT NULL,
            status_duplikasi        TEXT     NOT NULL,       -- 'EXACT_DUPLICATE', 'HASH_MATCH', 'URL_MATCH', 'SIMILAR_CONTENT', 'NEW'
            beasiswa_id_new         INTEGER  DEFAULT NULL,   -- beasiswa baru dari scraping
            beasiswa_id_existing    INTEGER  DEFAULT NULL,   -- beasiswa existing yang cocok
            nama_beasiswa           TEXT     DEFAULT NULL,
            url_sumber_baru         TEXT     DEFAULT NULL,
            url_sumber_existing     TEXT     DEFAULT NULL,
            hash_baru               TEXT     DEFAULT NULL,   -- content hash
            hash_existing           TEXT     DEFAULT NULL,
            similarity_score        REAL     DEFAULT NULL,   -- 0-100, untuk content similarity
            action_taken            TEXT     DEFAULT NULL,   -- 'SKIP', 'UPDATE', 'INSERT'
            dibuat_pada             TEXT     DEFAULT (datetime('now','localtime')),
            FOREIGN KEY(beasiswa_id_new) REFERENCES beasiswa(id),
            FOREIGN KEY(beasiswa_id_existing) REFERENCES beasiswa(id)
        )
    """)

    # Commit tabel dulu sebelum migrasi & index
    conn.commit()

    # ── Migrasi: tambah kolom baru jika tabel sudah ada tapi kolom belum ada ──
    # (backward compatible — aman dijalankan berulang kali)
    migrasi_kolom = [
        "ALTER TABLE beasiswa ADD COLUMN url             TEXT UNIQUE",
        "ALTER TABLE beasiswa ADD COLUMN url_resmi       TEXT DEFAULT NULL",
        "ALTER TABLE beasiswa ADD COLUMN sumber_website  TEXT DEFAULT NULL",
        "ALTER TABLE beasiswa ADD COLUMN tipe_beasiswa   TEXT DEFAULT NULL",
        "ALTER TABLE beasiswa ADD COLUMN deadline_text   TEXT DEFAULT NULL",
        "ALTER TABLE beasiswa ADD COLUMN kategori_raw    TEXT DEFAULT NULL",
        "ALTER TABLE beasiswa ADD COLUMN diupdate_pada   TEXT DEFAULT NULL",
        "ALTER TABLE beasiswa ADD COLUMN lokasi          TEXT DEFAULT NULL",
        "ALTER TABLE beasiswa ADD COLUMN ipk_minimal     REAL DEFAULT NULL",
        "ALTER TABLE beasiswa ADD COLUMN jurusan         TEXT DEFAULT NULL",
        "ALTER TABLE beasiswa ADD COLUMN syarat_utama    TEXT DEFAULT NULL",
        "ALTER TABLE beasiswa ADD COLUMN cakupan_beasiswa TEXT DEFAULT NULL",
        "ALTER TABLE beasiswa ADD COLUMN jenjang         TEXT DEFAULT NULL",
        "ALTER TABLE beasiswa ADD COLUMN penyelenggara   TEXT DEFAULT NULL",
        "ALTER TABLE beasiswa ADD COLUMN deadline        TEXT DEFAULT NULL",
        "ALTER TABLE beasiswa ADD COLUMN content_hash    TEXT DEFAULT NULL",
    ]
    for sql in migrasi_kolom:
        try:
            cur.execute(sql)
            conn.commit()
        except sqlite3.OperationalError:
            pass  # Kolom sudah ada, skip

    # ── Indeks untuk query yang sering dipakai ─────────────────────────
    try:
        cur.execute("CREATE INDEX IF NOT EXISTS idx_beasiswa_sumber   ON beasiswa (sumber_website)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_beasiswa_deadline ON beasiswa (deadline)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_beasiswa_lokasi   ON beasiswa (lokasi)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_beasiswa_hash     ON beasiswa (content_hash)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_bookmarks_user    ON user_bookmarks (user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_audit_log_source  ON scraping_audit_log (sumber_website)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_dedup_log_source  ON scraping_dedup_log (sumber_website)")
        conn.commit()
    except sqlite3.OperationalError as e:
        logger.warning(f"Index skip: {e}")

    conn.close()
    logger.info("Tabel beasiswa, scraping_log, user_bookmarks, scraping_audit_log, dan scraping_dedup_log siap.")


# ─── Helper ───────────────────────────────────────────────────────────────────

def _to_json(value) -> str | None:
    """Konversi list/dict ke JSON string. Return None jika kosong."""
    if value is None:
        return None
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=False) if value else None
    return str(value) if value else None


def _serialize_entry(entry: dict) -> dict:
    """
    Siapkan dict `entry` (hasil normalizer) menjadi dict siap INSERT ke tabel.

    Field array (jenjang, jurusan, kategori_raw) → JSON string
    Field lain  → string / float / None
    data_json   → seluruh entry di-dump sebagai JSON blob
    content_hash → SHA256 hash dari key fields untuk deduplication
    """
    # Tangani jenjang: bisa list atau string
    jenjang = entry.get('jenjang', [])
    if isinstance(jenjang, str):
        jenjang = [jenjang] if jenjang else []

    # Tangani jurusan: bisa list atau string
    jurusan = entry.get('jurusan', [])
    if isinstance(jurusan, str):
        jurusan = [jurusan] if jurusan else []

    kategori_raw = entry.get('kategori_raw', [])
    if isinstance(kategori_raw, str):
        kategori_raw = [kategori_raw] if kategori_raw else []

    # IPK: pastikan float atau None
    ipk = entry.get('ipk_minimal')
    try:
        ipk = float(ipk) if ipk is not None else None
    except (ValueError, TypeError):
        ipk = None

    # Deadline: ambil dari field 'deadline' (sudah dinormalisasi) atau fallback ke deadline_text
    deadline = entry.get('deadline') or None
    if isinstance(deadline, datetime):
        deadline = deadline.strftime('%Y-%m-%d')

    # Generate content hash dari key fields untuk deduplication
    hash_input = f"{entry.get('nama_beasiswa', '')}||{entry.get('penyelenggara', '')}||{entry.get('url_sumber', '')}"
    content_hash = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()

    return {
        'nama':             str(entry.get('nama_beasiswa', '')).strip()[:500],
        'nama_beasiswa':    str(entry.get('nama_beasiswa', '')).strip()[:500], # Keep for dedup tracking
        'url':              str(entry.get('url_sumber', '')).strip() or None,
        'url_sumber':       str(entry.get('url_sumber', '')).strip() or None, # Keep for dedup tracking
        'url_resmi':        str(entry.get('url_resmi', '')).strip() or None,
        'sumber_website':   str(entry.get('sumber_website', '')).strip() or None,
        'penyelenggara':    str(entry.get('penyelenggara', '')).strip()[:300] or None,
        'jenjang':          _to_json(jenjang),
        'jurusan':          _to_json(jurusan),
        'lokasi':           str(entry.get('lokasi', '')).strip()[:200] or None,
        'tipe_beasiswa':    str(entry.get('tipe_beasiswa', '')).strip()[:100] or None,
        'deadline':         str(deadline).strip()[:100] if deadline else None,
        'deadline_text':    str(entry.get('deadline_text', '')).strip()[:300] or None,
        'cakupan_beasiswa': str(entry.get('cakupan_beasiswa', '')).strip()[:1000] or None,
        'syarat_utama':     str(entry.get('syarat_utama', '')).strip()[:2000] or None,
        'ipk_minimal':      ipk,
        'kategori_raw':     _to_json(kategori_raw),
        'content_hash':     content_hash,
        'data_json':        json.dumps(entry, ensure_ascii=False, default=str),
    }


# ─── Bookmark Management (Preservasi saat update admin) ────────────────────────

def backup_user_bookmarks(progress_callback=None) -> dict:
    """
    Backup semua user bookmarks sebelum admin melakukan update data.
    Return dict dengan struktur: {beasiswa_id: [list of user_ids]}
    """
    if progress_callback:
        progress_callback("📌 Backup semua bookmark user...")

    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT beasiswa_id, user_id FROM user_bookmarks
            ORDER BY beasiswa_id
        """)
        rows = cur.fetchall()
        conn.close()

        # Organize dalam dict untuk easy lookup
        bookmarks_backup = {}
        for row in rows:
            bid = row[0]
            uid = row[1]
            if bid not in bookmarks_backup:
                bookmarks_backup[bid] = []
            bookmarks_backup[bid].append(uid)

        if progress_callback:
            total_bookmarks = sum(len(users) for users in bookmarks_backup.values())
            progress_callback(f"✓ Backup selesai: {len(bookmarks_backup)} beasiswa dengan {total_bookmarks} total bookmarks")

        return bookmarks_backup

    except Exception as e:
        logger.error(f"Error backup bookmarks: {e}")
        if progress_callback:
            progress_callback(f"⚠ Error saat backup bookmark: {e}")
        return {}


def restore_user_bookmarks(backup_data: dict, progress_callback=None) -> tuple[int, int]:
    """
    Restore user bookmarks dari backup setelah update selesai.
    
    Args:
        backup_data : dict dari backup_user_bookmarks()
    
    Returns:
        (restored_count, failed_count)
    """
    if not backup_data:
        return 0, 0

    if progress_callback:
        progress_callback("📌 Restore bookmark user...")

    try:
        conn = get_connection()
        cur = conn.cursor()

        restored = 0
        failed = 0

        for beasiswa_id, user_ids in backup_data.items():
            for user_id in user_ids:
                try:
                    # Cek apakah bookmark sudah ada di tabel (beasiswa_id mungkin berubah ID)
                    cur.execute("""
                        SELECT id FROM user_bookmarks
                        WHERE beasiswa_id = ? AND user_id = ?
                    """, (beasiswa_id, user_id))

                    if not cur.fetchone():
                        # Ambil data beasiswa untuk backup
                        cur.execute("""
                            SELECT id, url, nama
                            FROM beasiswa WHERE id = ?
                        """, (beasiswa_id,))
                        bea = cur.fetchone()
                        if bea:
                            cur.execute("""
                                INSERT OR IGNORE INTO user_bookmarks
                                    (beasiswa_id, user_id, url_sumber_beasiswa, nama_beasiswa)
                                VALUES (?, ?, ?, ?)
                            """, (bea[0], user_id, bea[1], bea[2]))
                            restored += 1
                    else:
                        restored += 1

                except Exception as e:
                    logger.warning(f"Gagal restore bookmark user {user_id} untuk beasiswa {beasiswa_id}: {e}")
                    failed += 1

        conn.commit()
        conn.close()

        if progress_callback:
            progress_callback(f"✓ Restore selesai: {restored} bookmark di-restore, {failed} gagal")

        return restored, failed

    except Exception as e:
        logger.error(f"Error restore bookmarks: {e}")
        if progress_callback:
            progress_callback(f"⚠ Error saat restore bookmark: {e}")
        return 0, len([u for users in backup_data.values() for u in users])


def record_audit_log(
    sumber_website: str,
    event_type: str,
    status: str,
    deskripsi: str = None,
    data_detail: dict = None,
    admin_user: str = None,
    sesi_scraping_id: int = None
) -> int:
    """
    Record event ke scraping_audit_log untuk audit trail & compliance.

    Args:
        sumber_website  : source website
        event_type      : 'SCRAPE_START', 'BACKUP_BOOKMARK', 'DEDUP_CHECK', 'UPDATE_DATA', 'RESTORE_BOOKMARK', 'SCRAPE_END'
        status          : 'SUCCESS', 'WARNING', 'ERROR'
        deskripsi       : detail pesan
        data_detail     : dict untuk di-serialize sebagai JSON
        admin_user      : username admin yang melakukan scraping
        sesi_scraping_id: reference ke scraping_log id

    Returns:
        audit_log id yang baru dibuat
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        detail_json = json.dumps(data_detail, ensure_ascii=False, default=str) if data_detail else None

        cur.execute("""
            INSERT INTO scraping_audit_log
                (sesi_scraping_id, sumber_website, event_type, status, deskripsi, data_detail, admin_user)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (sesi_scraping_id, sumber_website, event_type, status, deskripsi, detail_json, admin_user))

        audit_id = cur.lastrowid
        conn.commit()
        conn.close()

        return audit_id

    except Exception as e:
        logger.error(f"Error record audit log: {e}")
        return -1


def record_dedup_log(
    sumber_website: str,
    status_duplikasi: str,
    beasiswa_id_new: int = None,
    beasiswa_id_existing: int = None,
    nama_beasiswa: str = None,
    url_sumber_baru: str = None,
    url_sumber_existing: str = None,
    hash_baru: str = None,
    hash_existing: str = None,
    similarity_score: float = None,
    action_taken: str = None,
    sesi_scraping_id: int = None
) -> int:
    """
    Record deduplication detection & action untuk tracking & analytics.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO scraping_dedup_log
                (sesi_scraping_id, sumber_website, status_duplikasi, beasiswa_id_new, beasiswa_id_existing,
                 nama_beasiswa, url_sumber_baru, url_sumber_existing, hash_baru, hash_existing,
                 similarity_score, action_taken)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (sesi_scraping_id, sumber_website, status_duplikasi, beasiswa_id_new, beasiswa_id_existing,
              nama_beasiswa, url_sumber_baru, url_sumber_existing, hash_baru, hash_existing,
              similarity_score, action_taken))

        dedup_id = cur.lastrowid
        conn.commit()
        conn.close()

        return dedup_id

    except Exception as e:
        logger.error(f"Error record dedup log: {e}")
        return -1


# ─── CRUD Beasiswa ────────────────────────────────────────────────────────────

def simpan_beasiswa_batch(
    entries: list[dict],
    progress_callback=None
) -> tuple[int, int, int]:
    """
    Simpan banyak beasiswa sekaligus dari hasil scraping.

    Strategi UPSERT:
      - Jika `url_sumber` belum ada → INSERT baru
      - Jika `url_sumber` sudah ada → UPDATE semua field kecuali `dibuat_pada`

    Args:
        entries           : list of dict hasil normalize_beasiswa()
        progress_callback : callable(str) opsional untuk laporan progres

    Returns:
        (jumlah_baru, jumlah_update, jumlah_gagal)
    """
    if not entries:
        return 0, 0, 0

    conn = get_connection()
    cur  = conn.cursor()

    baru   = 0
    update = 0
    gagal  = 0

    for i, entry in enumerate(entries, 1):
        try:
            row = _serialize_entry(entry)

            # Cek apakah url_sumber sudah ada
            url = row.get('url_sumber')
            if url:
                cur.execute("SELECT id FROM beasiswa WHERE url = ?", (url,))
                existing = cur.fetchone()
            else:
                existing = None

            if existing:
                # UPDATE: perbarui semua field kecuali id & dibuat_pada
                cur.execute("""
                    UPDATE beasiswa SET
                        nama             = :nama,
                        url_resmi        = :url_resmi,
                        sumber_website   = :sumber_website,
                        penyelenggara    = :penyelenggara,
                        jenjang          = :jenjang,
                        jurusan          = :jurusan,
                        lokasi           = :lokasi,
                        tipe_beasiswa    = :tipe_beasiswa,
                        deadline         = :deadline,
                        deadline_text    = :deadline_text,
                        cakupan_beasiswa = :cakupan_beasiswa,
                        syarat_utama     = :syarat_utama,
                        ipk_minimal      = :ipk_minimal,
                        kategori_raw     = :kategori_raw,
                        data_json        = :data_json,
                        diupdate_pada    = datetime('now','localtime')
                    WHERE url = :url
                """, row)
                update += 1
            else:
                # INSERT baru
                cur.execute("""
                    INSERT INTO beasiswa (
                        nama, url, url_resmi, sumber_website,
                        penyelenggara, jenjang, jurusan, lokasi, tipe_beasiswa,
                        deadline, deadline_text, cakupan_beasiswa, syarat_utama,
                        ipk_minimal, kategori_raw, data_json
                    ) VALUES (
                        :nama, :url, :url_resmi, :sumber_website,
                        :penyelenggara, :jenjang, :jurusan, :lokasi, :tipe_beasiswa,
                        :deadline, :deadline_text, :cakupan_beasiswa, :syarat_utama,
                        :ipk_minimal, :kategori_raw, :data_json
                    )
                """, row)
                baru += 1

            # Laporan per 10 entri
            if progress_callback and i % 10 == 0:
                progress_callback(
                    f"Menyimpan ke DB... [{i}/{len(entries)}] "
                    f"(baru={baru}, update={update}, gagal={gagal})"
                )

        except Exception as e:
            gagal += 1
            nama = entry.get('nama_beasiswa', '?')[:60]
            logger.error(f"Gagal simpan '{nama}': {e}")

    conn.commit()
    conn.close()

    if progress_callback:
        progress_callback(
            f"Selesai simpan ke DB: {baru} baru, {update} diperbarui, {gagal} gagal."
        )

    logger.info(f"simpan_beasiswa_batch: baru={baru} update={update} gagal={gagal}")
    return baru, update, gagal


def simpan_satu_beasiswa(entry: dict) -> tuple[bool, str]:
    """
    Simpan satu beasiswa. Return (sukses, pesan).
    Praktis untuk kebutuhan insert manual / testing.
    """
    baru, update, gagal = simpan_beasiswa_batch([entry])
    if gagal:
        return False, "Gagal menyimpan beasiswa."
    if update:
        return True, "Beasiswa diperbarui."
    return True, "Beasiswa baru berhasil disimpan."


def safe_update_beasiswa_batch(
    entries: list[dict],
    sumber_website: str,
    admin_user: str = "admin",
    progress_callback=None,
    skip_bookmark_preservation: bool = False
) -> tuple[int, int, int, dict]:
    """
    Safe update beasiswa dengan preservasi bookmark user (FITUR UTAMA ADMIN SCRAPING).
    
    Workflow:
    1. Backup semua bookmark user
    2. Catat audit log: BACKUP_BOOKMARK
    3. Deteksi duplikat & catat ke dedup_log
    4. Update data (INSERT baru atau UPDATE existing)
    5. Catat audit log: UPDATE_DATA
    6. Restore semua bookmark user dari backup
    7. Catat audit log: RESTORE_BOOKMARK, SCRAPE_END
    
    Args:
        entries                      : list of dict hasil scraping
        sumber_website               : nama website sumber
        admin_user                   : username admin yang melakukan scraping (untuk audit)
        progress_callback            : callable(str) untuk progress reporting
        skip_bookmark_preservation   : jika True, skip backup/restore bookmark (untuk first-time setup)
    
    Returns:
        (jumlah_baru, jumlah_update, jumlah_gagal, detail_stats)
    """
    if not entries:
        return 0, 0, 0, {}

    # Create sesi scraping log dulu untuk reference audit
    sesi_id = catat_log_scraping(
        sumber_website=sumber_website,
        jumlah_baru=0,
        jumlah_update=0,
        jumlah_gagal=0,
        keterangan=f"Sesi scraping dimulai oleh {admin_user}"
    )

    # Audit: SCRAPE_START
    record_audit_log(
        sumber_website=sumber_website,
        event_type='SCRAPE_START',
        status='SUCCESS',
        deskripsi=f"Admin {admin_user} memulai scraping dari {sumber_website}",
        admin_user=admin_user,
        sesi_scraping_id=sesi_id
    )

    if progress_callback:
        progress_callback(f"\n🔄 Memulai SAFE UPDATE dari {sumber_website}...")

    # STEP 1: Backup user bookmarks
    bookmarks_backup = {}
    if not skip_bookmark_preservation:
        bookmarks_backup = backup_user_bookmarks(progress_callback)
        record_audit_log(
            sumber_website=sumber_website,
            event_type='BACKUP_BOOKMARK',
            status='SUCCESS',
            deskripsi=f"Backup {sum(len(u) for u in bookmarks_backup.values())} bookmark user",
            data_detail={'total_bookmarks': sum(len(u) for u in bookmarks_backup.values())},
            admin_user=admin_user,
            sesi_scraping_id=sesi_id
        )

    # STEP 2: Deteksi & log duplikasi
    if progress_callback:
        progress_callback("🔍 Deteksi duplikat...")

    conn = get_connection()
    cur = conn.cursor()

    dedup_stats = {
        'exact_duplicate': 0,
        'hash_match': 0,
        'url_match': 0,
        'new_entry': 0,
        'skipped': 0
    }

    baru = 0
    update = 0
    gagal = 0

    for i, entry in enumerate(entries, 1):
        try:
            row = _serialize_entry(entry)
            url = row.get('url_sumber')
            hash_val = row.get('content_hash')

            # Cek existing dengan berbagai kriteria
            existing_by_url = None
            existing_by_hash = None

            if url:
                cur.execute("SELECT id, content_hash FROM beasiswa WHERE url = ?", (url,))
                existing_by_url = cur.fetchone()

            if hash_val:
                cur.execute("SELECT id, url FROM beasiswa WHERE content_hash = ?", (hash_val,))
                existing_by_hash = cur.fetchone()

            # Tentukan action
            if existing_by_url:
                # URL match -> UPDATE existing
                cur.execute("""
                    UPDATE beasiswa SET
                        nama             = :nama,
                        url_resmi        = :url_resmi,
                        sumber_website   = :sumber_website,
                        penyelenggara    = :penyelenggara,
                        jenjang          = :jenjang,
                        jurusan          = :jurusan,
                        lokasi           = :lokasi,
                        tipe_beasiswa    = :tipe_beasiswa,
                        deadline         = :deadline,
                        deadline_text    = :deadline_text,
                        cakupan_beasiswa = :cakupan_beasiswa,
                        syarat_utama     = :syarat_utama,
                        ipk_minimal      = :ipk_minimal,
                        kategori_raw     = :kategori_raw,
                        content_hash     = :content_hash,
                        data_json        = :data_json,
                        diupdate_pada    = datetime('now','localtime')
                    WHERE url = :url
                """, row)
                update += 1
                dedup_stats['url_match'] += 1

                # Log dedup action
                record_dedup_log(
                    sumber_website=sumber_website,
                    status_duplikasi='URL_MATCH',
                    beasiswa_id_existing=existing_by_url[0],
                    nama_beasiswa=row.get('nama_beasiswa'),
                    url_sumber_existing=url,
                    hash_existing=existing_by_url[1],
                    hash_baru=hash_val,
                    action_taken='UPDATE',
                    sesi_scraping_id=sesi_id
                )

            elif existing_by_hash and existing_by_hash[0] != (existing_by_url[0] if existing_by_url else -1):
                # Hash match (content sama) tapi URL berbeda -> SKIP (exact duplicate)
                dedup_stats['hash_match'] += 1
                dedup_stats['skipped'] += 1

                record_dedup_log(
                    sumber_website=sumber_website,
                    status_duplikasi='HASH_MATCH',
                    beasiswa_id_new=None,
                    beasiswa_id_existing=existing_by_hash[0],
                    nama_beasiswa=row.get('nama_beasiswa'),
                    url_sumber_baru=url,
                    url_sumber_existing=existing_by_hash[1],
                    hash_baru=hash_val,
                    hash_existing=hash_val,
                    action_taken='SKIP',
                    sesi_scraping_id=sesi_id
                )

                if progress_callback and i % 20 == 0:
                    progress_callback(f"  ⏭️  Skip duplikat: {row['nama_beasiswa'][:50]}")

            else:
                # INSERT baru
                cur.execute("""
                    INSERT INTO beasiswa (
                        nama, url, url_resmi, sumber_website,
                        penyelenggara, jenjang, jurusan, lokasi, tipe_beasiswa,
                        deadline, deadline_text, cakupan_beasiswa, syarat_utama,
                        ipk_minimal, kategori_raw, content_hash, data_json
                    ) VALUES (
                        :nama, :url, :url_resmi, :sumber_website,
                        :penyelenggara, :jenjang, :jurusan, :lokasi, :tipe_beasiswa,
                        :deadline, :deadline_text, :cakupan_beasiswa, :syarat_utama,
                        :ipk_minimal, :kategori_raw, :content_hash, :data_json
                    )
                """, row)
                baru += 1
                dedup_stats['new_entry'] += 1

                record_dedup_log(
                    sumber_website=sumber_website,
                    status_duplikasi='NEW',
                    nama_beasiswa=row.get('nama_beasiswa'),
                    url_sumber_baru=url,
                    hash_baru=hash_val,
                    action_taken='INSERT',
                    sesi_scraping_id=sesi_id
                )

            # Progress report
            if progress_callback and i % 10 == 0:
                progress_callback(
                    f"  Proses data... [{i}/{len(entries)}] "
                    f"(baru={baru}, update={update}, skip={dedup_stats['skipped']})"
                )

        except Exception as e:
            gagal += 1
            nama = entry.get('nama_beasiswa', '?')[:60]
            logger.error(f"Gagal proses '{nama}': {e}")

    # STEP 3: Commit semua update
    try:
        conn.commit()
    except Exception as e:
        logger.error(f"Error commit update: {e}")
        gagal += len(entries) - baru - update

    conn.close()

    # Audit: UPDATE_DATA
    record_audit_log(
        sumber_website=sumber_website,
        event_type='UPDATE_DATA',
        status='SUCCESS',
        deskripsi=f"Update database selesai: {baru} baru, {update} diperbarui, {dedup_stats['skipped']} skip duplikat",
        data_detail=dedup_stats,
        admin_user=admin_user,
        sesi_scraping_id=sesi_id
    )

    # STEP 4: Restore bookmarks
    if not skip_bookmark_preservation:
        restored, restore_failed = restore_user_bookmarks(bookmarks_backup, progress_callback)
        record_audit_log(
            sumber_website=sumber_website,
            event_type='RESTORE_BOOKMARK',
            status='SUCCESS' if restore_failed == 0 else 'WARNING',
            deskripsi=f"Restore bookmark selesai: {restored} berhasil, {restore_failed} gagal",
            data_detail={'restored': restored, 'failed': restore_failed},
            admin_user=admin_user,
            sesi_scraping_id=sesi_id
        )

    # STEP 5: Final audit log & update sesi_id scraping_log
    record_audit_log(
        sumber_website=sumber_website,
        event_type='SCRAPE_END',
        status='SUCCESS',
        deskripsi=f"Scraping dari {sumber_website} selesai dengan sukses",
        data_detail={
            'total_input': len(entries),
            'baru': baru,
            'update': update,
            'gagal': gagal,
            'dedup_stats': dedup_stats
        },
        admin_user=admin_user,
        sesi_scraping_id=sesi_id
    )

    # Update scraping_log dengan hasil final
    try:
        conn = get_connection()
        conn.execute("""
            UPDATE scraping_log SET
                jumlah_baru = ?, jumlah_update = ?, jumlah_gagal = ?,
                keterangan = ?
            WHERE id = ?
        """, (baru, update, gagal, f"Safe update selesai. Dedup: {dedup_stats}", sesi_id))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error update scraping_log: {e}")

    if progress_callback:
        progress_callback("\n✅ Safe update selesai!")
        progress_callback(f"   Hasil: {baru} baru | {update} update | {dedup_stats['skipped']} duplikat skip | {gagal} error")

    logger.info(f"safe_update_beasiswa_batch: baru={baru} update={update} gagal={gagal} dedup_stats={dedup_stats}")
    
    return baru, update, gagal, dedup_stats


# ─── Query / Read ─────────────────────────────────────────────────────────────

def ambil_semua_beasiswa(
    sumber: str = None,
    jenjang: str = None,
    lokasi: str = None,
    keyword: str = None,
    limit: int = 500,
    offset: int = 0
) -> list[dict]:
    """
    Ambil beasiswa dari database dengan filter opsional.

    Args:
        sumber   : filter sumber_website ('indbeasiswa.com', 'beasiswa.id', 'scholarship.or.id')
        jenjang  : filter jenjang, cari di dalam kolom JSON (mis: 'S1')
        lokasi   : filter lokasi (LIKE, case-insensitive)
        keyword  : cari di nama_beasiswa dan penyelenggara (LIKE)
        limit    : jumlah maksimum baris yang dikembalikan
        offset   : paginasi

    Returns:
        list of dict
    """
    conn  = get_connection()
    cur   = conn.cursor()
    where = []
    params = []

    if sumber:
        where.append("sumber_website = ?")
        params.append(sumber)

    if jenjang:
        # Cari jenjang di dalam JSON array yang disimpan sebagai string
        where.append("jenjang LIKE ?")
        params.append(f'%"{jenjang}"%')

    if lokasi:
        where.append("lokasi LIKE ?")
        params.append(f'%{lokasi}%')

    if keyword:
        where.append("(nama_beasiswa LIKE ? OR penyelenggara LIKE ?)")
        params += [f'%{keyword}%', f'%{keyword}%']

    sql = "SELECT * FROM beasiswa"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY dibuat_pada DESC LIMIT ? OFFSET ?"
    params += [limit, offset]

    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def ambil_beasiswa_by_id(beasiswa_id: int) -> dict | None:
    """Ambil satu beasiswa berdasarkan ID."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM beasiswa WHERE id = ?", (beasiswa_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def ambil_beasiswa_json(beasiswa_id: int) -> dict | None:
    """
    Ambil data lengkap beasiswa dari kolom data_json.
    Return dict Python (hasil json.loads), atau None jika tidak ditemukan.
    """
    row = ambil_beasiswa_by_id(beasiswa_id)
    if not row:
        return None
    try:
        return json.loads(row['data_json'])
    except (json.JSONDecodeError, KeyError):
        return row


def hitung_beasiswa(sumber: str = None) -> int:
    """Hitung jumlah beasiswa. Opsional filter by sumber_website."""
    conn = get_connection()
    cur  = conn.cursor()
    if sumber:
        cur.execute("SELECT COUNT(*) FROM beasiswa WHERE sumber_website = ?", (sumber,))
    else:
        cur.execute("SELECT COUNT(*) FROM beasiswa")
    count = cur.fetchone()[0]
    conn.close()
    return count


def hapus_beasiswa(beasiswa_id: int) -> tuple[bool, str]:
    """Hapus satu beasiswa berdasarkan ID."""
    try:
        conn = get_connection()
        conn.execute("DELETE FROM beasiswa WHERE id = ?", (beasiswa_id,))
        conn.commit()
        conn.close()
        return True, "Beasiswa berhasil dihapus."
    except Exception as e:
        return False, str(e)


def hapus_semua_by_sumber(sumber_website: str) -> tuple[bool, str, int]:
    """
    Hapus semua beasiswa dari satu sumber website.
    Berguna saat ingin refresh data dari awal.
    Return: (sukses, pesan, jumlah_dihapus)
    """
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("DELETE FROM beasiswa WHERE sumber_website = ?", (sumber_website,))
        jumlah = cur.rowcount
        conn.commit()
        conn.close()
        return True, f"{jumlah} beasiswa dari '{sumber_website}' dihapus.", jumlah
    except Exception as e:
        return False, str(e), 0


# ─── Scraping Log ─────────────────────────────────────────────────────────────

def catat_log_scraping(
    sumber_website: str,
    jumlah_baru: int,
    jumlah_update: int,
    jumlah_gagal: int,
    durasi_detik: float = None,
    keterangan: str = None
) -> int:
    """
    Catat satu sesi scraping ke tabel scraping_log.
    Return: id log yang baru dibuat
    """
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            INSERT INTO scraping_log
                (sumber_website, jumlah_baru, jumlah_update, jumlah_gagal, durasi_detik, keterangan)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (sumber_website, jumlah_baru, jumlah_update, jumlah_gagal, durasi_detik, keterangan))
        log_id = cur.lastrowid
        conn.commit()
        conn.close()
        return log_id
    except Exception as e:
        logger.error(f"Gagal catat log scraping: {e}")
        return -1


def ambil_log_scraping(limit: int = 50) -> list[dict]:
    """Ambil riwayat sesi scraping terbaru."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        "SELECT * FROM scraping_log ORDER BY dibuat_pada DESC LIMIT ?",
        (limit,)
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def ambil_audit_log_scraping(
    sumber_website: str = None,
    event_type: str = None,
    sesi_scraping_id: int = None,
    limit: int = 100,
    offset: int = 0
) -> list[dict]:
    """
    Ambil audit log scraping dengan filter opsional.
    Berguna untuk review activity admin & compliance tracking.

    Args:
        sumber_website  : filter by sumber_website
        event_type      : filter by event_type ('SCRAPE_START', 'BACKUP_BOOKMARK', dll)
        sesi_scraping_id: filter by sesi_scraping_id
        limit, offset   : pagination

    Returns:
        list of dict dari tabel scraping_audit_log
    """
    conn = get_connection()
    cur = conn.cursor()

    where = []
    params = []

    if sumber_website:
        where.append("sumber_website = ?")
        params.append(sumber_website)

    if event_type:
        where.append("event_type = ?")
        params.append(event_type)

    if sesi_scraping_id:
        where.append("sesi_scraping_id = ?")
        params.append(sesi_scraping_id)

    sql = "SELECT * FROM scraping_audit_log"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY dibuat_pada DESC LIMIT ? OFFSET ?"
    params += [limit, offset]

    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()

    result = []
    for row in rows:
        r = dict(row)
        # Parse JSON detail jika ada
        if r.get('data_detail'):
            try:
                r['data_detail'] = json.loads(r['data_detail'])
            except (json.JSONDecodeError, TypeError):
                pass
        result.append(r)

    return result


def ambil_dedup_log_scraping(
    sumber_website: str = None,
    status_duplikasi: str = None,
    sesi_scraping_id: int = None,
    limit: int = 100,
    offset: int = 0
) -> list[dict]:
    """
    Ambil deduplication log dengan filter opsional.
    Berguna untuk analisis duplikasi & data quality.

    Args:
        sumber_website  : filter by sumber_website
        status_duplikasi: filter by status ('EXACT_DUPLICATE', 'HASH_MATCH', 'NEW', dll)
        sesi_scraping_id: filter by sesi_scraping_id
        limit, offset   : pagination

    Returns:
        list of dict dari tabel scraping_dedup_log
    """
    conn = get_connection()
    cur = conn.cursor()

    where = []
    params = []

    if sumber_website:
        where.append("sumber_website = ?")
        params.append(sumber_website)

    if status_duplikasi:
        where.append("status_duplikasi = ?")
        params.append(status_duplikasi)

    if sesi_scraping_id:
        where.append("sesi_scraping_id = ?")
        params.append(sesi_scraping_id)

    sql = "SELECT * FROM scraping_dedup_log"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY dibuat_pada DESC LIMIT ? OFFSET ?"
    params += [limit, offset]

    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()

    return [dict(r) for r in rows]


def get_scraping_stats(sesi_scraping_id: int = None) -> dict:
    """
    Dapatkan statistik lengkap dari satu sesi scraping.
    Berguna untuk dashboard admin.

    Args:
        sesi_scraping_id: id dari scraping_log (jika None, gunakan sesi terbaru)

    Returns:
        dict dengan detail stats
    """
    conn = get_connection()
    cur = conn.cursor()

    if not sesi_scraping_id:
        # Ambil sesi scraping terbaru
        cur.execute("SELECT id FROM scraping_log ORDER BY dibuat_pada DESC LIMIT 1")
        row = cur.fetchone()
        if not row:
            conn.close()
            return {}
        sesi_scraping_id = row[0]

    # Ambil info scraping_log
    cur.execute("SELECT * FROM scraping_log WHERE id = ?", (sesi_scraping_id,))
    sesi_row = cur.fetchone()
    if not sesi_row:
        conn.close()
        return {}

    sesi_info = dict(sesi_row)

    # Hitung dedup stats
    cur.execute("""
        SELECT status_duplikasi, COUNT(*) as count
        FROM scraping_dedup_log
        WHERE sesi_scraping_id = ?
        GROUP BY status_duplikasi
    """, (sesi_scraping_id,))
    dedup_rows = cur.fetchall()
    dedup_stats = {row[0]: row[1] for row in dedup_rows}

    # Hitung audit events
    cur.execute("""
        SELECT event_type, COUNT(*) as count, 
               SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) as success_count
        FROM scraping_audit_log
        WHERE sesi_scraping_id = ?
        GROUP BY event_type
    """, (sesi_scraping_id,))
    audit_rows = cur.fetchall()
    audit_stats = {}
    for row in audit_rows:
        audit_stats[row[0]] = {'total': row[1], 'success': row[2]}

    conn.close()

    return {
        'sesi_id': sesi_scraping_id,
        'sesi_info': sesi_info,
        'dedup_stats': dedup_stats,
        'audit_stats': audit_stats,
    }


# ─── Export JSON ──────────────────────────────────────────────────────────────

def export_beasiswa_ke_json(
    path_output: str,
    sumber: str = None,
    jenjang: str = None,
    keyword: str = None
) -> tuple[bool, str, int]:
    """
    Export beasiswa dari database ke file JSON.

    Args:
        path_output : path file output, mis: 'hasil_beasiswa.json'
        sumber      : filter sumber_website (opsional)
        jenjang     : filter jenjang (opsional)
        keyword     : filter keyword nama/penyelenggara (opsional)

    Returns:
        (sukses, pesan, jumlah_diekspor)
    """
    try:
        rows = ambil_semua_beasiswa(
            sumber=sumber, jenjang=jenjang, keyword=keyword, limit=10000
        )

        # Konversi kolom JSON string kembali ke list Python
        for row in rows:
            for field in ('jenjang', 'jurusan', 'kategori_raw'):
                if row.get(field):
                    try:
                        row[field] = json.loads(row[field])
                    except (json.JSONDecodeError, TypeError):
                        pass

        output = {
            'meta': {
                'total'       : len(rows),
                'diekspor_pada': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'filter'      : {
                    'sumber' : sumber,
                    'jenjang': jenjang,
                    'keyword': keyword,
                }
            },
            'data': rows
        }

        with open(path_output, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2, default=str)

        return True, f"Berhasil ekspor {len(rows)} beasiswa ke {path_output}", len(rows)

    except Exception as e:
        logger.error(f"Gagal export JSON: {e}")
        return False, str(e), 0


# ─── Fungsi Integrasi (dipanggil setelah scraping selesai) ───────────────────

def simpan_hasil_scraping(
    hasil: list[dict],
    sumber_website: str,
    durasi_detik: float = None,
    progress_callback=None
) -> tuple[int, int, int]:
    """
    Fungsi utama yang dipanggil setelah jalankan_scraper_*() selesai.
    Menyimpan seluruh hasil ke database dan mencatat log.

    Contoh penggunaan:
        hasil = jalankan_scraper_beasiswaid(...)
        baru, update, gagal = simpan_hasil_scraping(
            hasil, 'beasiswa.id', durasi_detik=120.5
        )

    Args:
        hasil           : list of dict hasil normalize_beasiswa()
        sumber_website  : nama website sumber ('indbeasiswa.com', 'beasiswa.id', dll.)
        durasi_detik    : opsional, durasi scraping untuk dicatat ke log
        progress_callback: callable(str) opsional

    Returns:
        (jumlah_baru, jumlah_update, jumlah_gagal)
    """
    if not hasil:
        if progress_callback:
            progress_callback("Tidak ada data untuk disimpan.")
        return 0, 0, 0

    if progress_callback:
        progress_callback(f"Menyimpan {len(hasil)} beasiswa ke database...")

    baru, update, gagal = simpan_beasiswa_batch(hasil, progress_callback)

    # Catat ke log
    catat_log_scraping(
        sumber_website=sumber_website,
        jumlah_baru=baru,
        jumlah_update=update,
        jumlah_gagal=gagal,
        durasi_detik=durasi_detik,
        keterangan=f"Scraping selesai. Total input: {len(hasil)}."
    )

    if progress_callback:
        progress_callback(
            f"Database diperbarui: {baru} baru, {update} diperbarui, {gagal} gagal."
        )

    return baru, update, gagal


# ─── Inisialisasi otomatis saat modul diimport ───────────────────────────────
# Tabel dibuat jika belum ada, aman dipanggil setiap startup aplikasi
init_beasiswa_db()


# ─── Testing langsung ─────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("=== Test database_beasiswa.py ===\n")

    # Contoh data dummy untuk testing
    dummy = [
        {
            'nama_beasiswa'  : 'Beasiswa LPDP 2026',
            'penyelenggara'  : 'Kementerian Keuangan RI',
            'jenjang'        : ['S2', 'S3'],
            'jurusan'        : ['Semua Jurusan'],
            'lokasi'         : 'Indonesia & Luar Negeri',
            'tipe_beasiswa'  : 'Dalam Negeri',
            'deadline'       : '2026-06-30',
            'deadline_text'  : '30 Juni 2026',
            'cakupan_beasiswa': 'Biaya kuliah penuh, biaya hidup, tunjangan buku',
            'syarat_utama'   : 'WNI, IPK min 3.0, usia max 35 tahun',
            'ipk_minimal'    : 3.0,
            'url_sumber'     : 'https://lpdp.kemenkeu.go.id/beasiswa-reguler',
            'url_resmi'      : 'https://lpdp.kemenkeu.go.id',
            'sumber_website' : 'indbeasiswa.com',
            'kategori_raw'   : ['Beasiswa Pemerintah'],
        },
        {
            'nama_beasiswa'  : 'Beasiswa MEXT Jepang S1 2026',
            'penyelenggara'  : 'Kementerian Pendidikan Jepang (MEXT)',
            'jenjang'        : ['S1'],
            'jurusan'        : ['Semua Jurusan'],
            'lokasi'         : 'Jepang',
            'tipe_beasiswa'  : 'Luar Negeri',
            'deadline'       : '2026-05-15',
            'deadline_text'  : 'Mei 2026',
            'cakupan_beasiswa': 'Biaya kuliah, tiket PP, tunjangan bulanan JPY 117.000',
            'syarat_utama'   : 'Lulusan SMA/sederajat, usia 17-25 tahun',
            'ipk_minimal'    : None,
            'url_sumber'     : 'https://cari.scholarship.or.id/listing/beasiswa-mext-s1-2026/',
            'url_resmi'      : 'https://www.id.emb-japan.go.jp',
            'sumber_website' : 'scholarship.or.id',
            'kategori_raw'   : ['Beasiswa Internasional'],
        },
    ]

    baru, update, gagal = simpan_hasil_scraping(
        dummy,
        sumber_website='test',
        durasi_detik=5.0,
        progress_callback=lambda m: print(f"  [DB] {m}")
    )
    print(f"\nHasil simpan: baru={baru}, update={update}, gagal={gagal}")

    total = hitung_beasiswa()
    print(f"Total beasiswa di DB: {total}")

    semua = ambil_semua_beasiswa(limit=5)
    print(f"\nContoh 5 data pertama:")
    for b in semua:
        print(f"  [{b['id']}] {b['nama_beasiswa'][:60]} | {b['sumber_website']} | {b['deadline']}")

    # Export ke JSON
    ok, pesan, jumlah = export_beasiswa_ke_json('test_export.json')
    print(f"\nExport: {pesan}")
