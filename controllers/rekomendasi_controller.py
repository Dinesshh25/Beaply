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


def bandingkan_beasiswa(profil_user: dict, beasiswa_a: dict, beasiswa_b: dict) -> dict:
    """
    Bandingkan dua beasiswa terhadap profil user.

    Return dict berisi:
        - 'a': {'beasiswa', 'skor', 'kriteria': [...]}
        - 'b': {'beasiswa', 'skor', 'kriteria': [...]}

    Setiap item 'kriteria' adalah:
        {'label', 'nilai_a', 'nilai_b', 'lulus_a', 'lulus_b'}
    """
    def _detail(profil: dict, bea: dict) -> tuple[int, list]:
        """Return (skor, kriteria_list) untuk satu beasiswa."""
        kriteria = []

        # IPK
        ipk_user = profil.get("ipk", 0)
        min_ipk = bea.get("min_ipk", 0)
        kriteria.append({
            "label": "Min. IPK",
            "nilai": f"{min_ipk:.2f}",
            "user": f"{ipk_user:.2f}",
            "lulus": ipk_user >= min_ipk,
        })

        # Semester
        sem_user = profil.get("semester", 1)
        max_sem = bea.get("max_semester", 8)
        kriteria.append({
            "label": "Max Semester",
            "nilai": str(max_sem),
            "user": str(sem_user),
            "lulus": sem_user <= max_sem,
        })

        # Jurusan
        jurusan_user = profil.get("jurusan", "")
        daftar_jur = bea.get("jurusan", [])
        jur_lulus = jurusan_user in daftar_jur if isinstance(daftar_jur, list) else jurusan_user == daftar_jur
        kriteria.append({
            "label": "Jurusan",
            "nilai": f"{len(daftar_jur)} jurusan" if isinstance(daftar_jur, list) else str(daftar_jur),
            "user": jurusan_user or "–",
            "lulus": jur_lulus,
        })

        # Organisasi
        wajib_org = bea.get("wajib_organisasi", False)
        punya_org = profil.get("organisasi", False)
        org_lulus = (not wajib_org) or punya_org
        kriteria.append({
            "label": "Wajib Organisasi",
            "nilai": "Ya" if wajib_org else "Tidak",
            "user": "Ada" if punya_org else "Tidak ada",
            "lulus": org_lulus,
        })

        # Penghasilan ortu
        penghasilan = profil.get("penghasilan_ortu", 0)
        max_penghasilan = bea.get("max_penghasilan_ortu", 999_999_999)
        kriteria.append({
            "label": "Max Penghasilan",
            "nilai": f"Rp {max_penghasilan:,.0f}".replace(",", "."),
            "user": f"Rp {penghasilan:,.0f}".replace(",", "."),
            "lulus": penghasilan <= max_penghasilan,
        })

        skor = hitung_skor_cocok(profil, bea)
        return skor, kriteria

    try:
        skor_a, krit_a = _detail(profil_user, beasiswa_a)
        skor_b, krit_b = _detail(profil_user, beasiswa_b)
        return {
            "a": {"beasiswa": beasiswa_a, "skor": skor_a, "kriteria": krit_a},
            "b": {"beasiswa": beasiswa_b, "skor": skor_b, "kriteria": krit_b},
        }
    except Exception as e:
        logger.error("bandingkan_beasiswa gagal: %s", e)
        return {}
