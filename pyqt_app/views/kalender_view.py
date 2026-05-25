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


class KalenderView(QWidget):
    def __init__(self, profil_id, bhs="id", mode="light",
                 navigate_cb=None, parent=None):
        super().__init__(parent)
        self._pid  = profil_id
        self._bhs  = bhs
        self._mode = mode
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
        mh.setStyleSheet(
            f"QFrame {{ background: {c['calendar_header']}; border-radius: 14px; }}"
        )
        mh.setFixedHeight(50)
        mhl = QHBoxLayout(mh)

        prev_btn = QPushButton("<")
        prev_btn.setFixedSize(36, 36)
        prev_btn.setStyleSheet(
            f"background: transparent; border: none; font-size: 16px; "
            f"font-weight: bold; color: {c['text_dark']};"
        )
        prev_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        prev_btn.clicked.connect(self._prev)
        mhl.addWidget(prev_btn)
        mhl.addStretch()

        mt = QLabel(f"{data['nama_bulan']} {data['tahun']}")
        mt.setFont(QFont(FONT_FAMILY, 15, QFont.Weight.Bold))
        mhl.addWidget(mt)
        mhl.addStretch()

        next_btn = QPushButton(">")
        next_btn.setFixedSize(36, 36)
        next_btn.setStyleSheet(
            f"background: transparent; border: none; font-size: 16px; "
            f"font-weight: bold; color: {c['text_dark']};"
        )
        next_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        next_btn.clicked.connect(self._next)
        mhl.addWidget(next_btn)
        ll.addWidget(mh)

        # Day-of-week headers
        grid   = QWidget()
        gl     = QGridLayout(grid)
        gl.setSpacing(4)
        for i, d in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            lbl = QLabel(d)
            lbl.setStyleSheet(
                f"color: {c['text_muted']}; font-size: 10px; font-weight: bold;"
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
            if warna:
                bg    = warna
                txt_c = "white"
                fw    = "bold"
            elif is_today:
                bg    = c["btn_primary"]
                txt_c = "white"
                fw    = "bold"
            else:
                bg    = "transparent"
                txt_c = c["text_dark"]
                fw    = "normal"

            # Tooltip: gabungkan info tracker + bookmark
            tooltip_parts = []
            for tr in tgl_tracker.get(day, []):
                tooltip_parts.append(
                    f"📌 {tr['nama_beasiswa']} — {fmt_status(tr['status'], self._bhs)}"
                )
            for bm in tgl_bookmark.get(day, []):
                tooltip_parts.append(f"🔖 {bm['nama']} (Bookmark)")
            tooltip = "\n".join(tooltip_parts) if tooltip_parts else ""

            btn = QPushButton(str(day))
            btn.setFixedSize(44, 36)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {bg}; color: {txt_c}; border: none;
                    border-radius: 8px; font-size: 12px; font-weight: {fw};
                }}
                QPushButton:hover {{ background: {c['btn_pale']}; color: {c['text_dark']}; }}
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

        ll.addWidget(grid)

        # Legend — sesuai aturan warna border bookmark
        leg  = QFrame()
        legl = QHBoxLayout(leg)
        legl.setContentsMargins(12, 4, 12, 0)
        legl.setSpacing(14)
        for txt, clr in [
            ("● Hari ini",   c["btn_primary"]),
            ("● > 14 hari",  "#22C55E"),
            ("● 7–14 hari",  "#F59E0B"),
            ("● < 7 hari",   "#EF4444"),
            ("● Expired",    "#9AA0A6"),
        ]:
            lbl = QLabel(txt)
            lbl.setStyleSheet(
                f"color: {clr}; font-size: 10px; font-weight: bold; "
                "background: transparent;"
            )
            legl.addWidget(lbl)
        legl.addStretch()
        ll.addWidget(leg)
        lay.addWidget(left, 7)

        # ── RIGHT: Events panel ───────────────────────────────
        right = QFrame()
        right.setFixedWidth(280)
        right.setStyleSheet(
            f"QFrame {{ background: {c['btn_pale']}; border-radius: 16px; "
            f"border: 1px solid {c['border']}; }}"
        )
        rl = QVBoxLayout(right)
        rl.setContentsMargins(16, 20, 16, 12)
        rl.setSpacing(8)

        rh = QLabel("Upcoming Events")
        rh.setFont(QFont(FONT_FAMILY, 15, QFont.Weight.Bold))
        rh.setStyleSheet(f"color: {c['text_dark']}; background: transparent;")
        rl.addWidget(rh)

        esc  = QScrollArea()
        esc.setWidgetResizable(True)
        esc.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        esc.setStyleSheet("background: transparent; border: none;")
        esw  = QWidget()
        esw.setStyleSheet("background: transparent;")
        esl  = QVBoxLayout(esw)
        esl.setContentsMargins(0, 0, 0, 0)
        esl.setSpacing(6)

        # ─ Tracker events ─
        trackers = ambil_semua_tracker(self._pid) if self._pid else []
        upcoming = sorted(
            [t for t in trackers if t.get("deadline")],
            key=lambda x: x["deadline"]
        )

        if upcoming:
            sec_lbl = QLabel("📌 Tracker Deadlines")
            sec_lbl.setStyleSheet(
                f"color: {c['text_muted']}; font-size: 9px; "
                "font-weight: bold; background: transparent;"
            )
            esl.addWidget(sec_lbl)
            for tr in upcoming[:6]:
                ev  = QFrame()
                ev.setStyleSheet(
                    f"QFrame {{ background: {c['card']}; "
                    "border-radius: 10px; border: none; }}"
                )
                evl = QVBoxLayout(ev)
                evl.setContentsMargins(10, 8, 10, 8)
                evl.setSpacing(2)
                en  = QLabel(tr.get("nama_beasiswa", ""))
                en.setFont(QFont(FONT_FAMILY, 10, QFont.Weight.Bold))
                en.setWordWrap(True)
                en.setStyleSheet(f"color: {c['text_dark']}; background: transparent;")
                evl.addWidget(en)
                ed  = QLabel(f"📅 {tr.get('deadline', '')}")
                ed.setStyleSheet(
                    f"color: {c['text_accent']}; font-size: 10px; background: transparent;"
                )
                evl.addWidget(ed)
                esl.addWidget(ev)

        # ─ Bookmark deadline events ─
        bm_all = get_bookmarks(self._pid) if self._pid else []
        bm_with_dl = sorted(
            [b for b in bm_all if b.get("deadline")],
            key=lambda x: x["deadline"]
        )

        if bm_with_dl:
            sep = QFrame()
            sep.setFixedHeight(1)
            sep.setStyleSheet(f"background: {c['border']};")
            esl.addWidget(sep)

            bm_sec = QLabel("🔖 Bookmark Deadlines")
            bm_sec.setStyleSheet(
                f"color: {BOOKMARK_COLOR}; font-size: 9px; "
                "font-weight: bold; background: transparent;"
            )
            esl.addWidget(bm_sec)

            for bea in bm_with_dl[:8]:
                try:
                    days_left = (
                        datetime.strptime(bea["deadline"], "%Y-%m-%d").date()
                        - datetime.now().date()
                    ).days
                    if days_left < 0:
                        day_txt = "Expired"
                        day_clr = "#9AA0A6"
                    elif days_left == 0:
                        day_txt = "Hari ini!"
                        day_clr = "#EF4444"
                    elif days_left <= 7:
                        day_txt = f"{days_left} hari lagi ⚠"
                        day_clr = "#EF4444"
                    elif days_left <= 14:
                        day_txt = f"{days_left} hari lagi"
                        day_clr = "#F59E0B"
                    else:
                        day_txt = f"{days_left} hari lagi"
                        day_clr = "#22C55E"
                except Exception:
                    day_txt = bea.get("deadline", "")
                    day_clr = c["text_muted"]

                bm_card = QFrame()
                bm_card.setStyleSheet(
                    f"QFrame {{ background: {day_clr}12; "
                    f"border-radius: 10px; border: 2px solid {day_clr}88; }}"
                )
                bm_lay = QVBoxLayout(bm_card)
                bm_lay.setContentsMargins(10, 8, 10, 8)
                bm_lay.setSpacing(2)

                bm_name = QLabel(bea.get("nama", ""))
                bm_name.setFont(QFont(FONT_FAMILY, 10, QFont.Weight.Bold))
                bm_name.setWordWrap(True)
                bm_name.setStyleSheet(
                    f"color: {c['text_dark']}; background: transparent;"
                )
                bm_lay.addWidget(bm_name)

                bm_dl = QLabel(f"📅 {bea.get('deadline', '')}")
                bm_dl.setStyleSheet(
                    f"color: {day_clr}; font-size: 10px; background: transparent;"
                )
                bm_lay.addWidget(bm_dl)

                bm_days = QLabel(day_txt)
                bm_days.setStyleSheet(
                    f"color: {day_clr}; font-size: 9px; "
                    "font-weight: bold; background: transparent;"
                )
                bm_lay.addWidget(bm_days)

                # Klik kartu → navigasi ke Bookmarks
                bm_card.mousePressEvent = lambda e, w=bm_card: self._go_bookmarks()
                bm_card.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

                esl.addWidget(bm_card)

            # Tombol "Lihat Semua Bookmark"
            if self._nav:
                go_btn = QPushButton("🔖 Lihat Semua Bookmark →")
                go_btn.setStyleSheet(
                    f"background: {BOOKMARK_COLOR}22; color: {BOOKMARK_COLOR}; "
                    f"border: 1px solid {BOOKMARK_COLOR}55; border-radius: 8px; "
                    f"font-size: 10px; font-weight: bold; padding: 5px 10px;"
                )
                go_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                go_btn.clicked.connect(self._go_bookmarks)
                esl.addWidget(go_btn)

        if not upcoming and not bm_with_dl:
            el = QLabel(
                "Belum ada event.\n\nBookmark beasiswa atau tambahkan\n"
                "deadline di Tracker untuk melihat\ndeadline di sini."
            )
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

        if not has_tracker and not has_bookmark:
            return

        if has_tracker and has_bookmark:
            # Ada keduanya — tanya mau lihat yang mana
            msg = QMessageBox(self)
            msg.setWindowTitle("Tanggal ini punya 2 jenis deadline")
            bm_names  = "\n".join(
                [f"  🔖 {b['nama']}" for b in tgl_bookmark[day]]
            )
            tr_names  = "\n".join(
                [f"  📌 {t['nama_beasiswa']}" for t in tgl_tracker[day]]
            )
            msg.setText(
                f"Tracker:\n{tr_names}\n\nBookmark Beasiswa:\n{bm_names}"
            )
            btn_bm = msg.addButton("Lihat Bookmarks 🔖", QMessageBox.ButtonRole.ActionRole)
            btn_tr = msg.addButton("Detail Tracker 📌", QMessageBox.ButtonRole.ActionRole)
            msg.addButton("Tutup", QMessageBox.ButtonRole.RejectRole)
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
            box.setWindowTitle(f"Bookmark Deadline — {day} {['','Jan','Feb','Mar','Apr','Mei','Jun','Jul','Ags','Sep','Okt','Nov','Des'][self._bulan]} {self._tahun}")
            box.setText(
                f"Beasiswa yang di-bookmark berdeadline tanggal ini:\n\n{bm_names}"
            )
            btn_go = box.addButton("Buka Halaman Bookmark 🔖", QMessageBox.ButtonRole.ActionRole)
            box.addButton("Tutup", QMessageBox.ButtonRole.RejectRole)
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
        QMessageBox.information(self, "Deadline Tracker", msg)

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
