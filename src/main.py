import cv2
import time
from datetime import datetime
from src.database.db_connection import get_db_session
from src.database.models import WorkSession, BlinkLog
from src.engine.vision import EyeTracker

class OcularGuardSystem:
    def __init__(self):
        self.tracker = EyeTracker()
        self.db = next(get_db_session()) 
        self.current_session = None
        
        self.blinks = 0
        self.start_time = time.time()
        self.minute_start_time = time.time()
        self.blink_status = False
        self.ear_history = [] 

        
        self.EAR_THRESHOLD = 0.22 # Below this = Closed
        self.BLINK_COOLDOWN = 0.1 # Seconds to wait between blinks
        self.last_blink_time = 0

    def start_session(self):
        print("Starting OcularGuard Session...")
        new_session = WorkSession()
        self.db.add(new_session)
        self.db.commit()
        self.db.refresh(new_session)
        self.current_session = new_session
        print(f"Session Started! ID: {self.current_session.id}")

    def log_minute_data(self, bpm, avg_ear):
        if not self.current_session:
            return

        print(f"Saving Data: {bpm} blinks/min | Avg EAR: {avg_ear:.3f}")
        
        log = BlinkLog(
            session_id=self.current_session.id,
            blink_rate=bpm,
            avg_ear=avg_ear
        )
        self.db.add(log)
        self.db.commit()

        if bpm < 10:
            print(f"ALERT: Low Blink Rate detected! ({bpm}/min)")

    def run(self):
        self.start_session()
        cap = cv2.VideoCapture(0) 
        
        
        if not cap.isOpened():
            print("Critical Error: Camera could not be opened.")
            return

        print("Press 'q' to quit and save session.")

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to grab frame.")
                break

            # 1. Vision Processing
            result = self.tracker.process_frame(frame)
            
            if result:
                left, right, avg = result
                self.ear_history.append(avg)

                # 2. Blink Detection Logic 
                if avg < self.EAR_THRESHOLD:
                    self.blink_status = True # Eye is closed
                else:
                    if self.blink_status:
                        # Ensure it's a real blink, not just noise
                        if (time.time() - self.last_blink_time) > self.BLINK_COOLDOWN:
                            self.blinks += 1
                            self.last_blink_time = time.time()
                            print(f"Blink! (Total: {self.blinks})")
                        
                        self.blink_status = False # Reset flag

            
            if time.time() - self.minute_start_time >= 60:
                # Calculate stats
                bpm = self.blinks
                avg_minute_ear = float(sum(self.ear_history) / len(self.ear_history)) if self.ear_history else 0.0
                
                # Log to DB
                self.log_minute_data(bpm, avg_minute_ear)
                
                # Reset counters for the new minute
                self.blinks = 0
                self.minute_start_time = time.time()
                self.ear_history = []

            
            cv2.putText(frame, f"Blinks: {self.blinks}", (30, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Show "Low Blink" Warning on screen
            if self.ear_history and (sum(self.ear_history[-50:]) / 50) < 0.20:
                 cv2.putText(frame, "DROWSY / DRY EYES!", (30, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            cv2.imshow("OcularGuard Live", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        
        # Close Session in DB
        if self.current_session:
            self.current_session.end_time = datetime.utcnow()
            self.db.commit()
            print("✅ Session Ended & Saved.")

if __name__ == "__main__":
    system = OcularGuardSystem()
    system.run()