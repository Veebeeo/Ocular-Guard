import threading
from plyer import notification

class NotificationManager:
    @staticmethod
    def send_alert(title, message):
        """
        Sends a desktop notification in a separate thread 
        so it doesn't freeze the camera feed.
        """
        def _show():
            try:
                notification.notify(
                    title=title,
                    message=message,
                    app_name="OcularGuard",
                    timeout=15  
                )
            except Exception as e:
                print(f"Error sending notification: {e}")

        
        threading.Thread(target=_show, daemon=True).start()

    @staticmethod
    def alert_20_20_20():
        NotificationManager.send_alert(
            "20-20-20 Rule", 
            "20 minutes passed! Look 20 feet away for 20 seconds."
        )

    @staticmethod
    def alert_dry_eyes(current_bpm):
        NotificationManager.send_alert(
            "Blink More!", 
            f"Your blink rate is low ({current_bpm} BPM). Blink now to hydrate your eyes."
        )