import re

with open('test_fiture.py', 'r', encoding='utf-8') as f:
    text = f.read()

profile_new_code = '''class HalamanProfil(ctk.CTkFrame):
    def __init__(self, master, profil_id, bhs="id"):
        super().__init__(master, fg_color="transparent")
        self.profil_id = profil_id
        self._bhs = bhs
        self._build()

    def _build(self):
        bhs = self._bhs
        profil = tampil_profil(self.profil_id)
        if not profil:
            return

        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="both", expand=True)

        left = ctk.CTkFrame(grid, fg_color="transparent", width=250)
        left.pack(side="left", fill="y", padx=(0, 10))
        left.pack_propagate(False)

        card1 = ctk.CTkFrame(left, fg_color=CARD_COLOR, corner_radius=15, border_width=1, border_color="#E0E0E0")
        card1.pack(fill="both", expand=True, pady=(0, 10))
        ctk.CTkLabel(card1, text="Profile\\nCompleteness", font=ctk.CTkFont(size=18, weight="bold"), justify="left", text_color=TEXT_DARK).pack(pady=20, padx=20, anchor="w")

        circ = ctk.CTkFrame(card1, fg_color=BG_COLOR, width=120, height=120, corner_radius=60)
        circ.pack(pady=10)
        circ.pack_propagate(False)
        ctk.CTkLabel(circ, text="100%", font=ctk.CTkFont(size=24, weight="bold"), text_color=TEXT_DARK).place(relx=0.5, rely=0.5, anchor="center")

        right = ctk.CTkFrame(grid, fg_color=CARD_COLOR, corner_radius=15, border_width=1, border_color="#E0E0E0")
        right.pack(side="left", fill="both", expand=True)

        header = ctk.CTkFrame(right, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(header, text="Personal Informations", font=ctk.CTkFont(size=18, weight="bold"), text_color=TEXT_DARK).pack(side="left")
        ctk.CTkButton(header, text=t("btn_edit_profile", bhs), fg_color=BTN_GREEN, text_color=TEXT_DARK).pack(side="right")

        scroll = ctk.CTkScrollableFrame(right, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        def baris(lbl, val):
            r = ctk.CTkFrame(scroll, fg_color="transparent")
            r.pack(fill="x", pady=5)
            ctk.CTkLabel(r, text=f"{t(lbl, bhs)}:", width=150, anchor="w", font=ctk.CTkFont(weight="bold"), text_color=TEXT_DARK).pack(side="left")
            ctk.CTkLabel(r, text=str(val), anchor="w", text_color=TEXT_DARK).pack(side="left", padx=10)

        baris("lb_nama",     profil["nama"])
        baris("lb_tgl",      format_tanggal(profil["tanggal_lahir"]))
        baris("lb_email",    profil["email"])
        baris("lb_jurusan",  profil["jurusan"])
        baris("lb_kampus",   profil["kampus"])
        baris("lb_jenjang",  profil["jenjang"])
        baris("lb_semester", profil["semester"])
        baris("lb_ip",       f"{profil['ip']:.2f}")
'''

text = re.sub(r'class HalamanProfil\(ctk\.CTkFrame\):.*?# ════════════════════════════════════════════════════════════\n# WINDOW SETTINGS \(Popup\)', profile_new_code + '\n# ════════════════════════════════════════════════════════════\n# WINDOW SETTINGS (Popup)', text, flags=re.DOTALL)

with open('test_fiture.py', 'w', encoding='utf-8') as f:
    f.write(text)
print('Replaced HalamanProfil!')
