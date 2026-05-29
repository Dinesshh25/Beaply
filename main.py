"""
pyqt_app/main_pyqt.py
Beaply — PyQt6 Entry Point.
Connects to the same database and controllers as the CustomTkinter version.
"""
import sys
import os

# ── Ensure project root is in sys.path ──
_project_root = os.path.abspath(os.path.dirname(__file__))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon

# ── Initialise database (same as main.py) ────────────────────
from database import init_db
init_db()

from controllers.auth_controller import init_auth
init_auth()

# ── App modules ──────────────────────────────────────────────
from pyqt_app.styles.theme import palette, FONT_FAMILY
from pyqt_app.styles.stylesheet import build_stylesheet
from pyqt_app.widgets.sidebar import SidebarWidget
from pyqt_app.widgets.topbar import TopbarWidget
from pyqt_app.views.auth_view import AuthView, load_session, clear_session
from pyqt_app.views.home_view import HomeView
from pyqt_app.views.dashboard_view import DashboardView
from pyqt_app.views.eksplorasi_view import EksplorasiView
from pyqt_app.views.bookmarks_view import BookmarksView
from pyqt_app.views.rekomendasi_view import RekomendasiView
from pyqt_app.views.kalender_view import KalenderView
from pyqt_app.views.tracker_view import TrackerView
from pyqt_app.views.notifikasi_view import NotifikasiView
from pyqt_app.views.profil_view import ProfilView
from pyqt_app.views.settings_view import SettingsView
from pyqt_app.views.bantuan_view import BantuanView

# ── Admin modules ────────────────────────────────────────────
from pyqt_app.widgets.admin_sidebar import AdminSidebarWidget
from pyqt_app.widgets.admin_topbar import AdminTopbarWidget
from pyqt_app.views.admin_scholarship_view import AdminScholarshipView
from pyqt_app.views.admin_userprofile_view import AdminUserProfileView
from pyqt_app.views.admin_helpcenter_view import AdminHelpCenterView
from pyqt_app.views.admin_settings_view import AdminSettingsView
from controllers.admin_controller import is_admin

# i18n helper
from pyqt_app.utils.i18n import t as _t
from controllers.profil_controller import tampil_profil, ambil_preferensi


# ═════════════════════════════════════════════════════════════
# Main Window
# ═════════════════════════════════════════════════════════════

