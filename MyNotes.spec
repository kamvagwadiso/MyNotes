# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\futur\\Documents\\MyNotes\\run.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\futur\\Documents\\MyNotes\\assets', 'assets'), ('C:\\Users\\futur\\Documents\\MyNotes\\data', 'data')],
    hiddenimports=['PIL._tkinter_finder', 'pymupdf'],
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
    name='MyNotes',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
