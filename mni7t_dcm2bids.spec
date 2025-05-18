# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src/mni_7t_dicom_to_bids/scripts/run_mni_7t_dicom_to_bids.py'],
    pathex=[],
    binaries=[],
    datas=[('src/mni_7t_dicom_to_bids/assets', 'mni_7t_dicom_to_bids/assets')],
    hiddenimports=[],
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
    name='mni7t_dcm2bids',
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
