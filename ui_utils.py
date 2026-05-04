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
