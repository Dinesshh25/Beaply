import customtkinter as ctk
import os
import sys
import traceback
import logging

from database import ambil_preferensi_db
from Profile_dan_Setting.settings import ambil_preferensi
from Profile_dan_Setting.profile import tampil_profil
from Tracker_dan_Pengingat import (
    ambil_semua_tracker, format_deadline_display, hitung_statistik
)
from Eksplorasi_dan_Navigasi import (
    ambil_semua_beasiswa, ambil_bookmark_user
)
from ui_utils import (
    t, BG_COLOR, CARD_COLOR, BORDER_COLOR, TEXT_DARK, TEXT_MUTED,
    BTN_PALE, BTN_PRIMARY, BTN_PRIMARY_HOVER, TEXT_ACCENT,
    SIDEBAR_BG, SIDEBAR_ACTIVE_BG, SIDEBAR_ACTIVE_TX,
    PASTEL_COLORS, hitung_completeness, get_bahasa, apply_pref
)

# Import Pages
from Eksplorasi_dan_Navigasi.gui_eksplorasi import HalamanEksplorasi, HalamanBookmarks
from Tracker_dan_Pengingat.gui_tracker import HalamanTracker, HalamanKalender
from Notifikasi_Terpusat.gui_notifikasi import HalamanNotifikasi
from Profile_dan_Setting.gui_profile import HalamanProfil
from Profile_dan_Setting.gui_settings import HalamanSettings
from PusatBantuan.gui_help_center import HalamanHelpCenter
from Rekomendasi.gui_rekomendasi import HalamanRekomendasi


# ════════════════════════════════════════════════════════════
# HALAMAN: Dashboard (dengan sidebar)
# ════════════════════════════════════════════════════════════

