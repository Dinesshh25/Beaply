<<<<<<< HEAD
import customtkinter as ctk
from datetime import datetime, timedelta
from tkinter import messagebox
from utils.ui_utils import (
    BG_COLOR, CARD_COLOR, BORDER_COLOR, TEXT_DARK, TEXT_MUTED,
    BTN_PALE, BTN_PRIMARY, BTN_PRIMARY_HOVER, TEXT_ACCENT, konfirm_yesno
)
from model.notifikasi_model import (
    ambil_riwayat_notif as ambil_riwayat, tandai_dibaca, tandai_semua_dibaca, hapus_notifikasi
)

=======
"""
views/notifikasi_view.py
Beaply - View: Notifikasi Terpusat

Dipindahkan dari: Notifikasi_Terpusat/gui_notifikasi.py
Import sekarang dari controllers/notifikasi_controller.
"""
import customtkinter as ctk
from datetime import datetime, timedelta
from tkinter import messagebox
from ui_utils import (
    BG_COLOR, CARD_COLOR, BORDER_COLOR, TEXT_DARK, TEXT_MUTED,
    BTN_PALE, BTN_PRIMARY, BTN_PRIMARY_HOVER, TEXT_ACCENT, konfirm_yesno
)
from controllers.notifikasi_controller import (
    ambil_riwayat, tandai_dibaca, tandai_semua_dibaca, hapus_notifikasi
)


>>>>>>> 14a6b3f28e0f19b0c641fd9179026190a55f2248
# ════════════════════════════════════════════════════════════
# HALAMAN: Notifikasi
# ════════════════════════════════════════════════════════════

class HalamanNotifikasi(ctk.CTkFrame):
    """Notifications page — redesigned to match mockup."""
    def __init__(self, master, profil_id, bhs="id"):
        super().__init__(master, fg_color="transparent")
        self.profil_id = profil_id
        self._bhs = bhs
        self._filter = None  # None=all, 0=unread, 1=read
        self._build()

    def _build(self):
        self._refresh_notif()

    def _refresh_notif(self):
        for w in self.winfo_children():
            w.destroy()
        bhs = self._bhs

<<<<<<< HEAD
        # Filter tabs + action buttons
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=(0, 16))

        # Pill filter tabs
        tabs_frame = ctk.CTkFrame(top, fg_color="#E8EBE4", corner_radius=20,
                                  height=36)
=======
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=(0, 16))

        tabs_frame = ctk.CTkFrame(top, fg_color="#E8EBE4", corner_radius=20, height=36)
>>>>>>> 14a6b3f28e0f19b0c641fd9179026190a55f2248
        tabs_frame.pack(side="left")
        tabs_frame.pack_propagate(False)
        for label, fval in [("All", None), ("Read", 1), ("Unread", 0)]:
            is_active = self._filter == fval
            ctk.CTkButton(
                tabs_frame, text=label, width=80, height=32,
                corner_radius=16,
                fg_color=CARD_COLOR if is_active else "transparent",
                text_color=TEXT_DARK,
                hover_color=CARD_COLOR,
                font=ctk.CTkFont(size=12, weight="bold" if is_active else "normal"),
                command=lambda f=fval: self._set_filter(f),
            ).pack(side="left", padx=2, pady=2)

<<<<<<< HEAD
        # Action buttons
=======
>>>>>>> 14a6b3f28e0f19b0c641fd9179026190a55f2248
        ctk.CTkButton(top, text="Clear All", width=90, height=32,
                      fg_color="#F6E6E4", text_color="#D94040",
                      hover_color="#FCE0E0", corner_radius=10,
                      border_width=0, font=ctk.CTkFont(size=11),
                      command=self._hapus_semua).pack(side="right", padx=(6, 0))
        ctk.CTkButton(top, text="Mark All as Read", width=130, height=32,
                      fg_color=BTN_PRIMARY, text_color=TEXT_DARK,
                      hover_color=BTN_PRIMARY_HOVER, corner_radius=10,
                      font=ctk.CTkFont(size=11, weight="bold"),
                      command=self._tandai_semua).pack(side="right")

<<<<<<< HEAD
        # Notifications list
