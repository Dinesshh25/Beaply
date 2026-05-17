"""
pyqt_app/views/dashboard_view.py
Dashboard page — 2-column layout matching Figma mockup.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QSizePolicy, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor, QPixmap, QColor
import datetime, os, calendar

from pyqt_app.styles.theme import FONT_FAMILY, palette, pastel
from pyqt_app.widgets.progress_ring import ProgressRing
from controllers.profil_controller import tampil_profil
from controllers.tracker_controller import (
    get_semua_tracker as ambil_semua_tracker,
    hitung_statistik, fmt_deadline,
)
from controllers.eksplorasi_controller import (
    get_semua_beasiswa as ambil_semua_beasiswa,
    get_bookmarks as ambil_bookmark_user,
)

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

        # ━━ SMART TIPS ━━
        ll.addWidget(self._header("Smart Tips For You", c))
        tips = [
            ("\U0001f4dd","Improve Your IELTS Score",
             "A push to 7.0+ can unlock\nmore scholarships.","View Tips \u203a"),
            ("\U0001f4c8","Strengthen Your GPA",
             "A higher GPA increases your\nchances for top-tier scholarships.","View Tips \u203a"),
            ("\U0001f4c4","Complete Your Documents",
             "Some scholarships require\nadditional documents.","More Tips \u203a"),
        ]
        tw = QWidget(); tw.setStyleSheet("background:transparent;")
        tlay = QHBoxLayout(tw); tlay.setContentsMargins(0,0,0,0); tlay.setSpacing(10)
        for i,(ic,ti,de,ac) in enumerate(tips):
            tc = QFrame(); tc.setObjectName(f"tip{i}"); bg = self._p(i)
            tc.setStyleSheet(f"#tip{i}{{background:{bg};border-radius:14px;border:1px solid {c['border']};}}")
            tc.setMinimumHeight(130)
            tcl = QVBoxLayout(tc); tcl.setContentsMargins(16,14,16,12); tcl.setSpacing(4)
            il = QLabel(ic); il.setFont(QFont(FONT_FAMILY,18))
            il.setStyleSheet("background:transparent;"); tcl.addWidget(il)
            tl2 = QLabel(ti); tl2.setFont(QFont(FONT_FAMILY,11,QFont.Weight.Bold))
            tl2.setStyleSheet(f"color:{c['text_dark']};background:transparent;"); tcl.addWidget(tl2)
            dl = QLabel(de); dl.setStyleSheet(f"color:{c['text_muted']};font-size:10px;background:transparent;")
            dl.setWordWrap(True); tcl.addWidget(dl); tcl.addStretch()
            ab = QPushButton(ac); ab.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            ab.setStyleSheet(f"background:transparent;border:none;color:{c['text_accent']};font-size:10px;text-align:left;")
            tcl.addWidget(ab)
            tlay.addWidget(tc)
        ll.addWidget(tw)
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
