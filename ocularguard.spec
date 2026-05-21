# ocularguard.spec
# Build:  pyinstaller ocularguard.spec --clean
#
# Step 1 — temporarily set console=True to see crash tracebacks.
# Step 2 — once working, flip console=False for the release build.

import os
import sys
import mediapipe

mediapipe_path = os.path.dirname(mediapipe.__file__)

# mediapipe 0.10.x stores models in modules/ AND in the package root
# We bundle the entire mediapipe package folder to be safe.
mediapipe_datas = [
    (os.path.join(mediapipe_path, 'modules'),  'mediapipe/modules'),
    (os.path.join(mediapipe_path, 'python'),   'mediapipe/python'),
]

# Only add tasks/ if it exists (mediapipe >= 0.10.3)
tasks_path = os.path.join(mediapipe_path, 'tasks')
if os.path.isdir(tasks_path):
    mediapipe_datas.append((tasks_path, 'mediapipe/tasks'))

a = Analysis(
    ['run_ocularguard.py'],
    pathex=['.'],
    binaries=[],
    datas=mediapipe_datas + [
        # UI assets (icons, etc.) — safe if folder is empty
        ('src/ui', 'src/ui'),
    ],
    hiddenimports=[
        # MediaPipe
        'mediapipe',
        'mediapipe.python',
        'mediapipe.python.solutions',
        'mediapipe.python.solutions.face_mesh',
        'mediapipe.python.solutions.drawing_utils',
        # OpenCV
        'cv2',
        # SQLAlchemy SQLite
        'sqlalchemy.dialects.sqlite',
        'sqlalchemy.dialects.sqlite.pysqlite',
        # Tkinter (usually auto-detected; listed for safety)
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        # Matplotlib TkAgg backend
        'matplotlib',
        'matplotlib.backends.backend_tkagg',
        'matplotlib.backends._backend_tk',
        # numpy / pandas internals that PyInstaller sometimes misses
        'numpy.core._dtype_ctypes',
        'pandas._libs.tslibs.np_datetime',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        # Removed dependencies
        'psycopg2',
        'dotenv',
        # PyQt6 no longer used for notifications
        'PyQt6',
        # Avoid bloat
        'jupyter',
        'IPython',
        'PyQt5',
        'PySide2',
        'PySide6',
        'wx',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='OcularGuard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    # ── CHANGE THIS TO False FOR RELEASE BUILD ───────────────────────────
    # Keep True during testing so crash tracebacks appear in a console window
    console=False,
    icon='src/ui/icon.ico' if os.path.exists('src/ui/icon.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='OcularGuard',
)
