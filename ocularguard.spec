# ocularguard.spec
# Build with:  pyinstaller ocularguard.spec

import os
import sys
import mediapipe

mediapipe_path = os.path.dirname(mediapipe.__file__)

a = Analysis(
    ['run_ocularguard.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        # MediaPipe face-mesh models (essential — without these the tracker silently fails)
        (os.path.join(mediapipe_path, 'modules'), 'mediapipe/modules'),
        # UI assets (overlay icons etc.) — glob handles missing files gracefully
        ('src/ui', 'src/ui'),
    ],
    hiddenimports=[
        # MediaPipe
        'mediapipe',
        'mediapipe.python',
        'mediapipe.python.solutions',
        'mediapipe.python.solutions.face_mesh',
        # OpenCV
        'cv2',
        # SQLAlchemy SQLite dialect (stdlib — no extra package needed)
        'sqlalchemy.dialects.sqlite',
        # Notifications
        'plyer.platforms.win.notification',
        # PyQt6 overlay
        'PyQt6',
        'PyQt6.QtWidgets',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        # Tkinter (usually auto-detected but listed for safety)
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.simpledialog',
        # Matplotlib TkAgg backend
        'matplotlib.backends.backend_tkagg',
    ],
    hookspath=[],
    runtime_hooks=[],
    # Exclude heavy packages we don't need in the bundle
    excludes=['psycopg2', 'python-dotenv', 'jupyter', 'IPython'],
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
    # console=True is useful during development to see crash tracebacks.
    # Flip to False for the final release build.
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
