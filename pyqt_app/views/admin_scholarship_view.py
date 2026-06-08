"""
pyqt_app/views/admin_scholarship_view.py
Admin — Scholarship Data management page.

Single-column layout showing all scholarships with edit/delete.
Bottom: Publish to Users + Auto Scrap buttons.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QMessageBox, QDialog, QLineEdit,
    QProgressBar, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QCursor, QColor, QPainter, QLinearGradient
import os
import sys

from pyqt_app.styles.theme import FONT_FAMILY, palette
from controllers.admin_controller import get_all_beasiswa_admin, delete_beasiswa

def show_custom_msgbox(parent, title, text, c, icon=QMessageBox.Icon.Information, is_question=False):
    msg = QMessageBox(parent)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.setIcon(icon)
    if is_question:
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    msg.setStyleSheet(f"QMessageBox {{ background-color: {c['card']}; }} QLabel {{ color: {c['text_dark']}; }} QPushButton {{ background: {c['btn_pale']}; color: {c['text_dark']}; border-radius: 4px; padding: 4px 12px; min-width: 60px; }}")
    return msg.exec()
from models.database import get_connection


class ScrapWorker(QThread):
    finished_signal = pyqtSignal()
    error_signal = pyqtSignal(str)

    def run(self):
        try:
            # Tambahkan folder 'Logika Scraping' ke Python path agar import berfungsi
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
            scraping_dir = os.path.join(base_dir, "Logika Scraping")
            if scraping_dir not in sys.path:
                sys.path.insert(0, scraping_dir)
            
            # pyrefly: ignore [missing-import]
            from run_all_scraping import jalankan_semua
            jalankan_semua(auto_sync=True)
            self.finished_signal.emit()
        except Exception as e:
            self.error_signal.emit(str(e))


# Jenjang yang valid untuk perguruan tinggi
JENJANG_PT = {"D3", "D4", "S1", "S2", "S3"}


def _is_perguruan_tinggi(jenjang_str: str) -> bool:
    """Check if jenjang string contains at least one perguruan tinggi level.
    Handles both 'S1, S2' and '["S1", "S2"]' formats.
    """
    if not jenjang_str:
        return False
    s = jenjang_str.strip()
    # Handle JSON array format from scraped data
    if s.startswith("["):
        import json
        try:
            parsed = json.loads(s)
            if isinstance(parsed, list):
                return any(str(p).strip().upper() in JENJANG_PT for p in parsed)
        except (json.JSONDecodeError, ValueError):
            pass
    # Fallback: comma/slash separated
    parts = [p.strip().upper() for p in s.replace("/", ",").split(",")]
    return any(p in JENJANG_PT for p in parts)


class EditScholarshipDialog(QDialog):
    def __init__(self, bea, mode, parent=None):
        super().__init__(parent)
        self.bea = bea
        self.mode = mode
        self._c = palette(mode)
        
        self.setWindowTitle("Edit Scholarship")
        self.setFixedSize(560, 480)
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
        dl.setContentsMargins(28, 24, 28, 24)
        dl.setSpacing(8)
        
        title = QLabel("Edit Scholarship")
        title.setFont(QFont(FONT_FAMILY, 15, QFont.Weight.Bold))
        dl.addWidget(title)
        dl.addSpacing(4)
        
        self.fields = {}
        for label, key, val in [
            ("Name", "nama", bea.get("nama", "")),
            ("Organizer", "penyelenggara", bea.get("penyelenggara", "")),
            ("Degree", "jenjang", bea.get("jenjang", "")),
            ("Deadline", "deadline", bea.get("deadline", "")),
            ("URL", "url", bea.get("url", "")),
        ]:
            lbl = QLabel(label)
            lbl.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Bold))
            dl.addWidget(lbl)
            inp = QLineEdit(str(val) if val else "")
            inp.setFixedHeight(38)
            inp.setStyleSheet(f"""
                QLineEdit {{
                    padding: 8px 14px;
                    font-size: 13px;
                    background: {self._c['input_bg']};
                    color: {self._c['text_dark']};
                    border: none;
                    border-radius: 10px;
                }}
                QLineEdit:focus {{
                    border: 2px solid {self._c['btn_primary']};
                }}
            """)
            dl.addWidget(inp)
            self.fields[key] = inp
            
        dl.addStretch()
        
        save = QPushButton("Save Changes")
        save.setFixedHeight(40)
        save.setStyleSheet(f"""
            QPushButton {{
                background: {self._c['btn_primary']};
                color: {self._c['text_dark']};
                border: none; border-radius: 10px;
                font-weight: bold; font-size: 13px;
            }}
            QPushButton:hover {{ background: {self._c['btn_primary_hover']}; }}
        """)
        save.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        save.clicked.connect(self.accept)
        dl.addWidget(save)
        
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


class AdminScholarshipView(QWidget):
    def __init__(self, mode="light", parent=None):
        super().__init__(parent)
        self._mode = mode
        self._init_layout()

    def _init_layout(self):
        """Create the outer layout once — never deleted."""
        self._outer = QVBoxLayout(self)
        self._outer.setContentsMargins(0, 0, 0, 0)
        self._outer.setSpacing(0)

        # Container widget holds all content; replaced on rebuild
        self._container = QWidget()
        self._outer.addWidget(self._container)
        self._populate()

    def _populate(self):
        """Build content inside _container."""
        c = palette(self._mode)
        lay = QVBoxLayout(self._container)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)

        # ── Stats row ────────────────────────────────────────
        beasiswa_list = get_all_beasiswa_admin()
        pt_count = sum(1 for b in beasiswa_list if _is_perguruan_tinggi(b.get("jenjang", "")))
        non_pt_count = len(beasiswa_list) - pt_count

        stats_row = QHBoxLayout()
        stats_row.setSpacing(12)

        total_lbl = QLabel(f"📊 Total: {len(beasiswa_list)}  |  "
                           f"🎓 Perguruan Tinggi: {pt_count}  |  "
                           f"⚠️ Non-PT (SMA dll): {non_pt_count}")
        total_lbl.setFont(QFont(FONT_FAMILY, 12, QFont.Weight.Bold))
        total_lbl.setStyleSheet(f"color: {c['text_dark']}; padding: 6px 0;")
        stats_row.addWidget(total_lbl)
        stats_row.addStretch()
        lay.addLayout(stats_row)

        # ── Scroll area with scholarship cards ───────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
            " QScrollArea > QWidget > QWidget { background: transparent; }")
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        scroll_lay = QVBoxLayout(scroll_content)
        scroll_lay.setContentsMargins(0, 0, 0, 0)
        scroll_lay.setSpacing(6)

        for bea in beasiswa_list:
            card = self._make_card(bea, c)
            scroll_lay.addWidget(card)

        scroll_lay.addStretch()
        scroll.setWidget(scroll_content)
        lay.addWidget(scroll, 1)

        # ── Status label for scraping ────────────────────────
        self.status_label = QLabel("")
        self.status_label.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Bold))
        self.status_label.setStyleSheet(f"color: {c['text_muted']}; font-style: italic;")
        self.status_label.hide()
        lay.addWidget(self.status_label)

        # ── Bottom buttons ───────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        # Publish button — removes non-PT scholarships
        publish_btn = QPushButton(f"🚀 Publish to Users (Remove {non_pt_count} non-PT)")
        publish_btn.setFixedHeight(40)
        publish_btn.setMinimumWidth(280)
        publish_btn.setStyleSheet(f"""
            QPushButton {{
                background: #E8B4A2;
                color: {c['text_dark']};
                border: none; border-radius: 10px;
                font-weight: bold; font-size: 13px;
                padding: 0 20px;
            }}
            QPushButton:hover {{ background: #D4917B; }}
        """)
        publish_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        publish_btn.clicked.connect(self._publish_to_users)
        if non_pt_count == 0:
            publish_btn.setText("✅ All data is PT-only")
            publish_btn.setEnabled(False)
            publish_btn.setStyleSheet(f"""
                QPushButton {{
                    background: #D6EAD8;
                    color: {c['text_dark']};
                    border: none; border-radius: 10px;
                    font-weight: bold; font-size: 13px;
                    padding: 0 20px;
                }}
            """)
        btn_row.addWidget(publish_btn)

        btn_row.addStretch()

        self.scrap_btn = QPushButton("🔄 Auto Scrap")
        self.scrap_btn.setFixedHeight(40)
        self.scrap_btn.setFixedWidth(160)
        self.scrap_btn.setStyleSheet(f"""
            QPushButton {{
                background: {c['btn_primary']};
                color: {c['text_dark']};
                border: none; border-radius: 10px;
                font-weight: bold; font-size: 13px;
            }}
            QPushButton:hover {{ background: {c['btn_primary_hover']}; }}
            QPushButton:disabled {{ background: #d3d3d3; color: #888888; }}
        """)
        self.scrap_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.scrap_btn.clicked.connect(self._start_scraping)
        btn_row.addWidget(self.scrap_btn)

        lay.addLayout(btn_row)

    # ── Card builder ─────────────────────────────────────────
    def _make_card(self, bea: dict, c: dict) -> QFrame:
        is_pt = _is_perguruan_tinggi(bea.get("jenjang", ""))
        if self._mode == "dark":
            border_color = "#2D6B3E" if is_pt else "#6B2D2D"
            bg_color = "#1E2A22" if is_pt else "#2A1E1E"
        else:
            border_color = "#D6EAD8" if is_pt else "#F5D0D0"
            bg_color = "#F5FAF6" if is_pt else "#FFF5F5"

        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {bg_color};
                border: 1.5px solid {border_color};
                border-radius: 12px;
            }}
        """)
        # Dynamic height — no fixed height
        card.setMinimumHeight(60)

        lay = QHBoxLayout(card)
        lay.setContentsMargins(16, 10, 10, 10)
        lay.setSpacing(10)

        # Info
        info = QFrame()
        info.setStyleSheet("border: none; background: transparent;")
        il = QVBoxLayout(info)
        il.setContentsMargins(0, 0, 0, 0)
        il.setSpacing(2)
        n = QLabel(bea.get("nama", "Unknown"))
        n.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Bold))
        n.setStyleSheet(
            f"color: {c['text_dark']}; border: none; background: transparent;")
        n.setWordWrap(True)
        il.addWidget(n)

        # Detail row: organizer + jenjang + deadline
        detail_parts = []
        if bea.get("penyelenggara"):
            detail_parts.append(bea["penyelenggara"])
        if bea.get("jenjang"):
            jenjang_tag = bea["jenjang"]
            if not is_pt:
                jenjang_tag = f"⚠️ {jenjang_tag}"
            detail_parts.append(f"[{jenjang_tag}]")
        if bea.get("deadline"):
            detail_parts.append(f"⏰ {bea['deadline']}")

        o = QLabel(" • ".join(detail_parts))
        o.setStyleSheet(
            f"color: {c['text_muted']}; font-size: 10px;"
            " border: none; background: transparent;")
        o.setWordWrap(True)
        il.addWidget(o)
        lay.addWidget(info, 1)

        # Buttons
        bc = QVBoxLayout()
        bc.setSpacing(4)
        bc.setContentsMargins(0, 0, 0, 0)

        edit_btn = QPushButton("📋")
        edit_btn.setFixedSize(32, 28)
        edit_btn.setStyleSheet(f"""
            QPushButton {{
                background: {c['btn_primary']};
                border: none; border-radius: 6px; font-size: 14px;
            }}
            QPushButton:hover {{ background: {c['btn_primary_hover']}; }}
        """)
        edit_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        edit_btn.clicked.connect(lambda _, b=bea: self._edit_beasiswa(b))
        bc.addWidget(edit_btn)

        del_btn = QPushButton("🗑")
        del_btn.setFixedSize(32, 28)
        del_btn.setStyleSheet(f"""
            QPushButton {{
                background: {c['danger_bg']};
                border: none; border-radius: 6px; font-size: 14px;
            }}
            QPushButton:hover {{ background: #F5D0D0; }}
        """)
        del_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        bea_id = bea.get("id")
        del_btn.clicked.connect(lambda _, bid=bea_id: self._delete_beasiswa(bid))
        bc.addWidget(del_btn)

        lay.addLayout(bc)
        return card

    # ── Actions ──────────────────────────────────────────────
    def _publish_to_users(self):
        """Remove all non-PT (non perguruan tinggi) scholarships from database."""
        beasiswa_list = get_all_beasiswa_admin()
        non_pt = [b for b in beasiswa_list if not _is_perguruan_tinggi(b.get("jenjang", ""))]
        c = palette(self._mode)

        if not non_pt:
            show_custom_msgbox(self, "Info", "All scholarships are already PT-level!", c, QMessageBox.Icon.Information)
            return

        text = (f"This will DELETE {len(non_pt)} non-perguruan-tinggi scholarships "
                f"(SMA, etc.) from the database.\n\n"
                f"Users will only see D3/D4/S1/S2/S3 scholarships.\n\n"
                f"Continue?")
        r = show_custom_msgbox(self, "Publish to Users", text, c, QMessageBox.Icon.Question, True)
        if r != QMessageBox.StandardButton.Yes:
            return

        try:
            conn = get_connection()
            deleted = 0
            for b in non_pt:
                conn.execute("DELETE FROM beasiswa WHERE id = ?", (b["id"],))
                deleted += 1
            conn.commit()
            conn.close()
            success_msg = (f"✅ Removed {deleted} non-PT scholarships.\n"
                           f"Users will now see only perguruan tinggi scholarships.")
            show_custom_msgbox(self, "Success", success_msg, c, QMessageBox.Icon.Information)
            self._rebuild()
        except Exception as e:
            show_custom_msgbox(self, "Error", f"Failed: {e}", c, QMessageBox.Icon.Critical)

    def _start_scraping(self):
        self.scrap_btn.setEnabled(False)
        self.scrap_btn.setText("Scraping...")
        self.status_label.setText("⏳ Sedang mengambil data (Est. 10-15 menit). Mohon tunggu...")
        self.status_label.show()

        c = palette(self._mode)
        show_custom_msgbox(self, "Info", "Auto scraping started in the background.\nPlease check the terminal for detailed progress.", c, QMessageBox.Icon.Information)
        
        self.worker = ScrapWorker()
        self.worker.finished_signal.connect(self._on_scrap_finished)
        self.worker.error_signal.connect(self._on_scrap_error)
        self.worker.start()

    def _on_scrap_finished(self):
        if hasattr(self, 'scrap_btn'):
            self.scrap_btn.setEnabled(True)
            self.scrap_btn.setText("🔄 Auto Scrap")
        if hasattr(self, 'status_label'):
            self.status_label.hide()
        c = palette(self._mode)
        msg = "Auto scraping completed and database updated!\n\nClick 'Publish to Users' to remove non-PT scholarships\nso users only see D3/D4/S1/S2/S3 beasiswa."
        show_custom_msgbox(self, "Success", msg, c, QMessageBox.Icon.Information)
        self._rebuild()

    def _on_scrap_error(self, err):
        if hasattr(self, 'scrap_btn'):
            self.scrap_btn.setEnabled(True)
            self.scrap_btn.setText("🔄 Auto Scrap")
        if hasattr(self, 'status_label'):
            self.status_label.hide()
        c = palette(self._mode)
        show_custom_msgbox(self, "Error", f"Auto scraping failed:\n{err}", c, QMessageBox.Icon.Critical)

    def _delete_beasiswa(self, bea_id):
        c = palette(self._mode)
        r = show_custom_msgbox(self, "Delete", "Are you sure you want to delete this scholarship?", c, QMessageBox.Icon.Question, True)
        if r == QMessageBox.StandardButton.Yes:
            ok, msg = delete_beasiswa(bea_id)
            if ok:
                show_custom_msgbox(self, "Success", msg, c, QMessageBox.Icon.Information)
                self._rebuild()
            else:
                show_custom_msgbox(self, "Error", msg, c, QMessageBox.Icon.Critical)

    def _edit_beasiswa(self, bea: dict):
        """Open edit dialog for a scholarship."""
        dlg = EditScholarshipDialog(bea, self._mode, self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            c = palette(self._mode)
            try:
                conn = get_connection()
                updates = {k: e.text().strip() for k, e in dlg.fields.items()}
                set_clause = ", ".join(f"{k} = ?" for k in updates)
                vals = list(updates.values()) + [bea["id"]]
                conn.execute(
                    f"UPDATE beasiswa SET {set_clause} WHERE id = ?", vals)
                conn.commit()
                conn.close()
                show_custom_msgbox(self, "Success", "Scholarship updated!", c, QMessageBox.Icon.Information)
                self._rebuild()
            except Exception as e:
                show_custom_msgbox(self, "Error", str(e), c, QMessageBox.Icon.Critical)

    # ── Rebuild ──────────────────────────────────────────────
    def _rebuild(self):
        """Replace _container with a fresh one."""
        old = self._container
        self._outer.removeWidget(old)
        old.deleteLater()

        self._container = QWidget()
        self._outer.addWidget(self._container)
        self._populate()
