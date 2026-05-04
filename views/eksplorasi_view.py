"""
views/eksplorasi_view.py
Beaply - View: Eksplorasi & Navigasi Beasiswa

Dipindahkan dari: Eksplorasi_dan_Navigasi/gui_eksplorasi.py
Import sekarang dari controllers/eksplorasi_controller.
"""
import customtkinter as ctk
from datetime import datetime
from ui_utils import (
    t, PASTEL_COLORS, BG_COLOR, CARD_COLOR, BORDER_COLOR,
    TEXT_DARK, TEXT_MUTED, BTN_PALE, BTN_PRIMARY, BTN_PRIMARY_HOVER,
    TEXT_ACCENT, konfirm_yesno
)
from controllers.eksplorasi_controller import (
    get_semua_beasiswa, get_bookmarks, check_bookmarked, toggle_bookmark_beasiswa,
)
from controllers.notifikasi_controller import buat_notifikasi_deadline


# Alias untuk keterbacaan
ambil_semua_beasiswa = get_semua_beasiswa
ambil_bookmark_user = get_bookmarks
cek_bookmark = check_bookmarked


# ════════════════════════════════════════════════════════════
# HALAMAN: Eksplorasi Beasiswa
# ════════════════════════════════════════════════════════════

class HalamanEksplorasi(ctk.CTkFrame):
    """Scholarships page — with sort, filter, deadline colors."""
    def __init__(self, master, profil_id, bhs="id"):
        super().__init__(master, fg_color="transparent")
        self.profil_id = profil_id
        self._bhs = bhs
        self._all_beasiswa = ambil_semua_beasiswa()
        self._filtered = list(self._all_beasiswa)
        self._sort_mode = "default"
        self._filter_jenjang = None
        self._filter_toefl = False
        self._filter_ielts = False
        self._check_deadline_notifs()
        self._build()

    def _check_deadline_notifs(self):
        """Auto-create notifications for bookmarked scholarships with deadline <7 days."""
        today = datetime.now().date()
        bookmarks = ambil_bookmark_user(self.profil_id)
        for bea in bookmarks:
            dl = bea.get("deadline", "")
            if not dl:
                continue
            try:
                dl_date = datetime.strptime(dl, "%Y-%m-%d").date()
                days_left = (dl_date - today).days
                if 0 <= days_left <= 7:
                    buat_notifikasi_deadline(
                        self.profil_id,
                        bea.get("nama", "Beasiswa"),
                        days_left,
                    )
            except (ValueError, TypeError):
                pass

    def _build(self):
        bhs = self._bhs

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=(0, 10))

        self.search_entry = ctk.CTkEntry(
            top, placeholder_text="Search Scholarships...",
            placeholder_text_color=TEXT_MUTED, height=40,
            corner_radius=12, fg_color=CARD_COLOR, border_width=1,
            border_color=BORDER_COLOR, text_color=TEXT_DARK)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.search_entry.bind("<KeyRelease>", self._on_search)

        ctk.CTkButton(top, text="\u2195 Sort by", width=100, height=40,
                      corner_radius=12, fg_color=CARD_COLOR,
                      border_width=1, border_color=BORDER_COLOR,
                      text_color=TEXT_DARK, hover_color=BTN_PALE,
                      font=ctk.CTkFont(size=12),
                      command=self._show_sort).pack(side="left", padx=(0, 6))

        ctk.CTkButton(top, text="\u2699 Filters", width=100, height=40,
                      corner_radius=12, fg_color=CARD_COLOR,
                      border_width=1, border_color=BORDER_COLOR,
                      text_color=TEXT_DARK, hover_color=BTN_PALE,
                      font=ctk.CTkFont(size=12),
                      command=self._show_filter).pack(side="left")

        self.filter_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.filter_bar.pack(fill="x", pady=(0, 4))
        self._update_filter_bar()

        self.count_label = ctk.CTkLabel(
            self, text=f"{len(self._filtered)} Scholarships Found",
            font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT_DARK,
            anchor="w")
        self.count_label.pack(fill="x", pady=(0, 8))

        self.grid_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.grid_scroll.pack(fill="both", expand=True)
        self._apply_filters_and_sort()
        self._render_grid()

    def _update_filter_bar(self):
        for w in self.filter_bar.winfo_children():
            w.destroy()
        tags = []
        if self._filter_jenjang:
            tags.append(f"Jenjang: {self._filter_jenjang}")
        if self._filter_toefl:
            tags.append("TOEFL Required")
        if self._filter_ielts:
            tags.append("IELTS Required")
        if self._sort_mode != "default":
            sort_names = {"deadline_asc": "Deadline \u2191", "deadline_desc": "Deadline \u2193",
                          "name_asc": "Name A-Z", "name_desc": "Name Z-A"}
            tags.append(f"Sort: {sort_names.get(self._sort_mode, self._sort_mode)}")
        for tag in tags:
            pill = ctk.CTkButton(self.filter_bar, text=f"{tag}  \u2715", height=26,
                                 fg_color=BTN_PRIMARY, hover_color=BTN_PRIMARY_HOVER,
                                 text_color=TEXT_DARK, corner_radius=12,
                                 font=ctk.CTkFont(size=10),
                                 command=lambda t=tag: self._remove_filter(t))
            pill.pack(side="left", padx=(0, 6))
        if tags:
            ctk.CTkButton(self.filter_bar, text="Clear All", height=26,
                          fg_color="transparent", text_color="#D94040",
                          hover_color="#FCE8E8", corner_radius=12,
                          font=ctk.CTkFont(size=10),
                          command=self._clear_filters).pack(side="left", padx=4)

    def _remove_filter(self, tag):
        if "Jenjang" in tag:
            self._filter_jenjang = None
        elif "TOEFL" in tag:
            self._filter_toefl = False
        elif "IELTS" in tag:
            self._filter_ielts = False
        elif "Sort" in tag:
            self._sort_mode = "default"
        self._apply_filters_and_sort()
        self._update_filter_bar()
        self._render_grid()

    def _clear_filters(self):
        self._filter_jenjang = None
        self._filter_toefl = False
        self._filter_ielts = False
        self._sort_mode = "default"
        self._apply_filters_and_sort()
        self._update_filter_bar()
        self._render_grid()

    def _apply_filters_and_sort(self):
        q = self.search_entry.get().strip().lower() if hasattr(self, 'search_entry') else ""
        result = list(self._all_beasiswa)
        if q:
            result = [b for b in result
                      if q in b.get("nama", "").lower()
                      or q in b.get("penyelenggara", "").lower()
                      or q in b.get("jenjang", "").lower()]
        if self._filter_jenjang:
            fj = self._filter_jenjang.upper()
            result = [b for b in result if fj in b.get("jenjang", "").upper()]
        if self._filter_toefl:
            result = [b for b in result if b.get("syarat_toefl")]
        if self._filter_ielts:
            result = [b for b in result if b.get("syarat_ielts")]
        if self._sort_mode == "deadline_asc":
            result.sort(key=lambda b: b.get("deadline") or "9999-99-99")
        elif self._sort_mode == "deadline_desc":
            result.sort(key=lambda b: b.get("deadline") or "0000-00-00", reverse=True)
        elif self._sort_mode == "name_asc":
            result.sort(key=lambda b: b.get("nama", "").lower())
        elif self._sort_mode == "name_desc":
            result.sort(key=lambda b: b.get("nama", "").lower(), reverse=True)
        self._filtered = result

    def _get_deadline_color(self, deadline_str):
        if not deadline_str:
            return None
        try:
            dl = datetime.strptime(deadline_str, "%Y-%m-%d").date()
            days = (dl - datetime.now().date()).days
            if days < 0:
                return "#999999"
            elif days <= 7:
                return "#EF4444"
            elif days <= 14:
                return "#F59E0B"
            else:
                return "#22C55E"
        except (ValueError, TypeError):
            return None

    def _render_grid(self):
        for w in self.grid_scroll.winfo_children():
            w.destroy()
        cols = 3
        for i, bea in enumerate(self._filtered):
            row_idx = i // cols
            col_idx = i % cols
            bg = PASTEL_COLORS[i % len(PASTEL_COLORS)]
            is_bm = cek_bookmark(self.profil_id, bea.get("id", 0))
            dl_color = self._get_deadline_color(bea.get("deadline")) if is_bm else None

            card = ctk.CTkFrame(self.grid_scroll, fg_color=bg, corner_radius=14,
                                border_width=2 if dl_color else 1,
                                border_color=dl_color if dl_color else BORDER_COLOR)
            card.grid(row=row_idx, column=col_idx, padx=6, pady=6, sticky="nsew")
            self.grid_scroll.grid_columnconfigure(col_idx, weight=1)

            ctk.CTkLabel(card, text=bea.get("nama", "Beasiswa"),
                         font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=TEXT_DARK, wraplength=200,
                         justify="left", anchor="w").pack(
                anchor="w", padx=14, pady=(14, 2))

            penyelenggara = bea.get("penyelenggara", "")
            if penyelenggara:
                ctk.CTkLabel(card, text=penyelenggara,
                             font=ctk.CTkFont(size=10), text_color=TEXT_MUTED,
                             anchor="w", wraplength=200).pack(anchor="w", padx=14, pady=(0, 4))

            jenjang = bea.get("jenjang", "-")
            ctk.CTkLabel(card, text=f"Jenjang: {jenjang}",
                         font=ctk.CTkFont(size=9), text_color=TEXT_MUTED,
                         anchor="w").pack(anchor="w", padx=14, pady=(2, 0))

            deadline = bea.get("deadline", "")
            if deadline:
                color = self._get_deadline_color(deadline)
                dl_frame = ctk.CTkFrame(card, fg_color="transparent")
                dl_frame.pack(anchor="w", padx=14, pady=(4, 0))
                if color:
                    dot = ctk.CTkFrame(dl_frame, fg_color=color, width=8, height=8, corner_radius=4)
                    dot.pack(side="left", padx=(0, 4), pady=2)
                ctk.CTkLabel(dl_frame, text=f"Deadline: {deadline}",
                             font=ctk.CTkFont(size=9),
                             text_color=color if color else TEXT_ACCENT,
                             anchor="w").pack(side="left")

            bot = ctk.CTkFrame(card, fg_color="transparent")
            bot.pack(fill="x", padx=10, pady=(6, 10))
            bm_text = "\u2605" if is_bm else "\u2606"
            bm_color = TEXT_ACCENT if is_bm else TEXT_MUTED
            ctk.CTkButton(bot, text=bm_text, width=28, height=24,
                          fg_color="transparent", text_color=bm_color,
                          hover_color=BORDER_COLOR, font=ctk.CTkFont(size=16),
                          command=lambda b=bea: self._toggle_bm(b)).pack(side="right")

        self.count_label.configure(text=f"{len(self._filtered)} Scholarships Found")

    def _on_search(self, event=None):
        self._apply_filters_and_sort()
        self._render_grid()

    def _toggle_bm(self, bea):
        toggle_bookmark_beasiswa(self.profil_id, bea.get("id", 0))
        self._render_grid()

    def _show_sort(self):
        top = ctk.CTkToplevel(self)
        top.title("Sort Scholarships")
        top.geometry("300x280")
        top.configure(fg_color=BG_COLOR)
        top.transient(self.winfo_toplevel())
        top.grab_set()
        ctk.CTkLabel(top, text="Sort By",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=TEXT_DARK).pack(pady=(20, 12))
        options = [
            ("Default", "default"),
            ("Deadline (Closest First)", "deadline_asc"),
            ("Deadline (Furthest First)", "deadline_desc"),
            ("Name (A \u2192 Z)", "name_asc"),
            ("Name (Z \u2192 A)", "name_desc"),
        ]
        for label, mode in options:
            is_active = self._sort_mode == mode
            ctk.CTkButton(top, text=label, height=36,
                          fg_color=BTN_PRIMARY if is_active else CARD_COLOR,
                          hover_color=BTN_PRIMARY_HOVER,
                          text_color=TEXT_DARK, corner_radius=10,
                          border_width=1, border_color=BORDER_COLOR,
                          font=ctk.CTkFont(size=12, weight="bold" if is_active else "normal"),
                          command=lambda m=mode, t=top: self._apply_sort(m, t)).pack(
                fill="x", padx=24, pady=3)

    def _apply_sort(self, mode, popup):
        self._sort_mode = mode
        popup.destroy()
        self._apply_filters_and_sort()
        self._update_filter_bar()
        self._render_grid()

    def _show_filter(self):
        top = ctk.CTkToplevel(self)
        top.title("Filter Scholarships")
        top.geometry("340x420")
        top.configure(fg_color=BG_COLOR)
        top.transient(self.winfo_toplevel())
        top.grab_set()
        scroll = ctk.CTkScrollableFrame(top, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=16, pady=16)
        ctk.CTkLabel(scroll, text="Filter By Jenjang",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_DARK).pack(anchor="w", pady=(0, 8))
        jenjang_options = ["All", "S1", "S2", "S3", "D3", "D4", "SMA"]
        jenjang_var = ctk.StringVar(value=self._filter_jenjang or "All")
        for j in jenjang_options:
            ctk.CTkRadioButton(scroll, text=j, variable=jenjang_var, value=j,
                               text_color=TEXT_DARK,
                               font=ctk.CTkFont(size=12)).pack(anchor="w", pady=2)
        ctk.CTkLabel(scroll, text="Test Score Requirements",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_DARK).pack(anchor="w", pady=(16, 8))
        toefl_var = ctk.BooleanVar(value=self._filter_toefl)
        ielts_var = ctk.BooleanVar(value=self._filter_ielts)
        ctk.CTkCheckBox(scroll, text="Requires TOEFL", variable=toefl_var,
                        text_color=TEXT_DARK, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=2)
        ctk.CTkCheckBox(scroll, text="Requires IELTS", variable=ielts_var,
                        text_color=TEXT_DARK, font=ctk.CTkFont(size=12)).pack(anchor="w", pady=2)

        def apply():
            jv = jenjang_var.get()
            self._filter_jenjang = None if jv == "All" else jv
            self._filter_toefl = toefl_var.get()
            self._filter_ielts = ielts_var.get()
            top.destroy()
            self._apply_filters_and_sort()
            self._update_filter_bar()
            self._render_grid()

        ctk.CTkButton(scroll, text="Apply Filters", height=40,
                      fg_color=BTN_PRIMARY, hover_color=BTN_PRIMARY_HOVER,
                      text_color=TEXT_DARK, corner_radius=12,
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=apply).pack(fill="x", pady=(16, 0))


