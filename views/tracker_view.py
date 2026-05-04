<<<<<<< HEAD
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from utils.ui_utils import (
    t, BG_COLOR, CARD_COLOR, BORDER_COLOR, TEXT_DARK, TEXT_MUTED,
    BTN_PALE, BTN_PRIMARY, BTN_PRIMARY_HOVER, TEXT_ACCENT
)
from model.tracker_model import (
    tampilan_kalender, tambah_penanda_manual, ubah_status,
    update_bookmark_tracker as toggle_bookmark, ambil_semua_tracker, ambil_tracker_by_id,
    hapus_tracker, format_status, warna_status,
    format_deadline_display, buat_pengingat_otomatis, STATUS_LIST
)
from model.notifikasi_model import tambah_notifikasi
=======
"""
views/tracker_view.py
Beaply - View: Tracker & Pengingat Beasiswa

Dipindahkan dari: Tracker_dan_Pengingat/gui_tracker.py
Import sekarang dari controllers/ bukan dari legacy folder.
"""
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from ui_utils import (
    t, BG_COLOR, CARD_COLOR, BORDER_COLOR, TEXT_DARK, TEXT_MUTED,
    BTN_PALE, BTN_PRIMARY, BTN_PRIMARY_HOVER, TEXT_ACCENT
)
from controllers.tracker_controller import (
    tampilan_kalender, tambah_penanda_manual, ubah_status,
    toggle_bookmark, get_semua_tracker, get_tracker_by_id,
    hapus, fmt_status, clr_status, fmt_deadline,
    buat_pengingat_otomatis,
    STATUS_LIST, ambil_semua_tracker, ambil_tracker_by_id,
)
from controllers.notifikasi_controller import buat_notifikasi_status


# Alias untuk backward compatibility
format_status = fmt_status
warna_status = clr_status
format_deadline_display = fmt_deadline
hapus_tracker = hapus

>>>>>>> 14a6b3f28e0f19b0c641fd9179026190a55f2248

# ════════════════════════════════════════════════════════════
# HALAMAN: Tracker Pendaftaran
# ════════════════════════════════════════════════════════════

class HalamanTracker(ctk.CTkFrame):
    def __init__(self, master, profil_id, bhs="id"):
        super().__init__(master, fg_color="transparent")
        self.profil_id = profil_id
        self._bhs = bhs
        self._build()

    def _build(self):
        self._refresh_list()

    def _refresh_list(self):
        for w in self.winfo_children():
            w.destroy()
        bhs = self._bhs

<<<<<<< HEAD
        # Header
=======
>>>>>>> 14a6b3f28e0f19b0c641fd9179026190a55f2248
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=8, pady=(8, 4))
        ctk.CTkLabel(hdr, text=t("t_judul", bhs),
                     font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")
        ctk.CTkButton(hdr, text=t("t_tambah", bhs), width=140, height=32,
                      font=ctk.CTkFont(size=12, weight="bold"),
                      command=self._form_tambah).pack(side="right")

<<<<<<< HEAD
        # List tracker
=======
>>>>>>> 14a6b3f28e0f19b0c641fd9179026190a55f2248
        trackers = ambil_semua_tracker(self.profil_id)
        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=8, pady=4)

        if not trackers:
            ctk.CTkLabel(scroll, text="Belum ada tracker. Tambahkan yang pertama!",
                         text_color="gray50",
                         font=ctk.CTkFont(size=12)).pack(pady=40)
            return

        for tr in trackers:
            self._card_tracker(scroll, tr)

    def _card_tracker(self, parent, tr):
        bhs = self._bhs
        card = ctk.CTkFrame(parent, corner_radius=10)
        card.pack(fill="x", pady=4)

<<<<<<< HEAD
        # Header row
