"""
eksplorasi_database.py
Beaply - Manajemen tabel & CRUD SQLite untuk Eksplorasi Data & Navigasi

Tabel:
  - beasiswa           : Data beasiswa (seed)
  - bookmark_beasiswa  : Beasiswa yang di-bookmark user
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "beaply.db")


def get_connection():
    """Buka koneksi ke database SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ════════════════════════════════════════════════════════════
# INISIALISASI TABEL
# ════════════════════════════════════════════════════════════

def init_eksplorasi_db():
    """Buat tabel beasiswa dan bookmark_beasiswa kalau belum ada."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS beasiswa (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            nama            TEXT    NOT NULL,
            penyelenggara   TEXT    NOT NULL,
            jenjang         TEXT    NOT NULL,
            kategori        TEXT    NOT NULL
                            CHECK(kategori IN ('pemerintah','swasta','internasional')),
            deadline        TEXT,
            deskripsi       TEXT    DEFAULT '',
            syarat_ipk      REAL    DEFAULT 0,
            syarat_toefl    INTEGER DEFAULT 0,
            syarat_ielts    REAL    DEFAULT 0,
            url             TEXT    DEFAULT '',
            dibuat_pada     TEXT    DEFAULT (datetime('now','localtime'))
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS bookmark_beasiswa (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            profil_id   INTEGER NOT NULL,
            beasiswa_id INTEGER NOT NULL,
            dibuat_pada TEXT    DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (profil_id)   REFERENCES profil(id)   ON DELETE CASCADE,
            FOREIGN KEY (beasiswa_id) REFERENCES beasiswa(id) ON DELETE CASCADE,
            UNIQUE(profil_id, beasiswa_id)
        )
    """)

    conn.commit()
    conn.close()

    # Seed data jika tabel kosong
    seed_beasiswa()


def seed_beasiswa():
    """Insert data beasiswa sample jika tabel masih kosong."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as cnt FROM beasiswa")
    row = cur.fetchone()
    if row and row["cnt"] > 0:
        conn.close()
        return  # sudah ada data

    data = [
        ("Beasiswa KIP-Kuliah", "Kemendikbud", "S1",
         "pemerintah", "2026-06-30",
         "Bantuan biaya pendidikan bagi mahasiswa tidak mampu secara ekonomi. "
         "Mencakup biaya kuliah, biaya hidup, dan biaya buku.",
         0.0, 0, 0.0,
         "https://kip-kuliah.kemdikbud.go.id"),

        ("Beasiswa LPDP", "Kementerian Keuangan", "S2",
         "pemerintah", "2026-09-30",
         "Beasiswa penuh untuk program magister dan doktoral di dalam "
         "dan luar negeri. Termasuk biaya kuliah, hidup, dan riset.",
         3.0, 0, 0.0,
         "https://lpdp.kemenkeu.go.id"),

        ("Beasiswa LPDP Doktoral", "Kementerian Keuangan", "S3",
         "pemerintah", "2026-09-30",
         "Beasiswa LPDP khusus program doktoral dengan fokus pada "
         "riset dan inovasi strategis nasional.",
         3.25, 0, 0.0,
         "https://lpdp.kemenkeu.go.id"),

        ("Beasiswa Djarum Plus", "Djarum Foundation", "S1",
         "swasta", "2026-05-31",
         "Beasiswa untuk mahasiswa S1 berprestasi semester 4+. "
         "Termasuk soft-skills training dan networking.",
         3.2, 0, 0.0,
         "https://djarum.com/djarum-beasiswa-plus"),

        ("Beasiswa Tanoto Foundation", "Tanoto Foundation", "S1",
         "swasta", "2026-07-15",
         "Beasiswa Leadership untuk pengembangan soft skill dan "
         "program magang di perusahaan Tanoto Group.",
         3.3, 0, 0.0,
         "https://www.tanotofoundation.org"),

        ("Chevening Scholarship", "UK Government", "S2",
         "internasional", "2026-11-03",
         "Beasiswa penuh pemerintah Inggris untuk program master "
         "di universitas top UK. Fully funded.",
         0.0, 0, 6.5,
         "https://www.chevening.org"),

        ("Fulbright Scholarship", "US Government", "S2",
         "internasional", "2026-04-15",
         "Program pertukaran pendidikan AS-Indonesia untuk studi S2 "
         "di universitas terbaik Amerika Serikat.",
         3.0, 80, 0.0,
         "https://www.aminef.or.id"),

        ("Australia Awards (AAS)", "Australian Government", "S2",
         "internasional", "2026-04-30",
         "Beasiswa pemerintah Australia untuk S2 dan S3. "
         "Mencakup biaya kuliah, hidup, dan asuransi.",
         2.9, 0, 6.5,
         "https://www.australiaawardsindonesia.org"),

        ("MEXT Scholarship", "Japan Government", "S2",
         "internasional", "2026-05-20",
         "Beasiswa pemerintah Jepang (Monbukagakusho) untuk studi S2/S3 "
         "di universitas Jepang. Fully funded.",
         3.0, 0, 0.0,
         "https://www.studyinjapan.go.jp"),

        ("Beasiswa BCA Finance", "BCA", "S1",
         "swasta", "2026-08-31",
         "Beasiswa prestasi untuk mahasiswa S1 jurusan ekonomi, "
         "manajemen, akuntansi, dan teknik informatika.",
         3.0, 0, 0.0,
         "https://www.bca.co.id"),

        ("Beasiswa Unggulan Kemendikbud", "Kemendikbud", "S1",
         "pemerintah", "2026-07-31",
         "Beasiswa bagi mahasiswa berprestasi di bidang akademik, "
         "seni, olahraga, dan kebudayaan.",
         3.5, 0, 0.0,
         "https://beasiswaunggulan.kemdikbud.go.id"),

        ("Beasiswa Baznas", "BAZNAS", "S1",
         "pemerintah", "2026-06-30",
         "Beasiswa dari Badan Amil Zakat Nasional untuk mahasiswa "
         "kurang mampu yang berprestasi.",
         3.0, 0, 0.0,
         "https://baznas.go.id"),

        ("Beasiswa Sampoerna Foundation", "Sampoerna Foundation", "S1",
         "swasta", "2026-05-15",
         "Beasiswa untuk mahasiswa S1 dari keluarga kurang mampu "
         "dengan potensi kepemimpinan.",
         3.0, 0, 0.0,
         "https://www.sampoernafoundation.org"),

        ("Erasmus Mundus", "European Commission", "S2",
         "internasional", "2026-01-15",
         "Beasiswa program master joint degree di beberapa universitas "
         "Eropa. Fully funded termasuk travel grant.",
         3.0, 0, 6.0,
         "https://www.eacea.ec.europa.eu"),

        ("GKS (Korean Government)", "Korean Government", "S2",
         "internasional", "2026-03-15",
         "Global Korea Scholarship untuk studi S2/S3 di Korea Selatan. "
         "Termasuk kursus bahasa Korea 1 tahun.",
         2.64, 0, 0.0,
         "https://www.studyinkorea.go.kr"),

        ("Beasiswa CIMB Niaga", "CIMB Niaga", "S1",
         "swasta", "2026-08-15",
         "Beasiswa bagi mahasiswa jurusan ekonomi, bisnis, dan "
         "teknologi informasi yang berprestasi.",
         3.25, 0, 0.0,
         "https://www.cimbniaga.co.id"),
    ]

    for d in data:
        cur.execute("""
            INSERT INTO beasiswa
                (nama, penyelenggara, jenjang, kategori, deadline,
                 deskripsi, syarat_ipk, syarat_toefl, syarat_ielts, url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, d)

    conn.commit()
    conn.close()


