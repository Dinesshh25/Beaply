"""
models/profil_model.py
Beaply - Model: Profil Mahasiswa & Preferensi

CRUD SQLite untuk tabel profil dan preferensi.
Digabungkan dari: database.py (profil parts)
"""

from models.database import get_connection


# ════════════════════════════════════════════════════════════
# INISIALISASI TABEL
# ════════════════════════════════════════════════════════════

def init_profil_db():
    """Buat tabel profil dan preferensi jika belum ada."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS profil (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         TEXT,
            nama            TEXT    NOT NULL,
            tanggal_lahir   TEXT    NOT NULL,
            email           TEXT    NOT NULL,
            jurusan         TEXT    NOT NULL,
            kampus          TEXT    NOT NULL,
            semester        INTEGER NOT NULL,
            ip              REAL    NOT NULL,
            jenjang         TEXT    NOT NULL,
            jenis_kelamin   TEXT    NOT NULL,
            status_kip      INTEGER DEFAULT 0,
            skor_ielts      REAL,
            skor_toefl      INTEGER,
            skor_duolingo   INTEGER,
            skor_sat        INTEGER,
            skor_act        INTEGER,
            skor_gre        INTEGER,
            skor_gmat       INTEGER,
            skor_hsk        INTEGER,
            level_jlpt      TEXT,
            dibuat_pada     TEXT DEFAULT (datetime('now','localtime')),
            diupdate_pada   TEXT DEFAULT (datetime('now','localtime'))
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS preferensi (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            id_profil   INTEGER NOT NULL UNIQUE,
            tema        TEXT    DEFAULT 'light',
            ukuran_teks TEXT    DEFAULT 'medium',
            bahasa      TEXT    DEFAULT 'id',
            FOREIGN KEY (id_profil) REFERENCES profil(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


# ════════════════════════════════════════════════════════════
# CRUD — PROFIL
# ════════════════════════════════════════════════════════════

def simpan_profil_db(data: dict) -> tuple[bool, str, int]:
    """
    Insert profil baru ke database.
    Return: (sukses, pesan, id_profil)
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cols = [
            "user_id", "nama", "tanggal_lahir", "email", "jurusan",
            "kampus", "semester", "ip", "jenjang", "jenis_kelamin",
            "status_kip", "skor_ielts", "skor_toefl", "skor_duolingo",
            "skor_sat", "skor_act", "skor_gre", "skor_gmat",
            "skor_hsk", "level_jlpt",
        ]
        placeholders = ", ".join("?" for _ in cols)
        col_names = ", ".join(cols)
        values = [data.get(c) for c in cols]

        cur.execute(
            f"INSERT INTO profil ({col_names}) VALUES ({placeholders})",
            values,
        )
        pid = cur.lastrowid
        conn.commit()
        conn.close()
        return True, "Profil berhasil disimpan.", pid
    except Exception as e:
        return False, str(e), -1


def ambil_profil_db(profil_id: int) -> dict | None:
    """Ambil satu profil berdasarkan ID."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM profil WHERE id = ?", (profil_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def ambil_semua_profil_db(user_id: str = None) -> list[dict]:
    """Ambil semua profil (opsional: filter by user_id)."""
    conn = get_connection()
    cur = conn.cursor()
    if user_id:
        cur.execute(
            "SELECT * FROM profil WHERE user_id = ? ORDER BY dibuat_pada DESC",
            (user_id,),
        )
    else:
        cur.execute("SELECT * FROM profil ORDER BY dibuat_pada DESC")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_profil_db(profil_id: int, data: dict) -> tuple[bool, str]:
    """Update data profil."""
    try:
        conn = get_connection()
        set_clause = ", ".join(f"{k} = ?" for k in data)
        vals = list(data.values()) + [profil_id]
        conn.execute(
            f"UPDATE profil SET {set_clause}, diupdate_pada = datetime('now','localtime') WHERE id = ?",
            vals,
        )
        conn.commit()
        conn.close()
        return True, "Profil diperbarui."
    except Exception as e:
        return False, str(e)


def hapus_profil_db(profil_id: int) -> tuple[bool, str]:
    """Hapus profil dan data terkait (via CASCADE)."""
    try:
        conn = get_connection()
        conn.execute("DELETE FROM profil WHERE id = ?", (profil_id,))
        conn.commit()
        conn.close()
        return True, "Profil dihapus."
    except Exception as e:
        return False, str(e)


# ════════════════════════════════════════════════════════════
# CRUD — PREFERENSI
# ════════════════════════════════════════════════════════════

def ambil_preferensi_db(profil_id: int) -> dict:
    """Ambil preferensi profil. Return default jika belum ada."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM preferensi WHERE id_profil = ?", (profil_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return dict(row)
    return {"tema": "light", "ukuran_teks": "medium", "bahasa": "id"}


def simpan_preferensi_db(profil_id: int, preferensi: dict) -> tuple[bool, str]:
    """Upsert preferensi tampilan."""
    try:
        conn = get_connection()
        conn.execute("""
            INSERT INTO preferensi (id_profil, tema, ukuran_teks, bahasa)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id_profil) DO UPDATE SET
                tema = excluded.tema,
                ukuran_teks = excluded.ukuran_teks,
                bahasa = excluded.bahasa
        """, (
            profil_id,
            preferensi.get("tema", "light"),
            preferensi.get("ukuran_teks", "medium"),
            preferensi.get("bahasa", "id"),
        ))
        conn.commit()
        conn.close()
        return True, "Preferensi tersimpan."
    except Exception as e:
        return False, str(e)


def ganti_password_db(profil_id: int, new_pass: str) -> tuple[bool, str]:
    """Ganti password — placeholder (actual password logic is in auth_model)."""
    # Implementasi sebenarnya ada di auth_model
    return True, "Password berhasil diubah."
