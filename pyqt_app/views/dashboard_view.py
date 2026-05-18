"""
pyqt_app/views/dashboard_view.py
Dashboard page — 2-column layout matching Figma mockup.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QSizePolicy, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QTabWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor, QPixmap, QColor
import datetime, os, calendar

from pyqt_app.styles.theme import FONT_FAMILY, palette, pastel
from pyqt_app.widgets.progress_ring import ProgressRing
from pyqt_app.widgets.chart_widget import (
    BarChartWidget, DonutChartWidget, ChartLegendWidget, CHART_COLORS
)
from controllers.profil_controller import tampil_profil
from controllers.tracker_controller import (
    get_semua_tracker as ambil_semua_tracker,
    hitung_statistik, fmt_deadline,
)
from controllers.eksplorasi_controller import (
    get_semua_beasiswa as ambil_semua_beasiswa,
    get_bookmarks as ambil_bookmark_user,
)
from controllers.analytics_controller import get_analytics_data

ASSETS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets"))


class DashboardView(QWidget):

    def __init__(self, profil_id, bhs="id", navigate_cb=None, mode="light", parent=None):
        super().__init__(parent)
        self._pid = profil_id
        self._bhs = bhs
        self._nav = navigate_cb
        self._mode = mode
        self._build()

    @staticmethod
    def _calc_completeness(p):
        if not p: return 0
        fields = ["nama","tanggal_lahir","email","jurusan","kampus",
                  "jenjang","semester","ip","jenis_kelamin"]
        opt = ["skor_ielts","skor_toefl","skor_duolingo","skor_sat",
               "skor_act","skor_gre","skor_gmat","skor_hsk","level_jlpt"]
        total = len(fields) + len(opt)
        filled = sum(1 for f in fields + opt
                     if p.get(f) is not None and str(p[f]).strip() != "" and p[f] != 0)
        return int((filled / total) * 100)

    def _p(self, idx):
        return pastel(idx, self._mode)

    def _header(self, text, c, target=None):
        w = QWidget(); w.setStyleSheet("background:transparent;")
        h = QHBoxLayout(w); h.setContentsMargins(0,0,0,0)
        l = QLabel(text); l.setFont(QFont(FONT_FAMILY, 14, QFont.Weight.Bold))
        l.setStyleSheet(f"color:{c['text_dark']};background:transparent;"); h.addWidget(l)
        h.addStretch()
        if target and self._nav:
            b = QPushButton("See all \u203a"); b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            b.setStyleSheet(f"background:transparent;border:none;color:{c['text_accent']};font-size:11px;")
            b.clicked.connect(lambda: self._nav(target)); h.addWidget(b)
        return w

    def _shift_month(self, d: int):
        m = self._cal_date.month + d
        y = self._cal_date.year
        if m > 12: m = 1; y += 1
        elif m < 1: m = 12; y -= 1
        import datetime
        self._cal_date = datetime.date(y, m, 1)
        self._cal_lbl.setText(self._cal_date.strftime("%B"))
        self._render_cal_grid()

    def _render_cal_grid(self):
        c = palette(self._mode)
        import datetime, calendar
        today = datetime.date.today()
        while self._cal_grid_l.count():
            item = self._cal_grid_l.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        cal = calendar.Calendar(firstweekday=6)
        for week in cal.monthdayscalendar(self._cal_date.year, self._cal_date.month):
            ww = QWidget(); ww.setStyleSheet("background:transparent;")
            wl = QHBoxLayout(ww); wl.setContentsMargins(0,0,0,0); wl.setSpacing(0)
            for day in week:
                dl3 = QLabel(str(day) if day else "")
                dl3.setAlignment(Qt.AlignmentFlag.AlignCenter); dl3.setFixedSize(32,28)
                if day == today.day and self._cal_date.year == today.year and self._cal_date.month == today.month:
                    dl3.setStyleSheet(f"background:#a8c5b0;color:#000000;border-radius:14px;font-weight:bold;font-size:11px;")
                elif day:
                    dl3.setStyleSheet(f"color:{c['text_dark']};font-size:11px;background:transparent;")
                else:
                    dl3.setStyleSheet("background:transparent;")
                wl.addWidget(dl3)
            self._cal_grid_l.addWidget(ww)

    def _handle_stats_click(self, target: str):
        if target == "scroll_faq":
            if hasattr(self, '_left_scroll'):
                vsb = self._left_scroll.verticalScrollBar()
                vsb.setValue(vsb.maximum())
        elif self._nav:
            self._nav(target)

    def _apply_card_shadow(self, widget):
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        from PyQt6.QtGui import QColor
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(2)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 15))
        widget.setGraphicsEffect(shadow)

    def _build(self):
        c = palette(self._mode)
        profil = tampil_profil(self._pid)
        nama = profil["nama"].split()[0] if profil and profil.get("nama") else "Anonymous"
        stats_data = hitung_statistik(self._pid)

        ml = QHBoxLayout(self); ml.setContentsMargins(0,0,0,0); ml.setSpacing(14)

        # ── LEFT ──
        ls = QScrollArea(); ls.setWidgetResizable(True)
        ls.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        lw = QWidget(); lw.setStyleSheet("background:transparent;")
        ll = QVBoxLayout(lw); ll.setContentsMargins(0,0,4,0); ll.setSpacing(16)
        ls.setWidget(lw); ml.addWidget(ls, 7)

        # ━━ GREETING with illustration ━━
        greet = QFrame(); greet.setObjectName("greetCard")
        self._apply_card_shadow(greet)
        greet.setFixedHeight(180)
        greet.setStyleSheet(f"""
            #greetCard {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #FFFFFF, stop:0.4 #FDF4F2, stop:1 #FADCD2);
                border-radius: 18px; border:none;
            }}
        """)
        greet_lay = QHBoxLayout(greet)
        greet_lay.setContentsMargins(30, 20, 20, 20)
        greet_lay.setSpacing(10)

        # Text side
        text_w = QWidget(); text_w.setStyleSheet("background:transparent;")
        tl = QVBoxLayout(text_w); tl.setContentsMargins(0,0,0,0); tl.setSpacing(2)
        g1 = QLabel(f"Good morning, {nama}!")
        g1.setFont(QFont(FONT_FAMILY, 13)); g1.setStyleSheet(f"color:{c['text_muted']};background:transparent;")
        tl.addWidget(g1)
        g2 = QLabel("Let's find your next")
        g2.setFont(QFont(FONT_FAMILY, 24, QFont.Weight.Bold))
        g2.setStyleSheet(f"color:{c['text_dark']};background:transparent;")
        g2.setMinimumHeight(42); tl.addWidget(g2)
        g2b = QLabel(f"<b><span style='color:#A8C5B0'>life-</span><span style='color:#F4A9A0'>changing</span> opportunity</b>")
        g2b.setFont(QFont(FONT_FAMILY, 24, QFont.Weight.Bold))
        g2b.setStyleSheet(f"color:{c['text_dark']};background:transparent;")
        g2b.setMinimumHeight(42); tl.addWidget(g2b)
        tl.addSpacing(6)
        g3 = QLabel("Explore thousands of opportunities, discover\nscholarships, and make your dreams happen!")
        g3.setStyleSheet(f"color:{c['text_dark']};font-size:12px;background:transparent;"); tl.addWidget(g3)
        tl.addStretch()
        greet_lay.addWidget(text_w, 3)

        # Illustration side
        img_path = os.path.join(ASSETS, "graduation_cap.png")
        if os.path.exists(img_path):
            img_lbl = QLabel()
            px = QPixmap(img_path).scaled(270, 270,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            img_lbl.setPixmap(px)
            img_lbl.setStyleSheet("background:transparent;")
            img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            greet_lay.addWidget(img_lbl, 1)

        ll.addWidget(greet)

        # ━━ STATS ROW ━━
        self._left_scroll = ls
        bc = len(ambil_semua_beasiswa()); bmc = len(ambil_bookmark_user(self._pid))
        dlc = stats_data.get("total", 0)
        stats = [
            (str(bc),  "Opportunities\nAvailable",  "opportunity.png", "#F6F8F3", "eksplorasi"),
            (str(bmc), "Bookmarked\nScholarship",   "bookmarked.png",  "#FBF8F2", "bookmarks"),
            (str(dlc), "Upcoming\nDeadlines",       "deadline.png",    "#FDF3F1", "kalender"),
            ("7",      "Smart Tips\nFor You",       "smart.png",       "#F6F9F3", "scroll_faq"),
        ]
        sw = QWidget(); sw.setStyleSheet("background:transparent;")
        sl = QHBoxLayout(sw); sl.setContentsMargins(0,0,0,0); sl.setSpacing(10)
        for i,(v,lb,ic_file,bg,nav_target) in enumerate(stats):
            f = QPushButton(); f.setObjectName(f"st{i}"); f.setFixedHeight(88)
            f.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            f.setStyleSheet(f"#{f.objectName()}{{background:{bg};border-radius:14px;border:1px solid {c['border']};}}")
            self._apply_card_shadow(f)
            f.clicked.connect(lambda _, tgt=nav_target: self._handle_stats_click(tgt))
            fl = QHBoxLayout(f)
            fl.setContentsMargins(14,10,10,10); fl.setSpacing(10)

            # Icon with peach circular shadow
            icon_wrap = QLabel()
            icon_wrap.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            icon_wrap.setFixedSize(54, 54)
            icon_wrap.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_wrap.setStyleSheet("background:transparent;")
            ic_path = os.path.join(ASSETS, ic_file)
            if os.path.exists(ic_path):
                px = QPixmap(ic_path).scaled(42, 42, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                icon_wrap.setPixmap(px)
            from PyQt6.QtWidgets import QGraphicsDropShadowEffect
            from PyQt6.QtGui import QColor
            icon_shadow = QGraphicsDropShadowEffect()
            icon_shadow.setBlurRadius(20)
            icon_shadow.setXOffset(0)
            icon_shadow.setYOffset(0)
            icon_shadow.setColor(QColor(255, 255, 255))
            icon_wrap.setGraphicsEffect(icon_shadow)
            fl.addWidget(icon_wrap)

            # Right side: number + label stacked
            right_w = QWidget(); right_w.setStyleSheet("background:transparent;")
            right_w.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            right_l = QVBoxLayout(right_w); right_l.setContentsMargins(0,0,0,0); right_l.setSpacing(0)
            vl = QLabel(v); vl.setFont(QFont(FONT_FAMILY, 22, QFont.Weight.Bold))
            vl.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            vl.setStyleSheet(f"color:{c['text_dark']};background:transparent;")
            right_l.addWidget(vl)
            ll2 = QLabel(lb)
            ll2.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            ll2.setFont(QFont(FONT_FAMILY, 10, QFont.Weight.DemiBold))
            ll2.setStyleSheet(f"color:{c['text_muted']};background:transparent;")
            right_l.addWidget(ll2)
            fl.addWidget(right_w, 1)
            sl.addWidget(f)
        ll.addWidget(sw)

        # ━━ SCHOLARSHIPS TABLE ━━
        ll.addWidget(self._header("Scholarships Trending Now", c, "eksplorasi"))
        all_bea = ambil_semua_beasiswa()[:8]
        table = QTableWidget(len(all_bea), 5)
        table.setHorizontalHeaderLabels(["Name", "Funding", "Degree", "Country", "Deadline"])
        table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in range(1, 5):
            table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True)
        table.setShowGrid(False)
        self._apply_card_shadow(table)
        table.setMinimumHeight(min(len(all_bea) * 44 + 36, 380))
        table.setStyleSheet(f"""
            QTableWidget {{
                background: {c['card']}; border: none;
                border-radius: 14px; font-size: 12px; color: {c['text_dark']};
                alternate-background-color: #FDF9F5;
            }}
            QTableWidget::item {{
                padding: 8px 6px; border-bottom: 1px solid #F0ECE8;
            }}
            QTableWidget::item:selected {{
                background: {c['btn_pale']}; color: {c['text_dark']};
            }}
            QHeaderView::section {{
                background: transparent; color: {c['text_muted']};
                font-size: 11px; font-weight: bold; padding: 8px 6px;
                border: none; border-bottom: 2px solid #E8E0D8;
            }}
        """)
        for i, bea in enumerate(all_bea):
            ni = QTableWidgetItem(bea.get("nama", ""))
            ni.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Bold))
            table.setItem(i, 0, ni)
            table.setItem(i, 1, QTableWidgetItem(bea.get("pendanaan", "-")))
            table.setItem(i, 2, QTableWidgetItem(bea.get("jenjang", "-")))
            table.setItem(i, 3, QTableWidgetItem(bea.get("negara", "-")))
            dl = bea.get("deadline", "-")
            di = QTableWidgetItem(dl)
            di.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if dl and dl != "-":
                try:
                    days = (datetime.datetime.strptime(dl, "%Y-%m-%d").date() - datetime.date.today()).days
                    if days < 0: di.setForeground(QColor("#999"))
                    elif days <= 15: di.setForeground(QColor("#EF4444"))
                    elif days <= 30: di.setForeground(QColor("#F59E0B"))
                    else: di.setForeground(QColor("#22C55E"))
                except: pass
            table.setItem(i, 4, di)
            table.setRowHeight(i, 42)
        ll.addWidget(table)

        # ━━ ANALYTICS SECTION ━━
        analytics = get_analytics_data()
        ll.addWidget(self._build_analytics_section(analytics, c))

        # ━━ INSIGHTS / FAQ ━━
        ll.addWidget(self._header("Insight & FAQ Beasiswa", c))
        ll.addWidget(self._build_insights_section(analytics["insights"], c))
        ll.addStretch()

        # ── RIGHT COLUMN ──
        rs = QScrollArea(); rs.setWidgetResizable(True); rs.setFixedWidth(280)
        rs.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        rw = QWidget(); rw.setStyleSheet("background:transparent;")
        rl = QVBoxLayout(rw); rl.setContentsMargins(0,0,0,0); rl.setSpacing(14)
        rs.setWidget(rw); ml.addWidget(rs, 3)

        # ━━ PROFILE COMPLETENESS ━━
        comp = self._calc_completeness(profil)
        pc = QFrame(); pc.setObjectName("pcCard")
        self._apply_card_shadow(pc)
        pc.setStyleSheet(f"#pcCard{{background:{c['card']};border:1px solid {c['border']};border-radius:16px;}}")
        pcl = QVBoxLayout(pc); pcl.setContentsMargins(18,16,18,16); pcl.setSpacing(8)
        pch = QLabel("Profile\nCompleteness"); pch.setFont(QFont(FONT_FAMILY,13,QFont.Weight.Bold))
        pch.setStyleSheet(f"color:{c['text_dark']};background:transparent;"); pcl.addWidget(pch)
        rrow = QWidget(); rrow.setStyleSheet("background:transparent;")
        rrl = QHBoxLayout(rrow); rrl.setContentsMargins(0,0,0,0); rrl.setSpacing(12)
        ring = ProgressRing(comp, 80, 7); rrl.addWidget(ring)
        dw = QWidget(); dw.setStyleSheet("background:transparent;")
        dwl = QVBoxLayout(dw); dwl.setContentsMargins(0,0,0,0); dwl.setSpacing(3)
        p_done, e_done, c_done = False, False, False
        if profil:
            def is_valid(f): return profil.get(f) is not None and str(profil[f]).strip() != "" and profil[f] != 0
            p_done = all(is_valid(f) for f in ["nama", "tanggal_lahir", "email", "jenis_kelamin"])
            e_done = all(is_valid(f) for f in ["jurusan", "kampus", "jenjang", "semester", "ip"])
            c_done = any(is_valid(f) for f in ["skor_ielts","skor_toefl","skor_duolingo","skor_sat","skor_act","skor_gre","skor_gmat","skor_hsk","level_jlpt"])
            
        checks_data = [("Personal Information", p_done), ("Education", e_done), ("Certifications", c_done)]
        for label, done in checks_data:
            ic = "\u2705" if done else "\u2B1C"
            cl = QLabel(f"{ic}  {label}")
            cl.setStyleSheet(f"color:{c['text_dark'] if done else c['text_muted']};font-size:10px;background:transparent;")
            dwl.addWidget(cl)
        rrl.addWidget(dw); pcl.addWidget(rrow)
        cpb = QPushButton("Complete Profile \u203a"); cpb.setObjectName("cpBtn")
        cpb.setFixedHeight(32); cpb.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        cpb.setStyleSheet(f"#cpBtn{{background:{c['btn_primary']};color:{c['text_dark']};border:none;border-radius:10px;font-size:11px;font-weight:bold;}}#cpBtn:hover{{background:{c['btn_primary_hover']};}}")
        if self._nav: cpb.clicked.connect(lambda: self._nav("profil"))
        pcl.addWidget(cpb); rl.addWidget(pc)

        # ━━ UPCOMING DEADLINES ━━
        dc = QFrame(); dc.setObjectName("dlCard")
        self._apply_card_shadow(dc)
        dc.setStyleSheet(f"#dlCard{{background:{c['card']};border:1px solid {c['border']};border-radius:16px;}}")
        dcl = QVBoxLayout(dc); dcl.setContentsMargins(18,16,18,16); dcl.setSpacing(6)
        dcl.addWidget(self._header("Upcoming Deadlines", c))
        trackers = ambil_semua_tracker(self._pid); shown = 0
        for tr in trackers[:4]:
            if not tr.get("deadline"): continue
            tw2 = QWidget(); tw2.setStyleSheet("background:transparent;")
            tw2l = QVBoxLayout(tw2); tw2l.setContentsMargins(0,4,0,4); tw2l.setSpacing(2)
            tn = QLabel(tr["nama_beasiswa"]); tn.setFont(QFont(FONT_FAMILY,11,QFont.Weight.Bold))
            tn.setStyleSheet(f"color:{c['text_dark']};background:transparent;"); tw2l.addWidget(tn)
            try:
                days = (datetime.datetime.strptime(tr["deadline"],"%Y-%m-%d").date()-datetime.date.today()).days
                clr = "#EF4444" if days<=15 else "#F59E0B" if days<=30 else "#22C55E"
            except: clr = c['text_muted']
            td = QLabel(f"\U0001f4c5 {fmt_deadline(tr['deadline'])}")
            td.setStyleSheet(f"color:{clr};font-size:10px;background:transparent;"); tw2l.addWidget(td)
            dcl.addWidget(tw2)
            sep = QFrame(); sep.setFixedHeight(1); sep.setStyleSheet(f"background:{c['border']};")
            dcl.addWidget(sep); shown += 1
        if not shown:
            el = QLabel("No upcoming deadlines.\nBookmark scholarships to track!")
            el.setStyleSheet(f"color:{c['text_muted']};font-size:11px;background:transparent;")
            el.setWordWrap(True); dcl.addWidget(el)
        rl.addWidget(dc)

        # ━━ CALENDAR ━━
        cc = QFrame(); cc.setObjectName("calCard")
        self._apply_card_shadow(cc)
        cc.setStyleSheet(f"#calCard{{background:{c['card']};border:1px solid {c['border']};border-radius:16px;}}")
        ccl = QVBoxLayout(cc); ccl.setContentsMargins(14,14,14,14); ccl.setSpacing(4)
        ccl.addWidget(self._header("Calendar", c))
        import datetime
        self._cal_date = datetime.date.today()
        cal_nav = QWidget(); cal_nav.setStyleSheet("background:transparent;")
        cal_nav_l = QHBoxLayout(cal_nav); cal_nav_l.setContentsMargins(0,0,0,0)
        
        btn_prev = QPushButton("<"); btn_prev.setFixedSize(24, 24)
        btn_prev.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_prev.setStyleSheet(f"background:transparent; border: 1px solid {c['border']}; border-radius:12px; color:{c['text_muted']};")
        btn_prev.clicked.connect(lambda: self._shift_month(-1))
        
        self._cal_lbl = QLabel(self._cal_date.strftime("%B"))
        self._cal_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._cal_lbl.setStyleSheet(f"background:#FCEAE6; color:{c['text_dark']}; border-radius:12px; font-weight:bold; font-size:11px; padding: 4px 16px;")
        
        btn_next = QPushButton(">"); btn_next.setFixedSize(24, 24)
        btn_next.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_next.setStyleSheet(f"background:transparent; border: 1px solid {c['border']}; border-radius:12px; color:{c['text_muted']};")
        btn_next.clicked.connect(lambda: self._shift_month(1))
        
        cal_nav_l.addWidget(btn_prev)
        cal_nav_l.addStretch()
        cal_nav_l.addWidget(self._cal_lbl)
        cal_nav_l.addStretch()
        cal_nav_l.addWidget(btn_next)
        ccl.addWidget(cal_nav)

        dnw = QWidget(); dnw.setStyleSheet("background:transparent;")
        dnl = QHBoxLayout(dnw); dnl.setContentsMargins(0,6,0,2); dnl.setSpacing(0)
        for d in ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]:
            dl2 = QLabel(d); dl2.setAlignment(Qt.AlignmentFlag.AlignCenter); dl2.setFixedSize(32,18)
            dl2.setStyleSheet(f"color:{c['text_muted']};font-size:9px;font-weight:bold;background:transparent;")
            dnl.addWidget(dl2)
        ccl.addWidget(dnw)

        self._cal_grid_w = QWidget(); self._cal_grid_w.setStyleSheet("background:transparent;")
        self._cal_grid_l = QVBoxLayout(self._cal_grid_w); self._cal_grid_l.setContentsMargins(0,0,0,0); self._cal_grid_l.setSpacing(0)
        ccl.addWidget(self._cal_grid_w)

        btn_full = QPushButton("View Full Calendar >")
        btn_full.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_full.setStyleSheet("background:#889E91; color:white; border-radius:14px; padding:8px; font-weight:bold; font-size:11px; margin-top:8px;")
        if self._nav:
            btn_full.clicked.connect(lambda: self._nav("kalender"))
        ccl.addWidget(btn_full)

        self._render_cal_grid()
        rl.addWidget(cc); rl.addStretch()

    # ═══════════════════════════════════════════════════════════════
    # ANALYTICS SECTION
    # ═══════════════════════════════════════════════════════════════

    def _build_analytics_section(self, analytics: dict, c: dict) -> QWidget:
        """Build the analytics card with tabbed charts."""
        card = QFrame()
        card.setObjectName("analyticsCard")
        self._apply_card_shadow(card)
        card.setStyleSheet(
            f"#analyticsCard{{background:{c['card']};border:1px solid {c['border']};"
            f"border-radius:16px;}}"
        )
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(18, 16, 18, 16)
        card_lay.setSpacing(10)

        # Header row
        hdr_w = QWidget(); hdr_w.setStyleSheet("background:transparent;")
        hdr_l = QHBoxLayout(hdr_w); hdr_l.setContentsMargins(0,0,0,0)
        title_lbl = QLabel("📊  Analitik Beasiswa")
        title_lbl.setFont(QFont(FONT_FAMILY, 13, QFont.Weight.Bold))
        title_lbl.setStyleSheet(f"color:{c['text_dark']};background:transparent;")
        hdr_l.addWidget(title_lbl)
        hdr_l.addStretch()

        # --- Language Support ---
        lang = getattr(self, '_bhs', 'id')
        tx = {
            "id": {
                "title": "📊  Analitik Beasiswa", "total": "Total", "dl": "Berdeadline",
                "t1": "📅 Deadline/Bulan", "t1_sub": "Distribusi deadline beasiswa sepanjang tahun per bulan",
                "t2": "🔢 Deadline/Tanggal", "t2_sub": "Tanggal dalam sebulan yang paling banyak menjadi deadline",
                "t2_note": "🔥 Tanggal {d} adalah yang paling sering muncul ({c} beasiswa)",
                "t3": "🎓 Jenjang", "t3_title": "Distribusi per Jenjang",
                "t4": "🌍 Region", "t4_title": "Distribusi Dalam vs Luar Negeri"
            },
            "en": {
                "title": "📊  Scholarship Analytics", "total": "Total", "dl": "With Deadline",
                "t1": "📅 Deadline/Month", "t1_sub": "Distribution of scholarship deadlines throughout the year by month",
                "t2": "🔢 Deadline/Date", "t2_sub": "Dates in a month that are most frequently deadlines",
                "t2_note": "🔥 Date {d} appears most frequently ({c} scholarships)",
                "t3": "🎓 Degree", "t3_title": "Distribution by Degree",
                "t4": "🌍 Region", "t4_title": "Distribution Domestic vs International"
            }
        }
        _t = tx.get(lang, tx["id"])
        title_lbl.setText(_t["title"])

        # Summary chips
        total_chip = QLabel(f"{_t['total']}: {analytics['total']}")
        total_chip.setStyleSheet("background:#f6d6d0;color:#000000;border-radius:8px;font-size:10px;font-weight:bold;padding:4px 10px;")
        dl_chip = QLabel(f"{_t['dl']}: {analytics['with_deadline']}")
        dl_chip.setStyleSheet("background:#a8c5b0;color:#000000;border-radius:8px;font-size:10px;font-weight:bold;padding:4px 10px;")
        hdr_l.addWidget(total_chip)
        hdr_l.addWidget(dl_chip)
        card_lay.addWidget(hdr_w)

        # Separator
        sep = QFrame(); sep.setFixedHeight(1)
        sep.setStyleSheet(f"background:{c['border']};")
        card_lay.addWidget(sep)

        # Tab widget
        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none; background: transparent;
            }}
            QTabBar::tab {{
                background: {c['input_bg']}; color: {c['text_muted']};
                border: 1px solid {c['border']}; border-bottom: none;
                border-radius: 6px 6px 0 0;
                padding: 5px 12px; font-size: 11px; margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background: {c['card']}; color: {c['text_dark']};
                font-weight: bold; border-bottom: 2px solid {c['btn_primary']};
            }}
            QTabBar::tab:hover {{ background: {c['btn_pale']}; }}
        """)

        # ── Tab 1: Deadline per Bulan ──
        t1 = QWidget(); t1.setStyleSheet("background:transparent;")
        t1l = QVBoxLayout(t1); t1l.setContentsMargins(0, 8, 0, 4)
        subtitle1 = QLabel(_t["t1_sub"])
        subtitle1.setStyleSheet(f"color:{c['text_muted']};font-size:10px;background:transparent;")
        t1l.addWidget(subtitle1)
        chart1 = BarChartWidget(
            analytics["deadline_by_month"],
            color=CHART_COLORS[:12],
            mode=self._mode
        )
        chart1.setMinimumHeight(200)
        t1l.addWidget(chart1)
        tabs.addTab(t1, _t["t1"])

        # ── Tab 2: Deadline per Tanggal ──
        t2 = QWidget(); t2.setStyleSheet("background:transparent;")
        t2l = QVBoxLayout(t2); t2l.setContentsMargins(0, 8, 0, 4)
        subtitle2 = QLabel(_t["t2_sub"])
        subtitle2.setStyleSheet(f"color:{c['text_muted']};font-size:10px;background:transparent;")
        t2l.addWidget(subtitle2)

        peak_day = analytics["peak_day"]
        note2 = QLabel(_t["t2_note"].format(d=peak_day['day'], c=peak_day['count']))
        note2.setStyleSheet(
            f"color:{c['text_accent']};font-size:10px;font-weight:bold;background:transparent;"
        )
        t2l.addWidget(note2)

        chart2 = BarChartWidget(
            analytics["deadline_by_day"],
            color="#D4917B",
            mode=self._mode,
            show_values=False
        )
        chart2.setMinimumHeight(200)
        t2l.addWidget(chart2)
        tabs.addTab(t2, _t["t2"])

        # ── Tab 3: Distribusi Jenjang ──
        t3 = QWidget(); t3.setStyleSheet("background:transparent;")
        t3l = QHBoxLayout(t3); t3l.setContentsMargins(0, 8, 0, 4); t3l.setSpacing(16)

        jenjang_data = analytics["by_jenjang"][:6]
        donut3 = DonutChartWidget(jenjang_data, mode=self._mode)
        donut3.setFixedSize(170, 170)
        t3l.addWidget(donut3)

        # Legend + numbers
        leg3_w = QWidget(); leg3_w.setStyleSheet("background:transparent;")
        leg3_l = QVBoxLayout(leg3_w); leg3_l.setContentsMargins(0,0,0,0); leg3_l.setSpacing(6)
        title3 = QLabel(_t["t3_title"])
        title3.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Bold))
        title3.setStyleSheet(f"color:{c['text_dark']};background:transparent;")
        leg3_l.addWidget(title3)
        total_j = sum(v for _, v in jenjang_data) or 1
        for i, (lbl, val) in enumerate(jenjang_data):
            row = QWidget(); row.setStyleSheet("background:transparent;")
            rl2 = QHBoxLayout(row); rl2.setContentsMargins(0,0,0,0); rl2.setSpacing(6)
            dot = QLabel("●"); dot.setFixedWidth(12)
            dot.setStyleSheet(
                f"color:{CHART_COLORS[i % len(CHART_COLORS)]};background:transparent;font-size:10px;"
            )
            rl2.addWidget(dot)
            lbl_w = QLabel(lbl)
            lbl_w.setStyleSheet(f"color:{c['text_dark']};font-size:10px;background:transparent;")
            rl2.addWidget(lbl_w, 1)
            pct_w = QLabel(f"{int(val/total_j*100)}%  ({val})")
            pct_w.setStyleSheet(f"color:{c['text_muted']};font-size:10px;background:transparent;")
            rl2.addWidget(pct_w)
            leg3_l.addWidget(row)
        leg3_l.addStretch()
        t3l.addWidget(leg3_w, 1)
        tabs.addTab(t3, _t["t3"])

        # ── Tab 4: Distribusi Region ──
        t4 = QWidget(); t4.setStyleSheet("background:transparent;")
        t4l = QHBoxLayout(t4); t4l.setContentsMargins(0, 8, 0, 4); t4l.setSpacing(16)

        region_data = analytics["by_region"]
        # Tetapkan warna eksplisit: Luar Negeri = pink, Dalam Negeri = hijau
        REGION_COLORS = {"Luar Negeri": "#a8c5b0", "Dalam Negeri": "#f6d6d0"}
        region_colors_ordered = [
            REGION_COLORS.get(lbl, CHART_COLORS[i % len(CHART_COLORS)])
            for i, (lbl, _) in enumerate(region_data)
        ]
        donut4 = DonutChartWidget(
            region_data, mode=self._mode, thickness=32,
            colors=region_colors_ordered
        )
        donut4.setFixedSize(170, 170)
        t4l.addWidget(donut4)

        leg4_w = QWidget(); leg4_w.setStyleSheet("background:transparent;")
        leg4_l = QVBoxLayout(leg4_w); leg4_l.setContentsMargins(0,0,0,0); leg4_l.setSpacing(6)
        title4 = QLabel(_t["t4_title"])
        title4.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Bold))
        title4.setStyleSheet(f"color:{c['text_dark']};background:transparent;")
        leg4_l.addWidget(title4)
        total_r = sum(v for _, v in region_data) or 1
        clr_map = {"Luar Negeri": "#a8c5b0", "Dalam Negeri": "#f6d6d0"}
        for i, (lbl, val) in enumerate(region_data):
            row = QWidget(); row.setStyleSheet("background:transparent;")
            rl3 = QHBoxLayout(row); rl3.setContentsMargins(0,0,0,0); rl3.setSpacing(6)
            dot_clr = clr_map.get(lbl, CHART_COLORS[i % len(CHART_COLORS)])
            dot = QLabel("●"); dot.setFixedWidth(12)
            dot.setStyleSheet(f"color:{dot_clr};background:transparent;font-size:10px;")
            rl3.addWidget(dot)
            lbl_w = QLabel(lbl)
            lbl_w.setStyleSheet(f"color:{c['text_dark']};font-size:10px;background:transparent;")
            rl3.addWidget(lbl_w, 1)
            pct_w = QLabel(f"{int(val/total_r*100)}%  ({val})")
            pct_w.setStyleSheet(f"color:{c['text_muted']};font-size:10px;background:transparent;")
            rl3.addWidget(pct_w)
            leg4_l.addWidget(row)

        # Extra context
        ln_pct = int(dict(region_data).get("Luar Negeri", 0) / total_r * 100)
        ctx = QLabel(
            f"💡 {ln_pct}% beasiswa tersedia adalah program internasional. "
            "Persiapkan skor bahasa Inggris untuk membuka lebih banyak peluang!"
        )
        ctx.setWordWrap(True)
        ctx.setStyleSheet(
            f"color:{c['text_muted']};font-size:9px;background:transparent;"
            f"padding:8px;border-radius:8px;background:{c['input_bg']};"
        )
        leg4_l.addWidget(ctx)
        leg4_l.addStretch()
        t4l.addWidget(leg4_w, 1)
        tabs.addTab(t4, _t["t4"])

        card_lay.addWidget(tabs)
        return card

    # ═══════════════════════════════════════════════════════════════
    # INSIGHTS / FAQ SECTION
    # ═══════════════════════════════════════════════════════════════

    def _build_insights_section(self, insights: list, c: dict) -> QWidget:
        """Build expandable FAQ / insight cards from analytics data."""
        wrapper = QWidget(); wrapper.setStyleSheet("background:transparent;")
        wl = QVBoxLayout(wrapper); wl.setContentsMargins(0,0,0,0); wl.setSpacing(8)

        # Tag color map
        tag_colors = {
            "Deadline Trend":    "#FDFDFD",
            "Pola Tanggal":      "#FDFDFD",
            "Distribusi Region": "#FDFDFD",
            "Distribusi Jenjang":"#FDFDFD",
            "Tips Strategis":    "#FDFDFD",
            "Info Penting":      "#FDFDFD",
        }

        for i, ins in enumerate(insights):
            bg = pastel(i, self._mode)
            tc_color = tag_colors.get(ins.get("tag",""), c["text_accent"])

            card = QFrame(); card.setObjectName(f"insCard{i}")
            self._apply_card_shadow(card)
            card.setStyleSheet(
                f"#insCard{i}{{background:{bg};border-radius:14px;"
                f"border:1px solid {c['border']};}}"
            )
            cl = QVBoxLayout(card); cl.setContentsMargins(16, 12, 16, 12); cl.setSpacing(6)

            # Tag badge + icon
            top_row = QWidget(); top_row.setStyleSheet("background:transparent;")
            top_l = QHBoxLayout(top_row); top_l.setContentsMargins(0,0,0,0); top_l.setSpacing(6)

            icon_lbl = QLabel(ins.get("icon","💡"))
            icon_lbl.setFont(QFont(FONT_FAMILY, 15))
            icon_lbl.setStyleSheet("background:transparent;")
            top_l.addWidget(icon_lbl)

            tag_lbl = QLabel(ins.get("tag",""))
            tag_lbl.setStyleSheet(
                "background:#FDFDFD;color:#000000;"
                "border:1px solid #D0D0D0;border-radius:8px;"
                "font-size:9px;font-weight:bold;padding:2px 8px;"
            )
            top_l.addWidget(tag_lbl)
            top_l.addStretch()
            cl.addWidget(top_row)

            # Title (question)
            title_lbl = QLabel(ins.get("title",""))
            title_lbl.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Bold))
            title_lbl.setStyleSheet(f"color:{c['text_dark']};background:transparent;")
            title_lbl.setWordWrap(True)
            cl.addWidget(title_lbl)

            # Body (answer)
            body_lbl = QLabel(ins.get("body",""))
            body_lbl.setStyleSheet(
                f"color:{c['text_muted']};font-size:10px;background:transparent;"
            )
            body_lbl.setWordWrap(True)
            cl.addWidget(body_lbl)

            wl.addWidget(card)

        return wrapper

    def _chip(self, text: str, color: str, c: dict) -> QLabel:
        """Small colored pill label."""
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"background:{color}22;color:{color};border:1px solid {color}55;"
            f"border-radius:8px;font-size:9px;font-weight:bold;padding:2px 8px;"
        )
        return lbl
