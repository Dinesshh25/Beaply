"""
models/beasiswa_model.py
Beaply - Model: Data Beasiswa & Bookmark

CRUD SQLite untuk tabel beasiswa dan bookmark_beasiswa.
Digabungkan dari: Eksplorasi_dan_Navigasi/eksplorasi_database.py + eksplorasi_utils.py
"""

import json
import os
from datetime import datetime

from models.database import get_connection


# ════════════════════════════════════════════════════════════
# INISIALISASI TABEL
# ════════════════════════════════════════════════════════════

def init_beasiswa_db():
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
    seed_beasiswa()
    _buat_index()


def _buat_index():
    """Buat index pada kolom yang sering di-query untuk performa optimal."""
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("CREATE INDEX IF NOT EXISTS idx_beasiswa_nama     ON beasiswa(nama)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_beasiswa_deadline ON beasiswa(deadline)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_beasiswa_jenjang  ON beasiswa(jenjang)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_beasiswa_kategori ON beasiswa(kategori)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_bookmark_profil   ON bookmark_beasiswa(profil_id)")
    conn.commit()
    conn.close()


def seed_beasiswa():
    """Load data beasiswa dari beasiswa.json jika tabel masih kosong."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as cnt FROM beasiswa")
    row = cur.fetchone()
    if row and row["cnt"] > 0:
        conn.close()
        return

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
        region = bea.get("region", "")
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
            pass

    conn.commit()
    conn.close()


# ════════════════════════════════════════════════════════════
# CRUD — BEASISWA
# ════════════════════════════════════════════════════════════

def ambil_semua_beasiswa() -> list:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM beasiswa
        ORDER BY CASE WHEN deadline IS NULL THEN 1 ELSE 0 END, deadline ASC
    """)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def cari_beasiswa(keyword: str) -> list:
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
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM beasiswa WHERE id = ?", (beasiswa_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def ambil_nama_beasiswa_list() -> list:
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
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id FROM bookmark_beasiswa WHERE profil_id = ? AND beasiswa_id = ?
        """, (profil_id, beasiswa_id))
        existing = cur.fetchone()

        if existing:
            cur.execute("DELETE FROM bookmark_beasiswa WHERE id = ?", (existing["id"],))
            conn.commit()
            conn.close()
            return True, "Bookmark dihapus.", False
        else:
            cur.execute("""
                INSERT INTO bookmark_beasiswa (profil_id, beasiswa_id) VALUES (?, ?)
            """, (profil_id, beasiswa_id))
            conn.commit()
            conn.close()
            return True, "Beasiswa di-bookmark.", True
    except Exception as e:
        return False, str(e), False


def ambil_bookmark(profil_id: int) -> list:
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
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 1 FROM bookmark_beasiswa WHERE profil_id = ? AND beasiswa_id = ?
    """, (profil_id, beasiswa_id))
    row = cur.fetchone()
    conn.close()
    return row is not None


# ════════════════════════════════════════════════════════════
# UTILS — FORMAT & KONSTANTA (dari eksplorasi_utils.py)
# ════════════════════════════════════════════════════════════

KATEGORI_VALID = ("pemerintah", "swasta", "internasional")
JENJANG_VALID = ("S1", "S2", "S3")
SORT_VALID = ("nama_asc", "nama_desc", "deadline_asc", "deadline_desc", "ipk_asc", "ipk_desc")

KATEGORI_LABEL = {
    "id": {"pemerintah": "🏛 Pemerintah", "swasta": "🏢 Swasta", "internasional": "🌍 Internasional"},
    "en": {"pemerintah": "🏛 Government", "swasta": "🏢 Private", "internasional": "🌍 International"},
}
KATEGORI_COLOR = {"pemerintah": "#3B82F6", "swasta": "#8B5CF6", "internasional": "#10B981"}


def normalisasi_keyword(keyword: str) -> str:
    if not keyword:
        return ""
    return keyword.strip().lower()


def validasi_filter(kriteria: dict) -> tuple:
    kategori = kriteria.get("kategori")
    if kategori and kategori not in KATEGORI_VALID:
        return False, f"Kategori harus: {', '.join(KATEGORI_VALID)}"
    jenjang = kriteria.get("jenjang")
    if jenjang and jenjang not in JENJANG_VALID:
        return False, f"Jenjang harus: {', '.join(JENJANG_VALID)}"
    ipk_min = kriteria.get("ipk_min")
    if ipk_min is not None:
        try:
            val = float(ipk_min)
            if val < 0 or val > 4.0:
                return False, "IPK min harus 0.00 - 4.00"
        except (ValueError, TypeError):
            return False, "IPK min harus berupa angka."
    return True, ""


def format_kategori(kategori: str, bhs: str = "id") -> str:
    return KATEGORI_LABEL.get(bhs, KATEGORI_LABEL["id"]).get(kategori, kategori)


def warna_kategori(kategori: str) -> str:
    return KATEGORI_COLOR.get(kategori, "#6B7280")


def format_deadline_beasiswa(deadline_str: str) -> str:
    if not deadline_str:
        return "Tidak ada deadline"
    bulan_id = ["", "Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
                "Jul", "Ags", "Sep", "Okt", "Nov", "Des"]
    try:
        d = datetime.strptime(deadline_str, "%Y-%m-%d")
        now = datetime.now()
        selisih = (d.date() - now.date()).days
        tgl = f"{d.day} {bulan_id[d.month]} {d.year}"
        if selisih < 0:
            return f"{tgl} (Ditutup)"
        elif selisih <= 7:
            return f"{tgl} (⚠ {selisih} hari lagi)"
        elif selisih <= 30:
            return f"{tgl} ({selisih} hari lagi)"
        else:
            return tgl
    except ValueError:
        return deadline_str


def format_syarat_singkat(beasiswa: dict) -> str:
    parts = []
    if beasiswa.get("syarat_ipk") and beasiswa["syarat_ipk"] > 0:
        parts.append(f"IPK ≥ {beasiswa['syarat_ipk']:.1f}")
    if beasiswa.get("syarat_toefl") and beasiswa["syarat_toefl"] > 0:
        parts.append(f"TOEFL ≥ {beasiswa['syarat_toefl']}")
    if beasiswa.get("syarat_ielts") and beasiswa["syarat_ielts"] > 0:
        parts.append(f"IELTS ≥ {beasiswa['syarat_ielts']:.1f}")
    return " • ".join(parts) if parts else "Tidak ada syarat khusus"
