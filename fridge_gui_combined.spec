# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['fridge_gui_combined.py'],
    pathex=[],
    binaries=[],
    datas=[('final_home_screen.png', '.'), ('fridge_police_logo.png', '.'), ('inside_screen_resized.png', '.'), ('rebuilt_model.h5', '.'), ('labels.txt', '.'), ('shelf_life.json', '.')],
    hiddenimports=['tensorflow', 'keras', 'h5py'],
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
    a.binaries,
    a.datas,
    [],
    name='fridge_gui_combined',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
