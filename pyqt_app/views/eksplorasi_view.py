"""
pyqt_app/views/eksplorasi_view.py
Explore Scholarships — grid view with search, sort, filter.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QLineEdit, QGridLayout,
    QDialog, QRadioButton, QCheckBox, QButtonGroup
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QCursor
from datetime import datetime

from pyqt_app.styles.theme import FONT_FAMILY, palette, pastel
from controllers.eksplorasi_controller import (
    get_semua_beasiswa, get_bookmarks, check_bookmarked, toggle_bookmark_beasiswa,
)
from controllers.notifikasi_controller import buat_notifikasi_deadline


class EksplorasiView(QWidget):
    # Emit ketika user menambah/hapus bookmark
    bookmark_changed = pyqtSignal()

    def __init__(self, profil_id, bhs="id", mode="light", parent=None):
        super().__init__(parent)
        self._pid = profil_id
        self._bhs = bhs
        self._mode = mode
        self._all = get_semua_beasiswa()
        self._filtered = list(self._all)
        self._sort_mode = "default"
        self._filter_jenjang = None
        self._filter_toefl = False
        self._filter_ielts = False
        self._check_deadlines()
        self._build()

    def _check_deadlines(self):
        today = datetime.now().date()
        for bea in get_bookmarks(self._pid):
            dl = bea.get("deadline", "")
            if not dl:
                continue
            try:
                dl_date = datetime.strptime(dl, "%Y-%m-%d").date()
                days = (dl_date - today).days
                if 0 <= days <= 7:
                    buat_notifikasi_deadline(self._pid, bea.get("nama", ""), days)
            except (ValueError, TypeError):
                pass

    def _deadline_color(self, dl):
        if not dl:
            return None
        try:
            days = (datetime.strptime(dl, "%Y-%m-%d").date() - datetime.now().date()).days
            if days < 0: return "#999"
            if days <= 7: return "#EF4444"
            if days <= 14: return "#F59E0B"
            return "#22C55E"
        except: return None

    def _apply_filters(self):
        q = self._search.text().strip().lower() if hasattr(self, '_search') else ""
        r = list(self._all)
        if q:
            r = [b for b in r if q in b.get("nama","").lower() or q in b.get("penyelenggara","").lower()]
        if self._filter_jenjang:
            fj = self._filter_jenjang.upper()
            r = [b for b in r if fj in b.get("jenjang","").upper()]
        if self._filter_toefl:
            r = [b for b in r if b.get("syarat_toefl")]
        if self._filter_ielts:
            r = [b for b in r if b.get("syarat_ielts")]
        if self._sort_mode == "deadline_asc":
            r.sort(key=lambda b: b.get("deadline") or "9999")
        elif self._sort_mode == "deadline_desc":
            r.sort(key=lambda b: b.get("deadline") or "0000", reverse=True)
        elif self._sort_mode == "name_asc":
            r.sort(key=lambda b: b.get("nama","").lower())
        elif self._sort_mode == "name_desc":
            r.sort(key=lambda b: b.get("nama","").lower(), reverse=True)
        self._filtered = r

    def _build(self):
        c = palette(self._mode)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        # Top bar
        top = QFrame()
        tl = QHBoxLayout(top)
        tl.setContentsMargins(0, 0, 0, 0)
        self._search = QLineEdit()
        self._search.setPlaceholderText("Search Scholarships...")
        self._search.setFixedHeight(40)
        self._search.textChanged.connect(self._on_search)
        tl.addWidget(self._search)
        sort_btn = QPushButton("\u2195 Sort by")
        sort_btn.setObjectName("btn_outline")
        sort_btn.setFixedSize(100, 40)
        sort_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        sort_btn.clicked.connect(self._show_sort)
        tl.addWidget(sort_btn)
        filt_btn = QPushButton("\u2699 Filters")
        filt_btn.setObjectName("btn_outline")
        filt_btn.setFixedSize(100, 40)
        filt_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        filt_btn.clicked.connect(self._show_filter)
        tl.addWidget(filt_btn)
        lay.addWidget(top)

        self._count = QLabel(f"{len(self._filtered)} Scholarships Found")
        self._count.setFont(QFont(FONT_FAMILY, 13, QFont.Weight.Bold))
        lay.addWidget(self._count)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        lay.addWidget(self._scroll)
        self._render_grid()

    def _render_grid(self):
        c = palette(self._mode)
        w = QWidget()
        grid = QGridLayout(w)
        grid.setSpacing(10)
        cols = 3
        for i, bea in enumerate(self._filtered):
            row, col = i // cols, i % cols
            bg = pastel(i, self._mode)
            is_bm = check_bookmarked(self._pid, bea.get("id", 0))
            dl_clr = self._deadline_color(bea.get("deadline")) if is_bm else None

            card = QFrame()
            card.setObjectName(f"beaCard{i}")
            border = f"2px solid {dl_clr}" if dl_clr else f"1px solid {c['border']}"
            card.setStyleSheet(f"#beaCard{i} {{ background: {bg}; border-radius: 14px; border: {border}; }}")
            cl = QVBoxLayout(card)
            cl.setContentsMargins(16, 14, 16, 10)
            cl.setSpacing(4)

            n = QLabel(bea.get("nama", ""))
            n.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Bold))
            n.setWordWrap(True)
            n.setStyleSheet(f"color: {c['text_dark']}; background: transparent;")
            cl.addWidget(n)
            if bea.get("penyelenggara"):
                p = QLabel(bea["penyelenggara"])
                p.setStyleSheet(f"color: {c['text_muted']}; font-size: 10px; background: transparent;")
                p.setWordWrap(True)
                cl.addWidget(p)
            j = QLabel(f"Jenjang: {bea.get('jenjang', '-')}")
            j.setStyleSheet(f"color: {c['text_muted']}; font-size: 9px; background: transparent;")
            cl.addWidget(j)
            dl = bea.get("deadline", "")
            if dl:
                dc = self._deadline_color(dl)
                dlbl = QLabel(f"Deadline: {dl}")
                dlbl.setStyleSheet(f"color: {dc or c['text_accent']}; font-size: 9px; background: transparent;")
                cl.addWidget(dlbl)
            cl.addStretch()
            # Bookmark btn
            bm_txt = "\u2605" if is_bm else "\u2606"
            bm = QPushButton(bm_txt)
            bm.setStyleSheet(f"background: transparent; border: none; font-size: 18px; color: {c['text_accent'] if is_bm else c['text_muted']};")
            bm.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            bm.clicked.connect(lambda _, b=bea: self._toggle_bm(b))
            cl.addWidget(bm, alignment=Qt.AlignmentFlag.AlignRight)
            grid.addWidget(card, row, col)

        self._scroll.setWidget(w)
        self._count.setText(f"{len(self._filtered)} Scholarships Found")

    def _on_search(self):
        self._apply_filters()
        self._render_grid()

    def _toggle_bm(self, bea):
        toggle_bookmark_beasiswa(self._pid, bea.get("id", 0))
        self.bookmark_changed.emit()  # beritahu kalender
        self._apply_filters()
        self._render_grid()

    def _show_sort(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Sort")
        dlg.setFixedSize(300, 260)
        dl = QVBoxLayout(dlg)
        for label, mode in [("Default","default"),("Deadline ↑","deadline_asc"),
                            ("Deadline ↓","deadline_desc"),("Name A→Z","name_asc"),("Name Z→A","name_desc")]:
            b = QPushButton(label)
            b.setObjectName("btn_primary" if self._sort_mode == mode else "btn_outline")
            b.setFixedHeight(36)
            b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            b.clicked.connect(lambda _, m=mode: (setattr(self,'_sort_mode',m), dlg.accept(),
                                                  self._apply_filters(), self._render_grid()))
            dl.addWidget(b)
        dlg.exec()

    def _show_filter(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Filter")
        dlg.setFixedSize(340, 400)
        dl = QVBoxLayout(dlg)
        dl.addWidget(QLabel("Filter By Jenjang"))
        group = QButtonGroup(dlg)
        for j in ["All","S1","S2","S3","D3","D4"]:
            rb = QRadioButton(j)
            if (j == "All" and not self._filter_jenjang) or j == self._filter_jenjang:
                rb.setChecked(True)
            group.addButton(rb)
            dl.addWidget(rb)
        dl.addWidget(QLabel("Test Score Requirements"))
        cb_toefl = QCheckBox("Requires TOEFL")
        cb_toefl.setChecked(self._filter_toefl)
        dl.addWidget(cb_toefl)
        cb_ielts = QCheckBox("Requires IELTS")
        cb_ielts.setChecked(self._filter_ielts)
        dl.addWidget(cb_ielts)
        btn = QPushButton("Apply Filters")
        btn.setObjectName("btn_primary")
        btn.setFixedHeight(40)
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        def apply():
            sel = group.checkedButton()
            jv = sel.text() if sel else "All"
            self._filter_jenjang = None if jv == "All" else jv
            self._filter_toefl = cb_toefl.isChecked()
            self._filter_ielts = cb_ielts.isChecked()
            dlg.accept()
            self._apply_filters()
            self._render_grid()
        btn.clicked.connect(apply)
        dl.addWidget(btn)
        dlg.exec()
