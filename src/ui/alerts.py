import multiprocessing
from src.ui.overlay import show_overlay_process

class NotificationManager:
    @staticmethod
    def _launch_popup(title, message, is_warning):
        """Helper to spawn the process."""
        p = multiprocessing.Process(
            target=show_overlay_process, 
            args=(title, message, is_warning)
        )
        p.start()
        # We don't join() because we want the main app to keep running
        # The popup process will die when the user clicks "OK"

    @staticmethod
    def alert_20_20_20():
        NotificationManager._launch_popup(
            "20-20-20 Rule", 
            "Time to look away!\n\nLook 20 feet away for 20 seconds to reset your vision.",
            is_warning=False
        )

    @staticmethod
    def alert_dry_eyes(current_bpm):
        NotificationManager._launch_popup(
            "DRY EYE ALERT", 
            f"Your blink rate is critically low ({current_bpm} BPM).\n\nSTOP and blink intentionally 5 times now.",
            is_warning=True
        )