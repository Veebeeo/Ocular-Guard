import pandas as pd
import matplotlib.pyplot as plt
from src.database.db_connection import get_db_session
from src.database.models import WorkSession, BlinkLog

def generate_report():
    db = next(get_db_session())
    
    last_session = db.query(WorkSession).order_by(WorkSession.start_time.desc()).first()
    
    if not last_session:
        print("No sessions found!")
        return

    print(f"Generating Report for Session ID: {last_session.id}")
    print(f"   Started: {last_session.start_time}")

    logs = db.query(BlinkLog).filter_by(session_id=last_session.id).order_by(BlinkLog.timestamp).all()
    
    if not logs:
        print("No data logged for this session yet.")
        return

    data = {
        "Time": [log.timestamp for log in logs],
        "Blink Rate": [log.blink_rate for log in logs],
        "Avg EAR": [log.avg_ear for log in logs]
    }
    df = pd.DataFrame(data)

    plt.figure(figsize=(10, 5))
    
    plt.plot(df["Time"], df["Blink Rate"], marker='o', linestyle='-', color='b', label='Blinks Per Minute')
    plt.axhline(y=10, color='r', linestyle='--', label='Dry Eye Threshold (10 bpm)')
    
    plt.title(f"Eye Health Report: {last_session.start_time.strftime('%Y-%m-%d %H:%M')}")
    plt.xlabel("Time")
    plt.ylabel("Blinks Per Minute")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    generate_report()