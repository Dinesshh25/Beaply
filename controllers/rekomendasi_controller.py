"""
controllers/rekomendasi_controller.py
Beaply - Controller: Rekomendasi Beasiswa

Mediator antara views/rekomendasi_view dan models/rekomendasi_model.
"""

import logging

from models.rekomendasi_model import (
    get_daftar_beasiswa_rekomendasi,
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
            for bea in get_daftar_beasiswa_rekomendasi()
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
    return get_daftar_beasiswa_rekomendasi()


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
        min_ipk = bea.get("min_ipk", 0) or 0
        kriteria.append({
            "label": "Min. IPK",
            "nilai": f"{min_ipk:.2f}" if min_ipk > 0 else "Tidak ada",
            "user": f"{ipk_user:.2f}",
            "lulus": ipk_user >= min_ipk if min_ipk > 0 else True,
        })

        # Jenjang
        jenjang_user = profil.get("jenjang", "S1") or "S1"
        jenjang_bea = bea.get("jenjang", "")
        kriteria.append({
            "label": "Jenjang",
            "nilai": jenjang_bea or "Semua",
            "user": jenjang_user,
            "lulus": jenjang_user.upper() in jenjang_bea.upper() if jenjang_bea else True,
        })

        # Deadline
        deadline = bea.get("deadline", "")
        if deadline:
            from datetime import datetime
            try:
                days = (datetime.strptime(deadline, "%Y-%m-%d").date() - datetime.now().date()).days
                dl_status = f"{days} hari lagi" if days >= 0 else "Expired"
                dl_lulus = days >= 0
            except (ValueError, TypeError):
                dl_status = deadline
                dl_lulus = True
            kriteria.append({
                "label": "Deadline",
                "nilai": deadline,
                "user": dl_status,
                "lulus": dl_lulus,
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

        # Penghasilan ortu — only show if beasiswa has a meaningful limit
        penghasilan = profil.get("penghasilan_ortu", 0) or 0
        max_penghasilan = bea.get("max_penghasilan_ortu", 999_999_999)
        if max_penghasilan < 999_999_999:
            kriteria.append({
                "label": "Max Penghasilan",
                "nilai": f"Rp {max_penghasilan:,.0f}".replace(",", "."),
                "user": f"Rp {penghasilan:,.0f}".replace(",", ".") if penghasilan > 0 else "Belum diisi",
                "lulus": penghasilan <= max_penghasilan if penghasilan > 0 else True,
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
