"""
pyqt_app/views/profil_view.py
Profile page — left panel with completeness ring, right with personal info.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QLineEdit, QComboBox, QMessageBox,
    QFileDialog, QDialog, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor, QPixmap, QIcon
import os
import shutil

from pyqt_app.styles.theme import FONT_FAMILY, palette
from pyqt_app.widgets.progress_ring import ProgressRing
from pyqt_app.widgets.avatar_widget import AvatarWidget
from controllers.profil_controller import (
    tampil_profil, simpan_data_opsional, update_avatar
)
from utils import format_tanggal

ASSETS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets"))

TRANSLATIONS = {
    'id': {
        'not_found': 'Profil tidak ditemukan.',
        'guest': 'Pengguna Tamu',
        'edit_prof': 'Edit Profil',
        'prof_complete': 'Profil Lengkap',
        'comp_sug': 'Lengkapi profilmu untuk\nmendapat kecocokan beasiswa!',
        'personal_info': 'Informasi Pribadi',
        'email': 'Email',
        'tgl_lahir': 'Tanggal Lahir',
        'jk': 'Jenis Kelamin',
        'academic_info': 'Informasi Akademik',
        'jurusan': 'Jurusan',
        'kampus': 'Kampus',
        'jenjang': 'Jenjang',
        'semester': 'Semester',
        'ip': 'IP / IPK',
        'kip': 'Penerima KIP',
        'org': 'Aktif Organisasi',
        'income': 'Penghasilan Orang Tua',
        'yes': 'Ya',
        'no': 'Tidak',
        'not_filled': 'Belum diisi',
        'add_test': 'Skor Tes Tambahan',
        'jlpt': 'Level JLPT',
        'add_info': 'Informasi Tambahan',
        'income_rp': 'Penghasilan Ortu (Rp)',
        'income_ph': 'contoh: 5000000',
        'save_prof': 'Simpan Profil',
        'back_prof': '← Kembali ke Profil',
        'complete_prof': 'Lengkapi Profilmu',
        'change_ava': 'Ganti Foto Profil',
        'req_info': 'Informasi Wajib',
        'success': 'Sukses',
        'success_msg': 'Profil berhasil diperbarui!',
        'error': 'Gagal',
        'logout': 'Keluar',
        'logout_msg': 'Apakah Anda yakin ingin keluar?',
        'sel_ava': 'Pilih Avatar',
        'sel_def_ava': 'Pilih avatar bawaan:',
        'or_upload': 'Atau upload dari komputer:',
        'upload_file': 'Upload File Lokal',
        'confirm_ava': 'Apakah Anda yakin ingin mengganti avatar dengan pilihan ini?',
        'confirm': 'Konfirmasi',
        'sel_photo': 'Pilih Foto',
    },
    'en': {
        'not_found': 'Profile not found.',
        'guest': 'Guest User',
        'edit_prof': 'Edit Profile',
        'prof_complete': 'Profile Complete',
        'comp_sug': 'Complete your profile to\nget better scholarship matches!',
        'personal_info': 'Personal Information',
        'email': 'Email',
        'tgl_lahir': 'Date of Birth',
        'jk': 'Gender',
        'academic_info': 'Academic Information',
        'jurusan': 'Major',
        'kampus': 'University',
        'jenjang': 'Degree',
        'semester': 'Semester',
        'ip': 'GPA',
        'kip': 'KIP Recipient',
        'org': 'Active in Organization',
        'income': 'Parent Income',
        'yes': 'Yes',
        'no': 'No',
        'not_filled': 'Not filled',
        'add_test': 'Additional Test Scores',
        'jlpt': 'JLPT Level',
        'add_info': 'Additional Info',
        'income_rp': 'Parent Income (Rp)',
        'income_ph': 'e.g.: 5000000',
        'save_prof': 'Save Profile',
        'back_prof': '← Back to Profile',
        'complete_prof': 'Complete Your Profile',
        'change_ava': 'Change Profile Picture',
        'req_info': 'Required Information',
        'success': 'Success',
        'success_msg': 'Profile updated successfully!',
        'error': 'Error',
        'logout': 'Logout',
        'logout_msg': 'Are you sure you want to logout?',
        'sel_ava': 'Select Avatar',
        'sel_def_ava': 'Select default avatar:',
        'or_upload': 'Or upload from computer:',
        'upload_file': 'Upload Local File',
        'confirm_ava': 'Are you sure you want to change your avatar to this selection?',
        'confirm': 'Confirm',
        'sel_photo': 'Select Photo',
    }
}


def _hitung_completeness(p):
    """Compute profile completeness percentage."""
    if not p:
        return 0
    fields = ["nama","tanggal_lahir","email","jurusan","kampus",
              "jenjang","semester","ip","jenis_kelamin"]
    opt = ["skor_ielts","skor_toefl","skor_duolingo","skor_sat",
           "skor_act","skor_gre","skor_gmat","skor_hsk","level_jlpt"]
    total = len(fields) + len(opt)
    filled = sum(1 for f in fields if p.get(f))
    filled += sum(1 for f in opt if p.get(f) and p[f] != 0)
    return int((filled / total) * 100)


class ProfilView(QWidget):
    def __init__(self, profil_id, bhs="id", mode="light", parent=None):
        super().__init__(parent)
        self._pid = profil_id
        self._bhs = bhs
        self._mode = mode
        self._t = TRANSLATIONS.get(bhs, TRANSLATIONS['id'])
        self._build()

    def _clear(self):
        if self.layout():
            while self.layout().count():
                item = self.layout().takeAt(0)
                if item.widget(): item.widget().deleteLater()
        else:
            QHBoxLayout(self)

    def _apply_card_shadow(self, widget):
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        from PyQt6.QtGui import QColor
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(2)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 15))
        widget.setGraphicsEffect(shadow)

    def _build(self):
        self._clear()
        c = palette(self._mode)
        t = self._t
        lay = self.layout()
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)

        profil = tampil_profil(self._pid)
        if not profil:
            lay.addWidget(QLabel(t['not_found']))
            return
        completeness = _hitung_completeness(profil)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        sw = QWidget()
        sw.setStyleSheet("background: transparent;")
        sl = QVBoxLayout(sw)
        sl.setContentsMargins(0, 0, 0, 20)
        sl.setSpacing(16)

        # ── 1. Top Section (Two Cards) ──
        top_lay = QHBoxLayout()
        top_lay.setContentsMargins(0, 0, 0, 0)
        top_lay.setSpacing(16)

        bg_color = "#FFFFFF" if self._mode == "light" else c['card']

        # Left Card: Profile Info
        header_left = QFrame()
        header_left.setProperty("frameClass", "card")
        header_left.setObjectName("headerLeft")
        header_left.setStyleSheet(f"#headerLeft {{ background: {bg_color}; border-radius: 14px; border: 1px solid {c['border']}; }}")
        self._apply_card_shadow(header_left)
        hl = QHBoxLayout(header_left)
        hl.setContentsMargins(24, 24, 24, 24)
        hl.setSpacing(20)

        # Left Card - Avatar
        ava_path = profil.get("avatar")
        if not ava_path:
            ava_path = os.path.join(ASSETS_DIR, "default_avatar.png")
            
        avatar_w = AvatarWidget(80)
        if ava_path and os.path.exists(ava_path):
            avatar_w.set_avatar(QPixmap(ava_path))
        hl.addWidget(avatar_w)
        
        # Left Card - Info & Button
        info_lay = QVBoxLayout()
        info_lay.setContentsMargins(0, 0, 0, 0)
        info_lay.setSpacing(4)
        info_lay.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        name_lbl = self._bold(profil.get("nama", t['guest']), 18)
        info_lay.addWidget(name_lbl)
        
        desc_text = f"{profil.get('jurusan', t['jurusan'])} • {profil.get('kampus', t['kampus'])}"
        desc_lbl = QLabel(desc_text)
        desc_lbl.setStyleSheet(f"color: {c['text_muted']}; font-size: 13px;")
        info_lay.addWidget(desc_lbl)
        
        info_lay.addSpacing(6)
        eb = QPushButton(t['edit_prof'])
        eb.setFixedWidth(120)
        eb.setFixedHeight(30)
        eb.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        eb.setStyleSheet(f"background: {c['btn_primary']}; color: {c['text_dark']}; font-weight: bold; border: none; border-radius: 6px; padding: 4px 12px; font-size: 11px;")
        eb.clicked.connect(self._show_edit)
        info_lay.addWidget(eb)
        
        hl.addLayout(info_lay)
        hl.addStretch()
        top_lay.addWidget(header_left, stretch=5)

        # Right Card: Completeness
        header_right = QFrame()
        header_right.setProperty("frameClass", "card")
        header_right.setObjectName("headerRight")
        header_right.setStyleSheet(f"#headerRight {{ background: {bg_color}; border-radius: 14px; border: 1px solid {c['border']}; }}")
        self._apply_card_shadow(header_right)
        hr = QHBoxLayout(header_right)
        hr.setContentsMargins(20, 20, 20, 20)
        hr.setSpacing(16)
        hr.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        ring = ProgressRing(completeness, 70, 6)
        ring_color = c['btn_primary'] if completeness >= 80 else c['text_accent']
        ring.set_colors("#DFE6E1", ring_color, c['text_dark'])
        hr.addWidget(ring)
        
        text_lay = QVBoxLayout()
        text_lay.setSpacing(4)
        text_lay.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        comp_lbl = self._bold(t['prof_complete'], 12)
        text_lay.addWidget(comp_lbl, alignment=Qt.AlignmentFlag.AlignLeft)
        
        comp_sug = QLabel(t['comp_sug'])
        comp_sug.setStyleSheet(f"color: {c['text_muted']}; font-size: 10px;")
        comp_sug.setAlignment(Qt.AlignmentFlag.AlignLeft)
        text_lay.addWidget(comp_sug, alignment=Qt.AlignmentFlag.AlignLeft)
        
        hr.addLayout(text_lay)
        hr.addStretch()
        
        top_lay.addWidget(header_right, stretch=2)
        sl.addLayout(top_lay)

        # ── 3. Info Cards ──
        # Card 1: Basic Info
        b_card = QFrame()
        b_card.setProperty("frameClass", "card")
        b_card.setObjectName("bCard")
        b_card.setStyleSheet(f"#bCard {{ background: {bg_color}; border-radius: 14px; border: 1px solid {c['border']}; }}")
        self._apply_card_shadow(b_card)
        b_lay = QVBoxLayout(b_card)
        b_lay.setContentsMargins(24, 20, 24, 20)
        b_lay.setSpacing(12)
        b_lay.addWidget(self._bold(t['personal_info'], 15))
        b_lay.addSpacing(8)
        
        for label, val in [(t['email'], profil.get("email")),
                           (t['tgl_lahir'], format_tanggal(profil.get("tanggal_lahir"))),
                           (t['jk'], profil.get("jenis_kelamin",""))]:
            self._info_row(b_lay, label, val, c)
        sl.addWidget(b_card)
        
        # Card 2: Academic Info
        a_card = QFrame()
        a_card.setProperty("frameClass", "card")
        a_card.setObjectName("aCard")
        a_card.setStyleSheet(f"#aCard {{ background: {bg_color}; border-radius: 14px; border: 1px solid {c['border']}; }}")
        self._apply_card_shadow(a_card)
        a_lay = QVBoxLayout(a_card)
        a_lay.setContentsMargins(24, 20, 24, 20)
        a_lay.setSpacing(12)
        a_lay.addWidget(self._bold(t['academic_info'], 15))
        a_lay.addSpacing(8)
        
        for label, val in [(t['jurusan'], profil.get("jurusan")),
                           (t['kampus'], profil.get("kampus")),
                           (t['jenjang'], profil.get("jenjang")),
                           (t['semester'], profil.get("semester")),
                           (t['ip'], f"{profil.get('ip', 0):.2f}"),
                           (t['kip'], t['yes'] if profil.get("status_kip") else t['no']),
                           (t['org'], t['yes'] if profil.get("aktif_organisasi") else t['no']),
                           (t['income'], f"Rp {profil.get('penghasilan_ortu', 0):,.0f}".replace(',', '.') if profil.get('penghasilan_ortu') else t['not_filled'])]:
            self._info_row(a_lay, label, val, c)
        sl.addWidget(a_card)

        # Card 3: Optional Test Scores
        has_optional = any(profil.get(k) for k in ["skor_ielts","skor_toefl","skor_duolingo","skor_sat","skor_act","skor_gre","skor_gmat","skor_hsk","level_jlpt"])
        if has_optional:
            o_card = QFrame()
            o_card.setProperty("frameClass", "card")
            o_card.setObjectName("oCard")
            o_card.setStyleSheet(f"#oCard {{ background: {bg_color}; border-radius: 14px; border: 1px solid {c['border']}; }}")
            self._apply_card_shadow(o_card)
            o_lay = QVBoxLayout(o_card)
            o_lay.setContentsMargins(24, 20, 24, 20)
            o_lay.setSpacing(12)
            o_lay.addWidget(self._bold(t['add_test'], 15))
            o_lay.addSpacing(8)
            
            for label, key in [("IELTS","skor_ielts"),("TOEFL iBT","skor_toefl"),
                              ("Duolingo","skor_duolingo"),("SAT","skor_sat"),
                              ("ACT","skor_act"),("GRE","skor_gre"),
                              ("GMAT","skor_gmat"),("HSK","skor_hsk"),("JLPT","level_jlpt")]:
                val = profil.get(key)
                if val and val != 0 and str(val).strip() != "":
                    self._info_row(o_lay, label, val, c)
            sl.addWidget(o_card)

        sl.addStretch()
        scroll.setWidget(sw)
        lay.addWidget(scroll)

    def _info_row(self, lay, label, val, c, muted=False):
        t = self._t
        r = QFrame()
        rl = QHBoxLayout(r)
        rl.setContentsMargins(0, 0, 0, 0)
        l = QLabel(label)
        l.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Bold))
        l.setFixedWidth(140)
        rl.addWidget(l)
        v = QLabel(str(val) if val else t['not_filled'])
        v.setStyleSheet(f"color: {c['text_muted'] if muted else c['text_dark']}; font-size: 12px;")
        rl.addWidget(v)
        rl.addStretch()
        lay.addWidget(r)

    def _bold(self, text, size):
        l = QLabel(text)
        l.setFont(QFont(FONT_FAMILY, size, QFont.Weight.Bold))
        return l

    def _show_edit(self):
        self._clear()
        c = palette(self._mode)
        t = self._t
        lay = self.layout()
        lay.setContentsMargins(0, 0, 0, 0)

        # Convert to vertical for the edit form
        wrapper = QWidget()
        wl = QVBoxLayout(wrapper)
        wl.setContentsMargins(0, 0, 0, 0)

        top_btn_lay = QHBoxLayout()
        top_btn_lay.setContentsMargins(0, 0, 0, 0)
        
        back = QPushButton(t['back_prof'])
        back.setStyleSheet(f"background: {c['card']}; color: {c['text_dark']}; border: 1px solid {c['border']}; border-radius: 8px; padding: 8px 16px; font-weight: bold;")
        back.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        back.clicked.connect(self._build)
        
        top_btn_lay.addWidget(back)
        top_btn_lay.addStretch()
        wl.addLayout(top_btn_lay)
        wl.addWidget(self._bold(t['complete_prof'], 17))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        sw = QWidget()
        sl = QVBoxLayout(sw)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.setSpacing(12)

        profil = tampil_profil(self._pid)

        # Avatar Section in Edit Mode
        ava_top_l = QVBoxLayout()
        ava_top_l.setSpacing(12)
        
        self.avatar_w = AvatarWidget(120)
        ava_path = profil.get("avatar")
        if not ava_path:
            ava_path = os.path.join(ASSETS_DIR, "default_avatar.png")
            
        if ava_path and os.path.exists(ava_path):
            self.avatar_w.set_avatar(QPixmap(ava_path))
            
        ava_top_l.addWidget(self.avatar_w, alignment=Qt.AlignmentFlag.AlignCenter)
        
        btn_ava = QPushButton(t['change_ava'])
        btn_ava.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_ava.setStyleSheet(f"background: {c['btn_primary']}; color: {c['text_dark']}; font-weight: bold; border: none; border-radius: 8px; padding: 6px 12px; font-size: 11px;")
        btn_ava.clicked.connect(self._change_avatar)
        ava_top_l.addWidget(btn_ava, alignment=Qt.AlignmentFlag.AlignCenter)
        sl.addLayout(ava_top_l)
        sl.addSpacing(10)

        # Required Fields
        self._req_entries = {}
        sl.addWidget(self._bold(t['req_info'], 13))
        req_fields = [
            ("nama", t['guest'] if not profil.get("nama") else profil.get("nama", ""), profil.get("nama", "")),
            ("tanggal_lahir", t['tgl_lahir'], profil.get("tanggal_lahir", "")),
            ("email", t['email'], profil.get("email", "")),
            ("jurusan", t['jurusan'], profil.get("jurusan", "")),
            ("kampus", t['kampus'], profil.get("kampus", "")),
            ("jenjang", t['jenjang'], profil.get("jenjang", "")),
            ("semester", t['semester'], str(profil.get("semester", ""))),
            ("ip", t['ip'], str(profil.get("ip", ""))),
            ("jenis_kelamin", t['jk'], profil.get("jenis_kelamin", "")),
        ]
        # Wait, the second element is the label. 
        req_fields_actual = [
            ("nama", "Nama" if self._bhs == "id" else "Name", profil.get("nama", "")),
            ("tanggal_lahir", t['tgl_lahir'], profil.get("tanggal_lahir", "")),
            ("email", t['email'], profil.get("email", "")),
            ("jurusan", t['jurusan'], profil.get("jurusan", "")),
            ("kampus", t['kampus'], profil.get("kampus", "")),
            ("jenjang", t['jenjang'], profil.get("jenjang", "")),
            ("semester", t['semester'], str(profil.get("semester", ""))),
            ("ip", t['ip'], str(profil.get("ip", ""))),
            ("jenis_kelamin", t['jk'], profil.get("jenis_kelamin", "")),
        ]
        
        for key, label, current in req_fields_actual:
            card = QFrame()
            card.setProperty("frameClass", "card")
            cl = QHBoxLayout(card)
            cl.setContentsMargins(16, 10, 16, 10)
            cl.addWidget(self._bold(label, 11))
            e = QLineEdit()
            e.setFixedWidth(200)
            e.setMinimumHeight(46)
            e.setText(current)
            cl.addWidget(e)
            self._req_entries[key] = e
            sl.addWidget(card)

        sl.addSpacing(16)
        sl.addWidget(self._bold(t['add_test'], 13))

        self._opt_entries = {}
        for key, label, current in [
            ("skor_ielts","IELTS Score (0.0-9.0)", profil.get("skor_ielts")),
            ("skor_toefl","TOEFL iBT (0-120)", profil.get("skor_toefl")),
            ("skor_duolingo","Duolingo (10-160)", profil.get("skor_duolingo")),
            ("skor_sat","SAT (400-1600)", profil.get("skor_sat")),
            ("skor_act","ACT (1-36)", profil.get("skor_act")),
            ("skor_gre","GRE (260-340)", profil.get("skor_gre")),
            ("skor_gmat","GMAT (200-800)", profil.get("skor_gmat")),
            ("skor_hsk","HSK (1-6)", profil.get("skor_hsk")),
        ]:
            card = QFrame()
            card.setProperty("frameClass", "card")
            cl = QHBoxLayout(card)
            cl.setContentsMargins(16, 10, 16, 10)
            cl.addWidget(self._bold(label, 11))
            e = QLineEdit()
            e.setFixedWidth(200)
            e.setMinimumHeight(46)
            if current and current != 0:
                e.setText(str(current))
            cl.addWidget(e)
            self._opt_entries[key] = e
            sl.addWidget(card)

        # JLPT
        card = QFrame()
        card.setProperty("frameClass", "card")
        cl = QHBoxLayout(card)
        cl.setContentsMargins(16, 10, 16, 10)
        cl.addWidget(self._bold(t['jlpt'], 11))
        self._jlpt_cb = QComboBox()
        self._jlpt_cb.addItems(["", "N1", "N2", "N3", "N4", "N5"])
        self._jlpt_cb.setCurrentText(profil.get("level_jlpt", "") or "")
        self._jlpt_cb.setFixedWidth(200)
        cl.addWidget(self._jlpt_cb)
        sl.addWidget(card)

        # ── Additional Info: KIP, Organisasi, Penghasilan ──
        sl.addSpacing(16)
        sl.addWidget(self._bold(t['add_info'], 13))

        # Status KIP
        card_kip = QFrame()
        card_kip.setProperty("frameClass", "card")
        cl_kip = QHBoxLayout(card_kip)
        cl_kip.setContentsMargins(16, 10, 16, 10)
        cl_kip.addWidget(self._bold(t['kip'], 11))
        self._kip_cb = QComboBox()
        self._kip_cb.addItems([t['no'], t['yes']])
        self._kip_cb.setCurrentIndex(1 if profil.get("status_kip") else 0)
        self._kip_cb.setFixedWidth(200)
        cl_kip.addWidget(self._kip_cb)
        sl.addWidget(card_kip)

        # Aktif Organisasi
        card_org = QFrame()
        card_org.setProperty("frameClass", "card")
        cl_org = QHBoxLayout(card_org)
        cl_org.setContentsMargins(16, 10, 16, 10)
        cl_org.addWidget(self._bold(t['org'], 11))
        self._org_cb = QComboBox()
        self._org_cb.addItems([t['no'], t['yes']])
        self._org_cb.setCurrentIndex(1 if profil.get("aktif_organisasi") else 0)
        self._org_cb.setFixedWidth(200)
        cl_org.addWidget(self._org_cb)
        sl.addWidget(card_org)

        # Penghasilan Orang Tua
        card_peng = QFrame()
        card_peng.setProperty("frameClass", "card")
        cl_peng = QHBoxLayout(card_peng)
        cl_peng.setContentsMargins(16, 10, 16, 10)
        cl_peng.addWidget(self._bold(t['income_rp'], 11))
        self._peng_entry = QLineEdit()
        self._peng_entry.setFixedWidth(200)
        self._peng_entry.setMinimumHeight(46)
        self._peng_entry.setPlaceholderText(t['income_ph'])
        peng_val = profil.get("penghasilan_ortu", 0)
        if peng_val and peng_val > 0:
            self._peng_entry.setText(str(peng_val))
        cl_peng.addWidget(self._peng_entry)
        sl.addWidget(card_peng)

        sl.addStretch()
        scroll.setWidget(sw)
        wl.addWidget(scroll)

        save = QPushButton(t['save_prof'])
        save.setObjectName("btn_primary")
        save.setFixedHeight(40)
        save.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        save.clicked.connect(self._save_all)
        wl.addWidget(save)
        lay.addWidget(wrapper)

    def _save_all(self):
        t = self._t
        from controllers.profil_controller import simpan_edit_profil
        data_baru = {"id_profil": self._pid}
        
        # Required fields
        for key, entry in self._req_entries.items():
            val = entry.text().strip()
            data_baru[key] = val
            
        # Add KIP, organisasi, penghasilan from the new combo/entry fields
        profil = tampil_profil(self._pid)
        data_baru["status_kip"] = 1 if self._kip_cb.currentIndex() == 1 else 0
        data_baru["aktif_organisasi"] = 1 if self._org_cb.currentIndex() == 1 else 0
        peng_text = self._peng_entry.text().strip()
        try:
            data_baru["penghasilan_ortu"] = int(peng_text) if peng_text else 0
        except ValueError:
            data_baru["penghasilan_ortu"] = 0

        # Optional fields
        for key, entry in self._opt_entries.items():
            val = entry.text().strip()
            if val:
                try:
                    data_baru[key] = float(val) if key in ("skor_ielts", "ip") else int(val)
                except ValueError:
                    data_baru[key] = None
            else:
                data_baru[key] = None
                
        jlpt = self._jlpt_cb.currentText().strip()
        data_baru["level_jlpt"] = jlpt if jlpt else None
        
        ok, msg = simpan_edit_profil(data_baru)
        
        c = palette(self._mode)
        msg_box = QMessageBox(self)
        msg_box.setStyleSheet(f"QMessageBox {{ background-color: {c['card']}; }} QLabel {{ color: {c['text_dark']}; font-weight: bold; }} QPushButton {{ background-color: {c['btn_primary']}; color: {c['text_dark']}; padding: 6px 16px; border-radius: 6px; font-weight: bold; border: none; }}")
        
        if ok:
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle(t['success'])
            msg_box.setText(t['success_msg'])
            msg_box.exec()
            self._refresh_topbar()
            self._build()
        else:
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle(t['error'])
            msg_box.setText(msg)
            msg_box.exec()

    def _refresh_topbar(self):
        top = self.window()
        if hasattr(top, '_build_main_layout'):
            top._build_main_layout()
            top._root_stack.setCurrentWidget(top._main_widget)
            top._navigate("profil")

    def _logout(self):
        c = palette(self._mode)
        t = self._t
        reply = QMessageBox(self)
        reply.setWindowTitle(t['logout'])
        reply.setText(t['logout_msg'])
        reply.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        reply.setStyleSheet(f"QMessageBox {{ background-color: {c['card']}; }} QLabel {{ color: {c['text_dark']}; font-weight: bold; }} QPushButton {{ background-color: {c['btn_primary']}; color: {c['text_dark']}; padding: 6px 16px; border-radius: 6px; font-weight: bold; border: none; }}")
        
        res = reply.exec()
        if res == QMessageBox.StandardButton.Yes:
            top = self.window()
            if hasattr(top, '_go_logout'):
                top._go_logout()

    def _change_avatar(self):
        c = palette(self._mode)
        t = self._t
        dlg = QDialog(self)
        dlg.setWindowTitle(t['sel_ava'])
        dlg.setFixedSize(360, 360)
        dlg.setStyleSheet(f"background-color: {c['card']};")
        dl = QVBoxLayout(dlg)
        
        lbl = QLabel(t['sel_def_ava'])
        lbl.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {c['text_dark']}; background: transparent;")
        dl.addWidget(lbl)
        
        grid = QGridLayout()
        grid.setSpacing(10)
        avatars = ["cat.png", "dog.png", "bear.png", "fox.png"]
        
        AVATARS_DIR = os.path.join(ASSETS_DIR, "avatars")
        
        for i, a in enumerate(avatars):
            p = os.path.join(AVATARS_DIR, a)
            btn = QPushButton()
            btn.setFixedSize(64, 64)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            if os.path.exists(p):
                px = QPixmap(p).scaled(64, 64, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                btn.setStyleSheet(f"background: transparent; border-radius: 32px; border: 2px solid {c['border']};")
                btn.setIcon(QIcon(px))
                btn.setIconSize(btn.size())
            btn.clicked.connect(lambda _, path=p: self._select_avatar(path, dlg))
            grid.addWidget(btn, i // 4, i % 4)
            
        dl.addLayout(grid)
        dl.addSpacing(10)
        
        lbl2 = QLabel(t['or_upload'])
        lbl2.setFont(QFont(FONT_FAMILY, 10))
        lbl2.setStyleSheet(f"color: {c['text_dark']}; background: transparent;")
        dl.addWidget(lbl2)
        btn_up = QPushButton(t['upload_file'])
        btn_up.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_up.setStyleSheet(f"background: {c['btn_primary']}; color: {c['text_dark']}; font-weight: bold; border: none; border-radius: 12px; padding: 10px;")
        btn_up.clicked.connect(lambda: self._upload_avatar(dlg))
        dl.addWidget(btn_up)
        dl.addStretch()
        
        dlg.exec()

    def _select_avatar(self, path, dlg):
        t = self._t
        msg = t['confirm_ava']
        title = t['confirm']
        
        c = palette(self._mode)
        reply = QMessageBox(self)
        reply.setWindowTitle(title)
        reply.setText(msg)
        reply.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        reply.setStyleSheet(f"QMessageBox {{ background-color: {c['card']}; }} QLabel {{ color: {c['text_dark']}; font-weight: bold; }} QPushButton {{ background-color: {c['btn_primary']}; color: {c['text_dark']}; padding: 6px 16px; border-radius: 6px; font-weight: bold; border: none; }}")
        
        res = reply.exec()
        if res == QMessageBox.StandardButton.Yes:
            update_avatar(self._pid, path)
            dlg.accept()
            self._refresh_topbar()
            self._build()

    def _upload_avatar(self, dlg):
        path, _ = QFileDialog.getOpenFileName(self, self._t['sel_photo'], "", "Images (*.png *.jpg *.jpeg)")
        if path:
            AVATARS_DIR = os.path.join(ASSETS_DIR, "avatars")
            dest = os.path.join(AVATARS_DIR, f"user_{self._pid}_{os.path.basename(path)}")
            shutil.copy(path, dest)
            update_avatar(self._pid, dest)
            dlg.accept()
            self._refresh_topbar()
            self._build()

