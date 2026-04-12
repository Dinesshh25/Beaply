import customtkinter as ctk
from tkinter import messagebox

# Import core functionalities
from Rekomendasi.hitung_skor_cocok import hitung_skor_cocok
from Rekomendasi.analisis_peluang import analisis_peluang
from Rekomendasi.tampilan_rekomendasi import DAFTAR_BEASISWA

# Import profile fetcher (if integrated with the main application database)
try:
    from profile import tampil_profil
except ImportError:
    tampil_profil = None

class HalamanRekomendasi(ctk.CTkFrame):
    def __init__(self, master, profil_id=None):
        super().__init__(master, fg_color="transparent")
        self.profil_id = profil_id
        
        # Load user profile from DB if exists
        self.profil_user = {}
        if self.profil_id and tampil_profil:
            raw_profil = tampil_profil(self.profil_id)
            if raw_profil:
                self.profil_user = {
                    "jurusan": raw_profil.get("jurusan", ""),
                    "ipk": raw_profil.get("ip", 0.0),
                    "semester": raw_profil.get("semester", 1),
                    "organisasi": True, # Assume true or map from other fields
                    "penghasilan_ortu": 5000000 # Dummy value if not in DB
                }
        
        self._build_ui()

    def _build_ui(self):
        # ── Header ──
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 10))
        ctk.CTkLabel(header, text="Scholarship Recommendations", font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(header, text="Explore opportunities tailored just for you.", font=ctk.CTkFont(size=14), text_color="gray").pack(anchor="w")

        # ── Scrollable Container ──
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=16, pady=4)

        # ── Check if profile data exists ──
        if not self.profil_user:
            self._show_input_form(scroll)
        else:
            self._tampilkan_hasil_rekomendasi(scroll, self.profil_user)


    def _show_input_form(self, container):
        # Fallback manual input if no profile is passed
        card_form = ctk.CTkFrame(container, corner_radius=12)
        card_form.pack(fill="x", pady=10, padx=8)

        ctk.CTkLabel(card_form, text="Complete your data to get matches", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(20,10))
        
        # We simulate input_jurusan.py here
        f_jur = ctk.CTkFrame(card_form, fg_color="transparent")
        f_jur.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(f_jur, text="Major", width=120, anchor="w").pack(side="left")
        self.e_jurusan = ctk.CTkEntry(f_jur, width=250)
        self.e_jurusan.pack(side="left")

        f_ipk = ctk.CTkFrame(card_form, fg_color="transparent")
        f_ipk.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(f_ipk, text="Latest GPA", width=120, anchor="w").pack(side="left")
        self.e_ipk = ctk.CTkEntry(f_ipk, width=250)
        self.e_ipk.pack(side="left")

        f_sem = ctk.CTkFrame(card_form, fg_color="transparent")
        f_sem.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(f_sem, text="Semester", width=120, anchor="w").pack(side="left")
        self.e_sem = ctk.CTkEntry(f_sem, width=250)
        self.e_sem.pack(side="left")

        ctk.CTkButton(card_form, text="Calculate Matches", font=ctk.CTkFont(weight="bold"), fg_color="#7A9A8A", hover_color="#638072", command=self._submit_manual).pack(pady=(15, 20))

    def _submit_manual(self):
        try:
            self.profil_user = {
                "jurusan": self.e_jurusan.get(),
                "ipk": float(self.e_ipk.get()),
                "semester": int(self.e_sem.get()),
                "organisasi": True,
                "penghasilan_ortu": 5000000
            }
            # Refresh UI
            for widget in self.winfo_children():
                widget.destroy()
            self._build_ui()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for GPA and Semester.", parent=self)

    def _tampilkan_hasil_rekomendasi(self, container, p_user):
        # Hitung skor
        hasil = []
        for bea in DAFTAR_BEASISWA:
            skor = hitung_skor_cocok(p_user, bea)
            hasil.append({"beasiswa": bea, "skor": skor})
        hasil.sort(key=lambda x: x["skor"], reverse=True)

        # ── Kartu Trending (Auto Slide in original, we mock as horizontal or grid) ──
        ctk.CTkLabel(container, text="Top Matches For You", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(10, 5))
        
        grid_frame = ctk.CTkFrame(container, fg_color="transparent")
        grid_frame.pack(fill="x", pady=5)

        # Pastel colors like the image
        pastel_colors = ["#E8EBE4", "#F4EFE6", "#F6E6E4", "#E8EEE4"]
        
        for i, item in enumerate(hasil[:4]): # Top 4
            beasiswa = item["beasiswa"]
            skor = item["skor"]
            bg_color = pastel_colors[i % len(pastel_colors)]
            
            card = ctk.CTkFrame(grid_frame, corner_radius=15, fg_color=bg_color, width=160, height=200)
            card.pack(side="left", padx=8, pady=8, fill="y", expand=True)
            card.pack_propagate(False) # lock size

            ctk.CTkLabel(card, text=f"{skor}% Match", font=ctk.CTkFont(size=16, weight="bold"), text_color="#7A9A8A").pack(pady=(20, 5))
            ctk.CTkLabel(card, text=beasiswa['nama'], font=ctk.CTkFont(size=13, weight="bold"), text_color="#333", wraplength=130).pack(pady=(5, 10))
            ctk.CTkLabel(card, text=f"Min IPK: {beasiswa['min_ipk']}", font=ctk.CTkFont(size=11), text_color="#555").pack(anchor="w", padx=10)
            ctk.CTkLabel(card, text=f"Max Sem: {beasiswa['max_semester']}", font=ctk.CTkFont(size=11), text_color="#555").pack(anchor="w", padx=10)

        # ── Smart Tips ──
        ctk.CTkLabel(container, text="Smart Tips For You", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(25, 5))
        tips_card = ctk.CTkFrame(container, corner_radius=12, fg_color="white", border_width=1, border_color="#E0E0E0")
        tips_card.pack(fill="x", pady=5, padx=8)
        
        top_beasiswa = hasil[0]["beasiswa"]
        saran = analisis_peluang(p_user, top_beasiswa)
        
        ctk.CTkLabel(tips_card, text=f"Berdasarkan analisis beasiswa: {top_beasiswa['nama']}", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=16, pady=(16, 5))
        ctk.CTkLabel(tips_card, text=saran, font=ctk.CTkFont(size=12), text_color="#444", justify="left", wraplength=600).pack(anchor="w", padx=16, pady=(0, 16))
