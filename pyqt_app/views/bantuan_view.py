"""
pyqt_app/views/bantuan_view.py
FAQ & Help Center — FAQ list + feedback form.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QComboBox, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor

from pyqt_app.styles.theme import FONT_FAMILY, palette, grad_peach
from controllers.bantuan_controller import get_faq_list, submit_feedback


class BantuanView(QWidget):
    def __init__(self, profil_id=None, bhs="id", mode="light", parent=None):
        super().__init__(parent)
        self._pid = profil_id
        self._bhs = bhs
        self._mode = mode
        self._build()

    def _build(self):
        c = palette(self._mode)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)

        # ── Left: FAQ list ───────────────────────────────────
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        lw = QWidget()
        ll = QVBoxLayout(lw)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(6)

        fh = QLabel("Frequently Asked Questions")
        fh.setFont(QFont(FONT_FAMILY, 15, QFont.Weight.Bold))
        ll.addWidget(fh)

        faqs = get_faq_list()
        for item in faqs:
            q = item.get("pertanyaan", "")
            a = item.get("jawaban", "")
            card = QFrame()
            card.setProperty("frameClass", "card")
            cl = QVBoxLayout(card)
            cl.setContentsMargins(16, 14, 16, 14)
            ql = QLabel(f"Q: {q}")
            ql.setFont(QFont(FONT_FAMILY, 12, QFont.Weight.Bold))
            ql.setWordWrap(True)
            cl.addWidget(ql)
            al = QLabel(f"A: {a}")
            al.setStyleSheet(f"color: {c['text_muted']}; font-size: 12px;")
            al.setWordWrap(True)
            cl.addWidget(al)
            ll.addWidget(card)
        ll.addStretch()
        left_scroll.setWidget(lw)
        lay.addWidget(left_scroll, 6)

        # ── Right: Report form ───────────────────────────────
        right = QFrame()
        right.setFixedWidth(300)
        right.setStyleSheet(f"""
            QFrame {{ background: {c['btn_pale']}; border-radius: 16px;
                      border: 1px solid {c['border']}; }}
        """)
        rl = QVBoxLayout(right)
        rl.setContentsMargins(20, 28, 20, 24)
        rl.setSpacing(8)

        rh = QLabel("Report an Issue or\nFeedback")
        rh.setFont(QFont(FONT_FAMILY, 15, QFont.Weight.Bold))
        rh.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rl.addWidget(rh)
        rl.addSpacing(12)

        rl.addWidget(self._bold_label("Category"))
        self._cat_cb = QComboBox()
        self._cat_cb.addItems(["Bug Report", "Suggestion", "Question", "Other"])
        self._cat_cb.setCurrentText("Question")
        self._cat_cb.setFixedHeight(34)
        rl.addWidget(self._cat_cb)
        rl.addSpacing(8)

        rl.addWidget(self._bold_label("Message"))
        self._msg_box = QTextEdit()
        self._msg_box.setFixedHeight(160)
        self._msg_box.setPlaceholderText("Describe your issue or feedback...")
        rl.addWidget(self._msg_box)
        rl.addSpacing(8)

        sb = QPushButton("Submit Report")
        sb.setFixedHeight(38)
        if self._mode == 'dark':
            sb.setStyleSheet(f"""
                QPushButton {{ background: {c['btn_primary']}; color: #1A1A1A;
                               border: none; border-radius: 10px;
                               font-weight: bold; font-size: 13px; }}
                QPushButton:hover {{ background: {c['btn_primary_hover']}; }}
            """)
        else:
            sb.setStyleSheet(f"""
                QPushButton {{ background: #F6D6D0; color: {c['text_dark']};
                               border: none; border-radius: 10px;
                               font-weight: bold; font-size: 13px; }}
                QPushButton:hover {{ background: #F0C0B8; }}
            """)
        sb.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        sb.clicked.connect(self._submit)
        rl.addWidget(sb)
        rl.addStretch()
        lay.addWidget(right, 3)

    def _bold_label(self, text):
        l = QLabel(text)
        l.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Bold))
        return l

    def _submit(self):
        cat = self._cat_cb.currentText()
        msg = self._msg_box.toPlainText().strip()
        uid = self._pid if self._pid else "Guest"
        if not msg:
            QMessageBox.warning(self, "Warning", "Message cannot be empty!")
            return
        ok = submit_feedback(uid, cat, msg)
        if ok:
            QMessageBox.information(self, "Success", "Your report has been submitted. Thank you!")
            self._msg_box.clear()
        else:
            QMessageBox.critical(self, "Error", "Failed to submit report.")
