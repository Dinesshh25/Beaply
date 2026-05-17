"""
pyqt_app/styles/theme.py
Beaply – Design tokens for PyQt6 (Light & Dark mode).
Matches the existing CustomTkinter design_tokens.py.
"""

# ── Colour Palettes ──────────────────────────────────────────
LIGHT = {
    "bg":               "#FDF6F0",
    "card":             "#FFFFFF",
    "sidebar_bg":       "#FDF6F0",
    "sidebar_active_bg":"#D6EAD8",
    "sidebar_active_tx":"#2D6A4F",
    "btn_primary":      "#A8C5B0",
    "btn_primary_hover":"#8FB898",
    "btn_pale":         "#E2EBE5",
    "text_dark":        "#2D2D2D",
    "text_muted":       "#888888",
    "text_accent":      "#D4917B",
    "border":           "#E8E0D8",
    "input_bg":         "#F0ECE8",
    "btn_green":        "#A8C5B0",
    "text_light":       "#FFFFFF",
    "danger":           "#D94040",
    "danger_bg":        "#FCE8E8",
    "greet_bg":         "#FCEBE3",
    "greet_border":     "#EED5C9",
    "calendar_header":  "#F6D6D0",
}

DARK = {
    "bg":               "#202124",
    "card":             "#292A2D",
    "sidebar_bg":       "#202124",
    "sidebar_active_bg":"#3C4043",
    "sidebar_active_tx":"#81C995",
    "btn_primary":      "#81C995",
    "btn_primary_hover":"#5BB974",
    "btn_pale":         "#414347",
    "text_dark":        "#E8EAED",
    "text_muted":       "#9AA0A6",
    "text_accent":      "#F28B82",
    "border":           "#3C4043",
    "input_bg":         "#171717",
    "btn_green":        "#81C995",
    "text_light":       "#E8EAED",
    "danger":           "#F28B82",
    "danger_bg":        "#3C2020",
    "greet_bg":         "#382928",
    "greet_border":     "#4A3530",
    "calendar_header":  "#382928",
}

# Pastel cards (index-based, each has light & dark variants)
PASTEL = [
    ("#E8EBE4", "#2B302C"),
    ("#F4EFE6", "#36322C"),
    ("#F6E6E4", "#382928"),
    ("#E8EEE4", "#2A3029"),
    ("#F0E8E4", "#332B28"),
    ("#E4EBE8", "#272E2B"),
]

# ── Font Family ──────────────────────────────────────────────
FONT_FAMILY = "Segoe UI"

def palette(mode: str = "light") -> dict:
    """Return colour dict for *mode* ('light' | 'dark')."""
    return LIGHT if mode == "light" else DARK

def pastel(index: int, mode: str = "light") -> str:
    """Return a pastel colour by index."""
    idx = index % len(PASTEL)
    return PASTEL[idx][0] if mode == "light" else PASTEL[idx][1]
