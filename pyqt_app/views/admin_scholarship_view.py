"""
pyqt_app/views/admin_scholarship_view.py
Admin — Scholarship Data management page.

Single-column layout showing all scholarships with edit/delete.
Bottom: Publish to Users + Auto Scrap buttons.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QMessageBox, QDialog, QLineEdit,
    QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QCursor
import os
import sys

from pyqt_app.styles.theme import FONT_FAMILY, palette
from controllers.admin_controller import get_all_beasiswa_admin, delete_beasiswa
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

        if not non_pt:
            QMessageBox.information(self, "Info", "All scholarships are already PT-level!")
            return

        r = QMessageBox.question(
            self, "Publish to Users",
            f"This will DELETE {len(non_pt)} non-perguruan-tinggi scholarships "
            f"(SMA, etc.) from the database.\n\n"
            f"Users will only see D3/D4/S1/S2/S3 scholarships.\n\n"
            f"Continue?"
        )
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
            QMessageBox.information(
                self, "Success",
                f"✅ Removed {deleted} non-PT scholarships.\n"
                f"Users will now see only perguruan tinggi scholarships."
            )
            self._rebuild()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed: {e}")

    def _start_scraping(self):
        self.scrap_btn.setEnabled(False)
        self.scrap_btn.setText("Scraping...")
        self.status_label.setText("⏳ Sedang mengambil data (Est. 10-15 menit). Mohon tunggu...")
        self.status_label.show()

        QMessageBox.information(
            self, "Info", 
            "Auto scraping started in the background.\nPlease check the terminal for detailed progress."
        )
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
        QMessageBox.information(
            self, "Success",
            "Auto scraping completed and database updated!\n\n"
            "Click 'Publish to Users' to remove non-PT scholarships\n"
            "so users only see D3/D4/S1/S2/S3 beasiswa."
        )
        self._rebuild()

    def _on_scrap_error(self, err):
        if hasattr(self, 'scrap_btn'):
            self.scrap_btn.setEnabled(True)
            self.scrap_btn.setText("🔄 Auto Scrap")
        if hasattr(self, 'status_label'):
            self.status_label.hide()
        QMessageBox.critical(self, "Error", f"Auto scraping failed:\n{err}")

    def _delete_beasiswa(self, bea_id):
        r = QMessageBox.question(
            self, "Delete",
            "Are you sure you want to delete this scholarship?")
        if r == QMessageBox.StandardButton.Yes:
            ok, msg = delete_beasiswa(bea_id)
            if ok:
                QMessageBox.information(self, "Success", msg)
                self._rebuild()
            else:
                QMessageBox.critical(self, "Error", msg)

    def _edit_beasiswa(self, bea: dict):
        """Open edit dialog for a scholarship."""
        c = palette(self._mode)
        dlg = QDialog(self)
        dlg.setWindowTitle("Edit Scholarship")
        dlg.setMinimumSize(560, 480)
        dl = QVBoxLayout(dlg)
        dl.setContentsMargins(28, 24, 28, 24)
        dl.setSpacing(8)

        title = QLabel("Edit Scholarship")
        title.setFont(QFont(FONT_FAMILY, 15, QFont.Weight.Bold))
        dl.addWidget(title)
        dl.addSpacing(4)

        fields = {}
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
                    background: {c['input_bg']};
                    border: none;
                    border-radius: 10px;
                }}
                QLineEdit:focus {{
                    border: 2px solid {c['btn_primary']};
                }}
            """)
            dl.addWidget(inp)
            fields[key] = inp

        dl.addStretch()

        save = QPushButton("Save Changes")
        save.setFixedHeight(40)
        save.setStyleSheet(f"""
            QPushButton {{
                background: {c['btn_primary']};
                color: {c['text_dark']};
                border: none; border-radius: 10px;
                font-weight: bold; font-size: 13px;
            }}
            QPushButton:hover {{ background: {c['btn_primary_hover']}; }}
        """)
        save.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        def do_save():
            try:
                conn = get_connection()
                updates = {k: e.text().strip() for k, e in fields.items()}
                set_clause = ", ".join(f"{k} = ?" for k in updates)
                vals = list(updates.values()) + [bea["id"]]
                conn.execute(
                    f"UPDATE beasiswa SET {set_clause} WHERE id = ?", vals)
                conn.commit()
                conn.close()
                QMessageBox.information(dlg, "Success", "Scholarship updated!")
                dlg.accept()
                self._rebuild()
            except Exception as e:
                QMessageBox.critical(dlg, "Error", str(e))

        save.clicked.connect(do_save)
        dl.addWidget(save)
        dlg.exec()

    # ── Rebuild ──────────────────────────────────────────────
    def _rebuild(self):
        """Replace _container with a fresh one."""
        old = self._container
        self._outer.removeWidget(old)
        old.deleteLater()

        self._container = QWidget()
        self._outer.addWidget(self._container)
        self._populate()
