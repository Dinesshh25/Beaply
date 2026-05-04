"""
views/rekomendasi_view.py
Beaply - View: Rekomendasi Beasiswa

Dipindahkan dari: Rekomendasi/gui_rekomendasi.py
Import sekarang dari controllers/rekomendasi_controller.
"""
import customtkinter as ctk
from tkinter import messagebox

from controllers.rekomendasi_controller import (
    get_profil_user, hitung_rekomendasi, get_analisis, get_daftar_beasiswa
)

try:
    from ui_utils import (
        BG_COLOR, CARD_COLOR, BORDER_COLOR, TEXT_DARK, TEXT_MUTED,
        TEXT_ACCENT, BTN_PRIMARY, BTN_PRIMARY_HOVER, PASTEL_COLORS
    )
    INPUT_BG = "#F0ECE8"
except ImportError:
    BG_COLOR          = "#FDF6F0"
    CARD_COLOR        = "#FFFFFF"
    BTN_PRIMARY       = "#A8C5B0"
    BTN_PRIMARY_HOVER = "#8FB898"
    TEXT_DARK         = "#2D2D2D"
    TEXT_MUTED        = "#888888"
    TEXT_ACCENT       = "#D4917B"
    BORDER_COLOR      = "#E8E0D8"
    INPUT_BG          = "#F0ECE8"
    PASTEL_COLORS     = ["#E8EBE4", "#F4EFE6", "#F6E6E4", "#E8EEE4", "#F0E8E4", "#E4EBE8"]



