"""
database.py
Beaply - Manajemen koneksi dan skema SQLite
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "beaply.db")


def get_connection():
    """Buka koneksi ke database SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # hasil query bisa diakses kayak dict
    return conn


def init_db():
    """Buat semua tabel kalau belum ada."""
    conn = get_connection()
    cur = conn.cursor()

    # Inisialisasi tabel modul fitur baru
    from Tracker_dan_Pengingat import init_tracker_db
    from Eksplorasi_dan_Navigasi import init_eksplorasi_db
    from Notifikasi_Terpusat import init_notifikasi_db
    init_tracker_db()
    init_eksplorasi_db()
    init_notifikasi_db()

    # ── Tabel profil mahasiswa ────────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS profil (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            password        TEXT    NOT NULL DEFAULT '123456',
            nama            TEXT    NOT NULL,
            tanggal_lahir   TEXT    NOT NULL,
            email           TEXT    NOT NULL UNIQUE,
            jurusan         TEXT    NOT NULL,
            kampus          TEXT    NOT NULL,
            semester        INTEGER NOT NULL,
            ip              REAL    NOT NULL,
            jenjang         TEXT    NOT NULL,
            jenis_kelamin   TEXT    NOT NULL,
            status_kip      INTEGER DEFAULT 0,
            skor_ielts      REAL    DEFAULT NULL,
            skor_toefl      INTEGER DEFAULT NULL,
            skor_duolingo   INTEGER DEFAULT NULL,
            skor_sat        INTEGER DEFAULT NULL,
            skor_act        INTEGER DEFAULT NULL,
            skor_gre        INTEGER DEFAULT NULL,
            skor_gmat       INTEGER DEFAULT NULL,
            skor_hsk        INTEGER DEFAULT NULL,
            level_jlpt      TEXT    DEFAULT NULL,
            dibuat_pada     TEXT    DEFAULT (datetime('now','localtime')),
            diupdate_pada   TEXT    DEFAULT (datetime('now','localtime'))
        )
    """)

    # Migrasi aman: tambahkan kolom password jika belum ada di tabel profil
    try:
        cur.execute("ALTER TABLE profil ADD COLUMN password TEXT NOT NULL DEFAULT '123456'")
    except sqlite3.OperationalError:
        pass  # Kolom sudah ada
        
    # ── Tabel preferensi tampilan ────────────────────────────
    cur.execute("""
        CREATE TABLE IF NOT EXISTS preferensi (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            id_profil   INTEGER NOT NULL UNIQUE,
            tema        TEXT    NOT NULL DEFAULT 'light',
            ukuran_teks TEXT    NOT NULL DEFAULT 'medium',
            bahasa      TEXT    NOT NULL DEFAULT 'id',
            FOREIGN KEY (id_profil) REFERENCES profil(id) ON DELETE CASCADE
        )
    """)

    # Migrasi: tambah kolom user_id jika belum ada (backward compatible)
    try:
        cur.execute("ALTER TABLE profil ADD COLUMN user_id TEXT DEFAULT NULL")
    except sqlite3.OperationalError:
        pass  # kolom sudah ada

    conn.commit()
    conn.close()


# ── CRUD Profil ───────────────────────────────────────────────

def simpan_profil_db(data: dict) -> tuple[bool, str, int]:
    """
    Insert profil baru ke database.
    Return: (sukses, pesan, id_profil)
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO profil (
                password, nama, tanggal_lahir, email, jurusan, kampus,
                semester, ip, jenjang, jenis_kelamin,
                status_kip, skor_ielts, skor_toefl, skor_duolingo,
                skor_sat, skor_act, skor_gre, skor_gmat,
                skor_hsk, level_jlpt
            ) VALUES (
                :password, :nama, :tanggal_lahir, :email, :jurusan, :kampus,
                :semester, :ip, :jenjang, :jenis_kelamin,
                :status_kip, :skor_ielts, :skor_toefl, :skor_duolingo,
                :skor_sat, :skor_act, :skor_gre, :skor_gmat,
                :skor_hsk, :level_jlpt
            )
        """, data)
        profil_id = cur.lastrowid
        # buat preferensi default
        cur.execute("""
            INSERT OR IGNORE INTO preferensi (id_profil) VALUES (?)
        """, (profil_id,))
        conn.commit()
        conn.close()
        return True, "Profil berhasil disimpan.", profil_id
    except sqlite3.IntegrityError:
        return False, "Email sudah terdaftar.", -1
    except Exception as e:
        return False, str(e), -1


def ambil_profil_db(profil_id: int) -> dict | None:
    """Ambil satu profil berdasarkan id."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM profil WHERE id = ?", (profil_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def ambil_semua_profil_db(user_id: str = None) -> list[dict]:
    """Ambil semua profil, opsional filter by user_id."""
    conn = get_connection()
    cur = conn.cursor()
    if user_id:
        cur.execute("SELECT * FROM profil WHERE user_id = ? ORDER BY dibuat_pada DESC", (user_id,))
    else:
        cur.execute("SELECT * FROM profil ORDER BY dibuat_pada DESC")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_profil_db(profil_id: int, data: dict) -> tuple[bool, str]:
    """Update data profil yang sudah ada."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE profil SET
                nama=:nama, tanggal_lahir=:tanggal_lahir, email=:email,
                jurusan=:jurusan, kampus=:kampus, semester=:semester,
                ip=:ip, jenjang=:jenjang, jenis_kelamin=:jenis_kelamin,
                status_kip=:status_kip, skor_ielts=:skor_ielts,
                skor_toefl=:skor_toefl, skor_duolingo=:skor_duolingo,
                skor_sat=:skor_sat, skor_act=:skor_act,
                skor_gre=:skor_gre, skor_gmat=:skor_gmat,
                skor_hsk=:skor_hsk, level_jlpt=:level_jlpt,
                diupdate_pada=datetime('now','localtime')
            WHERE id=:id
        """, {**data, "id": profil_id})
        conn.commit()
        conn.close()
        return True, "Profil berhasil diperbarui."
    except sqlite3.IntegrityError:
        return False, "Email sudah dipakai akun lain."
    except Exception as e:
        return False, str(e)


