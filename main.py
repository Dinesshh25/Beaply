import customtkinter as ctk

from model.auth_model import init_auth_db
from controllers.auth_controller import AuthController
from views.auth_view import HalamanAuth, HalamanLupaSandi

from views.dashboard_view import LayoutDenganSidebar

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

    def get_container(self):
        # Bersihkan layar sebelumnya setiap kali pindah halaman utama
        for widget in self.container.winfo_children():
            widget.destroy()
        return self.container

    def show_view(self, view_instance):
        view_instance.pack(fill="both", expand=True)

    def on_login_success(self, user_profile):
        """Callback dieksekusi oleh AuthController ketika login berhasil."""
        self.current_user = user_profile
        print(f"Login sukses untuk {user_profile['email']}")
        
        self._goToOldDashboard()

    def _goToOldDashboard(self):
        container = self.get_container()
        user_id = self.current_user["id"]
        
        layout = LayoutDenganSidebar(container, user_id, logout_callback=self._on_logout)
        layout.pack(fill="both", expand=True)

    def _showPlaceholder(self):
        container = self.get_container()
        ctk.CTkLabel(container, text="Login Berhasil!\nNamun dashboard belum di-refactor MVC dan modul lama tidak ditemukan.", font=ctk.CTkFont(size=20)).pack(expand=True)
        ctk.CTkButton(container, text="Logout", command=self._on_logout).pack(pady=20)

    def _on_logout(self):
        self.current_user = None
        self.auth_controller.tampilkan_auth()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = MainController()
    app.run()