=======
>>>>>>> 14a6b3f28e0f19b0c641fd9179026190a55f2248
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=12, pady=(8, 2))
        ctk.CTkLabel(top, text=tr["nama_beasiswa"],
                     font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")

<<<<<<< HEAD
        # Bookmark star
=======
>>>>>>> 14a6b3f28e0f19b0c641fd9179026190a55f2248
        bm_text = "⭐" if tr["dibookmark"] else "☆"
        ctk.CTkButton(top, text=bm_text, width=30, height=26,
                      fg_color="transparent",
                      command=lambda tid=tr["id"]: self._toggle_bm(tid)).pack(side="right")

<<<<<<< HEAD
        # Status badge
        status_lbl = format_status(tr["status"], bhs)
        status_clr = warna_status(tr["status"])
=======
        status_lbl = fmt_status(tr["status"], bhs)
        status_clr = clr_status(tr["status"])
>>>>>>> 14a6b3f28e0f19b0c641fd9179026190a55f2248
        ctk.CTkLabel(top, text=f"  {status_lbl}  ",
                     font=ctk.CTkFont(size=10),
                     text_color="white",
                     fg_color=status_clr,
                     corner_radius=4).pack(side="right", padx=4)

<<<<<<< HEAD
        # Info row
        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(fill="x", padx=12, pady=2)
        dl_text = format_deadline_display(tr["deadline"]) if tr.get("deadline") else "Tidak ada deadline"
=======
        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(fill="x", padx=12, pady=2)
        dl_text = fmt_deadline(tr["deadline"]) if tr.get("deadline") else "Tidak ada deadline"
>>>>>>> 14a6b3f28e0f19b0c641fd9179026190a55f2248
        ctk.CTkLabel(info, text=f"📅 {dl_text}",
                     font=ctk.CTkFont(size=10),
                     text_color="gray50").pack(side="left")

        if tr.get("catatan"):
            ctk.CTkLabel(info, text=f"📝 {tr['catatan'][:40]}",
                         font=ctk.CTkFont(size=10),
                         text_color="gray50").pack(side="left", padx=12)

<<<<<<< HEAD
        # Action buttons
        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.pack(fill="x", padx=12, pady=(2, 8))

        # Status dropdown
=======
        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.pack(fill="x", padx=12, pady=(2, 8))

>>>>>>> 14a6b3f28e0f19b0c641fd9179026190a55f2248
        status_var = ctk.StringVar(value=tr["status"])
        status_dd = ctk.CTkComboBox(
            actions, values=STATUS_LIST, width=140, height=26,
            variable=status_var,
            font=ctk.CTkFont(size=10),
            command=lambda val, tid=tr["id"]: self._ubah_status(tid, val))
        status_dd.pack(side="left")

        ctk.CTkButton(actions, text=t("t_hapus", bhs), width=60, height=26,
                      fg_color="#EF4444", hover_color="#DC2626",
                      font=ctk.CTkFont(size=10),
                      command=lambda tid=tr["id"]: self._hapus(tid)).pack(side="right")

    def _form_tambah(self):
        for w in self.winfo_children():
            w.destroy()
        bhs = self._bhs

        ctk.CTkButton(self, text=t("btn_kembali", bhs), width=100,
                      fg_color="transparent", border_width=1,
                      command=self._refresh_list).pack(anchor="w", padx=8, pady=(8, 4))

        ctk.CTkLabel(self, text=t("t_tambah", bhs),
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(4, 12))

        form = ctk.CTkFrame(self, corner_radius=10)
        form.pack(fill="x", padx=8, pady=4)

        self.e_nama_t = ctk.CTkEntry(form, placeholder_text=t("t_nama", bhs),
                                     width=400, height=38)
        self.e_nama_t.pack(padx=16, pady=(12, 6))
        self.e_deadline_t = ctk.CTkEntry(form, placeholder_text=t("t_deadline", bhs),
                                         width=400, height=38)
        self.e_deadline_t.pack(padx=16, pady=6)
        self.e_catatan_t = ctk.CTkEntry(form, placeholder_text=t("t_catatan", bhs),
                                        width=400, height=38)
        self.e_catatan_t.pack(padx=16, pady=6)

        self.err_tracker = ctk.CTkLabel(form, text="", text_color="#FF3B30",
                                        font=ctk.CTkFont(size=11))
        self.err_tracker.pack(pady=4)

        ctk.CTkButton(form, text=t("t_simpan", bhs), width=200, height=40,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._simpan_tracker).pack(pady=(4, 16))

    def _simpan_tracker(self):
        nama = self.e_nama_t.get().strip()
        dl = self.e_deadline_t.get().strip()
        cat = self.e_catatan_t.get().strip()

        ok, msg, tid = tambah_penanda_manual(self.profil_id, nama, dl, cat)
        if not ok:
            self.err_tracker.configure(text=msg)
            return
<<<<<<< HEAD
        # Buat pengingat otomatis jika ada deadline
=======
>>>>>>> 14a6b3f28e0f19b0c641fd9179026190a55f2248
        if dl:
            buat_pengingat_otomatis(tid)
        messagebox.showinfo(t("berhasil", self._bhs), t("t_ok", self._bhs))
        self._refresh_list()

    def _ubah_status(self, tracker_id, status_baru):
        ok, msg = ubah_status(tracker_id, status_baru)
        if ok:
<<<<<<< HEAD
            # Buat notifikasi perubahan status
            tr = ambil_tracker_by_id(tracker_id)
            if tr:
                tambah_notifikasi(self.profil_id, f"Status Update: {tr['nama_beasiswa']}", f"Status beasiswa telah diperbarui menjadi '{status_baru}'.", "status")
=======
            tr = ambil_tracker_by_id(tracker_id)
            if tr:
                buat_notifikasi_status(self.profil_id, tr["nama_beasiswa"], status_baru)
>>>>>>> 14a6b3f28e0f19b0c641fd9179026190a55f2248

    def _toggle_bm(self, tracker_id):
        toggle_bookmark(tracker_id)
        self._refresh_list()

    def _hapus(self, tracker_id):
        if messagebox.askyesno("Konfirmasi", "Hapus tracker ini?"):
            hapus_tracker(tracker_id)
            self._refresh_list()


# ════════════════════════════════════════════════════════════
# HALAMAN: Kalender Deadline
# ════════════════════════════════════════════════════════════

class HalamanKalender(ctk.CTkFrame):
    """Calendar — redesigned to match mockup with two-column layout."""
    def __init__(self, master, profil_id, bhs="id"):
        super().__init__(master, fg_color="transparent")
        self.profil_id = profil_id
        self._bhs = bhs
        now = datetime.now()
        self._bulan = now.month
        self._tahun = now.year
        self._build()

    def _build(self):
        self._refresh_kalender()

    def _refresh_kalender(self):
        for w in self.winfo_children():
            w.destroy()
        bhs = self._bhs

        data = tampilan_kalender(self.profil_id, self._bulan, self._tahun)

<<<<<<< HEAD
        # Two-column layout
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True)

        # LEFT: Calendar grid
