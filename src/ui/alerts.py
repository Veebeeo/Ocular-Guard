"""
alerts.py — Desktop notification popups for OcularGuard.

Uses threading.Thread instead of multiprocessing.Process.
multiprocessing causes PyInstaller .exe files to re-launch the entire
executable for each child process, producing cascading windows.
Threading is sufficient here : PyQt6 can run its own event loop on a
background thread independently of the main tkinter window.
"""

import threading


def _show_overlay_thread(title: str, message: str, is_warning: bool):
    """Target function run on a daemon thread."""
    # Import inside the function so the module loads fast on startup
    from src.ui.overlay import show_overlay_process
    try:
        show_overlay_process(title, message, is_warning)
    except Exception as e:
        # Never let a notification crash the main monitoring loop
        print(f"[OcularGuard] Notification error: {e}")


class NotificationManager:

    @staticmethod
    def _launch_popup(title: str, message: str, is_warning: bool):
        t = threading.Thread(
            target=_show_overlay_thread,
            args=(title, message, is_warning),
            daemon=True,   # Dies automatically when the main window closes
        )
        t.start()

    @staticmethod
    def alert_20_20_20():
        NotificationManager._launch_popup(
            "20-20-20 Rule",
            "Time to look away!\n\nLook 20 feet away for 20 seconds to reset your vision.",
            is_warning=False,
        )

    @staticmethod
    def alert_dry_eyes(current_bpm: int):
        NotificationManager._launch_popup(
            "DRY EYE ALERT",
            f"Your blink rate is critically low ({current_bpm} BPM).\n\n"
            "STOP and blink intentionally 5 times now.",
            is_warning=True,
        )
