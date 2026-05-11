"""
ui_utils.py
Beaply - COMPATIBILITY SHIM (Backward-compatible re-exports)

File ini sekarang hanya menjadi bridge/shim yang me-re-export semua
simbol dari lokasi MVC baru. File-file lama yang masih mengimpor dari
'ui_utils' akan tetap berfungsi tanpa perubahan.

LOKASI BARU:
  - Design Tokens → views/components/design_tokens.py
  - i18n (TEKS)   → views/components/i18n.py
  - UI Helpers     → views/components/ui_helpers.py
"""

# ── Re-export Design Tokens ──
from views.components.design_tokens import (
    BG_COLOR, CARD_COLOR, SIDEBAR_BG, SIDEBAR_ACTIVE_BG, SIDEBAR_ACTIVE_TX,
    BTN_PRIMARY, BTN_PRIMARY_HOVER, BTN_PALE,
    TEXT_DARK, TEXT_MUTED, TEXT_ACCENT, BORDER_COLOR, INPUT_BG,
    PASTEL_COLORS, BTN_GREEN, TEXT_LIGHT,
)

# ── Re-export i18n ──
from views.components.i18n import t, TEKS

# ── Re-export UI Helpers ──
from views.components.ui_helpers import (
    ukuran_font, apply_pref, get_bahasa,
    konfirm_yesno, show_info, show_error,
    hitung_completeness,
)
  # UIUTILS - Backward Compatibility Shim
# ----------------------------------------------------------------
# SEMUA CODE YANG DISINI HANYA UNTUK MENYELAMATKAN FILE-FILE
# DI FOLDER CONTROLLER AGAR TETAP BISA JALAN TANPA ERROR.
# LOGIKA UTAMA SUDAH PINDAH KE FOLDER views/components/
# ----------------------------------------------------------------

import os
from views.components.design_tokens import *
from views.components.i18n import *
from views.components.ui_helpers import *

# ----------------------------------------------------------------
# 1. RE-EXPORT FUNGSI DATABASE (views/components/database.py)
# ----------------------------------------------------------------

def get_db_path():
    return DATABASE_PATH

def connect_db():
    """Kembalikan koneksi database."""
    return sqlite3.connect(DATABASE_PATH)

def run_query(query, params=()):
    """Jalankan query SQL dan kembalikan hasilnya."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    rows = cursor.fetchall()
    conn.close()
    return rows

# ----------------------------------------------------------------
# 2. RE-EXPORT FUNGSI PROFIL (views/components/profil_logic.py)
# ----------------------------------------------------------------

def simpan_profil(nama, email, password):
    """Simpan profil baru."""
    from controllers.profil_controller import simpan_profil as simpan_controller
    return simpan_controller(nama, email, password)

def login_user(email, password):
    """Login user."""
    from controllers.profil_controller import login_user as login_controller
    return login_controller(email, password)

def tampil_profil(profil_id):
    """Tampilkan profil."""
    from controllers.profil_controller import tampil_profil as tampil_controller
    return tampil_controller(profil_id)

def simpan_preferensi(profil_id, bhs="id", tema="system"):
    """Simpan preferensi."""
    from controllers.profil_controller import simpan_preferensi as simpan_pref_controller
    return simpan_pref_controller(profil_id, bhs, tema)

def ambil_preferensi(profil_id):
    """Ambil preferensi."""
    from controllers.profil_controller import ambil_preferensi as ambil_pref_controller
    return ambil_pref_controller(profil_id)

def verifikasi_email(email):
    """Verifikasi email."""
    from controllers.profil_controller import verifikasi_email as verif_email_controller
    return verif_email_controller(email)

# ----------------------------------------------------------------
# 3. RE-EXPORT FUNGSI TRACKER (views/components/tracker_logic.py)
# ----------------------------------------------------------------

def simpan_tracker(user_id, nama, jenis, deadline, lokasi=""):
    """Simpan tracker."""
    from controllers.tracker_controller import simpan_tracker as simpan_tracker_controller
    return simpan_tracker_controller(user_id, nama, jenis, deadline, lokasi)

def hapus_tracker(tracker_id):
    """Hapus tracker."""
    from controllers.tracker_controller import hapus_tracker as hapus_tracker_controller
    return hapus_tracker_controller(tracker_id)

def update_tracker(tracker_id, nama=None, jenis=None, deadline=None, lokasi=None):
    """Update tracker."""
    from controllers.tracker_controller import update_tracker as update_tracker_controller
    return update_tracker_controller(tracker_id, nama, jenis, deadline, lokasi)

def get_semua_tracker(user_id):
    """Ambil semua tracker."""
    from controllers.tracker_controller import get_semua_tracker as get_all_tracker_controller
    return get_all_tracker_controller(user_id)

def hitung_statistik(user_id):
    """Hitung statistik tracker."""
    from controllers.tracker_controller import hitung_statistik as hitung_stats_controller
    return hitung_stats_controller(user_id)

def fmt_deadline(tanggal):
    """Format deadline."""
    from controllers.tracker_controller import fmt_deadline as format_deadline_controller
    return format_deadline_controller(tanggal)

# ----------------------------------------------------------------
# 4. RE-EXPORT FUNGSI EKSPLORASI (views/components/eksplorasi_logic.py)
# ----------------------------------------------------------------

def get_semua_beasiswa(limit=1000):
    """Ambil semua beasiswa."""
    from controllers.eksplorasi_controller import get_semua_beasiswa as get_all_scholarships_controller
    return get_all_scholarships_controller(limit)

def get_bookmarks(user_id):
    """Ambil bookmark user."""
    from controllers.eksplorasi_controller import get_bookmarks as get_bookmarks_controller
    return get_bookmarks_controller(user_id)

def toggle_bookmark(user_id, beasiswa_id):
    """Toggle bookmark."""
    from controllers.eksplorasi_controller import toggle_bookmark as toggle_bookmark_controller
    return toggle_bookmark_controller(user_id, beasiswa_id)

def simpan_pendaftaran(user_id, beasiswa_id, nama_beasiswa, status="applied"):
    """Simpan pendaftaran."""
    from controllers.eksplorasi_controller import simpan_pendaftaran as save_application_controller
    return save_application_controller(user_id, beasiswa_id, nama_beasiswa, status)

def get_semua_pendaftaran(user_id):
    """Ambil semua pendaftaran."""
    from controllers.eksplorasi_controller import get_semua_pendaftaran as get_all_applications_controller
    return get_all_pendaftaran(user_id)

def hapus_pendaftaran(pendaftaran_id):
    """Hapus pendaftaran."""
    from controllers.eksplorasi_controller import hapus_pendaftaran as delete_application_controller
    return delete_application_controller(pendaftaran_id)

def update_status_pendaftaran(pendaftaran_id, status):
    """Update status pendaftaran."""
    from controllers.eksplorasi_controller import update_status_pendaftaran as update_application_status_controller
    return update_application_status_controller(pendaftaran_id, status)