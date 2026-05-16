import cv2
import time
import numpy as np
from datetime import datetime
from src.database.db_connection import get_db_session
from src.database.models import WorkSession, BlinkLog
from src.engine.vision import EyeTracker
from src.ui.alerts import NotificationManager 

class OcularGuardSystem:
    def __init__(self):
        self.tracker = EyeTracker()
        self.db = next(get_db_session()) 
        self.current_session = None
        
       
        self.start_time = time.time()
        self.minute_start_time = time.time()
        
        # 20-20-20 Rule Timer
        self.last_break_time = time.time()
        self.BREAK_INTERVAL = 30
        
        
        self.smart_check_start = time.time()
        self.smart_blinks = 0     
        self.SMART_CHECK_INTERVAL = 15 

        # Blink Logic
        self.blinks = 0            
        self.blink_status = False 
        self.ear_history = [] 
        self.EAR_THRESHOLD = 0.22 
        self.BLINK_COOLDOWN = 0.1 
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
        if not self.current_session: return
        clean_ear = float(avg_ear)
        
        print(f"Saving Data: {bpm} blinks/min | Avg EAR: {clean_ear:.3f}")
        
        log = BlinkLog(
            session_id=self.current_session.id,
            blink_rate=bpm,
            avg_ear=clean_ear
        )
        self.db.add(log)
        self.db.commit()

    def run(self):
        self.start_session()
        
        
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Critical Error: Camera could not be opened.")
            return

        print("Press 'q' to quit.")

        while True:
            ret, frame = cap.read()
            if not ret: break

            #Vision Processing
            result = self.tracker.process_frame(frame)
            
            if result:
                left, right, avg = result
                self.ear_history.append(avg)

                # Blink Detection
                if avg < self.EAR_THRESHOLD:
                    self.blink_status = True
                else:
                    if self.blink_status:
                        if (time.time() - self.last_blink_time) > self.BLINK_COOLDOWN:
                            self.blinks += 1      
                            self.smart_blinks += 1 
                            self.last_blink_time = time.time()
                            print(f"Blink!")
                        self.blink_status = False

            current_time = time.time()

            #Notify
            
            if current_time - self.smart_check_start >= self.SMART_CHECK_INTERVAL:
                if self.smart_blinks < 3: 
                    
                    estimated_bpm = self.smart_blinks * (60 / self.SMART_CHECK_INTERVAL)
                    print(f"⚠️ Smart Alert Triggered: Only {self.smart_blinks} blinks in last 15s")
                    NotificationManager.alert_dry_eyes(int(estimated_bpm))
                
                # Reset Short-term counters
                self.smart_blinks = 0
                self.smart_check_start = current_time

            #20-20-20 Rule 
            if current_time - self.last_break_time >= self.BREAK_INTERVAL:
                print("⏳ 20 Minute Timer Reached!")
                NotificationManager.alert_20_20_20()
                self.last_break_time = current_time 

            #DB Logging
            if current_time - self.minute_start_time >= 60:
                bpm = self.blinks
                avg_minute_ear = float(sum(self.ear_history) / len(self.ear_history)) if self.ear_history else 0.0
                self.log_minute_data(bpm, avg_minute_ear)
                
                self.blinks = 0
                self.minute_start_time = current_time
                self.ear_history = []

           
            cv2.putText(frame, f"Blinks: {self.blinks}", (30, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("OcularGuard Live", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        if self.current_session:
            self.current_session.end_time = datetime.utcnow()
            self.db.commit()
            print("Session Ended.")

if __name__ == "__main__":
    system = OcularGuardSystem()
    system.run()