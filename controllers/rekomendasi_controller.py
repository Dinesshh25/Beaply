"""
controllers/rekomendasi_controller.py
Beaply - Controller: Rekomendasi Beasiswa

Mediator antara views/rekomendasi_view dan models/rekomendasi_model.
"""

import logging

from models.rekomendasi_model import (
    DAFTAR_BEASISWA_REKOMENDASI,
    hitung_skor_cocok,
    analisis_peluang,
    ambil_profil_untuk_rekomendasi,
)

logger = logging.getLogger(__name__)


def get_profil_user(profil_id: int) -> dict:
    """
    Ambil dan format data profil untuk algoritma rekomendasi.
    Data diambil dari DB — tidak ada nilai hardcoded.
    """
    try:
        return ambil_profil_untuk_rekomendasi(profil_id)
    except Exception as e:
        logger.error("get_profil_user gagal (profil_id=%s): %s", profil_id, e)
        return {}


def hitung_rekomendasi(profil_user: dict) -> list:
    """
    Hitung skor kecocokan untuk semua beasiswa dan urutkan dari terbaik.
    Return: list of {beasiswa, skor} sorted by skor desc.
    """
    if not profil_user:
        return []
    try:
        hasil = [
            {"beasiswa": bea, "skor": hitung_skor_cocok(profil_user, bea)}
            for bea in DAFTAR_BEASISWA_REKOMENDASI
        ]
        hasil.sort(key=lambda x: x["skor"], reverse=True)
        return hasil
    except Exception as e:
        logger.error("hitung_rekomendasi gagal: %s", e)
        return []


def get_analisis(profil_user: dict, target_beasiswa: dict) -> str:
    """Ambil analisis peluang untuk beasiswa tertentu."""
    try:
        return analisis_peluang(profil_user, target_beasiswa)
    except Exception as e:
        logger.error("get_analisis gagal: %s", e)
        return "Analisis tidak tersedia saat ini."


def get_daftar_beasiswa() -> list:
    """Ambil seluruh daftar beasiswa rekomendasi."""
    return DAFTAR_BEASISWA_REKOMENDASI