=======
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True)

>>>>>>> 14a6b3f28e0f19b0c641fd9179026190a55f2248
        left = ctk.CTkFrame(main_frame, fg_color=CARD_COLOR, corner_radius=16,
                            border_width=1, border_color=BORDER_COLOR)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))

<<<<<<< HEAD
        # Month header with pink/salmon color
        month_hdr = ctk.CTkFrame(left, fg_color="#F6D6D0", corner_radius=16,
                                 height=50)
=======
        month_hdr = ctk.CTkFrame(left, fg_color="#F6D6D0", corner_radius=16, height=50)
>>>>>>> 14a6b3f28e0f19b0c641fd9179026190a55f2248
        month_hdr.pack(fill="x")
        month_hdr.pack_propagate(False)
        ctk.CTkButton(month_hdr, text="<", width=36, height=36,
                      fg_color="transparent", text_color=TEXT_DARK,
                      hover_color="#EECAC4", corner_radius=8,
                      font=ctk.CTkFont(size=16, weight="bold"),
                      command=self._prev_bulan).pack(side="left", padx=8)
        ctk.CTkLabel(month_hdr, text=f"{data['nama_bulan']} {data['tahun']}",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=TEXT_DARK).pack(side="left", expand=True)
        ctk.CTkButton(month_hdr, text=">", width=36, height=36,
                      fg_color="transparent", text_color=TEXT_DARK,
                      hover_color="#EECAC4", corner_radius=8,
                      font=ctk.CTkFont(size=16, weight="bold"),
                      command=self._next_bulan).pack(side="right", padx=8)

<<<<<<< HEAD
        # Day headers
=======
>>>>>>> 14a6b3f28e0f19b0c641fd9179026190a55f2248
        grid = ctk.CTkFrame(left, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=8, pady=8)

        hari_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for c, h in enumerate(hari_labels):
            ctk.CTkLabel(grid, text=h, font=ctk.CTkFont(size=10, weight="bold"),
                         text_color=TEXT_MUTED).grid(row=0, column=c, padx=4, pady=6)

<<<<<<< HEAD
        # Date cells
=======
>>>>>>> 14a6b3f28e0f19b0c641fd9179026190a55f2248
        today = datetime.now()
        hari_pertama = data["hari_pertama"]
        total_hari = data["total_hari"]
        tgl_warna = data.get("tanggal_warna", {})
        tgl_tracker = data.get("tanggal_tracker", {})

        row = 1
        col = hari_pertama
        for day in range(1, total_hari + 1):
            warna = tgl_warna.get(day, None)
            is_today = (day == today.day and self._bulan == today.month
                        and self._tahun == today.year)
            fg = warna if warna else ("transparent" if not is_today else BTN_PRIMARY)
            txt_color = "white" if (warna or is_today) else TEXT_DARK

            btn = ctk.CTkButton(
                grid, text=str(day), width=44, height=36,
                fg_color=fg if fg != "transparent" else "transparent",
                text_color=txt_color,
                hover_color=BTN_PALE, corner_radius=8,
                font=ctk.CTkFont(size=12, weight="bold" if (warna or is_today) else "normal"),
                command=lambda d=day: self._klik_tanggal(d, tgl_tracker),
            )
            btn.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")
            col += 1
            if col > 6:
                col = 0
                row += 1

        for c in range(7):
            grid.grid_columnconfigure(c, weight=1)

