# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['srun_client.py'],
    pathex=[],
    binaries=[],
    datas=[('./srunpy/html','srunpy/html')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    name='SrunClient',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    exclude_binaries=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='file_version.txt',
    icon=['logo.ico'],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SrunClient',
)