"""
database_beasiswa.py
Modul database untuk menyimpan hasil scraping beasiswa ke SQLite (beaply.db).

Desain:
  - Tabel `beasiswa`      → data pokok setiap beasiswa (kolom terstruktur + JSON raw)
  - Tabel `scraping_log`  → riwayat setiap sesi scraping (kapan, dari mana, berapa data)

Strategi penyimpanan:
  - Field terstruktur (nama, penyelenggara, jenjang, deadline, dst.) disimpan sebagai
    kolom relasional agar bisa di-query/filter langsung dari GUI.
  - Field array (jenjang, jurusan, kategori_raw) disimpan sebagai JSON string.
  - Seluruh dict hasil scraping juga disimpan di kolom `data_json` sebagai cadangan
    lengkap agar tidak ada informasi yang hilang.
  - Mekanisme UPSERT berdasarkan `url_sumber` → data yang sama tidak duplikat,
    tapi diupdate jika ada versi lebih baru.
"""

import json
import logging
import os
import sqlite3
from datetime import datetime

# ─── Path ke database yang sama dengan beaply.db ─────────────────────────────
# Sesuaikan path ini jika lokasi beaply.db berbeda
DB_PATH = os.path.join(
    r"c:\PROYEK1\Beaply",
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
    Buat tabel `beasiswa` dan `scraping_log` jika belum ada.
    Aman dipanggil berulang kali (idempotent).
    """
    conn = get_connection()
    cur  = conn.cursor()

    # ── Tabel utama beasiswa ──────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS beasiswa (
            id                INTEGER  PRIMARY KEY AUTOINCREMENT,

            -- Identitas & sumber
            nama_beasiswa     TEXT     NOT NULL,
            url_sumber        TEXT     UNIQUE,          -- key deduplikasi
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

    # Commit tabel dulu sebelum migrasi & index
    conn.commit()

    # ── Migrasi: tambah kolom baru jika tabel sudah ada tapi kolom belum ada ──
    # (backward compatible — aman dijalankan berulang kali)
    migrasi_kolom = [
        "ALTER TABLE beasiswa ADD COLUMN url_sumber      TEXT UNIQUE",
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
        conn.commit()
    except sqlite3.OperationalError as e:
        logger.warning(f"Index skip: {e}")

    conn.close()
    logger.info("Tabel beasiswa & scraping_log siap.")


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

    return {
        'nama_beasiswa':    str(entry.get('nama_beasiswa', '')).strip()[:500],
        'url_sumber':       str(entry.get('url_sumber', '')).strip() or None,
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
        'data_json':        json.dumps(entry, ensure_ascii=False, default=str),
    }


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
                cur.execute("SELECT id FROM beasiswa WHERE url_sumber = ?", (url,))
                existing = cur.fetchone()
            else:
                existing = None

            if existing:
                # UPDATE: perbarui semua field kecuali id & dibuat_pada
                cur.execute("""
                    UPDATE beasiswa SET
                        nama_beasiswa    = :nama_beasiswa,
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
                    WHERE url_sumber = :url_sumber
                """, row)
                update += 1
            else:
                # INSERT baru
                cur.execute("""
                    INSERT INTO beasiswa (
                        nama_beasiswa, url_sumber, url_resmi, sumber_website,
                        penyelenggara, jenjang, jurusan, lokasi, tipe_beasiswa,
                        deadline, deadline_text, cakupan_beasiswa, syarat_utama,
                        ipk_minimal, kategori_raw, data_json
                    ) VALUES (
                        :nama_beasiswa, :url_sumber, :url_resmi, :sumber_website,
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
