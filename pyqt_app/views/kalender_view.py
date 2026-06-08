"""
pyqt_app/views/kalender_view.py
Calendar Deadline — two-column layout with calendar grid and events panel.

Fitur:
  - Deadline dari Tracker ditampilkan di kalender
  - Deadline dari Bookmark Beasiswa ditampilkan di kalender (biru)
  - Klik tanggal berwarna biru (bookmark) → navigasi ke halaman Bookmarks
  - Klik tanggal merah/kuning (tracker) → popup detail
  - Panel kanan menampilkan Tracker events + Bookmark deadlines
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QGridLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor
from datetime import datetime

from pyqt_app.styles.theme import FONT_FAMILY, palette
from controllers.tracker_controller import (
    tampilan_kalender, fmt_status, get_semua_tracker as ambil_semua_tracker,
)
from controllers.eksplorasi_controller import get_bookmarks


# Warna khusus bookmark deadline
BOOKMARK_COLOR = "#3B82F6"

TRANSLATIONS = {
    'id': {
        'months': ['', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'],
        'months_short': ['', 'Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Ags', 'Sep', 'Okt', 'Nov', 'Des'],
        'days_short': ['Sen', 'Sel', 'Rab', 'Kam', 'Jum', 'Sab', 'Min'],
        'today': 'Hari ini',
        'gt_14': '> 14 hari',
        '7_14': '7–14 hari',
        'lt_7': '< 7 hari',
        'expired': 'Kedaluwarsa',
        'upcoming': 'Acara Mendatang',
        'tracker_dl': 'Tenggat Waktu Tracker',
        'no_events': 'Belum ada acara.\n\nSimpan beasiswa atau tambahkan\ntenggat waktu di Tracker untuk\nmelihatnya di sini.',
        'see_all_bm': 'Lihat Semua Tersimpan >',
        'days_left_warn': '{} hari lagi ⚠',
        'days_left': '{} hari lagi',
        'today_excl': 'Hari ini!',
        'dual_dl_title': 'Tanggal ini memiliki 2 jenis tenggat waktu',
        'dual_dl_msg': 'Tracker:\n{}\n\nTersimpan:\n{}',
        'see_bm': 'Lihat Tersimpan 🔖',
        'detail_tr': 'Detail Tracker 📌',
        'close': 'Tutup',
        'bm_dl_title': 'Tenggat Waktu Tersimpan — {} {} {}',
        'bm_dl_msg': 'Beasiswa yang tersimpan memiliki tenggat waktu hari ini:\n\n{}',
        'go_bm': 'Buka Halaman Tersimpan 🔖',
        'tr_dl_title': 'Tenggat Waktu Tracker',
        'sel_month_year': 'Pilih Bulan & Tahun',
        'apply': 'Terapkan',
        'tracker_label': '📌 {} — {}',
        'bookmark_label': '🔖 {} (Tersimpan)',
    },
    'en': {
        'months': ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
        'months_short': ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        'days_short': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        'today': 'Today',
        'gt_14': '> 14 days',
        '7_14': '7–14 days',
        'lt_7': '< 7 days',
        'expired': 'Expired',
        'upcoming': 'Upcoming Events',
        'tracker_dl': 'Tracker Deadlines',
        'no_events': 'No events yet.\n\nBookmark scholarships or add\ndeadlines to the Tracker to\nsee them here.',
        'see_all_bm': 'See All Bookmarks >',
        'days_left_warn': '{} days left ⚠',
        'days_left': '{} days left',
        'today_excl': 'Today!',
        'dual_dl_title': 'This date has 2 types of deadlines',
        'dual_dl_msg': 'Tracker:\n{}\n\nBookmarks:\n{}',
        'see_bm': 'See Bookmarks 🔖',
        'detail_tr': 'Tracker Detail 📌',
        'close': 'Close',
        'bm_dl_title': 'Bookmark Deadline — {} {} {}',
        'bm_dl_msg': 'Bookmarked scholarships with deadline on this date:\n\n{}',
        'go_bm': 'Go to Bookmarks 🔖',
        'tr_dl_title': 'Tracker Deadline',
        'sel_month_year': 'Select Month & Year',
        'apply': 'Apply',
        'tracker_label': '📌 {} — {}',
        'bookmark_label': '🔖 {} (Bookmark)',
    }
}


class KalenderView(QWidget):
    def __init__(self, profil_id, bhs="id", mode="light",
                 navigate_cb=None, parent=None):
        super().__init__(parent)
        self._pid  = profil_id
        self._bhs  = bhs
        self._mode = mode
        self._t = TRANSLATIONS.get(bhs, TRANSLATIONS['id'])
        self._nav  = navigate_cb  # callback untuk navigasi antar halaman
        now = datetime.now()
        self._bulan = now.month
        self._tahun = now.year
        self._build()

    # ─────────────────────────────────────────────────────────
    # BUILD UTAMA
    # ─────────────────────────────────────────────────────────

    def _build(self):
        # Clear layout
        if self.layout():
            while self.layout().count():
                item = self.layout().takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        else:
            QHBoxLayout(self)

        c   = palette(self._mode)
        t   = self._t
        lay = self.layout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        data         = tampilan_kalender(self._pid, self._bulan, self._tahun)
        tgl_warna    = data.get("tanggal_warna",    {})
        tgl_tracker  = data.get("tanggal_tracker",  {})
        tgl_bookmark = data.get("tanggal_bookmark", {})

        # ── LEFT: Calendar grid ───────────────────────────────
        left = QFrame()
        left.setProperty("frameClass", "card")
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 12)

        # Month navigation header
        mh = QFrame()
        mh_bg = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #EAF5EC, stop:1 #DFF0E6)" if self._mode == "light" else c["card"]
        mh.setStyleSheet(
            f"QFrame {{ background: {mh_bg}; border-radius: 16px; }}"
        )
        mh.setFixedHeight(56)
        mhl = QHBoxLayout(mh)
        mhl.setContentsMargins(16, 0, 16, 0)

        mhl.addStretch()

        prev_btn = QPushButton("<")
        prev_btn.setFixedSize(32, 32)
        prev_btn.setStyleSheet(
            f"background: white; border-radius: 8px; font-size: 14px; "
            f"font-weight: bold; color: black;"
        )
        prev_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        prev_btn.clicked.connect(self._prev)
        mhl.addWidget(prev_btn)
        
        mhl.addSpacing(8)

        # Use translated month name
        month_name = t['months'][self._bulan]
        mt = QPushButton(f"{month_name} {self._tahun}")
        mt.setFont(QFont(FONT_FAMILY, 16, QFont.Weight.Bold))
        mt.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        mt.setStyleSheet(f"QPushButton {{ background:transparent; border:none; color:{c['text_dark']}; }}")
        mt.clicked.connect(self._pick_month_year)
        mhl.addWidget(mt)
        
        mhl.addSpacing(8)

        next_btn = QPushButton(">")
        next_btn.setFixedSize(32, 32)
        next_btn.setStyleSheet(
            f"background: white; border-radius: 8px; font-size: 14px; "
            f"font-weight: bold; color: black;"
        )
        next_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        next_btn.clicked.connect(self._next)
        mhl.addWidget(next_btn)
        
        mhl.addStretch()
        ll.addWidget(mh)

        # Day-of-week headers
        grid_frame = QFrame()
        grid_frame.setStyleSheet(f"QFrame {{ background: {c['card']}; border-radius: 16px; border: none; }}")
        gl = QGridLayout(grid_frame)
        gl.setSpacing(8)
        gl.setContentsMargins(20, 20, 20, 20)
        
        for i, d in enumerate(t['days_short']):
            lbl = QLabel(d)
            lbl.setStyleSheet(
                f"color: {c['text_muted']}; font-size: 11px; font-weight: bold;"
            )
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            gl.addWidget(lbl, 0, i)

        # Calendar day buttons
        today  = datetime.now()
        row    = 1
        col    = data["hari_pertama"]

        for day in range(1, data["total_hari"] + 1):
            warna    = tgl_warna.get(day)
            is_today = (
                day == today.day
                and self._bulan == today.month
                and self._tahun == today.year
            )

            # Color logic: bookmark/tracker warna > today > default
            if is_today:
                bg    = c["btn_primary"]
                txt_c = c["text_dark"]
                fw    = "bold"
                border = "none"
            elif warna:
                bg    = "transparent"
                txt_c = c["text_dark"]
                fw    = "bold"
                border = f"2px solid {warna}"
            else:
                bg    = "transparent"
                txt_c = c["text_dark"]
                fw    = "normal"
                border = "none"

            # Tooltip: gabungkan info tracker + bookmark
            tooltip_parts = []
            for tr in tgl_tracker.get(day, []):
                tooltip_parts.append(
                    t['tracker_label'].format(tr['nama_beasiswa'], fmt_status(tr['status'], self._bhs))
                )
            for bm in tgl_bookmark.get(day, []):
                tooltip_parts.append(t['bookmark_label'].format(bm['nama']))
            tooltip = "\n".join(tooltip_parts) if tooltip_parts else ""

            btn = QPushButton(str(day))
            btn.setFixedSize(50, 50)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {bg}; color: {txt_c}; border: {border};
                    border-radius: 25px; font-size: 13px; font-weight: {fw};
                }}
                QPushButton:hover {{ background: {c['btn_pale']}; color: {c['text_dark']}; border: none; }}
            """)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            if tooltip:
                btn.setToolTip(tooltip)

            # Click handler — distinguish bookmark vs tracker
            btn.clicked.connect(
                lambda _, d=day, tw=tgl_tracker, bw=tgl_bookmark, wr=tgl_warna:
                    self._click_day(d, tw, bw, wr)
            )
            gl.addWidget(btn, row, col)

            col += 1
            if col > 6:
                col = 0
                row += 1

        ll.addWidget(grid_frame)

        # Legend — sesuai aturan warna border bookmark
        leg  = QFrame()
        legl = QHBoxLayout(leg)
        legl.setContentsMargins(12, 4, 12, 0)
        legl.setSpacing(14)
        for txt, clr in [
            (f"● {t['today']}",   "#A8C5B0"),
            (f"● {t['gt_14']}",  "#22C55E"),
            (f"● {t['7_14']}",  "#F59E0B"),
            (f"● {t['lt_7']}",   "#EF4444"),
            (f"● {t['expired']}",    "#9AA0A6"),
        ]:
            lbl = QLabel(txt)
            lbl.setStyleSheet(
                f"color: {clr}; font-size: 13px; font-weight: bold; "
                "background: transparent;"
            )
            legl.addWidget(lbl)
        legl.addStretch()
        ll.addWidget(leg)

        ll.addStretch()
        lay.addWidget(left, 7)

        # ── RIGHT: Events panel ───────────────────────────────
        right = QFrame()
        right.setFixedWidth(300)
        r_bg = "#FFFFFF" if self._mode == "light" else c["bg"]
        right.setStyleSheet(
            f"QFrame {{ background: {r_bg}; border-radius: 16px; "
            f"border: none; }}"
        )
        rl = QVBoxLayout(right)
        rl.setContentsMargins(20, 20, 20, 16)
        rl.setSpacing(12)

        rh = QLabel(t['upcoming'])
        rh.setFont(QFont(FONT_FAMILY, 15, QFont.Weight.Bold))
        rh.setStyleSheet(f"color: {c['text_dark']}; background: transparent;")
        rl.addWidget(rh)

        esc  = QScrollArea()
        esc.setWidgetResizable(True)
        esc.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        esc.setStyleSheet("background: transparent; border: none;")
        esc.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        esw  = QWidget()
        esw.setFixedWidth(244)
        esw.setStyleSheet("background: transparent;")
        esl  = QVBoxLayout(esw)
        esl.setContentsMargins(0, 0, 0, 0)
        esl.setSpacing(6)

        # ─ Tracker events ─
        trackers = ambil_semua_tracker(self._pid) if self._pid else []
        upcoming = sorted(
            [tr for tr in trackers if tr.get("deadline")],
            key=lambda x: x["deadline"]
        )

        if upcoming:
            sec_lbl = QLabel(f"📌 {t['tracker_dl']}")
            sec_lbl.setStyleSheet(
                f"color: {c['text_muted']}; font-size: 9px; "
                "font-weight: bold; background: transparent;"
            )
            esl.addWidget(sec_lbl)
            for tr in upcoming[:6]:
                ev  = QFrame()
                ev.setFixedWidth(244)
                ev.setStyleSheet(
                    f"QFrame {{ background: {c['card']}; border-radius: 10px; border: none; }}"
                )
                ev_lay = QHBoxLayout(ev)
                ev_lay.setContentsMargins(0, 0, 0, 0)
                ev_lay.setSpacing(0)
                
                tr_bar = QFrame()
                tr_bar.setFixedWidth(4)
                tr_bar.setStyleSheet("background: #8B5CF6; border-top-left-radius: 10px; border-bottom-left-radius: 10px;")
                ev_lay.addWidget(tr_bar)
                
                evl = QVBoxLayout()
                evl.setContentsMargins(10, 8, 10, 8)
                evl.setSpacing(2)
                en  = QLabel(tr.get("nama_beasiswa", ""))
                en.setFont(QFont(FONT_FAMILY, 10, QFont.Weight.Bold))
                en.setWordWrap(True)
                en.setStyleSheet(f"color: {c['text_dark']}; background: transparent;")
                evl.addWidget(en)
                dl_hlay = QHBoxLayout()
                ed  = QLabel(f"📅 {tr.get('deadline', '')}")
                ed.setWordWrap(True)
                ed.setStyleSheet(
                    f"color: {c['text_muted']}; font-size: 10px; background: transparent;"
                )
                dl_hlay.addWidget(ed)
                
                dl_hlay.addStretch()
                
                status_lbl = QLabel(fmt_status(tr['status'], self._bhs))
                status_lbl.setStyleSheet(
                    f"color: white; font-size: 9px; font-weight: bold; "
                    f"background: #8B5CF6; border-radius: 6px; padding: 2px 6px;"
                )
                status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                dl_hlay.addWidget(status_lbl)
                
                evl.addLayout(dl_hlay)
                ev_lay.addLayout(evl)
                esl.addWidget(ev)

        # ─ Bookmark deadline events ─
        bm_all = get_bookmarks(self._pid) if self._pid else []
        bm_with_dl = sorted(
            [b for b in bm_all if b.get("deadline")],
            key=lambda x: x["deadline"]
        )

        if bm_with_dl:

            for i, bea in enumerate(bm_with_dl[:8]):
                if i % 2 == 0:
                    bg = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #F4FCF7, stop:1 #EAF6EE)" if self._mode == "light" else c["card"]
                else:
                    bg = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FFF6F4, stop:1 #FDEAE6)" if self._mode == "light" else c["bg"]
                try:
                    days_left = (
                        datetime.strptime(bea["deadline"], "%Y-%m-%d").date()
                        - datetime.now().date()
                    ).days
                    if days_left < 0:
                        day_txt = t['expired']
                        day_clr = "#9AA0A6"
                    elif days_left == 0:
                        day_txt = t['today_excl']
                        day_clr = "#A8C5B0"
                    elif days_left < 7:
                        day_txt = t['days_left_warn'].format(days_left)
                        day_clr = "#EF4444"
                    elif days_left <= 14:
                        day_txt = t['days_left'].format(days_left)
                        day_clr = "#F59E0B"
                    else:
                        day_txt = t['days_left'].format(days_left)
                        day_clr = "#22C55E"
                except Exception:
                    day_txt = bea.get("deadline", "")
                    day_clr = c["text_muted"]

                bm_card = QFrame()
                bm_card.setFixedWidth(244)
                bm_card.setStyleSheet(
                    f"QFrame {{ background: {bg}; border-radius: 10px; border: none; }}"
                )
                bm_card_lay = QHBoxLayout(bm_card)
                bm_card_lay.setContentsMargins(0, 0, 0, 0)
                bm_card_lay.setSpacing(0)
                
                bm_bar = QFrame()
                bm_bar.setFixedWidth(4)
                bm_bar.setStyleSheet(f"background: {day_clr}; border-top-left-radius: 10px; border-bottom-left-radius: 10px;")
                bm_card_lay.addWidget(bm_bar)
                
                bm_lay = QVBoxLayout()
                bm_lay.setContentsMargins(10, 8, 10, 8)
                bm_lay.setSpacing(2)

                bm_name = QLabel(bea.get("nama", ""))
                bm_name.setFont(QFont(FONT_FAMILY, 10, QFont.Weight.Bold))
                bm_name.setWordWrap(True)
                bm_name.setStyleSheet(
                    f"color: {c['text_dark']}; background: transparent;"
                )
                bm_lay.addWidget(bm_name)

                dl_hlay = QHBoxLayout()
                bm_dl = QLabel(f"📅 {bea.get('deadline', '')}")
                bm_dl.setWordWrap(True)
                bm_dl.setStyleSheet(
                    f"color: {c['text_muted']}; font-size: 10px; background: transparent;"
                )
                dl_hlay.addWidget(bm_dl)
                
                dl_hlay.addStretch()

                bm_days = QLabel(day_txt)
                bm_days.setStyleSheet(
                    f"color: white; font-size: 9px; font-weight: bold; "
                    f"background: {day_clr}; border-radius: 6px; padding: 2px 6px;"
                )
                bm_days.setAlignment(Qt.AlignmentFlag.AlignCenter)
                dl_hlay.addWidget(bm_days)
                
                bm_lay.addLayout(dl_hlay)

                # Klik kartu → navigasi ke Bookmarks
                bm_card.mousePressEvent = lambda e, w=bm_card: self._go_bookmarks()
                bm_card.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

                bm_card_lay.addLayout(bm_lay)
                esl.addWidget(bm_card)

            # Tombol "Lihat Semua Bookmark"
            if self._nav:
                go_btn = QPushButton(t['see_all_bm'])
                go_btn.setFixedWidth(244)
                go_btn.setStyleSheet(
                    "background:#889E91; color:white; border-radius:14px; padding:8px; font-weight:bold; font-size:13px; margin-top:8px;"
                )
                go_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                go_btn.clicked.connect(self._go_bookmarks)
                esl.addWidget(go_btn)

        if not upcoming and not bm_with_dl:
            el = QLabel(t['no_events'])
            el.setStyleSheet(f"color: {c['text_muted']}; font-size: 11px;")
            el.setAlignment(Qt.AlignmentFlag.AlignCenter)
            esl.addWidget(el)

        esl.addStretch()
        esc.setWidget(esw)
        rl.addWidget(esc)
        lay.addWidget(right, 3)

    # ─────────────────────────────────────────────────────────
    # EVENT HANDLERS
    # ─────────────────────────────────────────────────────────

    def _click_day(self, day, tgl_tracker, tgl_bookmark, tgl_warna):
        """
        Klik tanggal berwarna:
          - Jika tanggal bookmark-only → navigasi ke Bookmarks
          - Jika tanggal tracker (merah/kuning) → popup detail
          - Jika keduanya → tanya user
        """
        has_tracker  = bool(tgl_tracker.get(day))
        has_bookmark = bool(tgl_bookmark.get(day))
        warna        = tgl_warna.get(day, "")
        t = self._t

        if not has_tracker and not has_bookmark:
            return

        if has_tracker and has_bookmark:
            # Ada keduanya — tanya mau lihat yang mana
            msg = QMessageBox(self)
            msg.setWindowTitle(t['dual_dl_title'])
            bm_names  = "\n".join(
                [f"  🔖 {b['nama']}" for b in tgl_bookmark[day]]
            )
            tr_names  = "\n".join(
                [f"  📌 {tr['nama_beasiswa']}" for tr in tgl_tracker[day]]
            )
            msg.setText(t['dual_dl_msg'].format(tr_names, bm_names))
            
            btn_bm = msg.addButton(t['see_bm'], QMessageBox.ButtonRole.ActionRole)
            btn_tr = msg.addButton(t['detail_tr'], QMessageBox.ButtonRole.ActionRole)
            msg.addButton(t['close'], QMessageBox.ButtonRole.RejectRole)
            msg.exec()
            if msg.clickedButton() == btn_bm:
                self._go_bookmarks()
            elif msg.clickedButton() == btn_tr:
                self._show_tracker_popup(day, tgl_tracker)

        elif has_bookmark:
            # Hanya bookmark → langsung navigasi ke Bookmarks
            bm_names = "\n".join(
                [f"• {b['nama']} — {b['deadline']}" for b in tgl_bookmark[day]]
            )
            box = QMessageBox(self)
            box.setWindowTitle(t['bm_dl_title'].format(day, t['months_short'][self._bulan], self._tahun))
            box.setText(t['bm_dl_msg'].format(bm_names))
            btn_go = box.addButton(t['go_bm'], QMessageBox.ButtonRole.ActionRole)
            box.addButton(t['close'], QMessageBox.ButtonRole.RejectRole)
            box.exec()
            if box.clickedButton() == btn_go:
                self._go_bookmarks()

        else:
            # Hanya tracker
            self._show_tracker_popup(day, tgl_tracker)

    def _show_tracker_popup(self, day, tgl_tracker):
        items = tgl_tracker.get(day, [])
        if not items:
            return
        msg = "\n".join(
            [f"• {it['nama_beasiswa']} — {fmt_status(it['status'], self._bhs)}"
             for it in items]
        )
        QMessageBox.information(self, self._t['tr_dl_title'], msg)

    def _go_bookmarks(self):
        """Navigasi ke halaman Bookmarks."""
        if self._nav:
            self._nav("bookmarks")

    def _prev(self):
        self._bulan -= 1
        if self._bulan < 1:
            self._bulan = 12
            self._tahun -= 1
        self._build()

    def _next(self):
        self._bulan += 1
        if self._bulan > 12:
            self._bulan = 1
            self._tahun += 1
        self._build()

    def _pick_month_year(self):
        c = palette(self._mode)
        t = self._t
        from PyQt6.QtWidgets import QDialog, QComboBox, QSpinBox, QGraphicsDropShadowEffect
        from PyQt6.QtGui import QColor
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
        for i in range(1, 13): cb_m.addItem(t['months'][i], i)
        cb_m.setCurrentIndex(self._bulan - 1)
        cb_m.setStyleSheet(f"QComboBox {{ background:{c['input_bg']}; color:{c['text_dark']}; border:1px solid {c['border']}; border-radius:8px; padding:4px 8px; }}")
        
        sb_y = QSpinBox()
        sb_y.setRange(1900, 2100)
        sb_y.setValue(self._tahun)
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
            self._bulan = cb_m.currentData()
            self._tahun = sb_y.value()
            self._build()
