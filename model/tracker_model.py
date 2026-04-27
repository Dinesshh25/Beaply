"""
tracker_database.py
Beaply - Manajemen tabel & CRUD SQLite untuk Tracker & Pengingat

Tabel:
  - tracker_beasiswa  : Data pelacakan pendaftaran beasiswa
  - pengingat         : Pengingat deadline beasiswa
"""

from datetime import datetime
from model.database import get_connection


# ════════════════════════════════════════════════════════════
# INISIALISASI TABEL
# ════════════════════════════════════════════════════════════

def init_tracker_db():
    """Buat tabel tracker_beasiswa dan pengingat kalau belum ada."""
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

def tambah_tracker(profil_id: int, nama_beasiswa: str,
                   deadline: str = None, catatan: str = "") -> tuple:
    """
    Insert tracker beasiswa baru.
    Return: (sukses, pesan, tracker_id)
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO tracker_beasiswa
                (profil_id, nama_beasiswa, deadline, catatan)
            VALUES (?, ?, ?, ?)
        """, (profil_id, nama_beasiswa.strip(), deadline, catatan.strip()))
        tid = cur.lastrowid
        conn.commit()
        conn.close()
        return True, "Tracker berhasil ditambahkan.", tid
    except Exception as e:
        return False, str(e), -1


