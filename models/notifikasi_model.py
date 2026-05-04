"""
models/notifikasi_model.py
Beaply - Model: Manajemen Notifikasi Terpusat

CRUD SQLite + utils untuk tabel notifikasi dan preferensi_notifikasi.
Digabungkan dari: Notifikasi_Terpusat/notifikasi_database.py + notifikasi_utils.py
"""

from datetime import datetime, timedelta
from models.database import get_connection


# ════════════════════════════════════════════════════════════
# INISIALISASI TABEL
# ════════════════════════════════════════════════════════════

def init_notifikasi_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notifikasi (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            profil_id       INTEGER NOT NULL,
            judul           TEXT    NOT NULL,
            pesan           TEXT    NOT NULL,
            tipe            TEXT    NOT NULL DEFAULT 'info'
                            CHECK(tipe IN ('info','deadline','status','sistem')),
            sudah_dibaca    INTEGER DEFAULT 0,
            dibuat_pada     TEXT    DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (profil_id) REFERENCES profil(id) ON DELETE CASCADE
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS preferensi_notifikasi (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            profil_id       INTEGER NOT NULL UNIQUE,
            push_notif      INTEGER DEFAULT 1,
            email_notif     INTEGER DEFAULT 0,
            notif_deadline  INTEGER DEFAULT 1,
            notif_status    INTEGER DEFAULT 1,
            notif_sistem    INTEGER DEFAULT 1,
            FOREIGN KEY (profil_id) REFERENCES profil(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()


# ════════════════════════════════════════════════════════════
# CRUD — NOTIFIKASI
# ════════════════════════════════════════════════════════════

def tambah_notifikasi(profil_id, judul, pesan, tipe="info"):
    valid_tipe = ("info", "deadline", "status", "sistem")
    if tipe not in valid_tipe:
        tipe = "info"
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO notifikasi (profil_id, judul, pesan, tipe)
            VALUES (?, ?, ?, ?)
        """, (profil_id, judul.strip(), pesan.strip(), tipe))
        nid = cur.lastrowid
        conn.commit()
        conn.close()
        return True, "Notifikasi dibuat.", nid
    except Exception as e:
        return False, str(e), -1


def ambil_riwayat_notif(profil_id, filter_baca=None, limit=50):
    conn = get_connection()
    cur = conn.cursor()
    query = "SELECT * FROM notifikasi WHERE profil_id = ?"
    params = [profil_id]
    if filter_baca is not None:
        query += " AND sudah_dibaca = ?"
        params.append(filter_baca)
    query += " ORDER BY dibuat_pada DESC LIMIT ?"
    params.append(limit)
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def tandai_dibaca(notif_id):
    try:
        conn = get_connection()
        conn.execute("UPDATE notifikasi SET sudah_dibaca = 1 WHERE id = ?", (notif_id,))
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


def tandai_semua_dibaca(profil_id):
    try:
        conn = get_connection()
        conn.execute("""
            UPDATE notifikasi SET sudah_dibaca = 1
            WHERE profil_id = ? AND sudah_dibaca = 0
        """, (profil_id,))
        conn.commit()
        conn.close()
        return True, "Semua notifikasi ditandai dibaca."
    except Exception as e:
        return False, str(e)


def hapus_notifikasi(notif_id):
    try:
        conn = get_connection()
        conn.execute("DELETE FROM notifikasi WHERE id = ?", (notif_id,))
        conn.commit()
        conn.close()
        return True, "Notifikasi dihapus."
    except Exception as e:
        return False, str(e)


def hapus_semua_notifikasi(profil_id):
    try:
        conn = get_connection()
        conn.execute("DELETE FROM notifikasi WHERE profil_id = ?", (profil_id,))
        conn.commit()
        conn.close()
        return True, "Semua notifikasi dihapus."
    except Exception as e:
        return False, str(e)


def hitung_belum_dibaca(profil_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT COUNT(*) as cnt FROM notifikasi
        WHERE profil_id = ? AND sudah_dibaca = 0
    """, (profil_id,))
    row = cur.fetchone()
    conn.close()
    return row["cnt"] if row else 0


# ════════════════════════════════════════════════════════════
# CRUD — PREFERENSI NOTIFIKASI
# ════════════════════════════════════════════════════════════

def ambil_preferensi_notif(profil_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM preferensi_notifikasi WHERE profil_id = ?", (profil_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return dict(row)
    return {"push_notif": 1, "email_notif": 0, "notif_deadline": 1,
            "notif_status": 1, "notif_sistem": 1}


def simpan_preferensi_notif(profil_id, prefs):
    try:
        conn = get_connection()
        conn.execute("""
            INSERT INTO preferensi_notifikasi
                (profil_id, push_notif, email_notif, notif_deadline, notif_status, notif_sistem)
            VALUES (:profil_id, :push_notif, :email_notif, :notif_deadline, :notif_status, :notif_sistem)
            ON CONFLICT(profil_id) DO UPDATE SET
                push_notif = excluded.push_notif, email_notif = excluded.email_notif,
                notif_deadline = excluded.notif_deadline, notif_status = excluded.notif_status,
                notif_sistem = excluded.notif_sistem
        """, {"profil_id": profil_id, **prefs})
        conn.commit()
        conn.close()
        return True, "Preferensi notifikasi tersimpan."
    except Exception as e:
        return False, str(e)


# ════════════════════════════════════════════════════════════
# UTILS — FORMAT (dari notifikasi_utils.py)
# ════════════════════════════════════════════════════════════

TIPE_IKON = {"info": "ℹ️", "deadline": "⏰", "status": "📋", "sistem": "🔔"}
TIPE_WARNA = {"info": "#3B82F6", "deadline": "#EAB308", "status": "#10B981", "sistem": "#8B5CF6"}
TIPE_LABEL = {
    "id": {"info": "Informasi", "deadline": "Deadline", "status": "Status", "sistem": "Sistem"},
    "en": {"info": "Information", "deadline": "Deadline", "status": "Status", "sistem": "System"},
}


def format_waktu_relatif(waktu_str, bhs="id"):
    try:
        waktu = datetime.strptime(waktu_str, "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        try:
            waktu = datetime.strptime(waktu_str, "%Y-%m-%d")
        except (ValueError, TypeError):
            return waktu_str
    now = datetime.now()
    delta = now - waktu
    if bhs == "en":
        if delta.total_seconds() < 60: return "Just now"
        elif delta.total_seconds() < 3600: return f"{int(delta.total_seconds()/60)} min ago"
        elif delta.total_seconds() < 86400: return f"{int(delta.total_seconds()/3600)} hours ago"
        elif delta.days == 1: return "Yesterday"
        elif delta.days < 7: return f"{delta.days} days ago"
        else: return waktu.strftime("%d %b %Y")
    else:
        if delta.total_seconds() < 60: return "Baru saja"
        elif delta.total_seconds() < 3600: return f"{int(delta.total_seconds()/60)} menit lalu"
        elif delta.total_seconds() < 86400: return f"{int(delta.total_seconds()/3600)} jam lalu"
        elif delta.days == 1: return "Kemarin"
        elif delta.days < 7: return f"{delta.days} hari lalu"
        else:
            bulan_id = ["","Jan","Feb","Mar","Apr","Mei","Jun","Jul","Ags","Sep","Okt","Nov","Des"]
            return f"{waktu.day} {bulan_id[waktu.month]} {waktu.year}"


def group_by_tanggal(notifikasi_list, bhs="id"):
    if not notifikasi_list:
        return []
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    groups = {}
    for n in notifikasi_list:
        waktu_str = n.get("dibuat_pada", "")
        try:
            tgl = datetime.strptime(waktu_str, "%Y-%m-%d %H:%M:%S").date()
        except (ValueError, TypeError):
            tgl = today
        if tgl == today:
            label = "Hari Ini" if bhs == "id" else "Today"
        elif tgl == yesterday:
            label = "Kemarin" if bhs == "id" else "Yesterday"
        else:
            bulan = ["","Jan","Feb","Mar","Apr","Mei","Jun","Jul","Ags","Sep","Okt","Nov","Des"]
            label = f"{tgl.day} {bulan[tgl.month]} {tgl.year}"
        if label not in groups:
            groups[label] = []
        groups[label].append(n)
    return [{"tanggal": k, "items": v} for k, v in groups.items()]


def ikon_tipe(tipe):
    return TIPE_IKON.get(tipe, "🔔")


def warna_tipe(tipe):
    return TIPE_WARNA.get(tipe, "#6B7280")


def label_tipe(tipe, bhs="id"):
    return TIPE_LABEL.get(bhs, TIPE_LABEL["id"]).get(tipe, tipe)
