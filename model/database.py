"""
database.py
Beaply - Manajemen koneksi dan skema SQLite
"""

import sqlite3
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "beaply.db"))


def get_connection():
    """Buka koneksi ke database SQLite dengan foreign keys aktif."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Buat semua tabel kalau belum ada."""
    conn = get_connection()
    cur = conn.cursor()

    # ── Tabel user (akun login) ────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id_user     INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT    NOT NULL UNIQUE,
            password    TEXT    NOT NULL,
            email       TEXT    NOT NULL UNIQUE,
            role        TEXT    NOT NULL DEFAULT 'mahasiswa'
        )
    """)

    # ── Tabel profile (data akademik mahasiswa) ─────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS profile (
            id_profile      INTEGER PRIMARY KEY AUTOINCREMENT,
            id_user         INTEGER NOT NULL UNIQUE,
            nama            TEXT    NOT NULL,
            tanggal_lahir   TEXT    NOT NULL,
            jurusan         TEXT    NOT NULL,
            kampus          TEXT    NOT NULL,
            ipk             REAL    NOT NULL,
            jenjang         TEXT    NOT NULL,
            semester        INTEGER NOT NULL,
            jenis_kelamin   TEXT    NOT NULL,
            status_kip      INTEGER NOT NULL DEFAULT 0,
            skor_ielts      REAL    DEFAULT NULL,
            skor_toefl      INTEGER DEFAULT NULL,
            skor_duolingo   INTEGER DEFAULT NULL,
            skor_sat        INTEGER DEFAULT NULL,
            skor_act        INTEGER DEFAULT NULL,
            skor_gre        INTEGER DEFAULT NULL,
            skor_gmat       INTEGER DEFAULT NULL,
            skor_hsk        INTEGER DEFAULT NULL,
            level_jlpt      TEXT    DEFAULT NULL,
            FOREIGN KEY (id_user) REFERENCES user(id_user) ON DELETE CASCADE
        )
    """)

    # ── Tabel beasiswa ──────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS beasiswa (
            id_beasiswa         INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_beasiswa       TEXT    NOT NULL,
            nama_penyelenggara  TEXT    NOT NULL,
            deskripsi           TEXT    DEFAULT NULL,
            deadline            TEXT    DEFAULT NULL,
            lokasi              TEXT    DEFAULT NULL,
            jenjang             TEXT    DEFAULT NULL,
            ipk_minimal         REAL    DEFAULT NULL,
            url_sumber          TEXT    DEFAULT NULL,
            kategori            TEXT    DEFAULT NULL,
            tipe_beasiswa       TEXT    DEFAULT NULL
        )
    """)

    # ── Tabel bookmarks ─────────────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bookmarks (
            id_bookmark     INTEGER PRIMARY KEY AUTOINCREMENT,
            id_user         INTEGER NOT NULL,
            id_beasiswa     INTEGER NOT NULL,
            UNIQUE (id_user, id_beasiswa),
            FOREIGN KEY (id_user)     REFERENCES user(id_user)         ON DELETE CASCADE,
            FOREIGN KEY (id_beasiswa) REFERENCES beasiswa(id_beasiswa) ON DELETE CASCADE
        )
    """)

    # ── Tabel preferensi tampilan ────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS preferensi (
            id_preferensi   INTEGER PRIMARY KEY AUTOINCREMENT,
            id_user         INTEGER NOT NULL UNIQUE,
            tema            TEXT    NOT NULL DEFAULT 'light',
            ukuran_teks     TEXT    NOT NULL DEFAULT 'medium',
            bahasa          TEXT    NOT NULL DEFAULT 'id',
            FOREIGN KEY (id_user) REFERENCES user(id_user) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


# ══════════════════════════════════════════════════════════════
# CRUD User
# ══════════════════════════════════════════════════════════════

def simpan_user_db(data: dict) -> tuple[bool, str, int]:
    """
    Insert user baru ke database.
    Return: (sukses, pesan, id_user)
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO user (username, password, email, role)
            VALUES (:username, :password, :email, :role)
        """, data)
        user_id = cur.lastrowid
        # buat preferensi default otomatis
        cur.execute("INSERT OR IGNORE INTO preferensi (id_user) VALUES (?)", (user_id,))
        conn.commit()
        conn.close()
        return True, "User berhasil didaftarkan.", user_id
    except sqlite3.IntegrityError:
        return False, "Username atau email sudah terdaftar.", -1
    except Exception as e:
        return False, str(e), -1


def ambil_user_db(id_user: int) -> dict | None:
    """Ambil satu user berdasarkan id_user."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM user WHERE id_user = ?", (id_user,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def ambil_user_by_username_db(username: str) -> dict | None:
    """Ambil user berdasarkan username (untuk login)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM user WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def ganti_password_db(id_user: int, password_baru: str) -> tuple[bool, str]:
    """Update password user."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE user SET password = ? WHERE id_user = ?", (password_baru, id_user))
        conn.commit()
        conn.close()
        return True, "Password berhasil diubah."
    except Exception as e:
        return False, str(e)


def hapus_user_db(id_user: int) -> tuple[bool, str]:
    """Hapus user beserta semua data terkait via CASCADE."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM user WHERE id_user = ?", (id_user,))
        conn.commit()
        conn.close()
        return True, "Akun berhasil dihapus."
    except Exception as e:
        return False, str(e)


# ══════════════════════════════════════════════════════════════
# CRUD Profile
# ══════════════════════════════════════════════════════════════

