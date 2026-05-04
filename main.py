"""
main.py
Beaply — Aplikasi Desktop Manajemen Profil & Beasiswa
GUI: CustomTkinter
Fitur: Autentikasi, Profil, Beasiswa, Settings,
       Tracker & Pengingat, Eksplorasi & Navigasi, Notifikasi Terpusat
"""

import sys, traceback, logging

# ── Logging Configuration ────────────────────────────────────
_log_fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
_log_date = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(
    level=logging.DEBUG,
    format=_log_fmt,
    datefmt=_log_date,
    handlers=[
        logging.FileHandler("beaply.log", encoding="utf-8", mode="a"),
        logging.StreamHandler(sys.stdout),          # tampil di terminal saat dev
    ],
)
# Hanya tampilkan ERROR ke atas di console (bukan DEBUG/INFO)
logging.getLogger().handlers[1].setLevel(logging.WARNING)
logger = logging.getLogger("beaply.main")
logger.info("=== Beaply started ===")

import customtkinter as ctk

from database import init_db
from controllers.profil_controller import ambil_preferensi
from ui_utils import apply_pref
from controllers.auth_controller import init_auth, logout_pengguna, set_current_user

# Import GUI pages dari views/ (MVC)
from views.auth_view import HalamanAuth, HalamanLupaSandi
from views.profil_view import HalamanHome, HalamanBuatProfil
from gui_dashboard import LayoutDenganSidebar

class MainController:
    """
    Main Controller yang bertanggung jawab untuk mendirikan aplikasi (root window)
    serta navigasi antar controller/fitur.
    """
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Beaply — MVC Version")
        self.root.geometry("960x720")
        self.root.minsize(860, 600)
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        self.current_user = None
        
        # Setup container untuk menaruh View
        self.container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        # Inisialisasi Database Model
        init_auth_db()

        # Mulai dengan memanggil AuthController
        self.auth_controller = AuthController(self)
        self.auth_controller.mount_views(HalamanAuth, HalamanLupaSandi)
        self.auth_controller.tampilkan_auth()

    def _on_login_success(self, user_profile: dict):
        self._current_user = user_profile
        from controllers.auth_controller import set_current_user
        set_current_user(user_profile)
        self._go_home_after_login()

    def _go_lupa_sandi(self):
        self._clear()
        HalamanLupaSandi(self,
                         kembali_callback=self._go_auth,
                         ).pack(fill="both", expand=True)

    # ── Navigasi: Utama (setelah auth) ────────────────────
    def _go_home_after_login(self):
        self._clear()
        user_id = self._current_user.get("user_id") if self._current_user else None
        HalamanHome(self,
                    buka_buat=self._go_buat_profil,
                    buka_dashboard=self._go_dashboard,
                    user_id=user_id,
                    ).pack(fill="both", expand=True)

    def _go_buat_profil(self):
        self._clear()
        user_id = self._current_user.get("user_id") if self._current_user else None
        HalamanBuatProfil(self,
                          selesai_callback=self._go_dashboard,
                          kembali_callback=self._go_home_after_login,
                          user_id=user_id,
                          ).pack(fill="both", expand=True)

    def _showPlaceholder(self):
        container = self.get_container()
        ctk.CTkLabel(container, text="Login Berhasil!\nNamun dashboard belum di-refactor MVC dan modul lama tidak ditemukan.", font=ctk.CTkFont(size=20)).pack(expand=True)
        ctk.CTkButton(container, text="Logout", command=self._on_logout).pack(pady=20)

    def _go_logout(self):
        global PROFIL_AKTIF_ID
        PROFIL_AKTIF_ID = None
        if self._current_user:
            session_token = self._current_user.get("session_token", "")
            if session_token:
                logout_pengguna(session_token)
        self._current_user = None
        set_current_user(None)
        ctk.set_appearance_mode("light")
        self._go_auth()


if __name__ == "__main__":
    app = MainController()
    app.run()
