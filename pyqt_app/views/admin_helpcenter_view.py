"""
pyqt_app/views/admin_helpcenter_view.py
Admin — Help Center management page.

Tabs: All | Answered | Unanswered
Category dropdown: Bug report, Suggestion, Question, Other
Admin can reply to user feedback, and the reply is sent as a notification.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QComboBox, QMessageBox,
    QDialog, QTextEdit, QLineEdit, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor, QColor, QPainter, QLinearGradient
from datetime import datetime

from pyqt_app.styles.theme import FONT_FAMILY, palette, grad_green
from controllers.admin_controller import get_all_feedback, delete_feedback

def show_custom_msgbox(parent, title, text, c, icon=QMessageBox.Icon.Information, is_question=False):
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.setIcon(icon)
    if is_question:
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    msg.setStyleSheet(f"QMessageBox {{ background-color: {c['card']}; }} QLabel {{ color: {c['text_dark']}; }} QPushButton {{ background: {c['btn_pale']}; color: {c['text_dark']}; border-radius: 4px; padding: 4px 12px; min-width: 60px; }}")
    return msg.exec()

class ReplyFeedbackDialog(QDialog):
    def __init__(self, fb, mode, parent=None):
        super().__init__(parent)
        self.fb = fb
        self.mode = mode
        self._c = palette(mode)
        
        self.setWindowTitle("Reply to Feedback")
        self.setFixedSize(520, 420)
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
        
        dl = QVBoxLayout(self.content_frame)
        dl.setContentsMargins(24, 20, 24, 20)
        dl.setSpacing(10)
        
        title = QLabel("Reply to User Feedback")
        title.setFont(QFont(FONT_FAMILY, 15, QFont.Weight.Bold))
        dl.addWidget(title)
        
        def _lbl(text):
            l = QLabel(text)
            l.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Bold))
            return l
            
        dl.addWidget(_lbl("Category:"))
        cat_lbl = QLabel(fb.get("kategori", "N/A"))
        cat_lbl.setStyleSheet(f"font-size: 12px; padding: 4px;")
        dl.addWidget(cat_lbl)
        
        dl.addWidget(_lbl("User:"))
        user_lbl = QLabel(str(fb.get("id_user", "N/A")))
        user_lbl.setStyleSheet(f"font-size: 12px; padding: 4px;")
        dl.addWidget(user_lbl)
        
        dl.addWidget(_lbl("Message:"))
        msg_lbl = QLabel(fb.get("pesan", ""))
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet(
            f"font-size: 12px; "
            f"background: {self._c['input_bg']}; border-radius: 8px; padding: 10px;"
        )
        dl.addWidget(msg_lbl)
        
        dl.addWidget(_lbl("Your Reply:"))
        self.reply_box = QTextEdit()
        self.reply_box.setFixedHeight(100)
        self.reply_box.setPlaceholderText("Type your reply here...")
        self.reply_box.setStyleSheet(f"""
            QTextEdit {{
                background: {self._c['input_bg']};
                color: {self._c['text_dark']};
                border: none; border-radius: 10px;
                padding: 10px; font-size: 12px;
            }}
            QTextEdit:focus {{ border: 2px solid {self._c['btn_primary']}; }}
        """)
        if fb.get("admin_reply"):
            self.reply_box.setPlainText(fb["admin_reply"])
        dl.addWidget(self.reply_box)
        
        dl.addStretch()
        
        send_btn = QPushButton("📤 Send Reply & Notify User")
        send_btn.setFixedHeight(42)
        send_btn.setStyleSheet(f"""
            QPushButton {{
                background: {self._c['btn_primary']};
                color: {self._c['text_dark']};
                border: none; border-radius: 10px;
                font-weight: bold; font-size: 13px;
            }}
            QPushButton:hover {{ background: {self._c['btn_primary_hover']}; }}
        """)
        send_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        send_btn.clicked.connect(self.accept)
        dl.addWidget(send_btn)
        
        main_lay.addWidget(self.content_frame)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        grad = QLinearGradient(0, 0, self.width(), self.height())
        grad.setColorAt(0.0, QColor(self._c.get('grad_peach_start', '#F7D0B7')))
        grad.setColorAt(1.0, QColor(self._c.get('grad_green_start', '#D6EAD8')))
        painter.fillRect(self.rect(), grad)
        painter.end()
        super().paintEvent(event)


class AdminHelpCenterView(QWidget):
    def __init__(self, mode="light", parent=None):
        super().__init__(parent)
        self._mode = mode
        self._active_tab = "all"
        self._active_cat = "all"
        self._init_layout()

    def _init_layout(self):
        """Create outer layout once."""
        self._outer = QVBoxLayout(self)
        self._outer.setContentsMargins(0, 0, 0, 0)
        self._outer.setSpacing(0)
        self._container = QWidget()
        self._outer.addWidget(self._container)
        self._build()

    def _build(self):
        c = palette(self._mode)
        root = QVBoxLayout(self._container)
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
                           ("unanswered", "Unanswered")]:
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
        self._cat_cb.addItems(["Select Category", "Bug Report", "Suggestion", "Question", "Other"])
        self._cat_cb.setFixedHeight(36)
        self._cat_cb.setFixedWidth(200)
        self._cat_cb.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._cat_cb.setStyleSheet(f"""
            QComboBox {{
                background: {grad_green(c)};
                color: {c['text_dark']};
                border: none;
                border-radius: 10px;
                padding: 6px 16px;
                font-size: 12px;
                font-weight: bold;
            }}
            QComboBox:hover {{
                background: {c['btn_pale']};
            }}
            QComboBox::drop-down {{
                border: none; width: 30px;
            }}
            QComboBox QAbstractItemView {{
                background: {c['card']};
                color: {c['text_dark']};
                border: 1px solid {c['border']};
                selection-background-color: {c['btn_primary']};
                selection-color: {c['text_dark']};
                outline: none;
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

        # Filter by tab
        if self._active_tab == "answered":
            feedbacks = [f for f in feedbacks if f.get("admin_reply")]
        elif self._active_tab == "unanswered":
            feedbacks = [f for f in feedbacks if not f.get("admin_reply")]

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
        has_reply = bool(fb.get("admin_reply"))
        if self._mode == "dark":
            border_color = "#2D6B3E" if has_reply else "#6B5A40"
            bg_color = "#1E2A22" if has_reply else "#2A241E"
        else:
            border_color = "#D6EAD8" if has_reply else "#E8DDD4"
            bg_color = "#F5FAF6" if has_reply else "#FBF7F4"

        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {bg_color};
                border: 1.5px solid {border_color};
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

        # Category + status badge
        cat_row = QHBoxLayout()
        cat_row.setContentsMargins(0, 0, 0, 0)
        cat = QLabel(fb.get("kategori", "Other"))
        cat.setFont(QFont(FONT_FAMILY, 12, QFont.Weight.Bold))
        cat.setStyleSheet(f"color: {c['text_dark']}; border: none; background: transparent;")
        cat_row.addWidget(cat)

        if has_reply:
            badge = QLabel("✅ Answered")
            badge.setStyleSheet(
                "background: #D6EAD8; color: #2D6B3E; border-radius: 8px; "
                "padding: 2px 8px; font-size: 9px; font-weight: bold; border: none;"
            )
        else:
            badge = QLabel("⏳ Pending")
            badge.setStyleSheet(
                "background: #FFF3CD; color: #856404; border-radius: 8px; "
                "padding: 2px 8px; font-size: 9px; font-weight: bold; border: none;"
            )
        cat_row.addWidget(badge)
        cat_row.addStretch()
        il.addLayout(cat_row)

        # User ID
        user_lbl = QLabel(f"👤 User: {fb.get('id_user', 'N/A')}")
        user_lbl.setStyleSheet(f"color: {c['text_muted']}; font-size: 10px; border: none; background: transparent;")
        il.addWidget(user_lbl)

        msg = fb.get("pesan", "")
        q_text = msg[:80] + "..." if len(msg) > 80 else msg
        q = QLabel(f"Q: {q_text}")
        q.setStyleSheet(f"color: {c['text_dark']}; font-size: 11px; border: none; background: transparent;")
        q.setWordWrap(True)
        il.addWidget(q)

        if has_reply:
            reply_text = fb.get("admin_reply", "")
            r_text = reply_text[:80] + "..." if len(reply_text) > 80 else reply_text
            a = QLabel(f"A: {r_text}")
            a.setStyleSheet(f"color: #2D6B3E; font-size: 11px; border: none; background: transparent;")
            a.setWordWrap(True)
            il.addWidget(a)
        else:
            a = QLabel("A: (belum dijawab)")
            a.setStyleSheet(f"color: {c['text_muted']}; font-size: 11px; font-style: italic; border: none; background: transparent;")
            il.addWidget(a)

        lay.addWidget(info, 1)

        # Buttons
        bc = QVBoxLayout()
        bc.setSpacing(4)
        bc.setContentsMargins(0, 0, 0, 0)

        reply_btn = QPushButton("💬")
        reply_btn.setFixedSize(36, 30)
        reply_btn.setToolTip("Reply to this feedback")
        reply_btn.setStyleSheet(f"""
            QPushButton {{ background: {c['btn_primary']}; border: none; border-radius: 6px; font-size: 15px; }}
            QPushButton:hover {{ background: {c['btn_primary_hover']}; }}
        """)
        reply_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        reply_btn.clicked.connect(lambda _, f=fb: self._reply_feedback(f))
        bc.addWidget(reply_btn)

        del_btn = QPushButton("🗑")
        del_btn.setFixedSize(36, 30)
        del_btn.setToolTip("Delete this feedback")
        del_btn.setStyleSheet(f"""
            QPushButton {{ background: {c['danger_bg']}; border: none; border-radius: 6px; font-size: 15px; }}
            QPushButton:hover {{ background: #F5D0D0; }}
        """)
        del_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        idx = fb.get("_index", -1)
        del_btn.clicked.connect(lambda _, i=idx: self._del_feedback(i))
        bc.addWidget(del_btn)
        lay.addLayout(bc)
        return card

    def _reply_feedback(self, fb):
        """Open reply dialog for a feedback entry."""
        dlg = ReplyFeedbackDialog(fb, self._mode, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            reply_text = dlg.reply_box.toPlainText().strip()
            c = palette(self._mode)
            if not reply_text:
                show_custom_msgbox(self, "Warning", "Reply cannot be empty!", c, QMessageBox.Icon.Warning)
                return

            from controllers.admin_controller import reply_to_feedback
            ok, msg = reply_to_feedback(fb.get("_index", -1), reply_text)
            if not ok:
                show_custom_msgbox(self, "Error", msg, c, QMessageBox.Icon.Critical)
                return

            user_id = fb.get("id_user")
            if user_id and str(user_id) != "Guest":
                self._send_reply_notification(user_id, fb.get("kategori", "Feedback"), reply_text)

            show_custom_msgbox(self, "Success", "Reply sent successfully!\nThe user will see it in their notifications.", c, QMessageBox.Icon.Information)
            self._rebuild()

    def _send_reply_notification(self, user_id, kategori, reply_text):
        """Send notification to the user who submitted feedback."""
        try:
            # Get the user's profil_id from user_id
            from models.database import get_connection
            conn = get_connection()
            cur = conn.cursor()

            # user_id could be profil_id directly or a user.id
            # Try finding profil by user_id first
            profil_id = None
            try:
                uid_int = int(user_id)
                cur.execute("SELECT id FROM profil WHERE user_id = ?", (uid_int,))
                row = cur.fetchone()
                if row:
                    profil_id = row["id"]
                else:
                    # Maybe user_id IS the profil_id
                    cur.execute("SELECT id FROM profil WHERE id = ?", (uid_int,))
                    row = cur.fetchone()
                    if row:
                        profil_id = row["id"]
            except (ValueError, TypeError):
                pass
            conn.close()

            if profil_id:
                from models.notifikasi_model import tambah_notifikasi
                tambah_notifikasi(
                    profil_id,
                    f"📩 Admin Reply: {kategori}",
                    f"Admin telah menjawab pertanyaan Anda:\n\n{reply_text}",
                    "info"
                )
        except Exception as e:
            print(f"[WARN] Failed to send notification to user {user_id}: {e}")

    def _dlg_label(self, text, c):
        l = QLabel(text)
        l.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Bold))
        l.setStyleSheet(f"color: {c['text_dark']};")
        return l

    def _del_feedback(self, idx):
        c = palette(self._mode)
        r = show_custom_msgbox(self, "Delete", "Delete this feedback?", c, QMessageBox.Icon.Question, True)
        if r == QMessageBox.StandardButton.Yes:
            ok, msg = delete_feedback(idx)
            if ok:
                self._rebuild()
            else:
                show_custom_msgbox(self, "Error", msg, c, QMessageBox.Icon.Critical)

    def _show_detail(self, fb):
        msg = f"Category: {fb.get('kategori', 'N/A')}\n"
        msg += f"User: {fb.get('id_user', 'N/A')}\n"
        msg += f"Time: {fb.get('waktu', 'N/A')}\n\n"
        msg += f"Message:\n{fb.get('pesan', '')}"
        if fb.get("admin_reply"):
            msg += f"\n\nAdmin Reply:\n{fb['admin_reply']}"
        QMessageBox.information(self, "Feedback Detail", msg)

    def _set_tab(self, key):
        self._active_tab = key
        c = palette(self._mode)
        self._update_tab_styles(c)
        self._populate_feedback(c)

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

    def _rebuild(self):
        """Replace container with fresh one."""
        old = self._container
        self._outer.removeWidget(old)
        old.deleteLater()
        self._container = QWidget()
        self._outer.addWidget(self._container)
        self._build()