# ════════════════════════════════════════════════════════════
# CRUD — BEASISWA
# ════════════════════════════════════════════════════════════

def ambil_semua_beasiswa() -> list:
    """Ambil semua data beasiswa, urut deadline terdekat."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM beasiswa
        ORDER BY
            CASE WHEN deadline IS NULL THEN 1 ELSE 0 END,
            deadline ASC
    """)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def cari_beasiswa(keyword: str) -> list:
    """Cari beasiswa berdasarkan keyword (nama atau penyelenggara)."""
    conn = get_connection()
    cur = conn.cursor()
    like = f"%{keyword.strip()}%"
    cur.execute("""
        SELECT * FROM beasiswa
        WHERE nama LIKE ? OR penyelenggara LIKE ? OR deskripsi LIKE ?
        ORDER BY nama ASC
    """, (like, like, like))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def ambil_beasiswa_by_id(beasiswa_id: int) -> dict | None:
    """Ambil satu beasiswa berdasarkan ID."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM beasiswa WHERE id = ?", (beasiswa_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def ambil_nama_beasiswa_list() -> list:
    """Ambil semua nama beasiswa (untuk autocomplete)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT nama FROM beasiswa ORDER BY nama ASC")
    rows = cur.fetchall()
    conn.close()
    return [r["nama"] for r in rows]


# ════════════════════════════════════════════════════════════
# CRUD — BOOKMARK BEASISWA
# ════════════════════════════════════════════════════════════

def toggle_bookmark(profil_id: int, beasiswa_id: int) -> tuple:
    """
    Toggle bookmark beasiswa.
    Return: (sukses, pesan, is_bookmarked)
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id FROM bookmark_beasiswa
            WHERE profil_id = ? AND beasiswa_id = ?
        """, (profil_id, beasiswa_id))
        existing = cur.fetchone()

        if existing:
            cur.execute("DELETE FROM bookmark_beasiswa WHERE id = ?",
                        (existing["id"],))
            conn.commit()
            conn.close()
            return True, "Bookmark dihapus.", False
        else:
            cur.execute("""
                INSERT INTO bookmark_beasiswa (profil_id, beasiswa_id)
                VALUES (?, ?)
            """, (profil_id, beasiswa_id))
            conn.commit()
            conn.close()
            return True, "Beasiswa di-bookmark.", True
    except Exception as e:
        return False, str(e), False


def ambil_bookmark(profil_id: int) -> list:
    """Ambil semua beasiswa yang di-bookmark user."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT b.*, bk.dibuat_pada as bookmark_pada
        FROM beasiswa b
        JOIN bookmark_beasiswa bk ON b.id = bk.beasiswa_id
        WHERE bk.profil_id = ?
        ORDER BY bk.dibuat_pada DESC
    """, (profil_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def is_bookmarked(profil_id: int, beasiswa_id: int) -> bool:
    """Cek apakah beasiswa di-bookmark user."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 1 FROM bookmark_beasiswa
        WHERE profil_id = ? AND beasiswa_id = ?
    """, (profil_id, beasiswa_id))
    row = cur.fetchone()
    conn.close()
    return row is not None
