"""
controllers/bantuan_controller.py
Beaply - Controller: Pusat Bantuan & Umpan Balik

Mediator antara View (gui_help_center) dan Model (feedback_model).
"""

from models.feedback_model import kirim_feedback, DAFTAR_FAQ


def get_faq_list() -> list:
    """Ambil daftar FAQ untuk ditampilkan."""
    return DAFTAR_FAQ


def submit_feedback(user_id, kategori: str, pesan: str) -> bool:
    """
    Kirim feedback/laporan dari user.
    Return: True jika berhasil.
    """
    if not pesan or not pesan.strip():
        return False
    return kirim_feedback(user_id, kategori, pesan)
