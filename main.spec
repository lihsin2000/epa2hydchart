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
        'PIL.ImageQt', 'PIL.ImageTk',
        'setuptools', 'wheel', 'pkg_resources',
        '_pytest', 'pytest',
        'scipy', 'sklearn', 'sympy',
        'docutils', 'sphinx',
        'xmlrpc', 'ftplib', 'imaplib', 'poplib', 'smtplib',
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
    upx=False,
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
    upx=False,
    name='epa2HydChart',
)

import shutil as _shutil
import os as _os

_dist_dir = _os.path.join('dist', 'epa2HydChart')
_lib_dir = _os.path.join(_dist_dir, 'library')

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
