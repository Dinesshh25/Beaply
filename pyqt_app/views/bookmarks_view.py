"""
pyqt_app/views/bookmarks_view.py
Saved / Bookmarked Scholarships — list view with deadline colors.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QMessageBox, QDialog, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QCursor, QColor
from datetime import datetime

from pyqt_app.styles.theme import FONT_FAMILY, palette, grad_green, grad_peach, grad_mixed
from controllers.eksplorasi_controller import get_bookmarks, toggle_bookmark_beasiswa
from pyqt_app.views.eksplorasi_view import CardFrame, DetailDialog

TRANSLATIONS = {
    'id': {
        'bookmarks': 'Tersimpan',
        'sort': '⇅ Urutkan',
        'clear_all': '🗑 Hapus Semua',
        'days_left': 'hari lagi',
        'expired': 'Kedaluwarsa',
        'no_bookmarks': 'Belum ada beasiswa yang disimpan.\nJelajahi dan simpan beasiswa yang Anda minati!',
        'jenjang': 'Jenjang',
        'deadline': 'Batas Waktu',
        'remove': 'Hapus',
        'sort_title': 'Urutkan Tersimpan',
        'sort_default': 'Bawaan',
        'sort_dl_asc': 'Batas Waktu ↑',
        'sort_dl_desc': 'Batas Waktu ↓',
        'sort_name_asc': 'Nama A→Z',
        'sort_name_desc': 'Nama Z→A',
        'clear_confirm': 'Hapus semua yang tersimpan?',
        'unknown': 'Tidak Diketahui',
    },
    'en': {
        'bookmarks': 'Bookmarks',
        'sort': '⇅ Sort by',
        'clear_all': '🗑 Clear All',
        'days_left': 'days left',
        'expired': 'Expired',
        'no_bookmarks': "No bookmarked scholarships yet.\nExplore and save scholarships you're interested in!",
        'jenjang': 'Degree',
        'deadline': 'Deadline',
        'remove': 'Remove',
        'sort_title': 'Sort Bookmarks',
        'sort_default': 'Default',
        'sort_dl_asc': 'Deadline ↑',
        'sort_dl_desc': 'Deadline ↓',
        'sort_name_asc': 'Name A→Z',
        'sort_name_desc': 'Name Z→A',
        'clear_confirm': 'Remove all bookmarks?',
        'unknown': 'Unknown',
    }
}

class BookmarksView(QWidget):
    # Emit ketika ada perubahan bookmark (tambah/hapus)
    bookmark_changed = pyqtSignal()

    def __init__(self, profil_id, bhs="id", mode="light", parent=None):
        super().__init__(parent)
        self._pid = profil_id
        self._bhs = bhs
        self._mode = mode
        self._t = TRANSLATIONS.get(bhs, TRANSLATIONS['id'])
        self._sort_mode = "default"
        self._build()

    def _dl_info(self, dl):
        if not dl: return None, ""
        try:
            days = (datetime.strptime(dl, "%Y-%m-%d").date() - datetime.now().date()).days
            if days < 0: return "#999999", self._t['expired']
            if days <= 7: return "#EF4444", f"{days} {self._t['days_left']}!"
            if days <= 14: return "#F59E0B", f"{days} {self._t['days_left']}"
            return "#22C55E", f"{days} {self._t['days_left']}"
        except: return None, ""

    def _build(self):
        if self.layout():
            while self.layout().count():
                item = self.layout().takeAt(0)
                if item.widget(): item.widget().deleteLater()
        else:
            QVBoxLayout(self)
        lay = self.layout()
        lay.setContentsMargins(0, 0, 0, 0)
        c = palette(self._mode)
        t = self._t
        bm_list = get_bookmarks(self._pid)

        if self._sort_mode == "deadline_asc":
            bm_list.sort(key=lambda b: b.get("deadline") or "9999")
        elif self._sort_mode == "deadline_desc":
            bm_list.sort(key=lambda b: b.get("deadline") or "0000", reverse=True)
        elif self._sort_mode == "name_asc":
            bm_list.sort(key=lambda b: b.get("nama","").lower())
        elif self._sort_mode == "name_desc":
            bm_list.sort(key=lambda b: b.get("nama","").lower(), reverse=True)

        # Header
        hdr = QFrame()
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.addWidget(self._bold_label(f"{len(bm_list)} {t['bookmarks']}", 15))
        
        sort_btn = QPushButton(t['sort'])
        sort_btn.setStyleSheet(f"background: {grad_green(c)}; color: {c['text_dark']}; border: none; border-radius: 12px; font-weight: bold; font-size: 13px;")
        sort_btn.setFixedSize(110, 40)
        sort_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        sort_btn.clicked.connect(self._show_sort)
        
        clr = QPushButton(t['clear_all'])
        clr.setStyleSheet(f"""
            QPushButton {{
                background: {grad_peach(c)};
                color: {c['text_dark']};
                border: none;
                border-radius: 14px;
                padding: 6px 16px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: {c['card']};
            }}
        """)
        
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        from PyQt6.QtGui import QColor
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 2)
        clr.setGraphicsEffect(shadow)
        
        clr.setFixedSize(120, 40)
        clr.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        clr.clicked.connect(self._clear_all)
        hl.addStretch()
        hl.addWidget(sort_btn)
        hl.addWidget(clr)
        lay.addWidget(hdr)

        # Legend
        leg = QFrame()
        ll = QHBoxLayout(leg)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(16)
        for txt, clr2 in [("● >14d","#22C55E"),("● 7-14d","#F59E0B"),("● <7d","#EF4444"),("● Expired","#999999")]:
            l = QLabel(txt)
            l.setStyleSheet(f"color: {clr2}; font-size: 13px; font-weight: bold;")
            ll.addWidget(l)
        ll.addStretch()
        lay.addWidget(leg)

        # List
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        sw = QWidget()
        sl = QVBoxLayout(sw)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.setSpacing(6)

        if not bm_list:
            e = QLabel(t['no_bookmarks'])
            e.setStyleSheet(f"color: {c['text_muted']}; font-size: 13px;")
            e.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sl.addWidget(e)
            sl.addStretch()
        else:
            for i, bea in enumerate(bm_list):
                dc, dl_lbl = self._dl_info(bea.get("deadline"))
                card = CardFrame(bea)
                card.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                card.clicked.connect(self._show_detail)
                card.setObjectName(f"bmCard{i}")
                
                # Alternating gradients
                if i % 2 == 0:
                    bg = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #F4FCF7, stop:1 #EAF6EE)" if self._mode == "light" else c["card"]
                else:
                    bg = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FFF6F4, stop:1 #FDEAE6)" if self._mode == "light" else c["bg"]
                
                # Colored stroke for deadline
                bdr = f"2px solid {dc}" if dc else f"1px solid {c['border']}"
                card.setStyleSheet(f"#bmCard{i} {{ background: {bg}; border-radius: 12px; border: {bdr}; }}")
                
                # Drop shadow
                shadow_c = QGraphicsDropShadowEffect()
                shadow_c.setBlurRadius(10)
                shadow_c.setColor(QColor(0, 0, 0, 8))
                shadow_c.setOffset(0, 2)
                card.setGraphicsEffect(shadow_c)

                cl = QVBoxLayout(card)
                cl.setContentsMargins(20, 16, 20, 16)
                cl.setSpacing(4)
                
                # Top Row: Title + Deadline Pill
                tr = QHBoxLayout()
                
                n = QLabel(bea.get("nama",""))
                n.setFont(QFont(FONT_FAMILY, 14, QFont.Weight.Bold))
                n.setWordWrap(True)
                n.setStyleSheet(f"color:{c['text_dark']}; background:transparent; border: none;")
                tr.addWidget(n)
                
                tr.addStretch()
                
                if dl_lbl:
                    dl_l = QLabel(f"● {dl_lbl}")
                    dl_l.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
                    dl_l.setStyleSheet(f"color: {dc}; font-weight: bold; font-size: 13px; background: transparent; border: none;")
                    tr.addWidget(dl_l, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
                
                cl.addLayout(tr)
                
                # Organizer
                p_text = bea.get("penyelenggara", t['unknown'])
                if not p_text.strip(): p_text = t['unknown']
                p = QLabel(p_text)
                p.setStyleSheet(f"color: {c['text_muted']}; font-size: 11px; background:transparent; border: none;")
                cl.addWidget(p)
                
                cl.addSpacing(10)
                
                # Bottom Row: Info + Remove Button
                br = QHBoxLayout()
                info = f"{t['jenjang']}: {bea.get('jenjang','-')}"
                if bea.get("deadline"):
                    info += f"  |  {t['deadline']}: {bea['deadline']}"
                il = QLabel(info)
                il.setStyleSheet(f"color: {c['text_muted']}; font-size: 11px; background:transparent; border: none;")
                br.addWidget(il)
                
                br.addStretch()
                
                rm = QPushButton(t['remove'])
                rm.setStyleSheet(f"background: #E2A499; color: white; border: none; border-radius: 12px; padding: 6px 20px; font-weight: bold; font-size: 11px;")
                rm.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                rm.clicked.connect(lambda _, bid=bea.get("id",0): self._remove(bid))
                br.addWidget(rm)
                
                cl.addLayout(br)
                
                sl.addWidget(card)
            sl.addStretch()
        scroll.setWidget(sw)
        lay.addWidget(scroll)

    def _bold_label(self, text, size):
        l = QLabel(text)
        l.setFont(QFont(FONT_FAMILY, size, QFont.Weight.Bold))
        return l

    def _show_detail(self, bea):
        dlg = DetailDialog(bea, self._mode, self._pid, self, self._bhs)
        dlg.exec()

    def _remove(self, bid):
        toggle_bookmark_beasiswa(self._pid, bid)
        self.bookmark_changed.emit()  # beritahu kalender & komponen lain
        self._build()

    def _clear_all(self):
        r = QMessageBox.question(self, self._t['clear_all'], self._t['clear_confirm'])
        if r == QMessageBox.StandardButton.Yes:
            for bm in get_bookmarks(self._pid):
                toggle_bookmark_beasiswa(self._pid, bm.get("id", 0))
            self.bookmark_changed.emit()  # beritahu kalender & komponen lain
            self._build()

    def _show_sort(self):
        c = palette(self._mode)
        t = self._t
        dlg = QDialog(self)
        dlg.setWindowTitle(t['sort_title'])
        dlg.setFixedSize(300, 310)
        dlg.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        dlg.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        dlg.setStyleSheet("QDialog { background: transparent; }")
        
        main_lay = QVBoxLayout(dlg)
        main_lay.setContentsMargins(10, 10, 10, 10)
        
        bg_frame = QFrame()
        bg_frame.setStyleSheet(f"QFrame {{ background: {grad_mixed(c)}; border-radius: 20px; }}")
        main_lay.addWidget(bg_frame)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        bg_frame.setGraphicsEffect(shadow)
        
        dl = QVBoxLayout(bg_frame)
        dl.setContentsMargins(20, 20, 20, 20)
        dl.setSpacing(10)
        
        top_lay = QHBoxLayout()
        top_lay.addStretch(1)
        title = QLabel(t['sort_title'])
        title.setFont(QFont(FONT_FAMILY, 14, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {c['text_dark']}; background: transparent;")
        top_lay.addWidget(title)
        top_lay.addStretch(1)
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        close_btn.setStyleSheet("QPushButton { background: transparent; color: #888; font-size: 16px; font-weight: bold; border: none; } QPushButton:hover { color: #333; }")
        close_btn.clicked.connect(dlg.reject)
        top_lay.addWidget(close_btn)
        
        dl.addLayout(top_lay)
        
        for label, mode in [(t['sort_default'],"default"),(t['sort_dl_asc'],"deadline_asc"),
                            (t['sort_dl_desc'],"deadline_desc"),(t['sort_name_asc'],"name_asc"),(t['sort_name_desc'],"name_desc")]:
            b = QPushButton(label)
            if self._sort_mode == mode:
                b.setStyleSheet(f"background-color: {c['card']}; color: {c['text_dark']}; border: 2px solid {c['btn_primary']}; border-radius: 12px; font-weight: bold;")
            else:
                b.setStyleSheet(f"background-color: {c['btn_pale']}; color: {c['text_dark']}; border: none; border-radius: 12px;")
            b.setFixedHeight(36)
            b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            b.clicked.connect(lambda _, m=mode: (setattr(self,'_sort_mode',m), dlg.accept(), self._build()))
            dl.addWidget(b)
        dlg.exec()
