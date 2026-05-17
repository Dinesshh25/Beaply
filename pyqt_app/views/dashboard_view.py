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
        greet.setFixedHeight(160)
        greet.setStyleSheet(f"""
            #greetCard {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0.5,
                    stop:0 #FCEBE3, stop:0.6 #F9E0D5, stop:1 #F4C9BE);
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
        g1.setFont(QFont(FONT_FAMILY, 13)); g1.setStyleSheet("color:#777;background:transparent;")
        tl.addWidget(g1)
        g2 = QLabel("Let's find your next")
        g2.setFont(QFont(FONT_FAMILY, 22, QFont.Weight.Bold))
        g2.setStyleSheet(f"color:{c['text_dark']};background:transparent;"); tl.addWidget(g2)
        aw = QWidget(); aw.setStyleSheet("background:transparent;")
        al = QHBoxLayout(aw); al.setContentsMargins(0,0,0,0); al.setSpacing(0)
        for t, clr in [("life-","#7DB87D"),("changing","#E8A0A0"),(" opportunity",c['text_dark'])]:
            lb = QLabel(t); lb.setFont(QFont(FONT_FAMILY, 22, QFont.Weight.Bold))
            lb.setStyleSheet(f"color:{clr};background:transparent;"); al.addWidget(lb)
        al.addStretch(); tl.addWidget(aw)
        g3 = QLabel("Explore thousands of opportunities, discover\nscholarships, and make your dreams happen!")
        g3.setStyleSheet("color:#888;font-size:11px;background:transparent;"); tl.addWidget(g3)
        tl.addStretch()
        greet_lay.addWidget(text_w, 3)

        # Illustration side
        img_path = os.path.join(ASSETS, "graduation_cap.png")
        if os.path.exists(img_path):
            img_lbl = QLabel()
            px = QPixmap(img_path).scaled(140, 140,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            img_lbl.setPixmap(px)
            img_lbl.setStyleSheet("background:transparent;")
            img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            greet_lay.addWidget(img_lbl, 1)

        ll.addWidget(greet)

        # ━━ STATS ROW ━━
        bc = len(ambil_semua_beasiswa()); bmc = len(ambil_bookmark_user(self._pid))
        dlc = stats_data.get("total", 0)
        stats = [
            (str(bc),  "Opportunities\nAvailable",  "\U0001f4da", "#E8EBE4"),
            (str(bmc), "Bookmarked\nScholarship",   "\U0001f516", "#F4EFE6"),
            (str(dlc), "Upcoming\nDeadlines",       "\U0001f4c5", "#F6E6E4"),
            ("7",      "Smart Tips\nFor You",       "\U0001f4a1", "#E8EEE4"),
        ]
        sw = QWidget(); sw.setStyleSheet("background:transparent;")
        sl = QHBoxLayout(sw); sl.setContentsMargins(0,0,0,0); sl.setSpacing(10)
        for i,(v,lb,ic,bg) in enumerate(stats):
            f = QFrame(); f.setObjectName(f"st{i}"); f.setFixedHeight(88)
            f.setStyleSheet(f"#{f.objectName()}{{background:{bg};border-radius:14px;}}")
            fl = QVBoxLayout(f); fl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            fl.setContentsMargins(8,8,8,8)
            r = QWidget(); r.setStyleSheet("background:transparent;")
            rl = QHBoxLayout(r); rl.setContentsMargins(0,0,0,0)
            rl.setAlignment(Qt.AlignmentFlag.AlignCenter); rl.setSpacing(6)
            il = QLabel(ic); il.setFont(QFont(FONT_FAMILY,16))
            il.setStyleSheet("background:transparent;"); rl.addWidget(il)
            vl = QLabel(v); vl.setFont(QFont(FONT_FAMILY,22,QFont.Weight.Bold))
            vl.setStyleSheet(f"color:{c['text_dark']};background:transparent;"); rl.addWidget(vl)
            fl.addWidget(r)
            ll2 = QLabel(lb); ll2.setAlignment(Qt.AlignmentFlag.AlignCenter)
            ll2.setStyleSheet(f"color:{c['text_muted']};font-size:10px;background:transparent;")
            fl.addWidget(ll2)
            sl.addWidget(f)
        ll.addWidget(sw)

        # ━━ SCHOLARSHIPS TABLE ━━
        ll.addWidget(self._header("Scholarships Trending Now", c, "eksplorasi"))
        all_bea = ambil_semua_beasiswa()[:8]
        table = QTableWidget(len(all_bea), 5)
        table.setHorizontalHeaderLabels(["Name", "Funding", "Degree", "Country", "Deadline"])
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in range(1, 5):
            table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True)
        table.setShowGrid(False)
        table.setMinimumHeight(min(len(all_bea) * 44 + 36, 380))
        table.setStyleSheet(f"""
            QTableWidget {{
                background: {c['card']}; border: 1px solid {c['border']};
                border-radius: 14px; font-size: 12px; color: {c['text_dark']};
            }}
            QTableWidget::item {{
                padding: 8px 6px; border-bottom: 1px solid {c['border']};
            }}
            QTableWidget::item:selected {{
                background: {c['btn_pale']}; color: {c['text_dark']};
            }}
            QHeaderView::section {{
                background: {c['input_bg']}; color: {c['text_muted']};
                font-size: 11px; font-weight: bold; padding: 8px 6px;
                border: none; border-bottom: 2px solid {c['border']};
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
        pc.setStyleSheet(f"#pcCard{{background:{c['card']};border:1px solid {c['border']};border-radius:16px;}}")
        pcl = QVBoxLayout(pc); pcl.setContentsMargins(18,16,18,16); pcl.setSpacing(8)
        pch = QLabel("Profile\nCompleteness"); pch.setFont(QFont(FONT_FAMILY,13,QFont.Weight.Bold))
        pch.setStyleSheet(f"color:{c['text_dark']};background:transparent;"); pcl.addWidget(pch)
        rrow = QWidget(); rrow.setStyleSheet("background:transparent;")
        rrl = QHBoxLayout(rrow); rrl.setContentsMargins(0,0,0,0); rrl.setSpacing(12)
        ring = ProgressRing(comp, 80, 7); rrl.addWidget(ring)
        dw = QWidget(); dw.setStyleSheet("background:transparent;")
        dwl = QVBoxLayout(dw); dwl.setContentsMargins(0,0,0,0); dwl.setSpacing(3)
        checks = [("Personal Information","nama"),("Education","jurusan"),
                  ("Documents",None),("Achievements","skor_ielts")]
        for label, field in checks:
            done = bool(field and profil and profil.get(field) and str(profil[field]).strip() != "" and profil[field] != 0)
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
        cc.setStyleSheet(f"#calCard{{background:{c['card']};border:1px solid {c['border']};border-radius:16px;}}")
        ccl = QVBoxLayout(cc); ccl.setContentsMargins(14,14,14,14); ccl.setSpacing(4)
        ccl.addWidget(self._header("Calendar", c))
        today = datetime.date.today()
        cm = QLabel(today.strftime("%B %Y")); cm.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cm.setStyleSheet(f"color:{c['text_muted']};font-size:12px;background:transparent;"); ccl.addWidget(cm)
        dnw = QWidget(); dnw.setStyleSheet("background:transparent;")
        dnl = QHBoxLayout(dnw); dnl.setContentsMargins(0,6,0,2); dnl.setSpacing(0)
        for d in ["M","T","W","T","F","S","S"]:
            dl2 = QLabel(d); dl2.setAlignment(Qt.AlignmentFlag.AlignCenter); dl2.setFixedSize(32,18)
            dl2.setStyleSheet(f"color:{c['text_muted']};font-size:10px;font-weight:bold;background:transparent;")
            dnl.addWidget(dl2)
        ccl.addWidget(dnw)
        for week in calendar.monthcalendar(today.year, today.month):
            ww = QWidget(); ww.setStyleSheet("background:transparent;")
            wl = QHBoxLayout(ww); wl.setContentsMargins(0,0,0,0); wl.setSpacing(0)
            for day in week:
                dl3 = QLabel(str(day) if day else "")
                dl3.setAlignment(Qt.AlignmentFlag.AlignCenter); dl3.setFixedSize(32,28)
                if day == today.day:
                    dl3.setStyleSheet(f"background:{c['btn_primary']};color:white;border-radius:14px;font-weight:bold;font-size:11px;")
                elif day:
                    dl3.setStyleSheet(f"color:{c['text_dark']};font-size:11px;background:transparent;")
                else:
                    dl3.setStyleSheet("background:transparent;")
                wl.addWidget(dl3)
            ccl.addWidget(ww)
        rl.addWidget(cc); rl.addStretch()

    # ═══════════════════════════════════════════════════════════════
    # ANALYTICS SECTION
    # ═══════════════════════════════════════════════════════════════

    def _build_analytics_section(self, analytics: dict, c: dict) -> QWidget:
        """Build the analytics card with tabbed charts."""
        card = QFrame()
        card.setObjectName("analyticsCard")
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

        # Summary chips
        total_chip = self._chip(f"Total: {analytics['total']}", "#7DB87D", c)
        dl_chip    = self._chip(f"Berdeadline: {analytics['with_deadline']}", "#D4917B", c)
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
        subtitle1 = QLabel("Distribusi deadline beasiswa sepanjang tahun per bulan")
        subtitle1.setStyleSheet(f"color:{c['text_muted']};font-size:10px;background:transparent;")
        t1l.addWidget(subtitle1)
        chart1 = BarChartWidget(
            analytics["deadline_by_month"],
            color=CHART_COLORS[:12],
            mode=self._mode
        )
        chart1.setMinimumHeight(200)
        t1l.addWidget(chart1)
        tabs.addTab(t1, "📅 Deadline/Bulan")

        # ── Tab 2: Deadline per Tanggal ──
        t2 = QWidget(); t2.setStyleSheet("background:transparent;")
        t2l = QVBoxLayout(t2); t2l.setContentsMargins(0, 8, 0, 4)
        subtitle2 = QLabel("Tanggal dalam sebulan yang paling banyak menjadi deadline")
        subtitle2.setStyleSheet(f"color:{c['text_muted']};font-size:10px;background:transparent;")
        t2l.addWidget(subtitle2)

        peak_day = analytics["peak_day"]
        note2 = QLabel(
            f"🔥 Tanggal {peak_day['day']} adalah yang paling sering muncul "
            f"({peak_day['count']} beasiswa)"
        )
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
        tabs.addTab(t2, "🔢 Deadline/Tanggal")

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
        title3 = QLabel("Distribusi per Jenjang")
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
        tabs.addTab(t3, "🎓 Jenjang")

        # ── Tab 4: Distribusi Region ──
        t4 = QWidget(); t4.setStyleSheet("background:transparent;")
        t4l = QHBoxLayout(t4); t4l.setContentsMargins(0, 8, 0, 4); t4l.setSpacing(16)

        region_data = analytics["by_region"]
        # Tetapkan warna eksplisit: Luar Negeri = biru, Dalam Negeri = hijau
        REGION_COLORS = {"Luar Negeri": "#3B82F6", "Dalam Negeri": "#22C55E"}
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
        title4 = QLabel("Distribusi Dalam vs Luar Negeri")
        title4.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Bold))
        title4.setStyleSheet(f"color:{c['text_dark']};background:transparent;")
        leg4_l.addWidget(title4)
        total_r = sum(v for _, v in region_data) or 1
        clr_map = {"Luar Negeri": "#3B82F6", "Dalam Negeri": "#22C55E"}
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
        tabs.addTab(t4, "🌍 Region")

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
            "Deadline Trend":    "#D4917B",
            "Pola Tanggal":      "#C8A87D",
            "Distribusi Region": "#7DB8C8",
            "Distribusi Jenjang":"#A8C5B0",
            "Tips Strategis":    "#B07DB8",
            "Info Penting":      "#7D9AB8",
        }

        for i, ins in enumerate(insights):
            bg = pastel(i, self._mode)
            tc_color = tag_colors.get(ins.get("tag",""), c["text_accent"])

            card = QFrame(); card.setObjectName(f"insCard{i}")
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
                f"background:{tc_color}22;color:{tc_color};"
                f"border:1px solid {tc_color}55;border-radius:8px;"
                f"font-size:9px;font-weight:bold;padding:2px 8px;"
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
