"""
alerts.py — Notification manager for OcularGuard.

show_overlay() posts to the main tkinter thread via root.after(0, ...).
No threads, no Qt, no blocking — safe to call from the camera loop.
"""

from src.ui.overlay import show_overlay


class NotificationManager:

    @staticmethod
    def alert_20_20_20():
        show_overlay(
            "20-20-20 Rule",
            "Time to look away!\n\nLook 20 feet away for 20 seconds to reset your vision.",
            is_warning=False,
        )

    @staticmethod
    def alert_dry_eyes(current_bpm: int):
        show_overlay(
            "DRY EYE ALERT",
            f"Your blink rate is critically low ({current_bpm} BPM).\n\n"
            "STOP and blink intentionally 5 times now.",
            is_warning=True,
        )
