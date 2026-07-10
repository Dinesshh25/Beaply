# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_all

# Use relative paths for portability
project_root = os.path.abspath('.')

datas = [
    (os.path.join(project_root, 'assets'), 'assets'),
    (os.path.join(project_root, 'data', 'beasiswa.json'), 'data'),
]
binaries = []
hiddenimports = [
    'controllers',
    'controllers.admin_controller',
    'controllers.analytics_controller',
    'controllers.auth_controller',
    'controllers.bantuan_controller',
    'controllers.eksplorasi_controller',
    'controllers.notifikasi_controller',
    'controllers.profil_controller',
    'controllers.rekomendasi_controller',
    'controllers.tracker_controller',
    'models',
    'models.auth_model',
    'models.auth_utils',
    'models.beasiswa_model',
    'models.database',
    'models.email_service',
    'models.feedback_model',
    'models.notifikasi_model',
    'models.profil_model',
    'models.rekomendasi_model',
    'models.tracker_model',
    'models.validators',
    'pyqt_app',
    'pyqt_app.views',
    'pyqt_app.widgets',
    'pyqt_app.styles',
    'pyqt_app.utils',
    'database',
]

tmp_ret = collect_all('selenium')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    [os.path.join(project_root, 'main.py')],
    pathex=[project_root],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='beaply',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='beaply',
)
