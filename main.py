"""
main.py
Beaply — Aplikasi Desktop Manajemen Profil & Beasiswa
GUI: CustomTkinter
Fitur: Autentikasi, Profil, Beasiswa, Settings,
       Tracker & Pengingat, Eksplorasi & Navigasi, Notifikasi Terpusat
"""

import sys, traceback, logging
logging.basicConfig(filename='error.log', level=logging.ERROR,
                    format='%(asctime)s %(message)s', filemode='w')

import customtkinter as ctk

from database import init_db
from Profile_dan_Setting.settings import ambil_preferensi
from ui_utils import apply_pref
from Autentikasi_dan_Keamanan import init_auth, logout_pengguna

# Import GUI pages that are used directly in BeaplyApp
from Autentikasi_dan_Keamanan.gui_auth import HalamanAuth, HalamanLupaSandi
from Profile_dan_Setting.gui_profile import HalamanHome, HalamanBuatProfil
from gui_dashboard import LayoutDenganSidebar

init_db()
init_auth()

PROFIL_AKTIF_ID = None

class BeaplyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Beaply — Insight Beasiswa")
        self.geometry("960x720")
        self.minsize(860, 600)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self._current_user = None
        # Log Tkinter callback errors
        self.report_callback_exception = self._on_tk_error
        self._go_auth()

    def _on_tk_error(self, exc_type, exc_value, exc_tb):
        err = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
        logging.error(err)
        print(err, file=sys.stderr)

    def _clear(self):
        for w in self.winfo_children(): w.destroy()

    # ── Navigasi: Autentikasi ─────────────────────────────
    def _go_auth(self):
        self._clear()
        self._current_user = None
        HalamanAuth(self,
                    login_callback=self._on_login_success,
                    lupa_sandi_callback=self._go_lupa_sandi
                    ).pack(fill="both", expand=True)

    def _on_login_success(self, user_profile: dict):
        self._current_user = user_profile
        self._go_home_after_login()

    def _go_lupa_sandi(self):
        self._clear()
        HalamanLupaSandi(self,
                         kembali_callback=self._go_auth,
                         reset_selesai_callback=self._go_auth,
                         ).pack(fill="both", expand=True)

    # ── Navigasi: Utama (setelah auth) ────────────────────
    def _go_home_after_login(self):
        self._clear()
        user_id = self._current_user["id"] if self._current_user else None
        HalamanHome(self,
                    buka_buat=self._go_buat_profil,
                    buka_dashboard=self._go_dashboard,
                    user_id=user_id,
                    ).pack(fill="both", expand=True)

    def _go_buat_profil(self):
        self._clear()
        user_id = self._current_user["id"] if self._current_user else None
        HalamanBuatProfil(self,
                          selesai_callback=self._go_dashboard,
                          kembali_callback=self._go_home_after_login,
                          user_id=user_id,
                          ).pack(fill="both", expand=True)

    def _go_dashboard(self, profil_id=None):
        global PROFIL_AKTIF_ID
        if profil_id: PROFIL_AKTIF_ID = profil_id
        self._clear()

        def _apply_and_layout():
            pref = ambil_preferensi(PROFIL_AKTIF_ID)
            try:
                apply_pref(pref)
            except Exception as e:
                import logging
                logging.getLogger().error("Scaling error ignored: " + str(e))
                
            LayoutDenganSidebar(self, PROFIL_AKTIF_ID,
                                logout_callback=self._go_logout
                                ).pack(fill="both", expand=True)

        self.after(10, _apply_and_layout)

    def _go_logout(self):
        global PROFIL_AKTIF_ID
        PROFIL_AKTIF_ID = None
        logout_pengguna()
        self._current_user = None
        ctk.set_appearance_mode("light")
        self._go_auth()


if __name__ == "__main__":
    app = BeaplyApp()
    app.mainloop()