class BeaplyMainWindow(QMainWindow):
    """Root window — handles auth → dashboard flow."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Beaply — Scholarship Insight")
        self.setMinimumSize(1060, 720)
        self.resize(1200, 780)

        self._profil_id = None
        self._user_data = {}
        self._bhs = "id"
        self._mode = "light"
        self._is_admin = False

        # Central stacked widget: 0 = auth, 1 = home (profile select), 2 = main layout, 3 = admin layout
        self._root_stack = QStackedWidget()
        self._root_stack.setObjectName("central")
        self.setCentralWidget(self._root_stack)

        # Auth page
        self._auth = AuthView()
        self._auth.login_success.connect(self._on_login)
        self._auth.register_success.connect(self._on_register)
        self._root_stack.addWidget(self._auth)          # index 0

        # Home page placeholder (built after login)
        self._home = QWidget()
        self._root_stack.addWidget(self._home)           # index 1

        # Main placeholder (built after profile selected)
        self._main_widget = QWidget()
        self._root_stack.addWidget(self._main_widget)    # index 2

        # Admin placeholder (built after admin login)
        self._admin_widget = QWidget()
        self._root_stack.addWidget(self._admin_widget)   # index 3

        # Apply initial stylesheet
        self._apply_theme()
        self._root_stack.setCurrentIndex(0)

        # Auto-login from saved session
        self._try_auto_login()

    # ── Theme ────────────────────────────────────────────────
    def _apply_theme(self):
        qss = build_stylesheet(self._mode)
        self.setStyleSheet(qss)

    # ── Auth callback ────────────────────────────────────────
    def _on_login(self, data: dict):
        """Called when login succeeds. Auto-select profile if possible."""
        self._user_data = data
        self._user_id = data.get("user_id") or data.get("id")

        from controllers.auth_controller import set_current_user
        set_current_user(data)

        # Check if user is admin
        user_email = data.get("email", "")
        if is_admin(user_email):
            self._is_admin = True
            self._build_admin_layout()
            self._root_stack.setCurrentWidget(self._admin_widget)
            return

        self._is_admin = False

        # Each user has exactly 1 profile — pick it directly, no HomeView
        from controllers.profil_controller import tampil_semua_profil
        profiles = tampil_semua_profil(self._user_id)

        if profiles:
            # Always use the first (and only expected) profile
            self._on_profile_selected(profiles[0]["id"])
            return

        # No profile found — session is stale/invalid, return to login
        clear_session()
        self._root_stack.setCurrentIndex(0)

    def _on_register(self, data: dict, profil_id: int):
        """Called when register+profile creation succeeds. Go straight to dashboard."""
        self._user_data = data
        self._user_id = data.get("user_id") or data.get("id")
        # pyrefly: ignore [missing-import]
        from controllers.auth_controller import set_current_user
        set_current_user(data)
        self._profil_id = profil_id
        pref = ambil_preferensi(self._profil_id)
        self._bhs = pref.get("bahasa", "id")
        self._mode = pref.get("tema", "light")
        self._apply_theme()
        self._build_main_layout()
        self._root_stack.setCurrentWidget(self._main_widget)

    def _try_auto_login(self):
        """Check for saved session and auto-login."""
        saved = load_session()
        if not saved:
            return
        uid = saved.get("user_id") or saved.get("id")
        if not uid:
            clear_session()
            return
        # Validate that user still exists and has a profile before auto-login
        from controllers.profil_controller import tampil_semua_profil
        profiles = tampil_semua_profil(uid)
        if not profiles:
            # Stale session — user has no profile, force fresh login
            clear_session()
            return
        self._on_login(saved)

    # ── Profile selected callback ─────────────────────────────
    def _on_profile_selected(self, profil_id: int):
        """Called when user picks or creates a profile."""
        self._profil_id = profil_id

        # Load preferences
        pref = ambil_preferensi(self._profil_id)
        self._bhs = pref.get("bahasa", "id")
        self._mode = pref.get("tema", "light")
        self._apply_theme()

        self._build_main_layout()
        self._root_stack.setCurrentWidget(self._main_widget)

    # ── Build Main Layout (sidebar + topbar + content) ───────
    def _build_main_layout(self):
        # Remove old
        self._root_stack.removeWidget(self._main_widget)
        self._main_widget.deleteLater()


        self._main_widget = QWidget()
        self._main_widget.setObjectName("central")
        main_lay = QHBoxLayout(self._main_widget)
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)

        # Sidebar
        self._sidebar = SidebarWidget(_t, self._bhs)
        
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        from PyQt6.QtGui import QColor
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(2)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 15))
        self._sidebar.setGraphicsEffect(shadow)
        
        self._sidebar.navigate.connect(self._navigate)
        main_lay.addWidget(self._sidebar)

        # Right area
        right = QFrame()
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(20, 12, 20, 12)
        right_lay.setSpacing(8)

        profil = tampil_profil(self._profil_id)
        user_name = profil["nama"] if profil and profil.get("nama") else "Guest"
        self._topbar = TopbarWidget(user_name)
        self._topbar.bell_clicked.connect(lambda: self._navigate("notifikasi"))
        self._topbar.avatar_clicked.connect(lambda: self._navigate("profil"))
        right_lay.addWidget(self._topbar)

        # Content stack — one widget per page
        self._content_stack = QStackedWidget()
        right_lay.addWidget(self._content_stack)

        main_lay.addWidget(right, 1)
        self._root_stack.addWidget(self._main_widget)

        # Pre-build all pages
        self._pages = {}
        self._build_page("dashboard")
        self._navigate("dashboard")

    # ── Page factory ─────────────────────────────────────────
    def _build_page(self, key: str):
        """Lazily create and cache a page widget."""
        if key in self._pages:
            # Remove old page to rebuild with fresh data
            old = self._pages.pop(key)
            self._content_stack.removeWidget(old)
            old.deleteLater()

        pid = self._profil_id
        bhs = self._bhs
        mode = self._mode

        if key == "dashboard":
            page = DashboardView(pid, bhs, navigate_cb=self._navigate, mode=mode)
        elif key == "eksplorasi":
            page = EksplorasiView(pid, bhs, mode=mode)
        elif key == "rekomendasi":
            page = RekomendasiView(pid, bhs, mode=mode)
        elif key == "bookmarks":
            page = BookmarksView(pid, bhs, mode=mode)
        elif key == "kalender":
            page = KalenderView(pid, bhs, mode=mode, navigate_cb=self._navigate)
        elif key == "tracker":
            page = TrackerView(pid, bhs, mode=mode)
        elif key == "notifikasi":
            page = NotifikasiView(pid, bhs, mode=mode)
        elif key == "profil":
            page = ProfilView(pid, bhs, mode=mode)
        elif key == "settings":
            page = SettingsView(pid, bhs, mode=mode, refresh_cb=self._refresh_all)
        elif key == "bantuan":
            page = BantuanView(pid, bhs=bhs, mode=mode)
        else:
            page = QWidget()

        idx = self._content_stack.addWidget(page)
        self._pages[key] = page
        return idx

    # ── Navigation ───────────────────────────────────────────
    TITLES = {
        "dashboard": "title_dashboard", "eksplorasi": "title_scholarships",
        "rekomendasi": "title_recom", "bookmarks": "title_bookmarks",
        "kalender": "title_calendar", "notifikasi": "title_notif",
        "profil": "title_profile", "tracker": "t_judul",
        "bantuan": "title_help", "settings": "title_settings",
    }

    def _navigate(self, key: str):
        # Rebuild page with fresh data each time
        self._build_page(key)
        self._content_stack.setCurrentWidget(self._pages[key])

        # Update topbar title
        title_key = self.TITLES.get(key, key)
        self._topbar.set_title(_t(title_key, self._bhs))

        # Update sidebar highlight
        self._sidebar.set_active(key)

    # ── Refresh after settings change ────────────────────────
    def _refresh_all(self):
        pref = ambil_preferensi(self._profil_id)
        self._bhs = pref.get("bahasa", "id")
        self._mode = pref.get("tema", "light")

        # Apply theme stylesheet first
        self._apply_theme()

        # Process events so the new QSS is fully applied before
        # we tear down and rebuild the widget tree. This prevents
        # the white/black screen flash.
        QApplication.processEvents()

        self._build_main_layout()

        # Index 2 = main layout (sidebar + content).
        # Previously this was index 1 (Home/profile-select), which
        # caused a blank screen after theme/language changes.
        self._root_stack.setCurrentWidget(self._main_widget)

        # Navigate back to settings so the user stays on the same page
        self._navigate("settings")

    # ── Admin Layout ─────────────────────────────────────────
    def _build_admin_layout(self):
        """Build the admin panel layout with admin sidebar + topbar + content."""
        self._root_stack.removeWidget(self._admin_widget)
        self._admin_widget.deleteLater()

        self._admin_widget = QWidget()
        self._admin_widget.setObjectName("central")
        admin_lay = QHBoxLayout(self._admin_widget)
        admin_lay.setContentsMargins(0, 0, 0, 0)
        admin_lay.setSpacing(0)

        # Admin Sidebar
        self._admin_sidebar = AdminSidebarWidget()
        self._admin_sidebar.navigate.connect(self._admin_navigate)
        admin_lay.addWidget(self._admin_sidebar)

        # Right area
        right = QFrame()
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(20, 12, 20, 12)
        right_lay.setSpacing(8)

        user_name = self._user_data.get("nama_lengkap", "Anonymous")
        self._admin_topbar = AdminTopbarWidget(user_name)
        right_lay.addWidget(self._admin_topbar)

        # Admin content stack
        self._admin_content_stack = QStackedWidget()
        right_lay.addWidget(self._admin_content_stack)

        admin_lay.addWidget(right, 1)
        self._root_stack.addWidget(self._admin_widget)

        # Pre-build and navigate to first page
        self._admin_pages = {}
        self._admin_navigate("admin_scholarships")

    def _admin_build_page(self, key: str):
        """Lazily create and cache an admin page widget."""
        if key in self._admin_pages:
            old = self._admin_pages.pop(key)
            self._admin_content_stack.removeWidget(old)
            old.deleteLater()

        mode = self._mode

        if key == "admin_scholarships":
            page = AdminScholarshipView(mode=mode)
        elif key == "admin_users":
            page = AdminUserProfileView(mode=mode)
        elif key == "admin_helpcenter":
            page = AdminHelpCenterView(mode=mode)
        elif key == "admin_settings":
            page = AdminSettingsView(mode=mode, refresh_cb=self._admin_refresh)
        else:
            page = QWidget()

        self._admin_content_stack.addWidget(page)
        self._admin_pages[key] = page

    ADMIN_TITLES = {
        "admin_scholarships": ("Scholarship Data", "Manage scholarship data"),
        "admin_users":        ("User Profile", ""),
        "admin_helpcenter":   ("Help Center", ""),
        "admin_settings":     ("Settings", ""),
    }

    def _admin_navigate(self, key: str):
        self._admin_build_page(key)
        self._admin_content_stack.setCurrentWidget(self._admin_pages[key])
        title, subtitle = self.ADMIN_TITLES.get(key, (key, ""))
        self._admin_topbar.set_title(title, subtitle)
        self._admin_sidebar.set_active(key)

    def _admin_refresh(self):
        """Refresh admin layout after settings change."""
        self._mode = "light"  # Admin uses light mode by default
        self._apply_theme()
        QApplication.processEvents()
        self._build_admin_layout()
        self._root_stack.setCurrentWidget(self._admin_widget)
        self._admin_navigate("admin_settings")

    # ── Logout ───────────────────────────────────────────────
    def _go_logout(self):
        """Called from profile page logout."""
        self._profil_id = None
        self._user_data = {}
        self._user_id = None
        self._mode = "light"
        self._bhs = "id"
        self._is_admin = False
        self._apply_theme()

        # pyrefly: ignore [missing-import]
        from controllers.auth_controller import set_current_user
        set_current_user(None)

        # Rebuild auth
        clear_session()
        self._root_stack.removeWidget(self._auth)
        self._auth.deleteLater()
        self._auth = AuthView()
        self._auth.login_success.connect(self._on_login)
        self._auth.register_success.connect(self._on_register)
        self._root_stack.insertWidget(0, self._auth)
        self._root_stack.setCurrentIndex(0)


# ═════════════════════════════════════════════════════════════
# Entry Point
# ═════════════════════════════════════════════════════════════

def main():
    app = QApplication(sys.argv)
    app.setFont(QFont(FONT_FAMILY, 11))

    window = BeaplyMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
