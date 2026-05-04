"""
views/components/loading_mixin.py
Beaply - Mixin: Loading State untuk Views

Tambahkan ke views yang mengambil data dari DB agar UI tidak tampak freeze.

Cara pakai:
    class HalamanSaya(LoadingMixin, ctk.CTkFrame):
        def _build(self):
            self.show_loading()
            self.after(10, self._render)

        def _render(self):
            self.hide_loading()
            # ... render widget normal
"""
import customtkinter as ctk
from ui_utils import CARD_COLOR, TEXT_MUTED, TEXT_ACCENT


class LoadingMixin:
    """
    Mixin yang memberikan show_loading() / hide_loading() ke CTkFrame apapun.
    Tidak perlu inheritance tunggal — cukup ditambahkan ke class definition.
    """

    def show_loading(self, pesan: str = "Memuat data..."):
        """Tampilkan overlay loading di tengah frame."""
        self._loading_overlay = ctk.CTkFrame(
            self, fg_color=CARD_COLOR, corner_radius=16,
            border_width=1,
        )
        self._loading_overlay.place(relx=0.5, rely=0.5, anchor="center",
                                    relwidth=0.4, relheight=0.2)
        ctk.CTkLabel(
            self._loading_overlay,
            text="⏳",
            font=ctk.CTkFont(size=28),
        ).pack(pady=(16, 4))
        ctk.CTkLabel(
            self._loading_overlay,
            text=pesan,
            font=ctk.CTkFont(size=12),
            text_color=TEXT_MUTED,
        ).pack()

    def hide_loading(self):
        """Hapus overlay loading."""
        if hasattr(self, "_loading_overlay") and self._loading_overlay.winfo_exists():
            self._loading_overlay.destroy()

    def render_async(self, render_fn, pesan: str = "Memuat data..."):
        """
        Helper: tampilkan loading, lalu jalankan render_fn setelah 10ms.
        Ini cukup untuk membuat UI tetap responsif saat fetch data ringan.

        Contoh:
            def _build(self):
                self.render_async(self._render)

            def _render(self):
                data = ambil_data_dari_db()  # dipanggil setelah loading tampil
                # render widget...
        """
        self.show_loading(pesan)
        self.after(10, lambda: (self.hide_loading(), render_fn()))