class HalamanRekomendasi(ctk.CTkFrame):
    """Recommendations page with premium gating."""
    def __init__(self, master, profil_id=None):
        super().__init__(master, fg_color="transparent")
        self.profil_id = profil_id
        self._is_premium = False  # TODO: check from user profile/preferences
        self._results = None

        self.profil_user = {}
        if self.profil_id:
            self.profil_user = get_profil_user(self.profil_id)

        self._build_initial()

    def _build_initial(self):
        """Show initial state with Get Recommendations button."""
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        hdr = ctk.CTkFrame(scroll, fg_color=PASTEL_COLORS[3], corner_radius=16,
                           border_width=1, border_color=BORDER_COLOR,
                           height=120)
        hdr.pack(fill="x", pady=(0, 16))
        hdr.pack_propagate(False)
        inner = ctk.CTkFrame(hdr, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=16)
        ctk.CTkLabel(inner,
                     text="Let us match you with scholarships\ntailored just for you!",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=TEXT_DARK, justify="left", anchor="w").pack(
            side="left", fill="x", expand=True)
        ctk.CTkButton(inner, text="Get Recommendations",
                      fg_color=BTN_PRIMARY, hover_color=BTN_PRIMARY_HOVER,
                      text_color=TEXT_DARK, corner_radius=10,
                      font=ctk.CTkFont(size=12, weight="bold"),
                      height=38, width=180,
                      command=self._do_calculate).pack(side="right")

        if not self.profil_user:
            self._show_input_form(scroll)
        else:
            info_card = ctk.CTkFrame(scroll, fg_color=CARD_COLOR, corner_radius=14,
                                     border_width=1, border_color=BORDER_COLOR)
            info_card.pack(fill="x", pady=8)
            ctk.CTkLabel(info_card,
                         text="Click 'Get Recommendations' to analyze your profile\nand find the best scholarship matches for you.",
                         font=ctk.CTkFont(size=13), text_color=TEXT_MUTED,
                         justify="center").pack(pady=40)
            if not self._is_premium:
                pro_card = ctk.CTkFrame(scroll, fg_color=PASTEL_COLORS[1], corner_radius=14,
                                        border_width=1, border_color=BORDER_COLOR)
                pro_card.pack(fill="x", pady=8)
                ctk.CTkLabel(pro_card, text="Upgrade to Beaply Pro",
                             font=ctk.CTkFont(size=14, weight="bold"),
                             text_color=TEXT_DARK).pack(pady=(16, 4))
                ctk.CTkLabel(pro_card,
                             text="Free users can only see the #1 best match.\nUpgrade to Pro to unlock all recommendation scores!",
                             font=ctk.CTkFont(size=11), text_color=TEXT_MUTED,
                             justify="center").pack(padx=16, pady=(0, 16))

    def _show_input_form(self, container):
        card = ctk.CTkFrame(container, fg_color=CARD_COLOR, corner_radius=14,
                            border_width=1, border_color=BORDER_COLOR)
        card.pack(fill="x", pady=8)
        ctk.CTkLabel(card, text="Complete your data to get matches",
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=TEXT_DARK).pack(pady=(20, 12))
        for label, attr in [("Major", "e_jurusan"), ("Latest GPA", "e_ipk"),
                            ("Semester", "e_sem")]:
            f = ctk.CTkFrame(card, fg_color="transparent")
            f.pack(fill="x", padx=24, pady=4)
            ctk.CTkLabel(f, text=label, width=120, anchor="w",
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=TEXT_DARK).pack(side="left")
            e = ctk.CTkEntry(f, height=36, corner_radius=8,
                             fg_color=INPUT_BG, border_width=0,
                             text_color=TEXT_DARK, width=250)
            e.pack(side="left", fill="x", expand=True)
            setattr(self, attr, e)

    def _do_calculate(self):
        if not self.profil_user:
            try:
                self.profil_user = {
                    "jurusan": self.e_jurusan.get(),
                    "ipk": float(self.e_ipk.get()),
                    "semester": int(self.e_sem.get()),
                    "organisasi": True,
                    "penghasilan_ortu": 5000000
                }
            except (ValueError, AttributeError):
                messagebox.showerror("Error", "Please enter valid data first.", parent=self)
                return

        hasil = hitung_rekomendasi(self.profil_user)
        self._results = hasil

        for w in self.winfo_children():
            w.destroy()
        self._build_results()

    def _build_results(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        hdr = ctk.CTkFrame(scroll, fg_color=PASTEL_COLORS[3], corner_radius=16,
                           border_width=1, border_color=BORDER_COLOR)
        hdr.pack(fill="x", pady=(0, 16))
        inner = ctk.CTkFrame(hdr, fg_color="transparent")
        inner.pack(fill="x", padx=24, pady=16)
        ctk.CTkLabel(inner, text="Your Personalized Matches",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=TEXT_DARK, anchor="w").pack(side="left")
        ctk.CTkButton(inner, text="Refresh",
                      fg_color=CARD_COLOR, text_color=TEXT_DARK,
                      hover_color=BORDER_COLOR, corner_radius=8,
                      border_width=1, border_color=BORDER_COLOR,
                      font=ctk.CTkFont(size=11), height=30, width=80,
                      command=self._do_calculate).pack(side="right")

        ctk.CTkLabel(scroll,
                     text=f"Found {len(self._results)} scholarship matches",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_DARK, anchor="w").pack(fill="x", pady=(0, 8))

        for i, item in enumerate(self._results):
            bea = item["beasiswa"]
            skor = item["skor"]
            is_locked = (i > 0 and not self._is_premium)

            card = ctk.CTkFrame(scroll, fg_color=CARD_COLOR, corner_radius=14,
                                border_width=1, border_color=BORDER_COLOR)
            card.pack(fill="x", pady=4)
            card_inner = ctk.CTkFrame(card, fg_color="transparent")
            card_inner.pack(fill="x", padx=20, pady=14)

            left = ctk.CTkFrame(card_inner, fg_color="transparent")
            left.pack(side="left", fill="x", expand=True)

            rank_f = ctk.CTkFrame(left, fg_color="transparent")
            rank_f.pack(fill="x")
            ctk.CTkLabel(rank_f, text=f"#{i+1}",
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=TEXT_ACCENT).pack(side="left")
            if i == 0:
                ctk.CTkLabel(rank_f, text="  Best Match",
                             font=ctk.CTkFont(size=10, weight="bold"),
                             text_color=BTN_PRIMARY).pack(side="left")

            ctk.CTkLabel(left, text=bea["nama"],
                         font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=TEXT_DARK, anchor="w").pack(fill="x", pady=(2, 0))
            info = f"Min IPK: {bea['min_ipk']}  |  Max Sem: {bea['max_semester']}"
            ctk.CTkLabel(left, text=info,
                         font=ctk.CTkFont(size=10), text_color=TEXT_MUTED,
                         anchor="w").pack(fill="x")

            bg = PASTEL_COLORS[i % len(PASTEL_COLORS)]
            badge = ctk.CTkFrame(card_inner, fg_color=bg, corner_radius=12,
                                 width=72, height=44)
            badge.pack(side="right")
            badge.pack_propagate(False)

            if is_locked:
                ctk.CTkLabel(badge, text="[Locked]",
                             font=ctk.CTkFont(size=12, weight="bold"),
                             text_color=TEXT_MUTED).place(relx=0.5, rely=0.5, anchor="center")
                lock_f = ctk.CTkFrame(card, fg_color=PASTEL_COLORS[1])
                lock_f.pack(fill="x", padx=20, pady=(0, 8))
                ctk.CTkLabel(lock_f, text="Upgrade to Pro to see match score",
                             font=ctk.CTkFont(size=9),
                             text_color=TEXT_MUTED).pack(side="left", padx=8, pady=2)
            else:
                badge_color = BTN_PRIMARY if skor >= 60 else TEXT_ACCENT
                ctk.CTkLabel(badge, text=f"{skor}%",
                             font=ctk.CTkFont(size=15, weight="bold"),
                             text_color=badge_color).place(relx=0.5, rely=0.5, anchor="center")

        if self._results:
            top_bea = self._results[0]["beasiswa"]
            saran = get_analisis(self.profil_user, top_bea)

            ctk.CTkLabel(scroll, text="Smart Tips For You",
                         font=ctk.CTkFont(size=15, weight="bold"),
                         text_color=TEXT_DARK, anchor="w").pack(fill="x", pady=(16, 8))
            tips_card = ctk.CTkFrame(scroll, fg_color=CARD_COLOR, corner_radius=14,
                                     border_width=1, border_color=BORDER_COLOR)
            tips_card.pack(fill="x", pady=4)
            ctk.CTkLabel(tips_card,
                         text=f"Based on your #1 match: {top_bea['nama']}",
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=TEXT_DARK).pack(anchor="w", padx=20, pady=(16, 4))
            ctk.CTkLabel(tips_card, text=saran,
                         font=ctk.CTkFont(size=11), text_color=TEXT_MUTED,
                         justify="left", wraplength=600, anchor="w").pack(
                anchor="w", padx=20, pady=(0, 16))
