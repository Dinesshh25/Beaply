"""
pyqt_app/views/bookmarks_view.py
Saved / Bookmarked Scholarships — list view with deadline colors.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor
from datetime import datetime

from pyqt_app.styles.theme import FONT_FAMILY, palette
from controllers.eksplorasi_controller import get_bookmarks, toggle_bookmark_beasiswa


class BookmarksView(QWidget):
    def __init__(self, profil_id, bhs="id", mode="light", parent=None):
        super().__init__(parent)
        self._pid = profil_id
        self._bhs = bhs
        self._mode = mode
        self._build()

    def _dl_info(self, dl):
        if not dl: return None, ""
        try:
            days = (datetime.strptime(dl, "%Y-%m-%d").date() - datetime.now().date()).days
            if days < 0: return "#999", "Expired"
            if days <= 7: return "#EF4444", f"{days} days left!"
            if days <= 14: return "#F59E0B", f"{days} days left"
            return "#22C55E", f"{days} days left"
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
        bm_list = get_bookmarks(self._pid)

        # Header
        hdr = QFrame()
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.addWidget(self._bold_label(f"{len(bm_list)} Bookmarks", 15))
        clr = QPushButton("\U0001f5d1 Clear All")
        clr.setStyleSheet(f"background: {c['card']}; color: {c['danger']}; border: 1px solid {c['border']}; border-radius: 10px; padding: 5px 14px; font-size: 11px;")
        clr.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        clr.clicked.connect(self._clear_all)
        hl.addStretch()
        hl.addWidget(clr)
        lay.addWidget(hdr)

        # Legend
        leg = QFrame()
        ll = QHBoxLayout(leg)
        ll.setContentsMargins(0, 0, 0, 0)
        for txt, clr2 in [("● >14d","#22C55E"),("● 7-14d","#F59E0B"),("● <7d","#EF4444"),("● Expired","#999")]:
            l = QLabel(txt)
            l.setStyleSheet(f"color: {clr2}; font-size: 9px;")
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
            e = QLabel("No bookmarked scholarships yet.\nExplore and save scholarships you're interested in!")
            e.setStyleSheet(f"color: {c['text_muted']}; font-size: 13px;")
            e.setAlignment(Qt.AlignmentFlag.AlignCenter)
            sl.addWidget(e)
            sl.addStretch()
        else:
            for i, bea in enumerate(bm_list):
                dc, dl_lbl = self._dl_info(bea.get("deadline"))
                card = QFrame()
                card.setObjectName(f"bmCard{i}")
                bdr = f"2px solid {dc}" if dc else f"1px solid {c['border']}"
                card.setStyleSheet(f"#bmCard{i} {{ background: {c['card']}; border-radius: 14px; border: {bdr}; }}")
                cl = QVBoxLayout(card)
                cl.setContentsMargins(20, 16, 20, 16)
                cl.setSpacing(6)
                tr = QWidget()
                tr.setStyleSheet("background:transparent;")
                trl = QHBoxLayout(tr)
                trl.setContentsMargins(0,0,0,0)
                n = QLabel(bea.get("nama",""))
                n.setFont(QFont(FONT_FAMILY, 13, QFont.Weight.Bold))
                n.setWordWrap(True)
                n.setStyleSheet(f"color:{c['text_dark']};background:transparent;")
                trl.addWidget(n)
                if dl_lbl:
                    dl_l = QLabel(dl_lbl)
                    dl_l.setStyleSheet(f"color: {dc}; font-size: 10px; font-weight: bold; background:transparent;")
                    trl.addWidget(dl_l)
                cl.addWidget(tr)
                p = QLabel(bea.get("penyelenggara",""))
                p.setStyleSheet(f"color: {c['text_muted']}; font-size: 11px; background:transparent;")
                cl.addWidget(p)
                info = f"Jenjang: {bea.get('jenjang','-')}"
                if bea.get("deadline"):
                    info += f"  |  Deadline: {bea['deadline']}"
                il = QLabel(info)
                il.setStyleSheet(f"color: {c['text_muted']}; font-size: 10px; background:transparent;")
                cl.addWidget(il)
                rm = QPushButton("Remove")
                rm.setStyleSheet(f"background: transparent; color: {c['danger']}; border: 1px solid {c['danger']}; border-radius: 8px; padding: 3px 10px; font-size: 10px;")
                rm.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                rm.setFixedWidth(70)
                rm.clicked.connect(lambda _, bid=bea.get("id",0): self._remove(bid))
                cl.addWidget(rm, alignment=Qt.AlignmentFlag.AlignRight)
                sl.addWidget(card)
            sl.addStretch()
        scroll.setWidget(sw)
        lay.addWidget(scroll)

    def _bold_label(self, text, size):
        l = QLabel(text)
        l.setFont(QFont(FONT_FAMILY, size, QFont.Weight.Bold))
        return l

    def _remove(self, bid):
        toggle_bookmark_beasiswa(self._pid, bid)
        self._build()

    def _clear_all(self):
        r = QMessageBox.question(self, "Clear All", "Remove all bookmarks?")
        if r == QMessageBox.StandardButton.Yes:
            for bm in get_bookmarks(self._pid):
                toggle_bookmark_beasiswa(self._pid, bm.get("id", 0))
            self._build()
