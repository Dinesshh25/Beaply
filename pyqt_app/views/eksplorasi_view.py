"""
pyqt_app/views/eksplorasi_view.py
Explore Scholarships — grid view with search, sort, filter.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QLineEdit, QGridLayout,
    QDialog, QRadioButton, QCheckBox, QButtonGroup,
    QGraphicsDropShadowEffect, QApplication, QCompleter
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QUrl, QTimer
from PyQt6.QtGui import QFont, QCursor, QColor, QPainter, QPainterPath, QPixmap, QBrush, QPen, QIcon, QFontMetrics, QLinearGradient, QDesktopServices
from datetime import datetime

from pyqt_app.styles.theme import FONT_FAMILY, palette, pastel, grad_green, grad_peach, grad_peach_hover
from controllers.eksplorasi_controller import (
    get_semua_beasiswa, get_bookmarks, check_bookmarked, toggle_bookmark_beasiswa,
)
from controllers.notifikasi_controller import buat_notifikasi_deadline

def create_bookmark_icon(color_str, filled=False):
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    color = QColor(color_str)
    
    path = QPainterPath()
    path.moveTo(6, 4)
    path.lineTo(18, 4)
    path.lineTo(18, 20)
    path.lineTo(12, 16)
    path.lineTo(6, 20)
    path.closeSubpath()
    
    if filled:
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
    else:
        pen = QPen(color)
        pen.setWidth(2)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
    painter.drawPath(path)
    painter.end()
    
    return QIcon(pixmap)

class CardFrame(QFrame):
    clicked = pyqtSignal(dict)
    
    def __init__(self, bea_data, parent=None):
        super().__init__(parent)
        self.bea_data = bea_data
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.bea_data)
        try:
            super().mousePressEvent(event)
        except RuntimeError:
            pass  # C++ object already deleted — safe to ignore

class DetailDialog(QDialog):
    def __init__(self, bea, mode, pid, parent=None):
        super().__init__(parent)
        self.bea = bea
        self.mode = mode
        self.pid = pid
        self._c = palette(mode)
        
        self.setWindowTitle("Detail Beasiswa")
        self.setFixedSize(500, 560)
        self.setStyleSheet("QDialog { background: transparent; }")
        
        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(20, 20, 20, 20)
        
        self.content_frame = QFrame()
        _content_bg = 'rgba(255, 255, 255, 0.85)' if self.mode == 'light' else f'rgba(41, 42, 45, 0.95)'
        self.content_frame.setStyleSheet(f"QFrame {{ background-color: {_content_bg}; border-radius: 20px; }} QLabel {{ background: transparent; color: {self._c['text_dark']}; }}")
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 4)
        self.content_frame.setGraphicsEffect(shadow)
        
        lay = QVBoxLayout(self.content_frame)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(12)
        
        title = QLabel(bea.get("nama", ""))
        title.setFont(QFont(FONT_FAMILY, 18, QFont.Weight.Bold))
        title.setWordWrap(True)
        lay.addWidget(title)
        
        if bea.get("penyelenggara"):
            p = QLabel(bea.get("penyelenggara", ""))
            p.setStyleSheet(f"color: {self._c['text_muted']}; font-size: 14px;")
            p.setWordWrap(True)
            lay.addWidget(p)
            
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: rgba(0, 0, 0, 0.1);")
        line.setFixedHeight(1)
        lay.addWidget(line)
        
        toefl_val = bea.get("syarat_toefl")
        ielts_val = bea.get("syarat_ielts")
        
        try:
            toefl_show = f"≥ {int(toefl_val)}" if toefl_val and int(toefl_val) > 0 else "Tidak Wajib"
        except:
            toefl_show = "Tidak Wajib"
            
        try:
            ielts_show = f"≥ {float(ielts_val)}" if ielts_val and float(ielts_val) > 0 else "Tidak Wajib"
        except:
            ielts_show = "Tidak Wajib"

        info = [
            ("🎓 Jenjang", bea.get("jenjang", "-")),
            ("⏳ Deadline", bea.get("deadline", "-")),
            ("📝 Syarat TOEFL", toefl_show),
            ("📝 Syarat IELTS", ielts_show),
        ]
        
        info_lay = QGridLayout()
        info_lay.setHorizontalSpacing(20)
        info_lay.setVerticalSpacing(8)
        for i, (k, v) in enumerate(info):
            r, c_idx = i // 2, i % 2
            lbl = QLabel(f"<b>{k}</b>: {v}")
            lbl.setFont(QFont(FONT_FAMILY, 11))
            info_lay.addWidget(lbl, r, c_idx)
        lay.addLayout(info_lay)
            
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setStyleSheet("background-color: rgba(0, 0, 0, 0.1);")
        line2.setFixedHeight(1)
        lay.addWidget(line2)
        
        desc_scroll = QScrollArea()
        desc_scroll.setWidgetResizable(True)
        desc_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; } QScrollBar { width: 0px; }")
        desc_w = QWidget()
        desc_w.setStyleSheet("background: transparent;")
        desc_l = QVBoxLayout(desc_w)
        desc_l.setContentsMargins(0, 0, 0, 0)
        
        desc = QLabel(bea.get("deskripsi") or "Tidak ada deskripsi tambahan.")
        desc.setWordWrap(True)
        desc.setFont(QFont(FONT_FAMILY, 11))
        desc.setStyleSheet(f"color: {self._c['text_dark']}; line-height: 1.5;")
        desc_l.addWidget(desc)
        desc_l.addStretch()
        desc_scroll.setWidget(desc_w)
        lay.addWidget(desc_scroll, 1)
        
        btn_lay = QHBoxLayout()
        btn_lay.setSpacing(12)
        
        self.btn_share = QPushButton("🔗 Bagikan Link")
        self.btn_share.setFixedHeight(40)
        self.btn_share.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_share.setStyleSheet(f"QPushButton {{ background-color: #F1F5F1; color: {self._c['text_dark']}; border-radius: 20px; font-weight: bold; font-size: 12px; }} QPushButton:hover {{ background-color: #E2E8E2; }}")
        self.btn_share.clicked.connect(self._share_link)
        btn_lay.addWidget(self.btn_share)
        
        self.is_bm = check_bookmarked(self.pid, bea.get("id", 0))
        self.btn_bm = QPushButton()
        self.btn_bm.setIconSize(QSize(20, 20))
        self._update_bm_btn()
        self.btn_bm.setFixedHeight(40)
        self.btn_bm.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_bm.clicked.connect(self._toggle_bm)
        btn_lay.addWidget(self.btn_bm)
        
        lay.addLayout(btn_lay)
        lay.addSpacing(10)
        
        link = bea.get("url", "")
        self.btn_visit = QPushButton("Kunjungi Website Resmi")
        self.btn_visit.setFixedHeight(48)
        self.btn_visit.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_visit.setFont(QFont(FONT_FAMILY, 13, QFont.Weight.Bold))
        if link:
            self.btn_visit.setStyleSheet(f"QPushButton {{ background-color: {self._c['btn_primary']}; color: {self._c['text_dark']}; border-radius: 14px; }} QPushButton:hover {{ background-color: {self._c['btn_primary_hover']}; }}")
            self.btn_visit.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(link)))
        else:
            self.btn_visit.setStyleSheet(f"QPushButton {{ background-color: {self._c['btn_pale']}; color: {self._c['text_muted']}; border-radius: 14px; }}")
            self.btn_visit.setText("Link Tidak Tersedia")
            self.btn_visit.setEnabled(False)
            
        lay.addWidget(self.btn_visit)
        main_lay.addWidget(self.content_frame)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        grad = QLinearGradient(0, 0, self.width(), self.height())
        grad.setColorAt(0.0, QColor(self._c['grad_peach_start']))
        grad.setColorAt(1.0, QColor(self._c['grad_green_start']))
        painter.fillRect(self.rect(), grad)
        painter.end()
        super().paintEvent(event)

    def _share_link(self):
        link = self.bea.get("url", "") or ""
        if link:
            QApplication.clipboard().setText(link)
            self.btn_share.setText("✅ Link Disalin!")
            QTimer.singleShot(2000, lambda: self.btn_share.setText("🔗 Bagikan Link"))

    def _update_bm_btn(self):
        if self.is_bm:
            self.btn_bm.setText(" Tersimpan")
            self.btn_bm.setIcon(create_bookmark_icon("#D4917B", True))
            self.btn_bm.setStyleSheet(f"QPushButton {{ background-color: #FCEAE3; color: #D4917B; border-radius: 20px; font-weight: bold; font-size: 12px; text-align: left; padding-left: 20px; }} QPushButton:hover {{ background-color: #F5DED5; }}")
        else:
            self.btn_bm.setText(" Simpan Beasiswa")
            self.btn_bm.setIcon(create_bookmark_icon(self._c['text_dark'], False))
            self.btn_bm.setStyleSheet(f"QPushButton {{ background-color: #F1F5F1; color: {self._c['text_dark']}; border-radius: 20px; font-weight: bold; font-size: 12px; text-align: left; padding-left: 15px; }} QPushButton:hover {{ background-color: #E2E8E2; }}")

    def _toggle_bm(self):
        toggle_bookmark_beasiswa(self.pid, self.bea.get("id", 0))
        self.is_bm = not self.is_bm
        self._update_bm_btn()
        # Flag that parent needs refresh — do NOT call _render_grid() here
        # because this dialog's parent CardFrame would be deleted mid-event.
        self._bookmark_dirty = True

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
        self._filter_only_active = True
        self._apply_filters()
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
        def _to_float(v):
            try: return float(v) if v is not None else 0.0
            except: return 0.0

        if self._filter_toefl and self._filter_ielts:
            r = [b for b in r if _to_float(b.get("syarat_toefl")) > 0 or _to_float(b.get("syarat_ielts")) > 0]
        elif self._filter_toefl:
            r = [b for b in r if _to_float(b.get("syarat_toefl")) > 0]
        elif self._filter_ielts:
            r = [b for b in r if _to_float(b.get("syarat_ielts")) > 0]

        if self._filter_only_active:
            today_str = datetime.now().strftime('%Y-%m-%d')
            r = [b for b in r if not b.get("deadline") or b.get("deadline") >= today_str]
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
        lay.setSpacing(12)

        # Title
        title = QLabel("Scholarships")
        title.setObjectName("title")
        lay.addWidget(title)

        # Top bar
        top = QFrame()
        tl = QHBoxLayout(top)
        tl.setContentsMargins(0, 0, 0, 0)
        tl.setSpacing(12)
        
        self._search = QLineEdit()
        self._search.setPlaceholderText("🔍 Search Scholarships...")
        self._search.setFixedHeight(40)
        self._search.setStyleSheet(f"background-color: {c['card']}; border: 1px solid {c['border']}; border-radius: 12px; padding: 0 16px;")
        
        suggestions = list(set([b.get("nama") for b in self._all if b.get("nama")] + [b.get("penyelenggara") for b in self._all if b.get("penyelenggara")]))
        self._completer = QCompleter(suggestions)
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._completer.setFilterMode(Qt.MatchFlag.MatchContains)
        
        popup = self._completer.popup()
        popup.setStyleSheet(f"background-color: {c['card']}; color: {c['text_dark']}; border: 1px solid {c['border']}; border-radius: 8px; outline: none;")
        self._search.setCompleter(self._completer)
        
        self._search.textChanged.connect(self._on_search)
        tl.addWidget(self._search, 1)
        
        sort_btn = QPushButton("\u21C5 Sort by")
        sort_btn.setStyleSheet(f"background: {grad_green(c)}; color: {c['text_dark']}; border: none; border-radius: 12px; font-weight: bold; font-size: 13px;")
        sort_btn.setFixedSize(110, 40)
        sort_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        sort_btn.clicked.connect(self._show_sort)
        tl.addWidget(sort_btn)
        
        filt_btn = QPushButton("\u2699 Filters")
        filt_btn.setStyleSheet(f"background: {grad_peach(c)}; color: {c['text_dark']}; border: none; border-radius: 12px; font-weight: bold; font-size: 13px;")
        filt_btn.setFixedSize(110, 40)
        filt_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        filt_btn.clicked.connect(self._show_filter)
        tl.addWidget(filt_btn)

        refresh_btn = QPushButton("\u21BB")
        refresh_btn.setToolTip("Refresh data beasiswa")
        refresh_btn.setStyleSheet(f"background: {c['card']}; border: 1px solid {c['border']}; border-radius: 12px; font-size: 16px;")
        refresh_btn.setFixedSize(40, 40)
        refresh_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        refresh_btn.clicked.connect(self._refresh_data)
        tl.addWidget(refresh_btn)
        lay.addWidget(top)

        # Separator Line
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet(f"background-color: {c['border']};")
        line.setFixedHeight(1)
        lay.addWidget(line)

        self._count = QLabel(f"{len(self._filtered)} Scholarships Found")
        self._count.setFont(QFont(FONT_FAMILY, 13, QFont.Weight.Bold))
        self._count.setStyleSheet(f"color: {c['text_dark']}; margin-top: 4px;")
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
        grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        grid.setSpacing(12)
        grid.setContentsMargins(4, 4, 18, 4)
        cols = 4
        for col in range(cols):
            grid.setColumnStretch(col, 1)
        if self._mode == 'dark':
            card_colors = ["#2B302C", "#36322C", "#382928"]
        else:
            card_colors = ["#EBEDE0", "#FFF8E5", "#FCEAE6"]

        # Batch-load all bookmark IDs once (instead of 1 query per card)
        bm_ids = {b.get("id") for b in get_bookmarks(self._pid)}

        for i, bea in enumerate(self._filtered):
            row, col = i // cols, i % cols
            bg = card_colors[i % len(card_colors)]
            is_bm = bea.get("id", 0) in bm_ids
            dl_clr = self._deadline_color(bea.get("deadline")) if is_bm else None

            card = CardFrame(bea)
            card.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            card.clicked.connect(self._show_detail)
            card.setObjectName(f"beaCard{i}")
            card.setFixedHeight(240)
            card.setMinimumWidth(100)
            border = f"2px solid {dl_clr}" if dl_clr else "none"
            card.setStyleSheet(f"#beaCard{i} {{ background: {bg}; border-radius: 14px; border: {border}; }}")
            
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(10)
            shadow.setColor(QColor(0, 0, 0, 15))
            shadow.setOffset(0, 4)
            card.setGraphicsEffect(shadow)

            cl = QVBoxLayout(card)
            cl.setContentsMargins(16, 14, 16, 10)
            cl.setSpacing(4)

            nama = bea.get("nama", "")
            if len(nama) > 110:
                nama = nama[:107] + "..."
                
            n = QLabel(nama)
            n.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Bold))
            n.setWordWrap(True)
            n.setMinimumWidth(50)
            n.setToolTip(bea.get("nama", ""))
            n.setStyleSheet(f"color: {c['text_dark']}; background: transparent;")
            cl.addWidget(n)
            if bea.get("penyelenggara"):
                p = QLabel(bea["penyelenggara"])
                p.setStyleSheet(f"color: {c['text_muted']}; font-size: 10px; background: transparent;")
                p.setWordWrap(True)
                p.setMinimumWidth(50)
                cl.addWidget(p)
            j = QLabel(f"Jenjang: {bea.get('jenjang', '-')}")
            j.setStyleSheet(f"color: {c['text_muted']}; font-size: 9px; background: transparent;")
            j.setMinimumWidth(50)
            cl.addWidget(j)
            dl = bea.get("deadline", "")
            if dl:
                dc = self._deadline_color(dl)
                dlbl = QLabel(f"Deadline: {dl}")
                dlbl.setStyleSheet(f"color: {dc or c['text_accent']}; font-size: 9px; background: transparent;")
                dlbl.setMinimumWidth(50)
                cl.addWidget(dlbl)
            cl.addStretch()
            # Bookmark btn
            bm = QPushButton()
            icon_color = c['text_accent'] if is_bm else c['text_muted']
            bm.setIcon(create_bookmark_icon(icon_color, is_bm))
            bm.setIconSize(QSize(24, 24))
            bm.setStyleSheet("background: transparent; border: none;")
            bm.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            bm.clicked.connect(lambda _, b=bea: self._toggle_bm(b))
            cl.addWidget(bm, alignment=Qt.AlignmentFlag.AlignRight)
            grid.addWidget(card, row, col)

        self._scroll.setWidget(w)
        self._count.setText(f"{len(self._filtered)} Scholarships Found")

    def _refresh_data(self):
        """Reload scholarship data from database."""
        self._all = get_semua_beasiswa()
        self._apply_filters()
        self._render_grid()

    def _on_search(self):
        self._apply_filters()
        self._render_grid()

    def _show_detail(self, bea):
        dlg = DetailDialog(bea, self._mode, self._pid, self)
        dlg.exec()
        # Defer refresh to NEXT event loop tick — we are still inside
        # CardFrame.mousePressEvent; calling _render_grid() now would
        # delete the CardFrame before super().mousePressEvent() returns.
        if getattr(dlg, '_bookmark_dirty', False):
            QTimer.singleShot(0, self._deferred_refresh)

    def _deferred_refresh(self):
        """Called after the event loop finishes the current mouse event."""
        self.bookmark_changed.emit()
        self._apply_filters()
        self._render_grid()

    def _toggle_bm(self, bea):
        toggle_bookmark_beasiswa(self._pid, bea.get("id", 0))
        # Defer grid rebuild so the current click event finishes first
        QTimer.singleShot(0, self._deferred_refresh)

    def _show_sort(self):
        c = palette(self._mode)
        dlg = QDialog(self)
        dlg.setWindowTitle("Sort")
        dlg.setFixedSize(300, 310)
        dlg.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        dlg.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        dlg.setStyleSheet("QDialog { background: transparent; }")
        
        main_lay = QVBoxLayout(dlg)
        main_lay.setContentsMargins(10, 10, 10, 10)
        
        bg_frame = QFrame()
        bg_frame.setStyleSheet(f"QFrame {{ background: {grad_peach(c)}; border-radius: 20px; }}")
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
        title = QLabel("Sort Scholarships")
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
        
        for label, mode in [("Default","default"),("Deadline ↑","deadline_asc"),
                            ("Deadline ↓","deadline_desc"),("Name A→Z","name_asc"),("Name Z→A","name_desc")]:
            b = QPushButton(label)
            if self._sort_mode == mode:
                b.setStyleSheet(f"background-color: {c['card']}; color: {c['text_dark']}; border: 2px solid {c['btn_primary']}; border-radius: 12px; font-weight: bold;")
            else:
                b.setStyleSheet(f"background-color: {c['btn_pale']}; color: {c['text_dark']}; border: none; border-radius: 12px;")
            b.setFixedHeight(36)
            b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            b.clicked.connect(lambda _, m=mode: (setattr(self,'_sort_mode',m), dlg.accept(),
                                                  self._apply_filters(), self._render_grid()))
            dl.addWidget(b)
        dlg.exec()

    def _show_filter(self):
        c = palette(self._mode)
        dlg = QDialog(self)
        dlg.setWindowTitle("Filter")
        dlg.setFixedSize(340, 500)
        dlg.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        dlg.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        dlg.setStyleSheet("QDialog { background: transparent; }")
        
        main_lay = QVBoxLayout(dlg)
        main_lay.setContentsMargins(10, 10, 10, 10)
        
        bg_frame = QFrame()
        bg_frame.setStyleSheet(f"QFrame {{ background: {grad_peach(c)}; border-radius: 20px; }}")
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
        title = QLabel("Filter Scholarships")
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
        
        lbl_j = QLabel("Filter By Jenjang")
        lbl_j.setStyleSheet(f"color: {c['text_dark']}; font-weight: bold; background: transparent; margin-top: 5px;")
        dl.addWidget(lbl_j)
        group = QButtonGroup(dlg)
        
        j_lay = QGridLayout()
        j_lay.setSpacing(10)
        for idx, j in enumerate(["All","S1","S2","S3","D3","D4"]):
            rb = QRadioButton(j)
            _rb_bg = 'rgba(255,255,255,0.6)' if self._mode == 'light' else 'rgba(60,64,67,0.6)'
            rb.setStyleSheet(f"QRadioButton {{ color: {c['text_dark']}; background: transparent; }} QRadioButton::indicator {{ width: 14px; height: 14px; border-radius: 7px; border: 2px solid {c['text_muted']}; background: {_rb_bg}; }} QRadioButton::indicator:checked {{ border: 2px solid {c['text_accent']}; background: {c['text_accent']}; }}")
            if (j == "All" and not self._filter_jenjang) or j == self._filter_jenjang:
                rb.setChecked(True)
            group.addButton(rb)
            j_lay.addWidget(rb, idx // 3, idx % 3)
        dl.addLayout(j_lay)
            
        lbl_t = QLabel("Test Score Requirements")
        lbl_t.setStyleSheet(f"color: {c['text_dark']}; font-weight: bold; background: transparent; margin-top: 10px;")
        dl.addWidget(lbl_t)
        
        cb_toefl = QCheckBox("Requires TOEFL")
        _cb_bg = 'rgba(255,255,255,0.6)' if self._mode == 'light' else 'rgba(60,64,67,0.6)'
        cb_toefl.setStyleSheet(f"QCheckBox {{ color: {c['text_dark']}; background: transparent; }} QCheckBox::indicator {{ width: 16px; height: 16px; border-radius: 4px; border: 2px solid {c['text_muted']}; background: {_cb_bg}; }} QCheckBox::indicator:checked {{ border: 2px solid {c['btn_primary']}; background: {c['btn_primary']}; }}")
        cb_toefl.setChecked(self._filter_toefl)
        dl.addWidget(cb_toefl)
        cb_ielts = QCheckBox("Requires IELTS")
        cb_ielts.setStyleSheet(f"QCheckBox {{ color: {c['text_dark']}; background: transparent; }} QCheckBox::indicator {{ width: 16px; height: 16px; border-radius: 4px; border: 2px solid {c['text_muted']}; background: {_cb_bg}; }} QCheckBox::indicator:checked {{ border: 2px solid {c['btn_primary']}; background: {c['btn_primary']}; }}")
        cb_ielts.setChecked(self._filter_ielts)
        dl.addWidget(cb_ielts)

        lbl_s = QLabel("Status Beasiswa" if self._bhs == "id" else "Scholarship Status")
        lbl_s.setStyleSheet(f"color: {c['text_dark']}; font-weight: bold; background: transparent; margin-top: 10px;")
        dl.addWidget(lbl_s)

        cb_active = QCheckBox("Sembunyikan yang Expired" if self._bhs == "id" else "Hide Expired")
        cb_active.setStyleSheet(f"QCheckBox {{ color: {c['text_dark']}; background: transparent; }} QCheckBox::indicator {{ width: 16px; height: 16px; border-radius: 4px; border: 2px solid {c['text_muted']}; background: {_cb_bg}; }} QCheckBox::indicator:checked {{ border: 2px solid {c['btn_primary']}; background: {c['btn_primary']}; }}")
        cb_active.setChecked(self._filter_only_active)
        dl.addWidget(cb_active)
        
        dl.addStretch()
        
        btn = QPushButton("Apply Filters")
        btn.setStyleSheet(f"QPushButton {{ background: {grad_peach(c)}; color: {c['text_dark']}; border: none; border-radius: 14px; font-weight: bold; font-size: 13px; }} QPushButton:hover {{ background: {grad_peach_hover(c)}; }}")
        btn.setFixedHeight(44)
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        shadow_btn = QGraphicsDropShadowEffect()
        shadow_btn.setBlurRadius(15)
        shadow_btn.setColor(QColor(0,0,0,20))
        shadow_btn.setOffset(0,4)
        btn.setGraphicsEffect(shadow_btn)
        
        def apply():
            sel = group.checkedButton()
            jv = sel.text() if sel else "All"
            self._filter_jenjang = None if jv == "All" else jv
            self._filter_toefl = cb_toefl.isChecked()
            self._filter_ielts = cb_ielts.isChecked()
            self._filter_only_active = cb_active.isChecked()
            dlg.accept()
            self._apply_filters()
            self._render_grid()
        btn.clicked.connect(apply)
        dl.addWidget(btn)
        dlg.exec()
