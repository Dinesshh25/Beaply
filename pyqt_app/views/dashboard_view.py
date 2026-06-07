"""
pyqt_app/views/dashboard_view.py
Dashboard page — 2-column layout matching Figma mockup.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QSizePolicy, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView, QTabWidget,
    QDialog, QComboBox, QSpinBox, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor, QPixmap, QColor
import datetime, os, calendar
import json

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
from pyqt_app.views.eksplorasi_view import DetailDialog

ASSETS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets"))


TRANSLATIONS = {
    'id': {
        'see_all': 'Lihat semua \u203a',
        'sel_month_year': 'Pilih Bulan & Tahun',
        'apply': 'Terapkan',
        'g_morning': 'Selamat pagi',
        'g_afternoon': 'Selamat siang',
        'g_evening': 'Selamat sore',
        'g_night': 'Selamat malam',
        'g_anon': 'Anonim',
        'find_next': 'Mari temukan',
        'life_changing': 'peluang',
        'opportunity': 'yang mengubah hidupmu',
        'explore_desc': 'Jelajahi ribuan peluang, temukan\nbeasiswa, dan wujudkan impianmu!',
        'opp_avail': 'Peluang\nTersedia',
        'bm_sch': 'Beasiswa\nTersimpan',
        'up_deadlines': 'Batas Waktu\nMendatang',
        'smart_tips': 'Saran Cerdas\nUntukmu',
        'trending': 'Beasiswa Populer Saat Ini',
        'tbl_name': 'Nama',
        'tbl_fund': 'Pendanaan',
        'tbl_deg': 'Jenjang',
        'tbl_loc': 'Negara',
        'tbl_dl': 'Batas Waktu',
        'out_country': 'Luar Negeri',
        'in_country': 'Dalam Negeri',
        'prof_comp': 'Kelengkapan\nProfil',
        'p_info': 'Informasi Pribadi',
        'edu': 'Pendidikan',
        'cert': 'Sertifikasi',
        'comp_prof_btn': 'Lengkapi Profil >',
        'no_up_dl': 'Tidak ada batas waktu terdekat.\nSimpan beasiswa untuk dilacak!',
        'calendar': 'Kalender',
        'view_full_cal': 'Lihat Kalender Lengkap >',
        'insight_faq': 'Insight & FAQ Beasiswa',
        # Analytics tab
        "an_title": "📊  Analitik Beasiswa", "an_total": "Total", "an_dl": "Berdeadline",
        "t1": "📅 Deadline/Bulan", "t1_sub": "Distribusi deadline beasiswa sepanjang tahun per bulan",
        "t2": "🔢 Deadline/Tanggal", "t2_sub": "Tanggal dalam sebulan yang paling banyak menjadi deadline",
        "t2_note": "🔥 Tanggal {d} adalah yang paling sering muncul ({c} beasiswa)",
        "t3": "🎓 Jenjang", "t3_title": "Distribusi per Jenjang",
        "t4": "🌍 Region", "t4_title": "Distribusi Dalam vs Luar Negeri",
        "ctx_tips": "💡 {pct}% beasiswa tersedia adalah program internasional. Persiapkan skor bahasa Inggris untuk membuka lebih banyak peluang!"
    },
    'en': {
        'see_all': 'See all \u203a',
        'sel_month_year': 'Select Month & Year',
        'apply': 'Apply',
        'g_morning': 'Good morning',
        'g_afternoon': 'Good afternoon',
        'g_evening': 'Good evening',
        'g_night': 'Good night',
        'g_anon': 'Anonymous',
        'find_next': "Let's find your next",
        'life_changing': 'life-changing',
        'opportunity': 'opportunity',
        'explore_desc': 'Explore thousands of opportunities, discover\nscholarships, and make your dreams happen!',
        'opp_avail': 'Opportunities\nAvailable',
        'bm_sch': 'Bookmarked\nScholarship',
        'up_deadlines': 'Upcoming\nDeadlines',
        'smart_tips': 'Smart Tips\nFor You',
        'trending': 'Scholarships Trending Now',
        'tbl_name': 'Name',
        'tbl_fund': 'Funding',
        'tbl_deg': 'Degree',
        'tbl_loc': 'Country',
        'tbl_dl': 'Deadline',
        'out_country': 'International',
        'in_country': 'Domestic',
        'prof_comp': 'Profile\nCompleteness',
        'p_info': 'Personal Information',
        'edu': 'Education',
        'cert': 'Certifications',
        'comp_prof_btn': 'Complete Profile >',
        'no_up_dl': 'No upcoming deadlines.\nBookmark scholarships to track!',
        'calendar': 'Calendar',
        'view_full_cal': 'View Full Calendar >',
        'insight_faq': 'Insight & FAQ Scholarships',
        # Analytics tab
        "an_title": "📊  Scholarship Analytics", "an_total": "Total", "an_dl": "With Deadline",
        "t1": "📅 Deadline/Month", "t1_sub": "Distribution of scholarship deadlines throughout the year by month",
        "t2": "🔢 Deadline/Date", "t2_sub": "Dates in a month that are most frequently deadlines",
        "t2_note": "🔥 Date {d} appears most frequently ({c} scholarships)",
        "t3": "🎓 Degree", "t3_title": "Distribution by Degree",
        "t4": "🌍 Region", "t4_title": "Distribution Domestic vs International",
        "ctx_tips": "💡 {pct}% available scholarships are international programs. Prepare English scores to open more opportunities!"
    }
}


class DashboardView(QWidget):

    def __init__(self, profil_id, bhs="id", navigate_cb=None, mode="light", parent=None):
        super().__init__(parent)
        self._pid = profil_id
        self._bhs = bhs
        self._nav = navigate_cb
        self._mode = mode
        self._t = TRANSLATIONS.get(bhs, TRANSLATIONS['id'])
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
        t = self._t
        w = QWidget(); w.setStyleSheet("background:transparent;")
        h = QHBoxLayout(w); h.setContentsMargins(0,0,0,0)
        l = QLabel(text); l.setFont(QFont(FONT_FAMILY, 14, QFont.Weight.Bold))
        l.setStyleSheet(f"color:{c['text_dark']};background:transparent;"); h.addWidget(l)
        h.addStretch()
        if target and self._nav:
            b = QPushButton(t['see_all']); b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            b.setStyleSheet(f"background:transparent;border:none;color:{c['text_accent']};font-size:11px;")
            b.clicked.connect(lambda: self._nav(target)); h.addWidget(b)
        return w

    def _shift_month(self, d: int):
        m = self._cal_date.month + d
        y = self._cal_date.year
        if m > 12: m -= 12; y += 1
        elif m < 1: m += 12; y -= 1
        import datetime
        self._cal_date = datetime.date(y, m, 1)
        # Use simple strftime since full localization of month names requires more logic
        # For a truly localized experience, we can map month numbers to names here
        self._cal_btn.setText(self._cal_date.strftime("%B %Y"))
        self._render_cal_grid()

    def _pick_month_year(self):
        c = palette(self._mode)
        t = self._t
        dlg = QDialog(self)
        dlg.setWindowTitle(t['sel_month_year'])
        dlg.setFixedSize(280, 180)
        dlg.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        dlg.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        main_lay = QVBoxLayout(dlg)
        main_lay.setContentsMargins(10, 10, 10, 10)
        bg = QFrame()
        bg.setStyleSheet(f"QFrame {{ background: {c['card']}; border-radius: 16px; border: 1px solid {c['border']}; }}")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15); shadow.setColor(QColor(0,0,0,30)); shadow.setOffset(0,4)
        bg.setGraphicsEffect(shadow)
        main_lay.addWidget(bg)
        
        lay = QVBoxLayout(bg)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(12)
        
        top_lay = QHBoxLayout()
        top_lay.addStretch(1)
        title = QLabel(t['sel_month_year'])
        title.setStyleSheet(f"font-weight:bold; color:{c['text_dark']}; font-size:12px; border:none; background:transparent;")
        top_lay.addWidget(title)
        top_lay.addStretch(1)
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(20, 20)
        close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        close_btn.setStyleSheet("QPushButton { background:transparent; color:#888; font-weight:bold; border:none; } QPushButton:hover { color:#333; }")
        close_btn.clicked.connect(dlg.reject)
        top_lay.addWidget(close_btn)
        lay.addLayout(top_lay)
        
        hlay = QHBoxLayout()
        cb_m = QComboBox()
        import calendar
        for i in range(1, 13): cb_m.addItem(calendar.month_name[i], i)
        cb_m.setCurrentIndex(self._cal_date.month - 1)
        cb_m.setStyleSheet(f"QComboBox {{ background:{c['input_bg']}; color:{c['text_dark']}; border:1px solid {c['border']}; border-radius:8px; padding:4px 8px; }}")
        
        sb_y = QSpinBox()
        sb_y.setRange(1900, 2100)
        sb_y.setValue(self._cal_date.year)
        sb_y.setStyleSheet(f"QSpinBox {{ background:{c['input_bg']}; color:{c['text_dark']}; border:1px solid {c['border']}; border-radius:8px; padding:4px 8px; }}")
        
        hlay.addWidget(cb_m, 2)
        hlay.addWidget(sb_y, 1)
        lay.addLayout(hlay)
        
        btn_ok = QPushButton(t['apply'])
        btn_ok.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_ok.setStyleSheet(f"QPushButton {{ background:{c['btn_primary']}; color:{c['text_dark']}; border:none; border-radius:10px; font-weight:bold; padding:8px; }} QPushButton:hover {{ background:{c['btn_primary_hover']}; }}")
        btn_ok.clicked.connect(dlg.accept)
        lay.addWidget(btn_ok)
        
        if dlg.exec() == QDialog.DialogCode.Accepted:
            m = cb_m.currentData()
            y = sb_y.value()
            import datetime
            self._cal_date = datetime.date(y, m, 1)
            self._cal_btn.setText(self._cal_date.strftime("%B %Y"))
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

    def _on_table_click(self, row, column):
        if hasattr(self, '_all_bea') and row < len(self._all_bea):
            bea = self._all_bea[row]
            if 'nama' in bea and 'nama_beasiswa' not in bea:
                bea['nama_beasiswa'] = bea['nama']
            dlg = DetailDialog(bea, self._mode, self._pid, self, bhs=self._bhs)
            dlg.exec()

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
        t = self._t
        profil = tampil_profil(self._pid)
        nama = profil["nama"].split()[0] if profil and profil.get("nama") else t['g_anon']
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
        if self._mode == 'dark':
            greet_gradient = f"qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {c['card']}, stop:0.4 #332A28, stop:1 #3D2E2A)"
        else:
            greet_gradient = "qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #FFFFFF, stop:0.4 #FDF4F2, stop:1 #FADCD2)"
        greet.setStyleSheet(f"""
            #greetCard {{
                background: {greet_gradient};
                border-radius: 18px; border:none;
            }}
        """)
        greet_lay = QHBoxLayout(greet)
        greet_lay.setContentsMargins(30, 20, 20, 20)
        greet_lay.setSpacing(10)

        # Text side
        text_w = QWidget(); text_w.setStyleSheet("background:transparent;")
        tl = QVBoxLayout(text_w); tl.setContentsMargins(0,0,0,0); tl.setSpacing(2)
        
        hour = datetime.datetime.now().hour
        if 5 <= hour < 12: greeting_text = t['g_morning']
        elif 12 <= hour < 17: greeting_text = t['g_afternoon']
        elif 17 <= hour < 21: greeting_text = t['g_evening']
        else: greeting_text = t['g_night']
        
        g1 = QLabel(f"{greeting_text}, {nama}!")
        g1.setFont(QFont(FONT_FAMILY, 13)); g1.setStyleSheet(f"color:{c['text_muted']};background:transparent;")
        tl.addWidget(g1)
        g2 = QLabel(t['find_next'])
        g2.setFont(QFont(FONT_FAMILY, 24, QFont.Weight.Bold))
        g2.setStyleSheet(f"color:{c['text_dark']};background:transparent;")
        g2.setMinimumHeight(42); tl.addWidget(g2)
        
        grad_str = t['life_changing'] if self._bhs == 'en' else t['life_changing']
        grad_html = ""
        for idx, ch in enumerate(grad_str):
            frac = idx / (len(grad_str) - 1) if len(grad_str) > 1 else 0
            r = int(168 + frac * (244 - 168))
            g = int(197 + frac * (169 - 197))
            b = int(176 + frac * (160 - 176))
            grad_html += f"<span style='color:rgb({r},{g},{b})'>{ch}</span>"
            
        b_text = f"<b>{grad_html} {t['opportunity']}</b>"

        g2b = QLabel(b_text)
        g2b.setFont(QFont(FONT_FAMILY, 24, QFont.Weight.Bold))
        g2b.setStyleSheet(f"color:{c['text_dark']};background:transparent;")
        g2b.setMinimumHeight(42); tl.addWidget(g2b)
        tl.addSpacing(6)
        g3 = QLabel(t['explore_desc'])
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
        # Count bookmarked scholarships with upcoming deadlines
        _today = datetime.date.today()
        _bm_list = ambil_bookmark_user(self._pid)
        dlc = 0
        for _bm in _bm_list:
            _dl = _bm.get("deadline", "")
            if _dl:
                try:
                    _dl_date = datetime.datetime.strptime(_dl[:10], "%Y-%m-%d").date()
                    if _dl_date >= _today:
                        dlc += 1
                except (ValueError, TypeError):
                    pass
        if self._mode == 'dark':
            stat_bgs = ["#2B302C", "#36322C", "#382928", "#2A3029"]
        else:
            stat_bgs = ["#F6F8F3", "#FBF8F2", "#FDF3F1", "#F6F9F3"]
        stats = [
            (str(bc),  t['opp_avail'],  "opportunity.png", stat_bgs[0], "eksplorasi"),
            (str(bmc), t['bm_sch'],     "bookmarked.png",  stat_bgs[1], "bookmarks"),
            (str(dlc), t['up_deadlines'],"deadline.png",    stat_bgs[2], "kalender"),
            ("7",      t['smart_tips'],  "smart.png",       stat_bgs[3], "scroll_faq"),
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

            # Icon with white circular shadow (glow)
            icon_wrap = QLabel()
            icon_wrap.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            icon_wrap.setFixedSize(54, 54)
            icon_wrap.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if self._mode == 'dark':
                icon_wrap.setStyleSheet("background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 rgba(60,64,67,200), stop:0.6 rgba(60,64,67,100), stop:1 rgba(60,64,67,0)); border-radius:27px;")
            else:
                icon_wrap.setStyleSheet("background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 rgba(255,255,255,255), stop:0.6 rgba(255,255,255,150), stop:1 rgba(255,255,255,0)); border-radius:27px;")
            ic_path = os.path.join(ASSETS, ic_file)
            if os.path.exists(ic_path):
                px = QPixmap(ic_path).scaled(42, 42, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                icon_wrap.setPixmap(px)
            icon_shadow = QGraphicsDropShadowEffect()
            icon_shadow.setBlurRadius(25)
            icon_shadow.setXOffset(0)
            icon_shadow.setYOffset(0)
            icon_shadow.setColor(QColor(255, 255, 255, 200))
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
        ll.addWidget(self._header(t['trending'], c, "eksplorasi"))
        self._all_bea = ambil_semua_beasiswa()[:8]
        table = QTableWidget(len(self._all_bea), 5)
        table.setHorizontalHeaderLabels([t['tbl_name'], t['tbl_fund'], t['tbl_deg'], t['tbl_loc'], t['tbl_dl']])
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
        table.setMinimumHeight(min(len(self._all_bea) * 44 + 36, 380))
        alt_bg = '#2F3033' if self._mode == 'dark' else '#FDF9F5'
        item_border = c['border']
        table.setStyleSheet(f"""
            QTableWidget {{
                background: {c['card']}; border: none;
                border-radius: 14px; font-size: 12px; color: {c['text_dark']};
                alternate-background-color: {alt_bg};
            }}
            QTableWidget::item {{
                padding: 8px 6px; border-bottom: 1px solid {item_border};
            }}
            QTableWidget::item:selected {{
                background: {c['btn_pale']}; color: {c['text_dark']};
            }}
            QHeaderView::section {{
                background: transparent; color: {c['text_muted']};
                font-size: 11px; font-weight: bold; padding: 8px 6px;
                border: none; border-bottom: 2px solid {c['border']};
            }}
        """)
        for i, bea in enumerate(self._all_bea):
            ni = QTableWidgetItem(bea.get("nama", ""))
            ni.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Bold))
            table.setItem(i, 0, ni)
            
            # Funding (kategori)
            kategori_val = bea.get("kategori", "-")
            if kategori_val:
                kategori_val = kategori_val.title()
            else:
                kategori_val = "-"
            table.setItem(i, 1, QTableWidgetItem(kategori_val))
            
            # Degree (jenjang)
            jenjang_val = bea.get("jenjang", "-")
            if jenjang_val and jenjang_val.startswith("["):
                try:
                    parsed = json.loads(jenjang_val)
                    if isinstance(parsed, list):
                        jenjang_val = ", ".join(parsed)
                except:
                    pass
            elif not jenjang_val:
                jenjang_val = "-"
            table.setItem(i, 2, QTableWidgetItem(jenjang_val))
            
            # Country (lokasi)
            lokasi_val = bea.get("lokasi", "-")
            if not lokasi_val or lokasi_val == "None":
                if bea.get("kategori") == "internasional":
                    lokasi_val = t['out_country']
                else:
                    lokasi_val = t['in_country']
            table.setItem(i, 3, QTableWidgetItem(lokasi_val))
            
            # Deadline
            dl = bea.get("deadline")
            formatted_dl = fmt_deadline(dl) if dl else "-"
            di = QTableWidgetItem(formatted_dl)
            di.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if dl:
                try:
                    days = (datetime.datetime.strptime(dl[:10], "%Y-%m-%d").date() - datetime.date.today()).days
                    if days < 0: di.setForeground(QColor("#999"))
                    elif days <= 15: di.setForeground(QColor("#EF4444"))
                    elif days <= 30: di.setForeground(QColor("#F59E0B"))
                    else: di.setForeground(QColor("#22C55E"))
                except:
                    pass
            table.setItem(i, 4, di)
            table.setRowHeight(i, 42)
        table.cellClicked.connect(self._on_table_click)
        table.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        ll.addWidget(table)

        # ━━ ANALYTICS SECTION ━━
        analytics = get_analytics_data()
        ll.addWidget(self._build_analytics_section(analytics, c))

        # ━━ INSIGHTS / FAQ ━━
        ll.addWidget(self._header(t['insight_faq'], c))
        ll.addWidget(self._build_insights_section(analytics["insights"], c))
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
        pch = QLabel(t['prof_comp']); pch.setFont(QFont(FONT_FAMILY,13,QFont.Weight.Bold))
        pch.setStyleSheet(f"color:{c['text_dark']};background:transparent;"); pcl.addWidget(pch)
        rrow = QWidget(); rrow.setStyleSheet("background:transparent;")
        rrl = QHBoxLayout(rrow); rrl.setContentsMargins(0,0,0,0); rrl.setSpacing(12)
        ring = ProgressRing(comp, 80, 7, bg_color=c['border'], text_color=c['text_dark']); rrl.addWidget(ring)
        dw = QWidget(); dw.setStyleSheet("background:transparent;")
        dwl = QVBoxLayout(dw); dwl.setContentsMargins(0,0,0,0); dwl.setSpacing(3)
        p_done, e_done, c_done = False, False, False
        if profil:
            def is_valid(f): return profil.get(f) is not None and str(profil[f]).strip() != "" and profil[f] != 0
            p_done = all(is_valid(f) for f in ["nama", "tanggal_lahir", "email", "jenis_kelamin"])
            e_done = all(is_valid(f) for f in ["jurusan", "kampus", "jenjang", "semester", "ip"])
            c_done = any(is_valid(f) for f in ["skor_ielts","skor_toefl","skor_duolingo","skor_sat","skor_act","skor_gre","skor_gmat","skor_hsk","level_jlpt"])
            
        checks_data = [(t['p_info'], p_done), (t['edu'], e_done), (t['cert'], c_done)]
        for label, done in checks_data:
            ic = "\u2705" if done else "\u2B1C"
            cl = QLabel(f"{ic}  {label}")
            cl.setStyleSheet(f"color:{c['text_dark'] if done else c['text_muted']};font-size:12px;background:transparent;")
            dwl.addWidget(cl)
        rrl.addWidget(dw); pcl.addWidget(rrow)
        cpb = QPushButton(t['comp_prof_btn']); cpb.setObjectName("cpBtn")
        cpb.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        cpb.setStyleSheet(f"#cpBtn{{background:#889E91; color:black; border-radius:14px; padding:8px; font-size:11px; font-weight:bold;}}")
        if self._nav: cpb.clicked.connect(lambda: self._nav("profil"))
        pcl.addWidget(cpb); rl.addWidget(pc)

        # ━━ UPCOMING DEADLINES (Tracker + Bookmark) ━━
        dc = QFrame(); dc.setObjectName("dlCard")
        self._apply_card_shadow(dc)
        dc.setStyleSheet(f"#dlCard{{background:{c['card']};border:1px solid {c['border']};border-radius:16px;}}")
        dcl = QVBoxLayout(dc); dcl.setContentsMargins(18,16,18,16); dcl.setSpacing(6)
        dcl.addWidget(self._header(t['up_deadlines'].replace('\n', ' '), c, "kalender"))
        # Merge deadlines from tracker AND bookmarks
        upcoming_items = []
        trackers = ambil_semua_tracker(self._pid)
        for tr in trackers:
            dl = tr.get("deadline")
            if not dl: continue
            try:
                days = (datetime.datetime.strptime(dl, "%Y-%m-%d").date() - datetime.date.today()).days
                if days >= 0:
                    upcoming_items.append({"nama": tr["nama_beasiswa"], "deadline": dl, "days": days, "src": "tracker"})
            except: pass
        bookmarks = ambil_bookmark_user(self._pid)
        bm_names_added = {u["nama"] for u in upcoming_items}
        for bm in bookmarks:
            dl = bm.get("deadline")
            nm = bm.get("nama", "")
            if not dl or nm in bm_names_added: continue
            try:
                days = (datetime.datetime.strptime(dl, "%Y-%m-%d").date() - datetime.date.today()).days
                if days >= 0:
                    upcoming_items.append({"nama": nm, "deadline": dl, "days": days, "src": "bookmark"})
            except: pass
        upcoming_items.sort(key=lambda x: x["days"])
        shown = 0
        for item in upcoming_items[:4]:
            tw2 = QWidget(); tw2.setStyleSheet("background:transparent;")
            tw2l = QVBoxLayout(tw2); tw2l.setContentsMargins(0,4,0,4); tw2l.setSpacing(2)
            icon = "📌" if item["src"] == "tracker" else "🔖"
            tn = QLabel(f"{icon} {item['nama']}"); tn.setFont(QFont(FONT_FAMILY,11,QFont.Weight.Bold))
            tn.setWordWrap(True)
            tn.setStyleSheet(f"color:{c['text_dark']};background:transparent;"); tw2l.addWidget(tn)
            days = item["days"]
            clr = "#EF4444" if days<=7 else "#F59E0B" if days<=14 else "#22C55E"
            td = QLabel(f"\U0001f4c5 {fmt_deadline(item['deadline'])}")
            td.setStyleSheet(f"color:{clr};font-size:10px;background:transparent;"); tw2l.addWidget(td)
            dcl.addWidget(tw2)
            sep = QFrame(); sep.setFixedHeight(1); sep.setStyleSheet(f"background:{c['border']};")
            dcl.addWidget(sep); shown += 1
        if not shown:
            el = QLabel(t['no_up_dl'])
            el.setStyleSheet(f"color:{c['text_muted']};font-size:11px;background:transparent;")
            el.setWordWrap(True); dcl.addWidget(el)
        rl.addWidget(dc)

        # ━━ CALENDAR ━━
        cc = QFrame(); cc.setObjectName("calCard")
        self._apply_card_shadow(cc)
        cc.setStyleSheet(f"#calCard{{background:{c['card']};border:1px solid {c['border']};border-radius:16px;}}")
        ccl = QVBoxLayout(cc); ccl.setContentsMargins(14,14,14,14); ccl.setSpacing(4)
        ccl.addWidget(self._header(t['calendar'], c))
        self._cal_date = datetime.date.today()
        cal_nav = QWidget(); cal_nav.setStyleSheet("background:transparent;")
        cal_nav_l = QHBoxLayout(cal_nav); cal_nav_l.setContentsMargins(0,0,0,0)
        
        btn_prev = QPushButton("<"); btn_prev.setFixedSize(24, 24)
        btn_prev.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_prev.setStyleSheet(f"background:transparent; border: 1px solid {c['border']}; border-radius:12px; color:{c['text_muted']};")
        btn_prev.clicked.connect(lambda: self._shift_month(-1))
        
        self._cal_btn = QPushButton(self._cal_date.strftime("%B %Y"))
        self._cal_btn.setFixedHeight(24)
        self._cal_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._cal_btn.setStyleSheet(f"QPushButton {{ background:#FCEAE6; color:{c['text_dark']}; border:none; border-radius:12px; font-weight:bold; font-size:11px; padding: 0px 16px; }} QPushButton:hover {{ background:#F5DED5; }}")
        self._cal_btn.clicked.connect(self._pick_month_year)
        
        btn_next = QPushButton(">"); btn_next.setFixedSize(24, 24)
        btn_next.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_next.setStyleSheet(f"background:transparent; border: 1px solid {c['border']}; border-radius:12px; color:{c['text_muted']};")
        btn_next.clicked.connect(lambda: self._shift_month(1))
        
        cal_nav_l.addWidget(btn_prev)
        cal_nav_l.addStretch()
        cal_nav_l.addWidget(self._cal_btn)
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

        btn_full = QPushButton(t['view_full_cal'])
        btn_full.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_full.setStyleSheet("background:#889E91; color:black; border-radius:14px; padding:8px; font-weight:bold; font-size:11px; margin-top:8px;")
        if self._nav:
            btn_full.clicked.connect(lambda: self._nav("kalender"))
        ccl.addWidget(btn_full)

        self._render_cal_grid()
        rl.addWidget(cc)

    # ═══════════════════════════════════════════════════════════════
    # ANALYTICS SECTION
    # ═══════════════════════════════════════════════════════════════

    def _build_analytics_section(self, analytics: dict, c: dict) -> QWidget:
        t = self._t
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
        title_lbl = QLabel(t['an_title'])
        title_lbl.setFont(QFont(FONT_FAMILY, 13, QFont.Weight.Bold))
        title_lbl.setStyleSheet(f"color:{c['text_dark']};background:transparent;")
        hdr_l.addWidget(title_lbl)
        hdr_l.addStretch()

        # Summary chips
        total_chip = QLabel(f"{t['an_total']}: {analytics['total']}")
        total_chip.setStyleSheet("background:#f6d6d0;color:#000000;border-radius:8px;font-size:10px;font-weight:bold;padding:4px 10px;")
        dl_chip = QLabel(f"{t['an_dl']}: {analytics['with_deadline']}")
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
        subtitle1 = QLabel(t["t1_sub"])
        subtitle1.setStyleSheet(f"color:{c['text_muted']};font-size:10px;background:transparent;")
        t1l.addWidget(subtitle1)
        chart1 = BarChartWidget(
            analytics["deadline_by_month"],
            color=CHART_COLORS[:12],
            mode=self._mode
        )
        chart1.setMinimumHeight(200)
        t1l.addWidget(chart1)
        tabs.addTab(t1, t["t1"])

        # ── Tab 2: Deadline per Tanggal ──
        t2 = QWidget(); t2.setStyleSheet("background:transparent;")
        t2l = QVBoxLayout(t2); t2l.setContentsMargins(0, 8, 0, 4)
        subtitle2 = QLabel(t["t2_sub"])
        subtitle2.setStyleSheet(f"color:{c['text_muted']};font-size:10px;background:transparent;")
        t2l.addWidget(subtitle2)

        peak_day = analytics["peak_day"]
        note2 = QLabel(t["t2_note"].format(d=peak_day['day'], c=peak_day['count']))
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
        tabs.addTab(t2, t["t2"])

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
        title3 = QLabel(t["t3_title"])
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
        tabs.addTab(t3, t["t3"])

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
        title4 = QLabel(t["t4_title"])
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
            # Localize Region Label
            display_lbl = t['out_country'] if lbl == "Luar Negeri" else (t['in_country'] if lbl == "Dalam Negeri" else lbl)
            lbl_w = QLabel(display_lbl)
            lbl_w.setStyleSheet(f"color:{c['text_dark']};font-size:10px;background:transparent;")
            rl3.addWidget(lbl_w, 1)
            pct_w = QLabel(f"{int(val/total_r*100)}%  ({val})")
            pct_w.setStyleSheet(f"color:{c['text_muted']};font-size:10px;background:transparent;")
            rl3.addWidget(pct_w)
            leg4_l.addWidget(row)

        # Extra context
        ln_pct = int(dict(region_data).get("Luar Negeri", 0) / total_r * 100)
        ctx = QLabel(t['ctx_tips'].format(pct=ln_pct))
        ctx.setWordWrap(True)
        ctx.setStyleSheet(
            f"color:{c['text_muted']};font-size:9px;background:transparent;"
            f"padding:8px;border-radius:8px;background:{c['input_bg']};"
        )
        leg4_l.addWidget(ctx)
        leg4_l.addStretch()
        t4l.addWidget(leg4_w, 1)
        tabs.addTab(t4, t["t4"])

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
