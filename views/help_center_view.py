import customtkinter as ctk
from tkinter import messagebox
from model.help_center_model import kirim_feedback

BG_COLOR = "#FDF6F0"
CARD_COLOR = "#FFFFFF"
BTN_PRIMARY = "#A8C5B0"
BTN_PRIMARY_HOVER = "#8FB898"
TEXT_DARK = "#2D2D2D"
TEXT_MUTED = "#888888"
TEXT_ACCENT = "#D4917B"
BORDER_COLOR = "#E8E0D8"
INPUT_BG = "#F0ECE8"


class HalamanHelpCenter(ctk.CTkFrame):
    """FAQ & Help Center — redesigned to match mockup."""
    def __init__(self, master, profil_id=None):
        super().__init__(master, fg_color="transparent")
        self.profil_id = profil_id
        self._build_ui()

    def _build_ui(self):
        # Two-column layout
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True)

        # LEFT: FAQ
        left = ctk.CTkScrollableFrame(main, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))

        ctk.CTkLabel(left, text="Frequently Asked Questions",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=TEXT_DARK).pack(anchor="w", pady=(0, 12))

        faqs = [
            ("Bagaimana cara profil saya dinilai?",
             "Sistem menghitung persentase kecocokan berdasarkan IPK, semester aktif, dan syarat dari penyedia beasiswa."),
            ("Apa itu Smart Tips?",
             "Smart Tips adalah saran otomatis yang dihasilkan dari profil Anda untuk meningkatkan peluang melamar beasiswa."),
            ("Apakah saya harus mengisi skor TOEFL/IELTS?",
             "Tidak wajib jika beasiswa yang Anda inisiasi tidak memintanya. Tapi sangat disarankan untuk memperbesar peluang."),
            ("Apakah progres saya tersimpan otomatis?",
             "Ya, selama Anda sudah menyimpan profil di awal, data akan terus diperbarui dan tersimpan."),
            ("Bagaimana cara kerja fitur Rekomendasi?",
             "Fitur rekomendasi mencocokkan profil Anda dengan database beasiswa dan memberikan skor kecocokan untuk setiap beasiswa."),
            ("Apa itu Beaply Pro?",
             "Beaply Pro adalah fitur premium yang membuka akses semua skor rekomendasi beasiswa dan fitur-fitur advanced lainnya."),
        ]

        for q, a in faqs:
            card = ctk.CTkFrame(left, fg_color=CARD_COLOR, corner_radius=14,
                                border_width=1, border_color=BORDER_COLOR)
            card.pack(fill="x", pady=5)
            ctk.CTkLabel(card, text=f"Q: {q}",
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=TEXT_DARK, wraplength=440,
                         justify="left", anchor="w").pack(
                anchor="w", padx=16, pady=(14, 4))
            ctk.CTkLabel(card, text=f"A: {a}",
                         font=ctk.CTkFont(size=12),
                         text_color=TEXT_MUTED, wraplength=440,
                         justify="left", anchor="w").pack(
                anchor="w", padx=16, pady=(0, 14))

        # RIGHT: Report form
        right = ctk.CTkFrame(main, fg_color="#E8EBE4", corner_radius=16,
                             width=300, border_width=1, border_color=BORDER_COLOR)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        ctk.CTkLabel(right, text="Report an Issue or\nFeedback",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=TEXT_DARK, justify="center").pack(
            pady=(28, 20))

        ctk.CTkLabel(right, text="Category",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=TEXT_DARK).pack(anchor="w", padx=20)
        self.kategori_dropdown = ctk.CTkComboBox(
            right, values=["Bug Report", "Suggestion", "Question", "Other"],
            width=240, height=34, corner_radius=10,
            fg_color=CARD_COLOR, border_width=1, border_color=BORDER_COLOR)
        self.kategori_dropdown.set("Question")
        self.kategori_dropdown.pack(padx=20, pady=(4, 16))

        ctk.CTkLabel(right, text="Message",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=TEXT_DARK).pack(anchor="w", padx=20)
        self.pesan_box = ctk.CTkTextbox(
            right, width=240, height=160, corner_radius=10,
            fg_color=CARD_COLOR, border_width=1, border_color=BORDER_COLOR,
            text_color=TEXT_DARK)
        self.pesan_box.pack(padx=20, pady=(4, 20))

        ctk.CTkButton(right, text="Submit Report", width=200, height=38,
                      fg_color="#F6D6D0", hover_color="#F0C0B8",
                      text_color=TEXT_DARK, corner_radius=10,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._submit_laporan).pack(pady=(0, 24))

    def _submit_laporan(self):
        kategori = self.kategori_dropdown.get()
        pesan = self.pesan_box.get("1.0", "end-1c").strip()
        user_id = self.profil_id if self.profil_id else "Guest"

        if not pesan:
            messagebox.showwarning("Warning", "Message cannot be empty!", parent=self)
            return

        sukses = kirim_feedback(user_id, kategori, pesan)
        if sukses:
            messagebox.showinfo("Success", "Your report has been submitted. Thank you!", parent=self)
            self.pesan_box.delete("1.0", "end")
        else:
            messagebox.showerror("Error", "Failed to submit report.", parent=self)
