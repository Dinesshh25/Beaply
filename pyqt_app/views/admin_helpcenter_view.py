"""
pyqt_app/views/admin_helpcenter_view.py
Admin — Help Center management page.

Tabs: All | Answered | Unanswered | Uploaded
Category dropdown: Bug report, Suggestion, Question, Other
Feedback cards grouped by date with expand/download buttons.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor
from datetime import datetime, timedelta

from pyqt_app.styles.theme import FONT_FAMILY, palette
from controllers.admin_controller import get_all_feedback, delete_feedback


class AdminHelpCenterView(QWidget):
    def __init__(self, mode="light", parent=None):
        super().__init__(parent)
        self._mode = mode
        self._active_tab = "all"
        self._active_cat = "all"
        self._build()

    def _build(self):
        c = palette(self._mode)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        # ── Tab bar + Category dropdown ──────────────────────
        top_row = QHBoxLayout()
        top_row.setSpacing(12)

        # Tab bar
        tab_frame = QFrame()
        tab_frame.setStyleSheet(f"""
            QFrame {{
                background: {c['input_bg']};
                border-radius: 10px;
            }}
        """)
        tab_lay = QHBoxLayout(tab_frame)
        tab_lay.setContentsMargins(4, 4, 4, 4)
        tab_lay.setSpacing(0)

        self._tab_buttons = {}
        for key, label in [("all", "All"), ("answered", "Answered"),
                           ("unanswered", "Unanswered"), ("uploaded", "Uploaded")]:
            btn = QPushButton(label)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setFixedHeight(32)
            btn.clicked.connect(lambda _, k=key: self._set_tab(k))
            self._tab_buttons[key] = btn
            tab_lay.addWidget(btn)
        self._update_tab_styles(c)
        top_row.addWidget(tab_frame, 1)

        # Category dropdown
        self._cat_cb = QComboBox()
        self._cat_cb.addItems(["Select Category", "Bug report", "Suggestion", "Question", "Other"])
        self._cat_cb.setFixedHeight(36)
        self._cat_cb.setFixedWidth(200)
        self._cat_cb.setStyleSheet(f"""
            QComboBox {{
                background: {c['card']};
                border: 1px solid {c['border']};
                border-radius: 10px;
                padding: 6px 12px;
                font-size: 12px;
            }}
            QComboBox::drop-down {{
                border: none; width: 30px;
            }}
        """)
        self._cat_cb.currentTextChanged.connect(self._on_cat_change)
        top_row.addWidget(self._cat_cb)

        root.addLayout(top_row)

        # ── Feedback list ────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        sw = QWidget()
        self._feed_lay = QVBoxLayout(sw)
        self._feed_lay.setContentsMargins(0, 0, 0, 0)
        self._feed_lay.setSpacing(8)

        self._populate_feedback(c)

        scroll.setWidget(sw)
        root.addWidget(scroll, 1)

    def _populate_feedback(self, c):
        # Clear existing
        while self._feed_lay.count():
            item = self._feed_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        feedbacks = get_all_feedback()

        # Filter by category
        if self._active_cat != "all":
            feedbacks = [f for f in feedbacks if f.get("kategori", "").lower() == self._active_cat.lower()]

        if not feedbacks:
            empty = QLabel("No feedback found.")
            empty.setStyleSheet(f"color: {c['text_muted']}; font-size: 13px;")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._feed_lay.addWidget(empty)
            self._feed_lay.addStretch()
            return

        # Group by date
        groups = self._group_by_date(feedbacks)
        for date_label, items in groups.items():
            dl = QLabel(date_label)
            dl.setFont(QFont(FONT_FAMILY, 14, QFont.Weight.Bold))
            dl.setStyleSheet(f"color: {c['text_dark']};")
            self._feed_lay.addWidget(dl)

            for fb in items:
                card = self._make_feedback_card(fb, c)
                self._feed_lay.addWidget(card)

        self._feed_lay.addStretch()

    def _group_by_date(self, feedbacks: list) -> dict:
        """Group feedbacks by relative date."""
        groups = {}
        now = datetime.now()
        for fb in feedbacks:
            waktu = fb.get("waktu", "")
            try:
                dt = datetime.strptime(waktu, "%Y-%m-%d %H:%M:%S")
                diff = (now.date() - dt.date()).days
                if diff == 0:
                    key = "Today"
                elif diff == 1:
                    key = "Yesterday"
                else:
                    key = f"{diff} days ago"
            except Exception:
                key = "Unknown"
            if key not in groups:
                groups[key] = []
            groups[key].append(fb)
        return groups

    def _make_feedback_card(self, fb: dict, c: dict) -> QFrame:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: #F5FAF6;
                border: 1.5px solid #D6EAD8;
                border-radius: 12px;
            }}
        """)
        card.setMinimumHeight(70)
        lay = QHBoxLayout(card)
        lay.setContentsMargins(16, 12, 10, 12)
        lay.setSpacing(10)

        # Content
        info = QFrame()
        info.setStyleSheet("border: none; background: transparent;")
        il = QVBoxLayout(info)
        il.setContentsMargins(0, 0, 0, 0)
        il.setSpacing(3)

        cat = QLabel(fb.get("kategori", "Other"))
        cat.setFont(QFont(FONT_FAMILY, 12, QFont.Weight.Bold))
        cat.setStyleSheet(f"color: {c['text_dark']}; border: none; background: transparent;")
        il.addWidget(cat)

        msg = fb.get("pesan", "")
        q_text = msg[:60] + "..." if len(msg) > 60 else msg
        q = QLabel(f"Q: {q_text}")
        q.setStyleSheet(f"color: {c['text_dark']}; font-size: 11px; border: none; background: transparent;")
        q.setWordWrap(True)
        il.addWidget(q)

        a = QLabel("A: ...")
        a.setStyleSheet(f"color: {c['text_muted']}; font-size: 11px; border: none; background: transparent;")
        il.addWidget(a)
        lay.addWidget(info, 1)

        # Buttons
        bc = QVBoxLayout()
        bc.setSpacing(4)
        bc.setContentsMargins(0, 0, 0, 0)

        expand_btn = QPushButton("📋")
        expand_btn.setFixedSize(36, 30)
        expand_btn.setStyleSheet(f"""
            QPushButton {{ background: {c['btn_primary']}; border: none; border-radius: 6px; font-size: 15px; }}
            QPushButton:hover {{ background: {c['btn_primary_hover']}; }}
        """)
        expand_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        idx = fb.get("_index", -1)
        expand_btn.clicked.connect(lambda _, f=fb: self._show_detail(f))
        bc.addWidget(expand_btn)

        dl_btn = QPushButton("⬇")
        dl_btn.setFixedSize(36, 30)
        dl_btn.setStyleSheet(f"""
            QPushButton {{ background: {c['btn_primary']}; border: none; border-radius: 6px; font-size: 15px; }}
            QPushButton:hover {{ background: {c['btn_primary_hover']}; }}
        """)
        dl_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        bc.addWidget(dl_btn)
        lay.addLayout(bc)
        return card

    def _show_detail(self, fb):
        msg = f"Category: {fb.get('kategori', 'N/A')}\n"
        msg += f"User: {fb.get('id_user', 'N/A')}\n"
        msg += f"Time: {fb.get('waktu', 'N/A')}\n\n"
        msg += f"Message:\n{fb.get('pesan', '')}"
        QMessageBox.information(self, "Feedback Detail", msg)

    def _set_tab(self, key):
        self._active_tab = key
        c = palette(self._mode)
        self._update_tab_styles(c)

    def _on_cat_change(self, text):
        self._active_cat = "all" if text == "Select Category" else text
        c = palette(self._mode)
        self._populate_feedback(c)

    def _update_tab_styles(self, c):
        for key, btn in self._tab_buttons.items():
            if key == self._active_tab:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {c['card']};
                        color: {c['text_dark']};
                        border: none; border-radius: 8px;
                        font-weight: bold; font-size: 11px;
                        padding: 6px 16px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent;
                        color: {c['text_muted']};
                        border: none; border-radius: 8px;
                        font-size: 11px;
                        padding: 6px 16px;
                    }}
                    QPushButton:hover {{ background: {c['btn_pale']}; }}
                """)
