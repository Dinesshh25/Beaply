import customtkinter as ctk
from tkinter import messagebox
from PusatBantuan.kirim_feedback import kirim_feedback

class HalamanHelpCenter(ctk.CTkFrame):
    def __init__(self, master, profil_id=None):
        super().__init__(master, fg_color="transparent")
        self.profil_id = profil_id
        self._build_ui()

    def _build_ui(self):
        # ── Header ──
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 10))
        ctk.CTkLabel(header, text="FAQ & Help Center", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")

        # ── Scrollable Area ──
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=16, pady=4)

        # Container for layout (Left: FAQ, Right: Report Form)
        # Using a grid-like structure within the scrollable frame
        kiri = ctk.CTkFrame(scroll, fg_color="transparent")
        kanan = ctk.CTkFrame(scroll, fg_color="transparent")
        kiri.pack(side="left", fill="both", expand=True, padx=(0, 10))
        kanan.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # ── Kiri: FAQ ──
        ctk.CTkLabel(kiri, text="Frequently Asked Questions", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=(0, 10))
        
        faqs = [
            ("Bagaimana cara profil saya dinilai?", "Sistem menghitung persentase kecocokan berdasarkan IPK, semester aktif, dan syarat dari penyedia beasiswa."),
            ("Apa itu Smart Tips?", "Smart Tips adalah saran otomatis yang dihasilkan dari profil Anda untuk meningkatkan peluang melamar beasiswa."),
            ("Apakah saya harus mengisi skor TOEFL/IELTS?", "Tidak wajib jika beasiswa yang Anda inisiasi tidak memintanya. Tapi sangat disarankan untuk memperbesar peluang."),
            ("Apakah progres saya tersimpan otomatis?", "Ya, selama Anda sudah menyimpan profil di awal, data akan terus diperbarui dan tersimpan.")
        ]
        
        for p, j in faqs:
            card = ctk.CTkFrame(kiri, corner_radius=10, fg_color="#F8ECE1") # Using slightly pastel color matching the aesthetic
            card.pack(fill="x", pady=6)
            ctk.CTkLabel(card, text="Q: " + p, font=ctk.CTkFont(size=14, weight="bold"), text_color="#5D4037", wraplength=350, justify="left").pack(anchor="w", padx=12, pady=(10, 2))
            ctk.CTkLabel(card, text="A: " + j, font=ctk.CTkFont(size=13), text_color="#5D4037", wraplength=350, justify="left").pack(anchor="w", padx=12, pady=(2, 10))

        # ── Kanan: Form Pelaporan ──
        card_form = ctk.CTkFrame(kanan, corner_radius=12)
        card_form.pack(fill="both", expand=True, pady=(0, 20))
        
        ctk.CTkLabel(card_form, text="Report an Issue or Feedback", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(card_form, text="Category", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=20, pady=(5, 0))
        self.kategori_dropdown = ctk.CTkComboBox(card_form, values=["bug", "saran", "pertanyaan"], width=250)
        self.kategori_dropdown.set("pertanyaan")
        self.kategori_dropdown.pack(anchor="w", padx=20, pady=(5, 10))

        ctk.CTkLabel(card_form, text="Message", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=20, pady=(5, 0))
        self.pesan_box = ctk.CTkTextbox(card_form, width=250, height=120)
        self.pesan_box.pack(anchor="w", padx=20, pady=(5, 15))

        btn_submit = ctk.CTkButton(card_form, text="Submit Report", font=ctk.CTkFont(weight="bold"), fg_color="#7A9A8A", hover_color="#638072", command=self._submit_laporan)
        btn_submit.pack(anchor="w", padx=20, pady=(0, 20))

    def _submit_laporan(self):
        kategori = self.kategori_dropdown.get()
        pesan = self.pesan_box.get("1.0", "end-1c").strip()
        user_id = self.profil_id if self.profil_id else "Guest"

        if not pesan:
            messagebox.showwarning("Peringatan", "Pesan tidak boleh kosong!", parent=self)
            return
            
        sukses = kirim_feedback(user_id, kategori, pesan)
        if sukses:
            messagebox.showinfo("Berhasil", "Laporan/Umpan balik Anda telah terkirim. Terima kasih!", parent=self)
            self.pesan_box.delete("1.0", "end")
        else:
            messagebox.showerror("Gagal", "Terjadi kelasahan saat mengirim laporan.", parent=self)