=======
>>>>>>> 14a6b3f28e0f19b0c641fd9179026190a55f2248
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        notifs = ambil_riwayat(self.profil_id)
        if self._filter is not None:
            notifs = [n for n in notifs if n.get("dibaca", 0) == self._filter]

        if not notifs:
            ctk.CTkLabel(scroll, text="No notifications yet.",
                         font=ctk.CTkFont(size=14), text_color=TEXT_MUTED,
                         justify="center").pack(pady=60)
            return

<<<<<<< HEAD
        # Group by date
=======
>>>>>>> 14a6b3f28e0f19b0c641fd9179026190a55f2248
        now = datetime.now()
        groups = {}
        for n in notifs:
            ts = n.get("dibuat_pada", "")
            try:
                dt = datetime.strptime(ts[:10], "%Y-%m-%d")
                diff = (now.date() - dt.date()).days
                if diff == 0:
                    group = "Today"
                elif diff == 1:
                    group = "Yesterday"
                elif diff < 7:
                    group = f"{diff} days ago"
                else:
                    group = dt.strftime("%b %d")
            except (ValueError, TypeError):
                group = "Older"
            groups.setdefault(group, []).append(n)

        for group_name, items in groups.items():
            ctk.CTkLabel(scroll, text=group_name,
                         font=ctk.CTkFont(size=14, weight="bold"),
                         text_color=TEXT_DARK).pack(anchor="w", pady=(12, 6))
            for n in items:
                is_unread = not n.get("dibaca", 0)
                card_bg = CARD_COLOR if is_unread else "#F8F6F4"
                card = ctk.CTkFrame(scroll, fg_color=card_bg, corner_radius=12,
                                    border_width=1, border_color=BORDER_COLOR)
                card.pack(fill="x", pady=3)
                inner = ctk.CTkFrame(card, fg_color="transparent")
                inner.pack(fill="x", padx=16, pady=12)
<<<<<<< HEAD
                # Title
=======
>>>>>>> 14a6b3f28e0f19b0c641fd9179026190a55f2248
                title_f = ctk.CTkFrame(inner, fg_color="transparent")
                title_f.pack(fill="x")
                ctk.CTkLabel(title_f, text=n.get("judul", "Notification"),
                             font=ctk.CTkFont(size=13, weight="bold" if is_unread else "normal"),
                             text_color=TEXT_DARK, anchor="w").pack(side="left")
                if is_unread:
                    dot = ctk.CTkFrame(title_f, fg_color=TEXT_ACCENT,
                                       width=8, height=8, corner_radius=4)
                    dot.pack(side="right")
<<<<<<< HEAD
                # Message
=======
>>>>>>> 14a6b3f28e0f19b0c641fd9179026190a55f2248
                ctk.CTkLabel(inner, text=n.get("pesan", ""),
                             font=ctk.CTkFont(size=11), text_color=TEXT_MUTED,
                             anchor="w", wraplength=600, justify="left").pack(
                    fill="x", pady=(2, 0))
<<<<<<< HEAD
                # Actions
=======
>>>>>>> 14a6b3f28e0f19b0c641fd9179026190a55f2248
                act_f = ctk.CTkFrame(inner, fg_color="transparent")
                act_f.pack(fill="x", pady=(6, 0))
                ts_text = n.get("dibuat_pada", "")[:16]
                ctk.CTkLabel(act_f, text=ts_text,
                             font=ctk.CTkFont(size=9), text_color=TEXT_MUTED).pack(side="left")
                if is_unread:
                    ctk.CTkButton(act_f, text="Mark Read", width=70, height=22,
                                  fg_color="transparent", border_width=1,
                                  border_color=BORDER_COLOR, text_color=TEXT_MUTED,
                                  corner_radius=6, font=ctk.CTkFont(size=9),
                                  command=lambda nid=n["id"]: self._mark_read(nid)).pack(side="right")

    def _set_filter(self, f):
        self._filter = f
        self._refresh_notif()

    def _tandai_semua(self):
        tandai_semua_dibaca(self.profil_id)
        self._refresh_notif()

    def _mark_read(self, nid):
        tandai_dibaca(nid)
        self._refresh_notif()

    def _hapus_semua(self):
        if konfirm_yesno(self, "Clear All", "Delete all notifications?"):
            for n in ambil_riwayat(self.profil_id):
                hapus_notifikasi(n["id"])
            self._refresh_notif()