<<<<<<< HEAD
        # Legend
        leg = ctk.CTkFrame(left, fg_color="transparent")
        leg.pack(fill="x", padx=12, pady=(0, 12))
        legends = [("Deadline", "#EF4444"), ("Today", BTN_PRIMARY),
                   ("Bookmark", "#3B82F6")]
        for txt, clr in legends:
            f = ctk.CTkFrame(leg, fg_color="transparent")
            f.pack(side="left", padx=8)
            dot = ctk.CTkFrame(f, fg_color=clr, width=10, height=10,
                               corner_radius=5)
=======
        leg = ctk.CTkFrame(left, fg_color="transparent")
        leg.pack(fill="x", padx=12, pady=(0, 12))
        legends = [("Deadline", "#EF4444"), ("Today", BTN_PRIMARY), ("Bookmark", "#3B82F6")]
        for txt, clr in legends:
            f = ctk.CTkFrame(leg, fg_color="transparent")
            f.pack(side="left", padx=8)
            dot = ctk.CTkFrame(f, fg_color=clr, width=10, height=10, corner_radius=5)
>>>>>>> 14a6b3f28e0f19b0c641fd9179026190a55f2248
            dot.pack(side="left", padx=(0, 4))
            ctk.CTkLabel(f, text=txt, font=ctk.CTkFont(size=9),
                         text_color=TEXT_MUTED).pack(side="left")

<<<<<<< HEAD
        # RIGHT: Upcoming events sidebar
=======
>>>>>>> 14a6b3f28e0f19b0c641fd9179026190a55f2248
        right = ctk.CTkFrame(main_frame, fg_color="#E8EBE4", corner_radius=16,
                             width=260, border_width=1, border_color=BORDER_COLOR)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        ctk.CTkLabel(right, text="Upcoming Events",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=TEXT_DARK).pack(anchor="w", padx=16, pady=(20, 12))

        events_scroll = ctk.CTkScrollableFrame(right, fg_color="transparent")
        events_scroll.pack(fill="both", expand=True, padx=8, pady=(0, 8))

<<<<<<< HEAD
        # Get tracker events
=======
>>>>>>> 14a6b3f28e0f19b0c641fd9179026190a55f2248
        trackers = ambil_semua_tracker(self.profil_id) if self.profil_id else []
        upcoming = [t for t in trackers if t.get("deadline")]
        upcoming.sort(key=lambda x: x.get("deadline", "9999"))

        if not upcoming:
<<<<<<< HEAD
            ctk.CTkLabel(events_scroll, text="No upcoming events.\nAdd deadlines via Tracker.",
=======
            ctk.CTkLabel(events_scroll,
                         text="No upcoming events.\nAdd deadlines via Tracker.",
>>>>>>> 14a6b3f28e0f19b0c641fd9179026190a55f2248
                         font=ctk.CTkFont(size=11), text_color=TEXT_MUTED,
                         justify="center").pack(pady=40)
        else:
            for tr in upcoming[:10]:
<<<<<<< HEAD
                ev = ctk.CTkFrame(events_scroll, fg_color=CARD_COLOR,
                                  corner_radius=10)
=======
                ev = ctk.CTkFrame(events_scroll, fg_color=CARD_COLOR, corner_radius=10)
>>>>>>> 14a6b3f28e0f19b0c641fd9179026190a55f2248
                ev.pack(fill="x", pady=3)
                ctk.CTkLabel(ev, text=tr.get("nama_beasiswa", ""),
                             font=ctk.CTkFont(size=11, weight="bold"),
                             text_color=TEXT_DARK, wraplength=200,
                             anchor="w").pack(padx=10, pady=(8, 2), anchor="w")
                ctk.CTkLabel(ev, text=tr.get("deadline", ""),
                             font=ctk.CTkFont(size=10), text_color=TEXT_ACCENT,
                             anchor="w").pack(padx=10, pady=(0, 8), anchor="w")

    def _prev_bulan(self):
        self._bulan -= 1
        if self._bulan < 1:
            self._bulan = 12
            self._tahun -= 1
        self._refresh_kalender()

    def _next_bulan(self):
        self._bulan += 1
        if self._bulan > 12:
            self._bulan = 1
            self._tahun += 1
        self._refresh_kalender()

    def _klik_tanggal(self, day, tgl_tracker):
        items = tgl_tracker.get(day, [])
        if not items:
            return
<<<<<<< HEAD
        msg = "\n".join([f"\u2022 {it['nama_beasiswa']} \u2014 {format_status(it['status'], self._bhs)}"
=======
        msg = "\n".join([f"\u2022 {it['nama_beasiswa']} \u2014 {fmt_status(it['status'], self._bhs)}"
>>>>>>> 14a6b3f28e0f19b0c641fd9179026190a55f2248
                         for it in items])
        messagebox.showinfo(t("k_detail", self._bhs), msg)
