# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('icon.ico', '.'),
        ('example', 'example'),
        ('fonts', 'fonts'),
    ],
    hiddenimports=[
        'cairosvg',
        'cairocffi',
        'cssselect2',
        'tinycss2',
        'webencodings',
        'defusedxml',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'IPython', 'jupyter', 'notebook', 'ipykernel',
        # PIL plugins not used
        'PIL.ImageQt', 'PIL.ImageTk',
        'PIL.AvifImagePlugin',
        'PIL.FitsImagePlugin',
        'PIL.MpegImagePlugin',
        'PIL.PsdImagePlugin',
        # build/test tools
        'setuptools', 'wheel', 'pkg_resources',
        '_pytest', 'pytest',
        # heavy scientific libs not used
        'scipy', 'sklearn', 'sympy',
        'pandas.io.formats.style',  # removes Jinja2 dep
        # docs
        'docutils', 'sphinx',
        # network protocols not used
        'xmlrpc', 'ftplib', 'imaplib', 'poplib', 'smtplib',
        # Qt modules not used
        'PyQt6.QtPdf', 'PyQt6.QtPdfWidgets',
        'PyQt6.QtMultimedia', 'PyQt6.QtMultimediaWidgets',
        'PyQt6.QtBluetooth', 'PyQt6.QtNfc',
        'PyQt6.QtQml', 'PyQt6.QtQuick', 'PyQt6.QtQuickWidgets',
        'PyQt6.QtWebEngineCore', 'PyQt6.QtWebEngineWidgets', 'PyQt6.QtWebChannel',
        'PyQt6.QtSql', 'PyQt6.Qt3DCore',
    ],
    noarchive=False,
    optimize=1,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='epa2HydChart',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
    contents_directory='library',
    version='version_info.txt',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='epa2HydChart',
)

import shutil as _shutil
import os as _os
import glob as _glob

_dist_dir = _os.path.join('dist', 'epa2HydChart')
_lib_dir = _os.path.join(_dist_dir, 'library')

# Move shared assets out of library/ to dist root
for _item in ['example', 'fonts', 'icon.ico']:
    _src = _os.path.join(_lib_dir, _item)
    _dst = _os.path.join(_dist_dir, _item)
    if _os.path.exists(_src):
        if _os.path.isdir(_src):
            if _os.path.exists(_dst):
                _shutil.rmtree(_dst)
            _shutil.copytree(_src, _dst)
        else:
            _shutil.copy2(_src, _dst)

# Remove unnecessary large files from library/
_files_to_remove = [
    # Software OpenGL fallback (~20 MB) — not needed for 2D PyQt6 UI
    _os.path.join(_lib_dir, 'opengl32sw.dll'),
    # Qt PDF module (~4.5 MB) — not used
    _os.path.join(_lib_dir, 'PyQt6', 'Qt6', 'bin', 'Qt6Pdf.dll'),
    # AVIF image codec (~7.5 MB) — not used
    *_glob.glob(_os.path.join(_lib_dir, '_avif*.pyd')),
    # Duplicate fonts in library/ (already moved to dist root above)
    _os.path.join(_lib_dir, 'fonts'),
]
for _f in _files_to_remove:
    if _os.path.isfile(_f):
        _os.remove(_f)
        print(f'[post-build] removed {_f}')
    elif _os.path.isdir(_f):
        _shutil.rmtree(_f)
        print(f'[post-build] removed dir {_f}')
