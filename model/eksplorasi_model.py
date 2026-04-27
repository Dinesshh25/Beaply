"""
eksplorasi_database.py
Beaply - Manajemen tabel & CRUD SQLite untuk Eksplorasi Data & Navigasi

Tabel:
  - beasiswa           : Data beasiswa (seed)
  - bookmark_beasiswa  : Beasiswa yang di-bookmark user
"""

import json
import os
from datetime import datetime
from model.database import get_connection


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
    """Load data beasiswa dari beasiswa.json jika tabel masih kosong."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as cnt FROM beasiswa")
    row = cur.fetchone()
    if row and row["cnt"] > 0:
        conn.close()
        return

    # Load dari beasiswa.json
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "beasiswa.json")
    if not os.path.exists(json_path):
        conn.close()
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for bea in data.get("beasiswa", []):
        nama = bea.get("nama_beasiswa", "")
        penyelenggara = bea.get("penyelenggara", "") or "Unknown"
        jenjang_list = bea.get("jenjang", [])
        jenjang = ", ".join(jenjang_list) if jenjang_list else "S1"
        deadline = bea.get("deadline")
        deskripsi = bea.get("cakupan_beasiswa", "") or ""
        ipk_min = bea.get("ipk_minimal") or 0.0
        url = bea.get("url_sumber", "")
        # Map kategori to valid CHECK constraint values
        region = bea.get("region", "")
        tipe = bea.get("tipe_beasiswa", "")
        if "Luar Negeri" in region:
            kategori = "internasional"
        elif penyelenggara and any(k in penyelenggara.lower() for k in ["pemerintah", "kementerian", "kemendikbud", "baznas"]):
            kategori = "pemerintah"
        else:
            kategori = "swasta"

        try:
            cur.execute("""
                INSERT INTO beasiswa
                    (nama, penyelenggara, jenjang, kategori, deadline,
                     deskripsi, syarat_ipk, syarat_toefl, syarat_ielts, url)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0, 0.0, ?)
            """, (nama, penyelenggara, jenjang, kategori, deadline,
                  deskripsi, ipk_min, url))
        except Exception:
            pass  # skip duplicates or invalid entries

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
