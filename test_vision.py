import cv2
from src.engine.vision import EyeTracker

def main():
    tracker = EyeTracker()
    cap = cv2.VideoCapture(0) 

    print("Press 'q' to quit...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        result = tracker.process_frame(frame)

        if result:
            left, right, avg = result
            # Green if eyes open, red if closed 
            color = (0, 255, 0) if avg > 0.25 else (0, 0, 255)
            status = "Open" if avg > 0.25 else "Blink"
            
            cv2.putText(frame, f"EAR: {avg:.2f} | {status}", (30, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        cv2.imshow("OcularGuard Vision Test", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()