def simpan_profile_db(data: dict) -> tuple[bool, str, int]:
    """
    Insert profile baru.
    Return: (sukses, pesan, id_profile)
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO profile (
                id_user, nama, tanggal_lahir, jurusan, kampus,
                ipk, jenjang, semester, jenis_kelamin, status_kip,
                skor_ielts, skor_toefl, skor_duolingo,
                skor_sat, skor_act, skor_gre, skor_gmat,
                skor_hsk, level_jlpt
            ) VALUES (
                :id_user, :nama, :tanggal_lahir, :jurusan, :kampus,
                :ipk, :jenjang, :semester, :jenis_kelamin, :status_kip,
                :skor_ielts, :skor_toefl, :skor_duolingo,
                :skor_sat, :skor_act, :skor_gre, :skor_gmat,
                :skor_hsk, :level_jlpt
            )
        """, data)
        profile_id = cur.lastrowid
        conn.commit()
        conn.close()
        return True, "Profile berhasil disimpan.", profile_id
    except sqlite3.IntegrityError:
        return False, "Profile untuk user ini sudah ada.", -1
    except Exception as e:
        return False, str(e), -1


def ambil_profile_db(id_user: int) -> dict | None:
    """Ambil profile berdasarkan id_user."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM profile WHERE id_user = ?", (id_user,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def update_profile_db(id_user: int, data: dict) -> tuple[bool, str]:
    """Update data profile."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE profile SET
                nama=:nama, tanggal_lahir=:tanggal_lahir,
                jurusan=:jurusan, kampus=:kampus,
                ipk=:ipk, jenjang=:jenjang, semester=:semester,
                jenis_kelamin=:jenis_kelamin, status_kip=:status_kip,
                skor_ielts=:skor_ielts, skor_toefl=:skor_toefl,
                skor_duolingo=:skor_duolingo, skor_sat=:skor_sat,
                skor_act=:skor_act, skor_gre=:skor_gre,
                skor_gmat=:skor_gmat, skor_hsk=:skor_hsk,
                level_jlpt=:level_jlpt
            WHERE id_user=:id_user
        """, {**data, "id_user": id_user})
        conn.commit()
        conn.close()
        return True, "Profile berhasil diperbarui."
    except Exception as e:
        return False, str(e)


# ══════════════════════════════════════════════════════════════
# CRUD Bookmarks
# ══════════════════════════════════════════════════════════════

def tambah_bookmark_db(id_user: int, id_beasiswa: int) -> tuple[bool, str]:
    """Tambah bookmark beasiswa untuk user."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO bookmarks (id_user, id_beasiswa)
            VALUES (?, ?)
        """, (id_user, id_beasiswa))
        conn.commit()
        conn.close()
        return True, "Beasiswa berhasil dibookmark."
    except sqlite3.IntegrityError:
        return False, "Beasiswa sudah ada di bookmark."
    except Exception as e:
        return False, str(e)


def hapus_bookmark_db(id_user: int, id_beasiswa: int) -> tuple[bool, str]:
    """Hapus bookmark beasiswa."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            DELETE FROM bookmarks WHERE id_user = ? AND id_beasiswa = ?
        """, (id_user, id_beasiswa))
        conn.commit()
        conn.close()
        return True, "Bookmark berhasil dihapus."
    except Exception as e:
        return False, str(e)


def ambil_bookmarks_db(id_user: int) -> list[dict]:
    """Ambil semua beasiswa yang dibookmark oleh user beserta detailnya."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT b.*, bk.id_bookmark
        FROM bookmarks bk
        JOIN beasiswa b ON bk.id_beasiswa = b.id_beasiswa
        WHERE bk.id_user = ?
    """, (id_user,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def cek_bookmark_db(id_user: int, id_beasiswa: int) -> bool:
    """Cek apakah beasiswa sudah dibookmark oleh user."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 1 FROM bookmarks WHERE id_user = ? AND id_beasiswa = ?
    """, (id_user, id_beasiswa))
    hasil = cur.fetchone()
    conn.close()
    return hasil is not None


# ══════════════════════════════════════════════════════════════
# CRUD Preferensi
# ══════════════════════════════════════════════════════════════

def ambil_preferensi_db(id_user: int) -> dict:
    """Ambil preferensi tampilan. Return default kalau belum ada."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM preferensi WHERE id_user = ?", (id_user,))
    row = cur.fetchone()
    conn.close()
    if row:
        return dict(row)
    return {"tema": "light", "ukuran_teks": "medium", "bahasa": "id"}


def simpan_preferensi_db(id_user: int, preferensi: dict) -> tuple[bool, str]:
    """Upsert preferensi tampilan."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO preferensi (id_user, tema, ukuran_teks, bahasa)
            VALUES (:id_user, :tema, :ukuran_teks, :bahasa)
            ON CONFLICT(id_user) DO UPDATE SET
                tema        = excluded.tema,
                ukuran_teks = excluded.ukuran_teks,
                bahasa      = excluded.bahasa
        """, {"id_user": id_user, **preferensi})
        conn.commit()
        conn.close()
        return True, "Preferensi tersimpan."
    except Exception as e:
        return False, str(e)


# ══════════════════════════════════════════════════════════════
# CRUD Beasiswa
# ══════════════════════════════════════════════════════════════

def ambil_semua_beasiswa_db() -> list[dict]:
    """Ambil semua beasiswa."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM beasiswa")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def ambil_beasiswa_db(id_beasiswa: int) -> dict | None:
    """Ambil satu beasiswa berdasarkan id."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM beasiswa WHERE id_beasiswa = ?", (id_beasiswa,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def cari_beasiswa_db(keyword: str) -> list[dict]:
    """Cari beasiswa berdasarkan nama atau penyelenggara."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM beasiswa
        WHERE nama_beasiswa LIKE ? OR nama_penyelenggara LIKE ?
    """, (f"%{keyword}%", f"%{keyword}%"))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]