class HalamanBookmarks(ctk.CTkFrame):
    """Bookmarks page — with deadline color indicators."""
    def __init__(self, master, profil_id, bhs="id"):
        super().__init__(master, fg_color="transparent")
        self.profil_id = profil_id
        self._bhs = bhs
        self._build()

    def _get_deadline_info(self, deadline_str):
        if not deadline_str:
            return None, ""
        try:
            dl = datetime.strptime(deadline_str, "%Y-%m-%d").date()
            days = (dl - datetime.now().date()).days
            if days < 0:
                return "#999999", "Expired"
            elif days <= 7:
                return "#EF4444", f"{days} days left!"
            elif days <= 14:
                return "#F59E0B", f"{days} days left"
            else:
                return "#22C55E", f"{days} days left"
        except (ValueError, TypeError):
            return None, ""

    def _build(self):
        bm_list = ambil_bookmark_user(self.profil_id)

        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(hdr, text=f"{len(bm_list)} Bookmarks",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=TEXT_DARK).pack(side="left")
        ctk.CTkButton(hdr, text="\U0001f5d1 Clear All", width=100, height=32,
                      fg_color=CARD_COLOR, border_width=1,
                      border_color=BORDER_COLOR, text_color="#D94040",
                      hover_color="#FCE8E8", corner_radius=10,
                      font=ctk.CTkFont(size=11),
                      command=self._clear_all).pack(side="right")

        leg = ctk.CTkFrame(self, fg_color="transparent")
        leg.pack(fill="x", pady=(0, 8))
        for txt, clr in [("\u2022 >14 days", "#22C55E"), ("\u2022 7-14 days", "#F59E0B"),
                          ("\u2022 <7 days", "#EF4444"), ("\u2022 Expired", "#999999")]:
            ctk.CTkLabel(leg, text=txt, font=ctk.CTkFont(size=9), text_color=clr).pack(
                side="left", padx=6)

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        if not bm_list:
            ctk.CTkLabel(scroll, text="No bookmarked scholarships yet.\nExplore and save scholarships you're interested in!",
                         font=ctk.CTkFont(size=13), text_color=TEXT_MUTED,
                         justify="center").pack(pady=60)
            return

        for bea in bm_list:
            dl_color, dl_label = self._get_deadline_info(bea.get("deadline"))
            border_clr = dl_color if dl_color else BORDER_COLOR
            card = ctk.CTkFrame(scroll, fg_color=CARD_COLOR, corner_radius=14,
                                border_width=2 if dl_color else 1,
                                border_color=border_clr)
            card.pack(fill="x", pady=5)
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=20, pady=16)
            title_row = ctk.CTkFrame(inner, fg_color="transparent")
            title_row.pack(fill="x")
            ctk.CTkLabel(title_row, text=bea.get("nama", ""),
                         font=ctk.CTkFont(size=14, weight="bold"),
                         text_color=TEXT_DARK, anchor="w",
                         wraplength=500).pack(side="left", fill="x", expand=True)
            if dl_label:
                ctk.CTkLabel(title_row, text=dl_label,
                             font=ctk.CTkFont(size=10, weight="bold"),
                             text_color=dl_color).pack(side="right")
            ctk.CTkLabel(inner, text=bea.get("penyelenggara", ""),
                         font=ctk.CTkFont(size=11), text_color=TEXT_MUTED,
                         anchor="w").pack(fill="x", pady=(2, 0))
            info = f"Jenjang: {bea.get('jenjang', '-')}"
            if bea.get("deadline"):
                info += f"  |  Deadline: {bea['deadline']}"
            ctk.CTkLabel(inner, text=info,
                         font=ctk.CTkFont(size=10), text_color=TEXT_MUTED,
                         anchor="w").pack(fill="x", pady=(4, 0))
            ctk.CTkButton(inner, text="Remove", width=70, height=24,
                          fg_color="transparent", border_width=1,
                          border_color="#D94040", text_color="#D94040",
                          hover_color="#FCE8E8", corner_radius=8,
                          font=ctk.CTkFont(size=10),
                          command=lambda bid=bea.get("id", 0): self._remove_bm(bid)).pack(
                anchor="e", pady=(6, 0))

    def _remove_bm(self, beasiswa_id):
        toggle_bookmark_beasiswa(self.profil_id, beasiswa_id)
        for w in self.winfo_children():
            w.destroy()
        self._build()

    def _clear_all(self):
        if konfirm_yesno(self, "Clear All", "Remove all bookmarks?"):
            for bm in ambil_bookmark_user(self.profil_id):
                toggle_bookmark_beasiswa(self.profil_id, bm.get("id", 0))
            for w in self.winfo_children():
                w.destroy()
            self._build()