def hapus_profil_db(profil_id: int) -> tuple[bool, str]:
    """Hapus profil (dan preferensinya via CASCADE)."""
    try:
        conn = get_connection()
        conn.execute("PRAGMA foreign_keys = ON")
        cur = conn.cursor()
        cur.execute("DELETE FROM profil WHERE id = ?", (profil_id,))
        conn.commit()
        conn.close()
        return True, "Akun berhasil dihapus."
    except Exception as e:
        return False, str(e)


def ganti_password_db(profil_id: int, password_baru: str) -> tuple[bool, str]:
    """Ganti password profil."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE profil SET password = ? WHERE id = ?", (password_baru, profil_id))
        conn.commit()
        conn.close()
        return True, "Password berhasil diubah."
    except Exception as e:
        return False, str(e)


# ── CRUD Preferensi ───────────────────────────────────────────

def ambil_preferensi_db(profil_id: int) -> dict:
    """Ambil preferensi tampilan. Return default kalau belum ada."""
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
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO preferensi (id_profil, tema, ukuran_teks, bahasa)
            VALUES (:id_profil, :tema, :ukuran_teks, :bahasa)
            ON CONFLICT(id_profil) DO UPDATE SET
                tema        = excluded.tema,
                ukuran_teks = excluded.ukuran_teks,
                bahasa      = excluded.bahasa
        """, {"id_profil": profil_id, **preferensi})
        conn.commit()
        conn.close()
        return True, "Preferensi tersimpan."
    except Exception as e:
        return False, str(e)

def ganti_password_db(profil_id: int, password_baru: str) -> tuple[bool, str]:
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute('UPDATE profil SET password = ? WHERE id = ?', (password_baru, profil_id))
        conn.commit()
        conn.close()
        return True, 'Password berhasil diubah.'
    except Exception as e:
        return False, str(e)
