"""
models/tracker_model.py
Beaply - Model: Tracker & Pengingat Beasiswa

CRUD SQLite + utils untuk tabel tracker_beasiswa dan pengingat.
Digabungkan dari: Tracker_dan_Pengingat/tracker_database.py + tracker_utils.py
"""

import os
from datetime import datetime, timedelta

from models.database import get_connection


# ════════════════════════════════════════════════════════════
# INISIALISASI TABEL
# ════════════════════════════════════════════════════════════

def init_tracker_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tracker_beasiswa (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            profil_id       INTEGER NOT NULL,
            nama_beasiswa   TEXT    NOT NULL,
            status          TEXT    NOT NULL DEFAULT 'belum_mulai'
                            CHECK(status IN (
                                'belum_mulai','sedang_proses',
                                'terkirim','diterima','ditolak'
                            )),
            deadline        TEXT,
            catatan         TEXT    DEFAULT '',
            dibookmark      INTEGER DEFAULT 0,
            dibuat_pada     TEXT    DEFAULT (datetime('now','localtime')),
            diupdate_pada   TEXT    DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (profil_id) REFERENCES profil(id) ON DELETE CASCADE
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pengingat (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            tracker_id      INTEGER NOT NULL,
            waktu_pengingat TEXT    NOT NULL,
            sudah_tampil    INTEGER DEFAULT 0,
            dibuat_pada     TEXT    DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (tracker_id) REFERENCES tracker_beasiswa(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()


# ════════════════════════════════════════════════════════════
# CRUD — TRACKER BEASISWA
# ════════════════════════════════════════════════════════════

def tambah_tracker(profil_id, nama_beasiswa, deadline=None, catatan=""):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO tracker_beasiswa (profil_id, nama_beasiswa, deadline, catatan)
            VALUES (?, ?, ?, ?)
        """, (profil_id, nama_beasiswa.strip(), deadline, catatan.strip()))
        tid = cur.lastrowid
        conn.commit()
        conn.close()
        return True, "Tracker berhasil ditambahkan.", tid
    except Exception as e:
        return False, str(e), -1


def ambil_semua_tracker(profil_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM tracker_beasiswa WHERE profil_id = ?
        ORDER BY CASE WHEN deadline IS NULL THEN 1 ELSE 0 END,
                 deadline ASC, dibuat_pada DESC
    """, (profil_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def ambil_tracker_by_id(tracker_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tracker_beasiswa WHERE id = ?", (tracker_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def update_status_tracker(tracker_id, status):
    valid = ('belum_mulai', 'sedang_proses', 'terkirim', 'diterima', 'ditolak')
    if status not in valid:
        return False, f"Status harus salah satu dari: {', '.join(valid)}"
    try:
        conn = get_connection()
        conn.execute("""
            UPDATE tracker_beasiswa
            SET status = ?, diupdate_pada = datetime('now','localtime')
            WHERE id = ?
        """, (status, tracker_id))
        conn.commit()
        conn.close()
        return True, "Status diperbarui."
    except Exception as e:
        return False, str(e)


def update_tracker(tracker_id, nama_beasiswa, deadline, catatan):
    try:
        conn = get_connection()
        conn.execute("""
            UPDATE tracker_beasiswa
            SET nama_beasiswa = ?, deadline = ?, catatan = ?,
                diupdate_pada = datetime('now','localtime')
            WHERE id = ?
        """, (nama_beasiswa.strip(), deadline, catatan.strip(), tracker_id))
        conn.commit()
        conn.close()
        return True, "Tracker diperbarui."
    except Exception as e:
        return False, str(e)


def hapus_tracker(tracker_id):
    try:
        conn = get_connection()
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("DELETE FROM tracker_beasiswa WHERE id = ?", (tracker_id,))
        conn.commit()
        conn.close()
        return True, "Tracker dihapus."
    except Exception as e:
        return False, str(e)


def update_bookmark_tracker(tracker_id, status):
    try:
        conn = get_connection()
        conn.execute("""
            UPDATE tracker_beasiswa
            SET dibookmark = ?, diupdate_pada = datetime('now','localtime')
            WHERE id = ?
        """, (status, tracker_id))
        conn.commit()
        conn.close()
        return True, "Bookmark diperbarui."
    except Exception as e:
        return False, str(e)


def ambil_tracker_by_bulan(profil_id, bulan, tahun):
    conn = get_connection()
    cur = conn.cursor()
    pattern = f"{tahun:04d}-{bulan:02d}-%"
    cur.execute("""
        SELECT * FROM tracker_beasiswa
        WHERE profil_id = ? AND deadline LIKE ?
        ORDER BY deadline ASC
    """, (profil_id, pattern))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def hitung_statistik_tracker(profil_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN status = 'belum_mulai' THEN 1 ELSE 0 END) as belum_mulai,
            SUM(CASE WHEN status = 'sedang_proses' THEN 1 ELSE 0 END) as sedang_proses,
            SUM(CASE WHEN status = 'terkirim' THEN 1 ELSE 0 END) as terkirim,
            SUM(CASE WHEN status = 'diterima' THEN 1 ELSE 0 END) as diterima,
            SUM(CASE WHEN status = 'ditolak' THEN 1 ELSE 0 END) as ditolak,
            SUM(CASE WHEN dibookmark = 1 THEN 1 ELSE 0 END) as bookmark
        FROM tracker_beasiswa WHERE profil_id = ?
    """, (profil_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return dict(row)
    return {"total": 0, "belum_mulai": 0, "sedang_proses": 0,
            "terkirim": 0, "diterima": 0, "ditolak": 0, "bookmark": 0}


# ════════════════════════════════════════════════════════════
# CRUD — PENGINGAT
# ════════════════════════════════════════════════════════════

def tambah_pengingat(tracker_id, waktu_pengingat):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO pengingat (tracker_id, waktu_pengingat) VALUES (?, ?)",
                    (tracker_id, waktu_pengingat))
        pid = cur.lastrowid
        conn.commit()
        conn.close()
        return True, "Pengingat ditambahkan.", pid
    except Exception as e:
        return False, str(e), -1


def ambil_pengingat_aktif(profil_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.*, t.nama_beasiswa, t.deadline
        FROM pengingat p
        JOIN tracker_beasiswa t ON p.tracker_id = t.id
        WHERE t.profil_id = ? AND p.sudah_tampil = 0
              AND p.waktu_pengingat <= datetime('now','localtime')
        ORDER BY p.waktu_pengingat ASC
    """, (profil_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def tandai_pengingat_tampil(pengingat_id):
    conn = get_connection()
    conn.execute("UPDATE pengingat SET sudah_tampil = 1 WHERE id = ?", (pengingat_id,))
    conn.commit()
    conn.close()


# ════════════════════════════════════════════════════════════
# UTILS — FORMAT & KONSTANTA (dari tracker_utils.py)
# ════════════════════════════════════════════════════════════

STATUS_LABEL = {
    "id": {"belum_mulai": "Belum Mulai", "sedang_proses": "Sedang Proses",
           "terkirim": "Terkirim", "diterima": "Diterima ✅", "ditolak": "Ditolak ❌"},
    "en": {"belum_mulai": "Not Started", "sedang_proses": "In Progress",
           "terkirim": "Submitted", "diterima": "Accepted ✅", "ditolak": "Rejected ❌"},
}
STATUS_COLOR = {"belum_mulai": "#6B7280", "sedang_proses": "#3B82F6",
                "terkirim": "#EAB308", "diterima": "#22C55E", "ditolak": "#EF4444"}
STATUS_LIST = ["belum_mulai", "sedang_proses", "terkirim", "diterima", "ditolak"]


def validasi_deadline(tanggal_str):
    if not tanggal_str or not tanggal_str.strip():
        return True, ""
    try:
        datetime.strptime(tanggal_str.strip(), "%Y-%m-%d")
        return True, ""
    except ValueError:
        return False, "Format deadline harus YYYY-MM-DD."


def validasi_tracker_input(nama, deadline=""):
    if not nama or not nama.strip():
        return False, "Nama beasiswa tidak boleh kosong."
    if len(nama.strip()) < 3:
        return False, "Nama beasiswa minimal 3 karakter."
    ok, msg = validasi_deadline(deadline)
    if not ok:
        return False, msg
    return True, ""


def hitung_selisih_hari(deadline_str):
    if not deadline_str or not deadline_str.strip():
        return None
    try:
        dl = datetime.strptime(deadline_str.strip(), "%Y-%m-%d").date()
        today = datetime.now().date()
        return (dl - today).days
    except ValueError:
        return None


def logika_warna_tanggal(deadline_str, dibookmark=False):
    if dibookmark:
        return "#3B82F6"
    selisih = hitung_selisih_hari(deadline_str)
    if selisih is None:
        return "#6B7280"
    if selisih < 0:
        return "#991B1B"
    elif selisih <= 15:
        return "#EF4444"
    elif selisih <= 30:
        return "#EAB308"
    else:
        return "#22C55E"


def format_status(status, bhs="id"):
    return STATUS_LABEL.get(bhs, STATUS_LABEL["id"]).get(status, status)


def warna_status(status):
    return STATUS_COLOR.get(status, "#6B7280")


def format_deadline_display(deadline_str):
    if not deadline_str or not deadline_str.strip():
        return "Tidak ada deadline"
    bulan_id = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
                "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    try:
        d = datetime.strptime(deadline_str.strip(), "%Y-%m-%d")
        tgl = f"{d.day} {bulan_id[d.month]} {d.year}"
        selisih = hitung_selisih_hari(deadline_str)
        if selisih is not None:
            if selisih < 0:
                tgl += f" (lewat {abs(selisih)} hari)"
            elif selisih == 0:
                tgl += " (HARI INI!)"
            elif selisih == 1:
                tgl += " (besok)"
            else:
                tgl += f" (dalam {selisih} hari)"
        return tgl
    except ValueError:
        return deadline_str