class HalamanDashboardUtama(ctk.CTkFrame):
    """Dashboard — redesigned to match mockup with 2-column layout."""
    def __init__(self, master, profil_id, bhs="id", navigate_cb=None):
        super().__init__(master, fg_color="transparent")
        self.profil_id = profil_id
        self._bhs = bhs
        self._navigate_cb = navigate_cb
        self._build()

    def _build(self):
        bhs = self._bhs
        profil = tampil_profil(self.profil_id)
        nama = profil["nama"].split()[0] if profil and profil.get("nama") else "Anonymous"
        stats = hitung_statistik(self.profil_id)

        # ── Two-column layout ──
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True)

        # LEFT COLUMN (main content)
        left = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        # ── Greeting Card ──
        greet = ctk.CTkFrame(left, fg_color="#FCEBE3", corner_radius=16,
                             border_width=1, border_color="#EED5C9")
        greet.pack(fill="x", pady=(0, 12))
        gp = ctk.CTkFrame(greet, fg_color="transparent")
        gp.pack(fill="x", padx=24, pady=24)
        ctk.CTkLabel(gp, text=f"Good morning, {nama}!",
                     font=ctk.CTkFont(size=14, weight="bold"), text_color="#555555",
                     anchor="w").pack(fill="x")
        # Title with accent
        title_f = ctk.CTkFrame(gp, fg_color="transparent")
        title_f.pack(fill="x", pady=(4, 0))
        ctk.CTkLabel(title_f, text="Let's find your next",
                     font=ctk.CTkFont(size=24, weight="bold"),
                     text_color="#333333").pack(anchor="w")
        accent_f = ctk.CTkFrame(gp, fg_color="transparent")
        accent_f.pack(fill="x")
        ctk.CTkLabel(accent_f, text="life-",
                     font=ctk.CTkFont(size=24, weight="bold"),
                     text_color="#A2D2A2").pack(side="left")
        ctk.CTkLabel(accent_f, text="changing",
                     font=ctk.CTkFont(size=24, weight="bold"),
                     text_color="#EAA6A6").pack(side="left")
        ctk.CTkLabel(accent_f, text=" opportunity",
                     font=ctk.CTkFont(size=24, weight="bold"),
                     text_color="#333333").pack(side="left")
        ctk.CTkLabel(gp, text="Explore thousands of opportunities, discover\nscholarships, and make your dreams happen!",
                     font=ctk.CTkFont(size=13), text_color="#555555",
                     anchor="w", justify="left").pack(fill="x", pady=(12, 0))

        # ── Stats Row ──
        stats_f = ctk.CTkFrame(left, fg_color="transparent")
        stats_f.pack(fill="x", pady=(0, 12))
        beasiswa_count = len(ambil_semua_beasiswa())
        bookmark_count = len(ambil_bookmark_user(self.profil_id))
        dl_count = stats.get("total", 0)
        stat_data = [
            (str(beasiswa_count), "Opportunities\nAvailable", PASTEL_COLORS[0]),
            (str(bookmark_count), "Bookmarked\nScholarship", PASTEL_COLORS[1]),
            (str(dl_count), "Upcoming\nDeadlines", PASTEL_COLORS[2]),
            ("7", "Smart Tips\nFor You", PASTEL_COLORS[3]),
        ]
        for val, lbl, bg in stat_data:
            c = ctk.CTkFrame(stats_f, fg_color=bg, corner_radius=12,
                             height=80, border_width=1, border_color=BORDER_COLOR)
            c.pack(side="left", padx=3, expand=True, fill="x")
            c.pack_propagate(False)
            ctk.CTkLabel(c, text=val, font=ctk.CTkFont(size=22, weight="bold"),
                         text_color=TEXT_DARK).pack(pady=(14, 0))
            ctk.CTkLabel(c, text=lbl, font=ctk.CTkFont(size=10),
                         text_color=TEXT_MUTED, justify="center").pack()

        # ── Trending Scholarships ──
        trend_card = ctk.CTkFrame(left, fg_color="transparent", border_width=1,
                                  corner_radius=16, border_color=BORDER_COLOR)
        trend_card.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(trend_card, text="Scholarships Trending Now",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#555555").pack(anchor="w", padx=20, pady=(16, 10))
        trend_grid = ctk.CTkFrame(trend_card, fg_color="transparent")
        trend_grid.pack(fill="x", padx=16, pady=(0, 16))
        all_bea = ambil_semua_beasiswa()[:3]
        for i, bea in enumerate(all_bea):
            bg = PASTEL_COLORS[i % len(PASTEL_COLORS)]
            tc = ctk.CTkFrame(trend_grid, fg_color=bg, corner_radius=14,
                              height=140, border_width=0)
            tc.pack(side="left", padx=4, expand=True, fill="both")
            tc.pack_propagate(False)
            ctk.CTkLabel(tc, text=bea.get("nama", "Beasiswa"),
                         font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=TEXT_DARK, wraplength=120,
                         justify="center").pack(pady=(20, 4))
            ctk.CTkLabel(tc, text=bea.get("penyelenggara", ""),
                         font=ctk.CTkFont(size=9), text_color=TEXT_MUTED,
                         wraplength=110).pack()

        # ── Smart Tips ──
        tips_card = ctk.CTkFrame(left, fg_color=CARD_COLOR, corner_radius=16,
                                 border_width=1, border_color=BORDER_COLOR)
        tips_card.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(tips_card, text="Smart Tips For You",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_DARK).pack(anchor="w", padx=20, pady=(16, 6))
        ctk.CTkLabel(tips_card, text="Complete your profile to unlock personalized scholarship recommendations.\nThe more details you provide, the better matches we can find!",
                     font=ctk.CTkFont(size=12), text_color=TEXT_MUTED,
                     anchor="w", justify="left", wraplength=500).pack(
            anchor="w", padx=20, pady=(0, 16))

        # RIGHT COLUMN (sidebar info)
        right = ctk.CTkFrame(main_frame, fg_color="transparent", width=280)
        right.pack(side="right", fill="y", padx=(0, 0))
        right.pack_propagate(False)

        # Profile Completeness
        pc_card = ctk.CTkFrame(right, fg_color=CARD_COLOR, corner_radius=16,
                               border_width=1, border_color=BORDER_COLOR)
        pc_card.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(pc_card, text="Profile\nCompleteness",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#555555", justify="left").pack(
            anchor="w", padx=20, pady=(16, 8))
        # Circle placeholder
        circ_f = ctk.CTkFrame(pc_card, fg_color="transparent")
        circ_f.pack(fill="x", padx=16, pady=(0, 4))

        canv = ctk.CTkCanvas(circ_f, width=70, height=70, bg=CARD_COLOR, highlightthickness=0)
        canv.pack(side="left", padx=(0, 8))
        completeness = hitung_completeness(profil)

        # Background circle
        canv.create_arc(5, 5, 65, 65, start=0, extent=359, width=6, style="arc", outline="#DFE6E1")
        # Foreground arc
        extent = int((completeness / 100) * 359)
        if extent > 0:
            canv.create_arc(5, 5, 65, 65, start=90, extent=-extent, width=6, style="arc", outline="#F4B3AD")

        canv.create_text(35, 35, text=f"{completeness}%", font=("Helvetica", 14, "bold"), fill="#555555")

        desc_f = ctk.CTkFrame(circ_f, fg_color="transparent")
        desc_f.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(desc_f, text="Profile Complete", font=ctk.CTkFont(size=10, weight="bold"), text_color="#555555", anchor="w").pack(fill="x")
        ctk.CTkLabel(desc_f, text="Complete your profile to\nget more better\nscholarship matches!",
                     font=ctk.CTkFont(size=8), text_color=TEXT_MUTED,
                     justify="left", anchor="w").pack(fill="x")

        ctk.CTkButton(pc_card, text="Complete Profile >",
                      fg_color="#8EA996", hover_color="#7A9382",
                      text_color="white", corner_radius=10, height=32,
                      font=ctk.CTkFont(size=11, weight="bold"),
                      command=lambda: self._navigate_cb("profil") if self._navigate_cb else None).pack(
            fill="x", padx=20, pady=(12, 16))

        # Upcoming Deadlines
        dl_card = ctk.CTkFrame(right, fg_color=CARD_COLOR, corner_radius=16,
                               border_width=1, border_color=BORDER_COLOR)
        dl_card.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(dl_card, text="Upcoming Deadlines",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color="#555555").pack(anchor="w", padx=20, pady=(16, 8))
        trackers = ambil_semua_tracker(self.profil_id)

        for i in range(3):
            r = ctk.CTkFrame(dl_card, fg_color="transparent")
            r.pack(fill="x", padx=20, pady=6)
            if i < len(trackers) and trackers[i].get("deadline"):
                tr = trackers[i]
                ctk.CTkLabel(r, text=tr["nama_beasiswa"],
                             font=ctk.CTkFont(size=11, weight="bold"),
                             text_color=TEXT_DARK, anchor="w").pack(fill="x")
                ctk.CTkLabel(r, text=format_deadline_display(tr["deadline"]),
                             font=ctk.CTkFont(size=9),
                             text_color=TEXT_MUTED, anchor="w").pack(fill="x")
            else:
                ctk.CTkFrame(r, fg_color="#EAEAEA", height=2).pack(fill="x", pady=12)

        ctk.CTkFrame(dl_card, height=16, fg_color="transparent").pack()

        # Calendar mini
        cal_card = ctk.CTkFrame(right, fg_color=CARD_COLOR, corner_radius=16,
                                border_width=1, border_color=BORDER_COLOR)
        cal_card.pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(cal_card, text="Calendar",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_DARK).pack(anchor="w", padx=16, pady=(16, 8))
        import datetime
        today = datetime.date.today()
        ctk.CTkLabel(cal_card, text=today.strftime("%B %Y"),
                     font=ctk.CTkFont(size=12), text_color=TEXT_MUTED).pack(
            padx=16, pady=(0, 4))
        ctk.CTkLabel(cal_card, text=today.strftime("%d"),
                     font=ctk.CTkFont(size=28, weight="bold"),
                     text_color=BTN_PRIMARY).pack(pady=(0, 16))


# ════════════════════════════════════════════════════════════
# LAYOUT: Sidebar + Content Area
# ════════════════════════════════════════════════════════════

class LayoutDenganSidebar(ctk.CTkFrame):
    """Main layout with sidebar navigation — redesigned to match mockup."""
    def __init__(self, master, user_profile_or_id, logout_callback):
        super().__init__(master, fg_color=BG_COLOR)
        if isinstance(user_profile_or_id, dict):
            self.user_profile = user_profile_or_id
            self.profil_id = user_profile_or_id.get("profil_id") or user_profile_or_id.get("id")
        else:
            self.profil_id = user_profile_or_id
            profil_data = tampil_profil(self.profil_id) if self.profil_id else {}
            self.user_profile = profil_data or {}
        self.logout_cb = logout_callback
        self._bhs = get_bahasa(self.profil_id) if self.profil_id else "id"
        self._current_nav = "dashboard"
        self._build()
        self._navigate("dashboard")

    def _build(self):
        bhs = self._bhs

        # ══════ SIDEBAR ══════
        self.sidebar = ctk.CTkFrame(self, fg_color=SIDEBAR_BG, width=200,
                                    corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Bottom items FIRST (pack side=bottom so they stay pinned)
        bottom_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom_frame.pack(side="bottom", fill="x", pady=(0, 10))

        self.nav_buttons = {}
        for key, icon, label in [
            ("settings", "\u2699", "Settings"),
            ("bantuan", "\u2753", "Help Center"),
        ]:
            btn = ctk.CTkButton(
                bottom_frame, text=f"  {icon}  {label}",
                anchor="w", height=32, corner_radius=8,
                fg_color="transparent", text_color=TEXT_MUTED,
                hover_color=BTN_PALE, font=ctk.CTkFont(size=12),
                command=lambda k=key: self._navigate(k),
            )
            btn.pack(fill="x", padx=12, pady=1)
            self.nav_buttons[key] = btn

        # Beaply Pro card
        pro_card = ctk.CTkFrame(self.sidebar, fg_color="#E8F0EA",
                                corner_radius=14)
        pro_card.pack(side="bottom", fill="x", padx=10, pady=(0, 8))
        ctk.CTkLabel(pro_card, text="Upgrade to",
                     font=ctk.CTkFont(size=9), text_color=TEXT_MUTED).pack(pady=(8, 0))
        ctk.CTkLabel(pro_card, text="Beaply Pro",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=SIDEBAR_ACTIVE_TX).pack()
        ctk.CTkLabel(pro_card, text="Unlock premium features\nand scholarship matches\ntailored just for you.",
                     font=ctk.CTkFont(size=8), text_color=TEXT_MUTED,
                     justify="center").pack(padx=6, pady=(2, 4))
        ctk.CTkButton(pro_card, text="Upgrade Now >", height=26,
                      fg_color=BTN_PRIMARY, hover_color=BTN_PRIMARY_HOVER,
                      text_color=TEXT_DARK, corner_radius=8,
                      font=ctk.CTkFont(size=10, weight="bold")).pack(
            fill="x", padx=10, pady=(0, 8))

        # Logo
        logo_f = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_f.pack(pady=(16, 16), padx=16)
        try:
            from PIL import Image
            import os
            logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "assets", "logo_beaply.png"))
            img = ctk.CTkImage(light_image=Image.open(logo_path), size=(110, 55))
            ctk.CTkLabel(logo_f, text="", image=img).pack()
        except Exception as e:
            print("Logo Error:", e)
            ctk.CTkLabel(logo_f, text="beaply",
                         font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
                         text_color=TEXT_ACCENT).pack()

        # Nav items
        nav_items = [
            ("dashboard",    "\ud83c\udfe0", "Dashboard"),
            ("eksplorasi",   "\ud83d\udcda", "Scholarships"),
            ("rekomendasi",  "\u2728", "Recommendations"),
            ("bookmarks",    "\ud83d\udd16", "Bookmarks"),
            ("kalender",     "\ud83d\udcc5", "Calendar"),
            ("notifikasi",   "\ud83d\udd14", "Notifications"),
            ("profil",       "\ud83d\udc64", "Profile"),
        ]

        for nav_key, icon, label in nav_items:
            btn = ctk.CTkButton(
                self.sidebar, text=f"  {icon}  {label}",
                anchor="w", height=34, corner_radius=10,
                fg_color="transparent",
                text_color=TEXT_DARK,
                hover_color=BTN_PALE,
                font=ctk.CTkFont(size=12),
                command=lambda k=nav_key: self._navigate(k),
            )
            btn.pack(fill="x", padx=12, pady=1)
            self.nav_buttons[nav_key] = btn


        # ══════ RIGHT AREA ══════
        right_area = ctk.CTkFrame(self, fg_color="transparent")
        right_area.pack(side="right", fill="both", expand=True)

        # ── Top Bar ──
        self.topbar = ctk.CTkFrame(right_area, fg_color="transparent", height=56)
        self.topbar.pack(fill="x", padx=20, pady=(12, 8))
        self.topbar.pack_propagate(False)

        self.page_title = ctk.CTkLabel(
            self.topbar, text="Dashboard",
            font=ctk.CTkFont(size=22, weight="bold"), text_color=TEXT_DARK)
        self.page_title.pack(side="left")

        # User info
        user_frame = ctk.CTkFrame(self.topbar, fg_color="transparent")
        user_frame.pack(side="right")
        
        # Avatar
        try:
            from PIL import Image
            ava_img = ctk.CTkImage(light_image=Image.open("assets/default_avatar.png"), size=(40, 40))
            ctk.CTkLabel(user_frame, text="", image=ava_img).pack(side="left", padx=(0, 8))
        except:
            ctk.CTkLabel(user_frame, text="👤", font=ctk.CTkFont(size=24)).pack(side="left", padx=(0, 8))
            
        # Details Stack
        user_text = ctk.CTkFrame(user_frame, fg_color="transparent")
        user_text.pack(side="left")
        
        nama = self.user_profile.get("nama", t("guest_name", bhs))
        ctk.CTkLabel(user_text, text=nama,
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=TEXT_DARK).pack(anchor="w")
        ctk.CTkLabel(user_text, text="Student",
                     font=ctk.CTkFont(size=11), text_color=TEXT_MUTED).pack(anchor="w")

        # Bell icon
        bell_btn = ctk.CTkButton(self.topbar, text="🔔", width=36, height=36,
                                 fg_color="transparent", text_color=TEXT_DARK,
                                 hover_color=BTN_PALE, corner_radius=18,
                                 font=ctk.CTkFont(size=16),
                                 command=lambda: self._navigate("notifikasi"))
        bell_btn.pack(side="right", padx=(0, 12))

        # ── Content Area ──
        self.content = ctk.CTkFrame(right_area, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=20, pady=(0, 12))

    def _navigate(self, key):
        self._current_nav = key

        # Update page title
        titles = {
            "dashboard": "Dashboard", "eksplorasi": "Scholarships",
            "rekomendasi": "Recommendations", "bookmarks": "Bookmarks",
            "kalender": "Calendar", "notifikasi": "Notifications",
            "profil": "Profile", "tracker": "Tracker",
            "bantuan": "FAQ & Help Center", "settings": "Settings",
        }
        self.page_title.configure(text=titles.get(key, key.title()))

        # Update sidebar highlight
        for nav_key, btn in self.nav_buttons.items():
            if nav_key == key:
                btn.configure(fg_color=SIDEBAR_ACTIVE_BG,
                              text_color=SIDEBAR_ACTIVE_TX)
            else:
                btn.configure(fg_color="transparent",
                              text_color=TEXT_DARK)

        # Clear content
        for w in self.content.winfo_children():
            w.destroy()

        bhs = self._bhs

        if key == "dashboard":
            HalamanDashboardUtama(self.content, self.profil_id, bhs,
                                  navigate_cb=self._navigate).pack(
                fill="both", expand=True)
        elif key == "eksplorasi":
            HalamanEksplorasi(self.content, self.profil_id, bhs).pack(
                fill="both", expand=True)
        elif key == "rekomendasi":
            HalamanRekomendasi(self.content, profil_id=self.profil_id).pack(
                fill="both", expand=True)
        elif key == "bookmarks":
            HalamanBookmarks(self.content, self.profil_id, bhs).pack(
                fill="both", expand=True)
        elif key == "tracker":
            HalamanTracker(self.content, self.profil_id, bhs).pack(
                fill="both", expand=True)
        elif key == "kalender":
            HalamanKalender(self.content, self.profil_id, bhs).pack(
                fill="both", expand=True)
        elif key == "notifikasi":
            HalamanNotifikasi(self.content, self.profil_id, bhs).pack(
                fill="both", expand=True)
        elif key == "profil":
            HalamanProfil(self.content, self.profil_id, bhs).pack(
                fill="both", expand=True)
        elif key == "bantuan":
            HalamanHelpCenter(self.content, profil_id=self.profil_id).pack(
                fill="both", expand=True)
        elif key == "settings":
            HalamanSettings(self.content, self.profil_id, self._bhs,
                            logout_cb=self._refresh_all).pack(
                fill="both", expand=True)

    def _refresh_all(self):
        pref = ambil_preferensi(self.profil_id)
        apply_pref(pref)
        self._bhs = pref.get("bahasa", "id")
        for w in self.winfo_children():
            w.destroy()
        self._build()
        self._navigate(self._current_nav)
