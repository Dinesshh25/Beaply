"""
views/components/ui_helpers.py
Beaply - Helper UI: Dialog, Konfirmasi, Utilitas Tampilan

Dipecah dari: ui_utils.py (bagian helper)
"""

import customtkinter as ctk
from tkinter import messagebox


def ukuran_font(pref: dict) -> tuple:
    tbl = {"small": (14, 11, 9), "medium": (18, 13, 11), "large": (22, 16, 13)}
    return tbl.get(pref.get("ukuran_teks", "medium"), tbl["medium"])


def apply_pref(pref: dict):
    ctk.set_appearance_mode(pref.get("tema", "light"))
    ukuran = pref.get("ukuran_teks", "medium").lower()
    if ukuran == "small":
        ctk.set_widget_scaling(0.9)
    elif ukuran == "large":
        ctk.set_widget_scaling(1.1)
    else:
        ctk.set_widget_scaling(1.0)


def get_bahasa(profil_id) -> str:
    from controllers.profil_controller import ambil_preferensi
    pref = ambil_preferensi(profil_id)
    return pref.get("bahasa", "id")


def konfirm_yesno(parent, judul, pesan):
    return messagebox.askyesno(judul, pesan, parent=parent)


def show_info(parent, judul, pesan):
    messagebox.showinfo(judul, pesan, parent=parent)


def show_error(parent, judul, pesan):
    messagebox.showerror(judul, pesan, parent=parent)


def hitung_completeness(profil):
    """Calculate profile completeness percentage."""
    if not profil:
        return 0
    _required = ["nama", "tanggal_lahir", "email", "jurusan",
                 "kampus", "semester", "ip", "jenjang", "jenis_kelamin"]
    _optional = ["skor_ielts", "skor_toefl", "skor_duolingo",
                 "skor_sat", "skor_act", "skor_gre", "skor_gmat",
                 "skor_hsk", "level_jlpt"]
    _all = _required + _optional
    filled = 0
    for fld in _all:
        val = profil.get(fld)
        if val is not None and str(val).strip() != "" and val != 0 and val != 0.0:
            filled += 1
    return int((filled / len(_all)) * 100)
