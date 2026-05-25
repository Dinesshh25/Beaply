"""
pyqt_app/views/admin_settings_view.py
Admin — Settings page (reuses user SettingsView logic).
"""
from pyqt_app.views.settings_view import SettingsView


class AdminSettingsView(SettingsView):
    """Admin settings — same as user settings."""

    def __init__(self, profil_id=None, bhs="id", mode="light", refresh_cb=None, parent=None):
        # Use a default profil_id if none provided (admin may not have a profile)
        super().__init__(
            profil_id=profil_id or 0,
            bhs=bhs,
            mode=mode,
            refresh_cb=refresh_cb,
            parent=parent,
        )
