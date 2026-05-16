"""
OcularGuard — Desktop Eye Health Monitor
Launch this file to start the application.
"""

import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.database.db_connection import init_db
from src.ui.app import launch


def main():
    print("╔══════════════════════════════════════╗")
    print("║        OcularGuard v2.0              ║")
    print("║   Desktop Eye Health Monitor         ║")
    print("╚══════════════════════════════════════╝")
    print()

    # Initialise database tables if needed
    print("[1/2] Checking database...")
    try:
        init_db()
    except Exception as e:
        print(f"  ⚠ Database warning: {e}")
        print("  Dashboard history may be unavailable.")

    # Launch GUI
    print("[2/2] Launching application...\n")
    launch()


if __name__ == "__main__":
    main()