def ambil_semua_tracker(profil_id: int) -> list:
    """Ambil semua tracker milik profil, urut deadline terdekat."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM tracker_beasiswa
        WHERE profil_id = ?
        ORDER BY
            CASE WHEN deadline IS NULL THEN 1 ELSE 0 END,
            deadline ASC,
            dibuat_pada DESC
    """, (profil_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def ambil_tracker_by_id(tracker_id: int) -> dict | None:
    """Ambil satu tracker berdasarkan ID."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tracker_beasiswa WHERE id = ?", (tracker_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def update_status_tracker(tracker_id: int, status: str) -> tuple:
    """Update status tracker. Return: (sukses, pesan)"""
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


def update_tracker(tracker_id: int, nama_beasiswa: str,
                   deadline: str, catatan: str) -> tuple:
    """Update data tracker. Return: (sukses, pesan)"""
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


def hapus_tracker(tracker_id: int) -> tuple:
    """Hapus tracker (dan pengingat via CASCADE). Return: (sukses, pesan)"""
    try:
        conn = get_connection()
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("DELETE FROM tracker_beasiswa WHERE id = ?", (tracker_id,))
        conn.commit()
        conn.close()
        return True, "Tracker dihapus."
    except Exception as e:
        return False, str(e)


def update_bookmark_tracker(tracker_id: int, status: int) -> tuple:
    """Toggle bookmark status. Return: (sukses, pesan)"""
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


def ambil_tracker_by_bulan(profil_id: int, bulan: int, tahun: int) -> list:
    """Ambil tracker yang deadline-nya di bulan & tahun tertentu (untuk kalender)."""
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


def hitung_statistik_tracker(profil_id: int) -> dict:
    """Hitung jumlah tracker per status."""
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
        FROM tracker_beasiswa
        WHERE profil_id = ?
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

def tambah_pengingat(tracker_id: int, waktu_pengingat: str) -> tuple:
    """
    Tambah pengingat untuk tracker.
    Return: (sukses, pesan, pengingat_id)
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO pengingat (tracker_id, waktu_pengingat)
            VALUES (?, ?)
        """, (tracker_id, waktu_pengingat))
        pid = cur.lastrowid
        conn.commit()
        conn.close()
        return True, "Pengingat ditambahkan.", pid
    except Exception as e:
        return False, str(e), -1


def ambil_pengingat_aktif(profil_id: int) -> list:
    """Ambil semua pengingat aktif (belum tampil) milik profil."""
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


def tandai_pengingat_tampil(pengingat_id: int):
    """Tandai pengingat sudah ditampilkan."""
    conn = get_connection()
    conn.execute("UPDATE pengingat SET sudah_tampil = 1 WHERE id = ?",
                 (pengingat_id,))
    conn.commit()
    conn.close()


"""
tracker_utils.py
Beaply - Utilitas untuk Tracker & Pengingat

Modul:
  - validasi_deadline       — Validasi format tanggal deadline
  - hitung_selisih_hari     — Hitung selisih hari dari sekarang
  - logika_warna_tanggal    — Tentukan warna berdasarkan jarak deadline
  - format_status           — Label status dalam bahasa Indonesia/Inggris
"""

from datetime import datetime, timedelta


# ════════════════════════════════════════════════════════════
# VALIDASI
# ════════════════════════════════════════════════════════════

def validasi_deadline(tanggal_str: str) -> tuple:
    """
    Validasi format deadline (YYYY-MM-DD).
    Return: (valid: bool, pesan: str)
    """
    if not tanggal_str or not tanggal_str.strip():
        return True, ""  # deadline opsional

    try:
        datetime.strptime(tanggal_str.strip(), "%Y-%m-%d")
        return True, ""
    except ValueError:
        return False, "Format deadline harus YYYY-MM-DD."


def validasi_tracker_input(nama: str, deadline: str = "") -> tuple:
    """
    Validasi input tracker baru.
    Return: (valid: bool, pesan: str)
    """
    if not nama or not nama.strip():
        return False, "Nama beasiswa tidak boleh kosong."

    if len(nama.strip()) < 3:
        return False, "Nama beasiswa minimal 3 karakter."

    ok, msg = validasi_deadline(deadline)
    if not ok:
        return False, msg

    return True, ""


# ════════════════════════════════════════════════════════════
# HITUNG SELISIH HARI
# ════════════════════════════════════════════════════════════

def hitung_selisih_hari(deadline_str: str) -> int | None:
    """
    Hitung selisih hari antara deadline dan hari ini.
    Positif = masih ada waktu, negatif = sudah lewat.
    Return: int atau None jika deadline kosong.
    """
    if not deadline_str or not deadline_str.strip():
        return None
    try:
        dl = datetime.strptime(deadline_str.strip(), "%Y-%m-%d").date()
        today = datetime.now().date()
        return (dl - today).days
    except ValueError:
        return None


# ════════════════════════════════════════════════════════════
# LOGIKA WARNA TANGGAL (untuk kalender)
# ════════════════════════════════════════════════════════════

def logika_warna_tanggal(deadline_str: str, dibookmark: bool = False) -> str:
    """
    Menentukan warna tanggal di kalender berdasarkan selisih hari.

    Aturan:
      - 🔵 Biru (#3B82F6)     : Di-bookmark
      - 🟢 Hijau (#22C55E)    : > 30 hari
      - 🟡 Kuning (#EAB308)   : ≤ 30 hari
      - 🔴 Merah (#EF4444)    : ≤ 15 hari
      - 🟤 Merah Tua (#991B1B): Sudah lewat

    Return: hex color string
    """
    if dibookmark:
        return "#3B82F6"  # biru

    selisih = hitung_selisih_hari(deadline_str)
    if selisih is None:
        return "#6B7280"  # abu-abu (default)

    if selisih < 0:
        return "#991B1B"  # merah tua — sudah lewat
    elif selisih <= 15:
        return "#EF4444"  # merah — darurat
    elif selisih <= 30:
        return "#EAB308"  # kuning — segera
    else:
        return "#22C55E"  # hijau — masih lama


# ════════════════════════════════════════════════════════════
# FORMAT STATUS
# ════════════════════════════════════════════════════════════

STATUS_LABEL = {
    "id": {
        "belum_mulai":   "Belum Mulai",
        "sedang_proses": "Sedang Proses",
        "terkirim":      "Terkirim",
        "diterima":      "Diterima ✅",
        "ditolak":       "Ditolak ❌",
    },
    "en": {
        "belum_mulai":   "Not Started",
        "sedang_proses": "In Progress",
        "terkirim":      "Submitted",
        "diterima":      "Accepted ✅",
        "ditolak":       "Rejected ❌",
    },
}

STATUS_COLOR = {
    "belum_mulai":   "#6B7280",
    "sedang_proses": "#3B82F6",
    "terkirim":      "#EAB308",
    "diterima":      "#22C55E",
    "ditolak":       "#EF4444",
}

STATUS_LIST = ["belum_mulai", "sedang_proses", "terkirim", "diterima", "ditolak"]


def format_status(status: str, bhs: str = "id") -> str:
    """Label status dalam bahasa yang dipilih."""
    return STATUS_LABEL.get(bhs, STATUS_LABEL["id"]).get(status, status)


def warna_status(status: str) -> str:
    """Warna hex untuk status."""
    return STATUS_COLOR.get(status, "#6B7280")


def format_deadline_display(deadline_str: str) -> str:
    """Format deadline untuk ditampilkan: '14 Mei 2026 (dalam 30 hari)'"""
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


"""
tracker.py
Beaply - Logika Bisnis Tracker & Pengingat

Modul sesuai spesifikasi:
  1. tampilan_kalender          — Data untuk render kalender grid
  2. logika_warna_tanggal       — Warna tanggal berdasarkan jarak deadline
  3. tambah_penanda_manual      — Simpan tracker baru
  4. hitung_statistik           — Statistik ringkasan tracker
  5. kelola_pengingat           — Buat pengingat otomatis
"""



import calendar
from datetime import datetime, timedelta


# ════════════════════════════════════════════════════════════
# 1. TAMPILAN KALENDER
# ════════════════════════════════════════════════════════════

def tampilan_kalender(profil_id: int, bulan: int = None,
                      tahun: int = None) -> dict:
    """
    Siapkan data untuk render kalender grid bulanan.

    Return: {
        bulan: int,
        tahun: int,
        nama_bulan: str,
        hari_pertama: int (0=Senin),
        total_hari: int,
        tanggal_hari_ini: str,
        tracker_di_bulan: list[dict],
        tanggal_warna: dict[int, str]   # {tanggal: hex_color}
    }
    """
    now = datetime.now()
    if bulan is None:
        bulan = now.month
    if tahun is None:
        tahun = now.year

    nama_bulan_id = [
        "", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ]

    hari_pertama, total_hari = calendar.monthrange(tahun, bulan)

    # Ambil tracker di bulan ini
    tracker_list = ambil_tracker_by_bulan(profil_id, bulan, tahun)

    # Bangun mapping tanggal → warna
    tgl_warna = {}
    tgl_tracker = {}  # tanggal → list tracker
    for t in tracker_list:
        if t["deadline"]:
            try:
                d = datetime.strptime(t["deadline"], "%Y-%m-%d")
                day = d.day
                warna = logika_warna_tanggal(t["deadline"], bool(t["dibookmark"]))
                # Jika sudah ada, prioritaskan warna merah (lebih mendesak)
                if day not in tgl_warna or _prioritas_warna(warna) > _prioritas_warna(tgl_warna[day]):
                    tgl_warna[day] = warna
                if day not in tgl_tracker:
                    tgl_tracker[day] = []
                tgl_tracker[day].append(t)
            except ValueError:
                pass

    return {
        "bulan": bulan,
        "tahun": tahun,
        "nama_bulan": nama_bulan_id[bulan],
        "hari_pertama": hari_pertama,
        "total_hari": total_hari,
        "tanggal_hari_ini": now.strftime("%Y-%m-%d"),
        "tracker_di_bulan": tracker_list,
        "tanggal_warna": tgl_warna,
        "tanggal_tracker": tgl_tracker,
    }


def _prioritas_warna(hex_color: str) -> int:
    """Semakin tinggi semakin mendesak."""
    prio = {
        "#991B1B": 5,  # merah tua
        "#EF4444": 4,  # merah
        "#EAB308": 3,  # kuning
        "#3B82F6": 2,  # biru (bookmark)
        "#22C55E": 1,  # hijau
        "#6B7280": 0,  # abu-abu
    }
    return prio.get(hex_color, 0)


# ════════════════════════════════════════════════════════════
# 2. TAMBAH PENANDA MANUAL
# ════════════════════════════════════════════════════════════

def tambah_penanda_manual(profil_id: int, nama_beasiswa: str,
                          deadline: str = "", catatan: str = "") -> tuple:
    """
    Validasi lalu tambah tracker baru.
    Return: (sukses, pesan, tracker_id)
    """
    ok, msg = validasi_tracker_input(nama_beasiswa, deadline)
    if not ok:
        return False, msg, -1

    dl = deadline.strip() if deadline and deadline.strip() else None
    return tambah_tracker(profil_id, nama_beasiswa, dl, catatan)


# ════════════════════════════════════════════════════════════
# 3. KELOLA STATUS & DATA
# ════════════════════════════════════════════════════════════

def ubah_status(tracker_id: int, status_baru: str) -> tuple:
    """
    Update status tracker.
    Return: (sukses, pesan)
    """
    if status_baru not in STATUS_LIST:
        return False, f"Status tidak valid: {status_baru}"
    return update_status_tracker(tracker_id, status_baru)


def ubah_tracker(tracker_id: int, nama: str, deadline: str,
                 catatan: str) -> tuple:
    """
    Validasi & update data tracker.
    Return: (sukses, pesan)
    """
    ok, msg = validasi_tracker_input(nama, deadline)
    if not ok:
        return False, msg
    dl = deadline.strip() if deadline and deadline.strip() else None
    return update_tracker(tracker_id, nama, dl, catatan)


def toggle_bookmark(tracker_id: int) -> tuple:
    """Toggle bookmark on/off."""
    t = ambil_tracker_by_id(tracker_id)
    if not t:
        return False, "Tracker tidak ditemukan."
    new_val = 0 if t["dibookmark"] else 1
    return update_bookmark_tracker(tracker_id, new_val)


# ════════════════════════════════════════════════════════════
# 4. HITUNG STATISTIK
# ════════════════════════════════════════════════════════════

def hitung_statistik(profil_id: int) -> dict:
    """
    Ambil ringkasan statistik tracker.
    Return: dict dengan jumlah per status + deadline terdekat.
    """
    stats = hitung_statistik_tracker(profil_id)

    # Cari deadline terdekat
    semua = ambil_semua_tracker(profil_id)
    deadline_terdekat = None
    for t in semua:
        if t["deadline"] and t["status"] not in ("diterima", "ditolak"):
            selisih = hitung_selisih_hari(t["deadline"])
            if selisih is not None and selisih >= 0:
                deadline_terdekat = t
                break  # sudah terurut ASC

    stats["deadline_terdekat"] = deadline_terdekat
    return stats


# ════════════════════════════════════════════════════════════
# 5. KELOLA PENGINGAT
# ════════════════════════════════════════════════════════════

def buat_pengingat_otomatis(tracker_id: int) -> tuple:
    """
    Buat pengingat otomatis: H-7, H-3, H-1 dari deadline.
    Return: (sukses, pesan)
    """
    t = ambil_tracker_by_id(tracker_id)
    if not t or not t["deadline"]:
        return False, "Tracker tidak ditemukan atau tidak punya deadline."

    selisih = hitung_selisih_hari(t["deadline"])
    if selisih is None or selisih < 0:
        return False, "Deadline sudah lewat."

    dl = datetime.strptime(t["deadline"], "%Y-%m-%d")

    pengingat_hari = []
    if selisih >= 7:
        pengingat_hari.append(7)
    if selisih >= 3:
        pengingat_hari.append(3)
    if selisih >= 1:
        pengingat_hari.append(1)

    for h in pengingat_hari:
        waktu = (dl - timedelta(days=h)).strftime("%Y-%m-%d 08:00:00")
        tambah_pengingat(tracker_id, waktu)

    return True, f"{len(pengingat_hari)} pengingat dibuat."


def cek_pengingat(profil_id: int) -> list:
    """
    Cek dan ambil pengingat yang sudah waktunya ditampilkan.
    Otomatis tandai sudah_tampil.
    Return: list pengingat yang perlu ditampilkan.
    """
    aktif = ambil_pengingat_aktif(profil_id)
    for p in aktif:
        tandai_pengingat_tampil(p["id"])
    return aktif
