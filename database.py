"""
database.py
Beaply - COMPATIBILITY SHIM (Backward-compatible re-exports)

File ini sekarang hanya menjadi bridge/shim yang me-re-export semua
simbol dari models/profil_model.py dan models/database.py.

LOKASI BARU:
  - Koneksi DB       → models/database.py
  - CRUD Profil      → models/profil_model.py
"""

from models.database import get_connection, DB_PATH, init_all_tables
from models.profil_model import (
    init_profil_db,
    simpan_profil_db,
    ambil_profil_db,
    ambil_semua_profil_db,
    update_profil_db,
    hapus_profil_db,
    ambil_preferensi_db,
    simpan_preferensi_db,
    ganti_password_db,
)

# Alias untuk backward compatibility
init_db = init_all_tables

# Legacy alias — beberapa file lama menggunakan seed_beasiswa dari sini
try:
    from models.beasiswa_model import seed_beasiswa
except ImportError:
    pass
