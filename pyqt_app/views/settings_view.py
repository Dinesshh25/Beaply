"""
pyqt_app/views/settings_view.py
Settings page — account, display, notifications, delete account.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QScrollArea, QLineEdit, QComboBox,
    QDialog, QMessageBox, QButtonGroup
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor

from pyqt_app.styles.theme import FONT_FAMILY, palette
from controllers.profil_controller import (
    ambil_preferensi, simpan_preferensi, hapus_akun, tampil_profil,
)

TRANSLATIONS = {
    'id': {
        'subtitle': 'Kelola preferensi dan keamanan akun Anda',
        'acct_sec': 'Akun & Keamanan',
        'change_pw': 'Ubah Kata Sandi',
        'change_pw_desc': 'Ubah kata sandi untuk menjaga keamanan akun',
        'email_verif': 'Verifikasi Email',
        'verified_email': 'Email terverifikasi: ',
        'verified': 'Terverifikasi',
        'logout_title': 'Keluar',
        'logout_desc': 'Keluar dari akun Anda',
        'display': 'Tampilan',
        'theme': 'Tema',
        'theme_desc': 'Pilih tema aplikasi',
        'light': 'Light',
        'dark': 'Dark',
        'language': 'Bahasa',
        'lang_desc': 'Pilih bahasa antarmuka',
        'text_size': 'Ukuran Teks',
        'text_size_desc': 'Pilih ukuran teks',
        'small': 'Kecil',
        'medium': 'Sedang',
        'large': 'Besar',
        'notification': 'Notifikasi',
        'push_notif': 'Notifikasi Push',
        'delete_acct': 'Hapus Akun',
        'del_confirm_title': 'Hapus Akun',
        'del_confirm_msg': 'Apakah Anda yakin? Tindakan ini tidak dapat dibatalkan.',
        'info': 'Info',
        'text_size_msg': 'Perubahan ukuran teks akan diterapkan setelah aplikasi dimuat ulang.',
        'done': 'Selesai',
        'acct_deleted': 'Akun dihapus.',
        'error': 'Kesalahan',
        'logout_confirm_msg': 'Apakah Anda yakin ingin keluar?',
        'curr_pw': 'Kata Sandi Saat Ini',
        'new_pw': 'Kata Sandi Baru',
        'conf_new_pw': 'Konfirmasi Kata Sandi Baru',
        'err_req': 'Semua kolom wajib diisi!',
        'err_match': 'Kata sandi tidak cocok!',
        'succ_pw': 'Kata sandi berhasil diubah!',
        'success': 'Sukses',
    },
    'en': {
        'subtitle': 'Manage your account preferences and security',
        'acct_sec': 'Account & Security',
        'change_pw': 'Change Password',
        'change_pw_desc': 'Change password to keep account secure',
        'email_verif': 'Email Verification',
        'verified_email': 'Verified email: ',
        'verified': 'Verified',
        'logout_title': 'Logout',
        'logout_desc': 'Sign out of your account',
        'display': 'Display',
        'theme': 'Theme',
        'theme_desc': 'Select application theme',
        'light': 'Light',
        'dark': 'Dark',
        'language': 'Language',
        'lang_desc': 'Select interface language',
        'text_size': 'Text Size',
        'text_size_desc': 'Select text size',
        'small': 'Small',
        'medium': 'Medium',
        'large': 'Large',
        'notification': 'Notification',
        'push_notif': 'Push notifications',
        'delete_acct': 'Delete Account',
        'del_confirm_title': 'Delete Account',
        'del_confirm_msg': "Are you sure? This can't be undone.",
        'info': 'Info',
        'text_size_msg': 'Text size changes will apply after restart.',
        'done': 'Done',
        'acct_deleted': 'Account deleted.',
        'error': 'Error',
        'logout_confirm_msg': 'Are you sure you want to logout?',
        'curr_pw': 'Current Password',
        'new_pw': 'New Password',
        'conf_new_pw': 'Confirm New Password',
        'err_req': 'All fields required!',
        'err_match': "Passwords don't match!",
        'succ_pw': 'Password changed!',
        'success': 'Success',
    }
}


class SettingsView(QWidget):
    def __init__(self, profil_id, bhs="id", mode="light", refresh_cb=None, parent=None):
        super().__init__(parent)
        self._pid = profil_id
        self._bhs = bhs
        self._mode = mode
        self._t = TRANSLATIONS.get(bhs, TRANSLATIONS['id'])
        self._refresh_cb = refresh_cb
        self._refreshing = False   # guard against re-entrant signals during rebuild
        self._build()

    def _build(self):
        c = palette(self._mode)
        t = self._t
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        sw = QWidget()
        sl = QVBoxLayout(sw)
        sl.setContentsMargins(0, 0, 0, 0)
        sl.setSpacing(12)

        sub = QLabel(t['subtitle'])
        sub.setObjectName("subtitle")
        sl.addWidget(sub)

        # ── Account & Security ───────────────────────────────
        sl.addWidget(self._section(t['acct_sec']))
        sec = QFrame()
        sec.setProperty("frameClass", "card")
        secl = QVBoxLayout(sec)
        secl.setContentsMargins(20, 14, 20, 14)

        pw_row = QFrame()
        pwl = QHBoxLayout(pw_row)
        pwl.setContentsMargins(0,0,0,0)
        pw_left = QFrame()
        pwll = QVBoxLayout(pw_left)
        pwll.setContentsMargins(0,0,0,0)
        pwll.setSpacing(0)
        pwll.addWidget(self._bold(t['change_pw'], 12))
        pwll.addWidget(self._muted(t['change_pw_desc']))
        pwl.addWidget(pw_left)
        pwl.addStretch()
        pwb = QPushButton(">")
        pwb.setFixedSize(32, 32)
        pwb.setStyleSheet(f"background: transparent; border: none; color: {c['text_dark']}; font-size: 16px;")
        pwb.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        pwb.clicked.connect(self._change_pw)
        pwl.addWidget(pwb)
        secl.addWidget(pw_row)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background: {c['border']};")
        secl.addWidget(sep)

        profil = tampil_profil(self._pid) or {}
        em_row = QFrame()
        eml = QHBoxLayout(em_row)
        eml.setContentsMargins(0,0,0,0)
        em_left = QFrame()
        emll = QVBoxLayout(em_left)
        emll.setContentsMargins(0,0,0,0)
        emll.setSpacing(0)
        emll.addWidget(self._bold(t['email_verif'], 12))
        emll.addWidget(self._muted(f"{t['verified_email']}{profil.get('email', 'N/A')}"))
        eml.addWidget(em_left)
        eml.addStretch()
        vb = QLabel(t['verified'])
        vb.setStyleSheet(f"background: {c['btn_primary']}; color: {c['text_dark']}; border-radius: 8px; padding: 4px 12px; font-size: 10px; font-weight: bold;")
        eml.addWidget(vb)
        secl.addWidget(em_row)

        secl.addWidget(self._sep(c))
        lo_row = QFrame()
        lol = QHBoxLayout(lo_row)
        lol.setContentsMargins(0,0,0,0)
        lol_left = QFrame()
        loll = QVBoxLayout(lol_left)
        loll.setContentsMargins(0,0,0,0)
        loll.setSpacing(0)
        loll.addWidget(self._bold(t['logout_title'], 12))
        loll.addWidget(self._muted(t['logout_desc']))
        lol.addWidget(lol_left)
        lol.addStretch()
        lob = QPushButton(t['logout_title'])
        lob.setStyleSheet(f"background: #F6D6D0; color: {c['danger']}; border: none; border-radius: 8px; padding: 6px 16px; font-size: 11px; font-weight: bold;")
        lob.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        lob.clicked.connect(self._logout)
        lol.addWidget(lob)
        secl.addWidget(lo_row)

        sl.addWidget(sec)

        # ── Display ──────────────────────────────────────────
        sl.addWidget(self._section(t['display']))
        pref = ambil_preferensi(self._pid)
        disp = QFrame()
        disp.setProperty("frameClass", "card")
        displ = QVBoxLayout(disp)
        displ.setContentsMargins(20, 12, 20, 12)

        # Theme
        th_row = QFrame()
        thl = QHBoxLayout(th_row)
        thl.setContentsMargins(0,0,0,0)
        thl_left = QFrame()
        thll = QVBoxLayout(thl_left)
        thll.setContentsMargins(0,0,0,0)
        thll.setSpacing(0)
        thll.addWidget(self._bold(t['theme'], 12))
        thll.addWidget(self._muted(t['theme_desc']))
        thl.addWidget(thl_left)
        thl.addStretch()
        theme_grp = QFrame()
        tgl = QHBoxLayout(theme_grp)
        tgl.setContentsMargins(0,0,0,0)
        tgl.setSpacing(4)
        for label, val in [(t['light'], "light"), (t['dark'], "dark")]:
            active = pref.get("tema", "light") == val
            b = QPushButton(label)
            bg = c['btn_primary'] if active else c['btn_pale']
            b.setStyleSheet(f"background: {bg}; border: none; border-radius: 8px; padding: 6px 16px; font-size: 11px; font-weight: {'bold' if active else 'normal'};")
            b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            b.clicked.connect(lambda _, v=val: self._set_theme(v))
            tgl.addWidget(b)
        thl.addWidget(theme_grp)
        displ.addWidget(th_row)

        displ.addWidget(self._sep(c))

        # Language
        ln_row = QFrame()
        lnl = QHBoxLayout(ln_row)
        lnl.setContentsMargins(0,0,0,0)
        lnl_left = QFrame()
        lnll = QVBoxLayout(lnl_left)
        lnll.setContentsMargins(0,0,0,0)
        lnll.setSpacing(0)
        lnll.addWidget(self._bold(t['language'], 12))
        lnll.addWidget(self._muted(t['lang_desc']))
        lnl.addWidget(lnl_left)
        lnl.addStretch()
        self._lang_cb = QComboBox()
        self._lang_cb.addItems(["Bahasa Indonesia", "English"])
        self._lang_cb.setCurrentText("Bahasa Indonesia" if pref.get("bahasa") == "id" else "English")
        self._lang_cb.setFixedWidth(160)
        self._lang_cb.currentTextChanged.connect(self._set_lang)
        lnl.addWidget(self._lang_cb)
        displ.addWidget(ln_row)

        displ.addWidget(self._sep(c))

        # Text size
        ts_row = QFrame()
        tsl = QHBoxLayout(ts_row)
        tsl.setContentsMargins(0,0,0,0)
        tsl_left = QFrame()
        tsll = QVBoxLayout(tsl_left)
        tsll.setContentsMargins(0,0,0,0)
        tsll.setSpacing(0)
        tsll.addWidget(self._bold(t['text_size'], 12))
        tsll.addWidget(self._muted(t['text_size_desc']))
        tsl.addWidget(tsl_left)
        tsl.addStretch()
        sz_grp = QFrame()
        szl = QHBoxLayout(sz_grp)
        szl.setContentsMargins(0,0,0,0)
        szl.setSpacing(4)
        for label, val in [(t['small'],"small"), (t['medium'],"medium"), (t['large'],"large")]:
            active = pref.get("ukuran_teks","medium") == val
            b = QPushButton(label)
            bg = c['btn_primary'] if active else c['btn_pale']
            b.setStyleSheet(f"background: {bg}; border: none; border-radius: 8px; padding: 6px 12px; font-size: 11px; font-weight: {'bold' if active else 'normal'};")
            b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            b.clicked.connect(lambda _, v=val: self._set_size(v))
            szl.addWidget(b)
        tsl.addWidget(sz_grp)
        displ.addWidget(ts_row)
        sl.addWidget(disp)

        # ── Notification ─────────────────────────────────────
        sl.addWidget(self._section(t['notification']))
        notif = QFrame()
        notif.setProperty("frameClass", "card")
        nl = QHBoxLayout(notif)
        nl.setContentsMargins(20, 14, 20, 14)
        nl.addWidget(self._bold(t['push_notif'], 12))
        nl.addStretch()
        # Simple toggle
        tog = QPushButton("ON")
        tog.setStyleSheet(f"background: {c['btn_primary']}; border: none; border-radius: 10px; padding: 4px 14px; font-size: 11px; font-weight: bold;")
        nl.addWidget(tog)
        sl.addWidget(notif)

        # ── Delete Account ───────────────────────────────────
        delc = QFrame()
        delc.setStyleSheet(f"QFrame {{ background: {c['card']}; border: 2px solid {c['danger']}; border-radius: 14px; }}")
        dcl = QVBoxLayout(delc)
        dcl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        db = QPushButton(t['delete_acct'])
        db.setStyleSheet(f"background: transparent; color: {c['danger']}; border: none; font-weight: bold; font-size: 13px;")
        db.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        db.clicked.connect(self._del_acct)
        dcl.addWidget(db)
        sl.addWidget(delc)
        sl.addStretch()
        scroll.setWidget(sw)
        lay.addWidget(scroll)

    def _section(self, text):
        l = QLabel(text)
        l.setFont(QFont(FONT_FAMILY, 15, QFont.Weight.Bold))
        return l

    def _bold(self, text, size):
        l = QLabel(text)
        l.setFont(QFont(FONT_FAMILY, size, QFont.Weight.Bold))
        return l

    def _muted(self, text):
        l = QLabel(text)
        l.setObjectName("muted")
        return l

    def _sep(self, c):
        s = QFrame()
        s.setFixedHeight(1)
        s.setStyleSheet(f"background: {c['border']};")
        return s

    def _save_pref(self, key, value):
        pref = ambil_preferensi(self._pid)
        pref[key] = value
        simpan_preferensi(self._pid, pref["tema"], pref["ukuran_teks"], pref["bahasa"])

    def _set_theme(self, val):
        if self._refreshing:
            return
        self._save_pref("tema", val)
        if self._refresh_cb:
            self._refreshing = True
            self._refresh_cb()
            self._refreshing = False

    def _set_lang(self, choice):
        if self._refreshing:
            return
        val = "id" if choice == "Bahasa Indonesia" else "en"
        self._save_pref("bahasa", val)
        if self._refresh_cb:
            self._refreshing = True
            self._refresh_cb()
            self._refreshing = False

    def _set_size(self, val):
        self._save_pref("ukuran_teks", val)
        QMessageBox.information(self, self._t['info'], self._t['text_size_msg'])

    def _del_acct(self):
        r = QMessageBox.question(self, self._t['del_confirm_title'], self._t['del_confirm_msg'])
        if r == QMessageBox.StandardButton.Yes:
            ok, msg = hapus_akun(self._pid, True)
            if ok:
                QMessageBox.information(self, self._t['done'], self._t['acct_deleted'])
                if self._refresh_cb:
                    self._refresh_cb()
            else:
                QMessageBox.critical(self, self._t['error'], msg)

    def _logout(self):
        c = palette(self._mode)
        reply = QMessageBox(self)
        reply.setWindowTitle(self._t['logout_title'])
        reply.setText(self._t['logout_confirm_msg'])
        reply.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        reply.setStyleSheet(f"QMessageBox {{ background-color: {c['card']}; }} QLabel {{ color: {c['text_dark']}; font-weight: bold; }} QPushButton {{ background-color: {c['btn_primary']}; color: {c['text_dark']}; padding: 6px 16px; border-radius: 6px; font-weight: bold; border: none; }}")
        
        res = reply.exec()
        if res == QMessageBox.StandardButton.Yes:
            top = self.window()
            if hasattr(top, '_go_logout'):
                top._go_logout()

    def _change_pw(self):
        dlg = QDialog(self)
        dlg.setWindowTitle(self._t['change_pw'])
        dlg.setFixedSize(380, 320)
        dl = QVBoxLayout(dlg)
        dl.setContentsMargins(24, 20, 24, 20)
        dl.addWidget(self._bold(self._t['change_pw'], 15))
        e1 = QLineEdit()
        e1.setPlaceholderText(self._t['curr_pw'])
        e1.setEchoMode(QLineEdit.EchoMode.Password)
        e1.setFixedHeight(38)
        dl.addWidget(e1)
        e2 = QLineEdit()
        e2.setPlaceholderText(self._t['new_pw'])
        e2.setEchoMode(QLineEdit.EchoMode.Password)
        e2.setFixedHeight(38)
        dl.addWidget(e2)
        e3 = QLineEdit()
        e3.setPlaceholderText(self._t['conf_new_pw'])
        e3.setEchoMode(QLineEdit.EchoMode.Password)
        e3.setFixedHeight(38)
        dl.addWidget(e3)
        def save():
            if not e1.text() or not e2.text() or not e3.text():
                QMessageBox.warning(dlg, self._t['error'], self._t['err_req'])
                return
            if e2.text() != e3.text():
                QMessageBox.warning(dlg, self._t['error'], self._t['err_match'])
                return
            QMessageBox.information(dlg, self._t['success'], self._t['succ_pw'])
            dlg.accept()
        sb = QPushButton(self._t['change_pw'])
        sb.setObjectName("btn_primary")
        sb.setFixedHeight(40)
        sb.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        sb.clicked.connect(save)
        dl.addWidget(sb)
        dlg.exec()
