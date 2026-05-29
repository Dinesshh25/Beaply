"""
pyqt_app/views/admin_scholarship_view.py
Admin — Scholarship Data management page.

Two-column layout: Current Data (left) and Incoming Data (right).
Each scholarship shown as a text card with edit/delete buttons.
Bottom: Save Changes + Auto Scrap buttons.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QMessageBox, QDialog, QLineEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
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
            
            from run_all_scraping import jalankan_semua
            jalankan_semua(auto_sync=True)
            self.finished_signal.emit()
        except Exception as e:
            self.error_signal.emit(str(e))


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
        lay.setSpacing(16)

        # ── Two columns ──────────────────────────────────────
        cols = QHBoxLayout()
        cols.setSpacing(20)

        # ── Left: Current Data ───────────────────────────────
        left_frame = QFrame()
        left_lay = QVBoxLayout(left_frame)
        left_lay.setContentsMargins(0, 0, 0, 0)
        left_lay.setSpacing(8)

        left_title = QLabel("Current Data")
        left_title.setFont(QFont(FONT_FAMILY, 16, QFont.Weight.Bold))
        left_lay.addWidget(left_title)

        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        left_scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }")
        lsw = QWidget()
        ll = QVBoxLayout(lsw)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(6)

        beasiswa_list = get_all_beasiswa_admin()
        for bea in beasiswa_list:
            ll.addWidget(self._make_card(bea, c, is_current=True))
        ll.addStretch()
        left_scroll.setWidget(lsw)
        left_lay.addWidget(left_scroll)
        cols.addWidget(left_frame, 1)

        # ── Right: Incoming Data ─────────────────────────────
        right_frame = QFrame()
        right_lay = QVBoxLayout(right_frame)
        right_lay.setContentsMargins(0, 0, 0, 0)
        right_lay.setSpacing(8)

        right_title = QLabel("Incoming Data")
        right_title.setFont(QFont(FONT_FAMILY, 16, QFont.Weight.Bold))
        right_lay.addWidget(right_title)

        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        right_scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }")
        rsw = QWidget()
        rl = QVBoxLayout(rsw)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(6)

        for bea in beasiswa_list:
            rl.addWidget(self._make_card(bea, c, is_current=False))
        rl.addStretch()
        right_scroll.setWidget(rsw)
        right_lay.addWidget(right_scroll)
        cols.addWidget(right_frame, 1)

        lay.addLayout(cols, 1)

        # ── Bottom buttons ───────────────────────────────────
        btn_row = QHBoxLayout()
        
        self.status_label = QLabel("")
        self.status_label.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Bold))
        self.status_label.setStyleSheet(f"color: {c['text_muted']}; font-style: italic;")
        self.status_label.hide()
        btn_row.addWidget(self.status_label)
        
        btn_row.addStretch()

        save_btn = QPushButton("Save  Changes")
        save_btn.setFixedHeight(40)
        save_btn.setFixedWidth(160)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {c['card']};
                color: {c['text_dark']};
                border: 1px solid {c['border']};
                border-radius: 10px;
                font-weight: bold; font-size: 13px;
            }}
            QPushButton:hover {{ background: {c['btn_pale']}; }}
        """)
        save_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        save_btn.clicked.connect(
            lambda: QMessageBox.information(self, "Info", "Changes saved!"))
        btn_row.addWidget(save_btn)

        self.scrap_btn = QPushButton("Auto Scrap")
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
    def _make_card(self, bea: dict, c: dict, is_current: bool) -> QFrame:
        border_color = "#D6EAD8" if is_current else "#E8DDD4"
        bg_color = "#F5FAF6" if is_current else "#FBF7F4"

        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {bg_color};
                border: 1.5px solid {border_color};
                border-radius: 12px;
            }}
        """)
        card.setFixedHeight(72)

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
        o = QLabel(bea.get("penyelenggara", ""))
        o.setStyleSheet(
            f"color: {c['text_muted']}; font-size: 10px;"
            " border: none; background: transparent;")
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
        bea_id = bea.get("id")
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
        del_btn.clicked.connect(lambda _, bid=bea_id: self._delete_beasiswa(bid))
        bc.addWidget(del_btn)

        lay.addLayout(bc)
        return card

    # ── Actions ──────────────────────────────────────────────
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
            self.scrap_btn.setText("Auto Scrap")
        if hasattr(self, 'status_label'):
            self.status_label.hide()
        QMessageBox.information(self, "Success", "Auto scraping completed and database updated successfully!")
        self._rebuild()

    def _on_scrap_error(self, err):
        if hasattr(self, 'scrap_btn'):
            self.scrap_btn.setEnabled(True)
            self.scrap_btn.setText("Auto Scrap")
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
