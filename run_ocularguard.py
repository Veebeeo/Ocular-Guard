"""
OcularGuard — Desktop Eye Health Monitor
Run this file to launch the application.

"""

import sys
import os
import multiprocessing

# ── CRITICAL for PyInstaller + multiprocessing on Windows ────────────────────
# Must be called at the very top of the entry point, before anything else.
# Without this, every multiprocessing.Process re-launches the whole .exe,
# causing cascading windows.
multiprocessing.freeze_support()

# Ensure the project root is importable whether running as .py or frozen .exe
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database.db_connection import init_db, DB_PATH
from src.ui.app import launch


def main():
    print("╔══════════════════════════════════════╗")
    print("║        OcularGuard v2.0              ║")
    print("║   Desktop Eye Health Monitor         ║")
    print("╚══════════════════════════════════════╝\n")

    print(f"[1/2] Database → {DB_PATH}")
    try:
        init_db()
    except Exception as e:
        print(f"  ✖  Database error: {e}")
        sys.exit(1)

    print("[2/2] Launching window...\n")
    launch()


if __name__ == "__main__":
    main()
