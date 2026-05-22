# Ocular Guard

> A modern desktop eye health monitoring application built with Python, OpenCV, MediaPipe, and PyQt6.

Ocular Guard is an intelligent desktop application designed to help users maintain healthier screen habits while working for long periods on a computer. The application combines computer vision, eye-tracking, activity monitoring, and productivity-aware reminders to reduce digital eye strain and encourage healthier workstation behavior.

Built using Python and powered by OpenCV + MediaPipe, Ocular Guard continuously monitors user eye activity and screen engagement in real time.

---

##  Features

###  Real-Time Eye Monitoring

* Uses webcam-based eye tracking with **MediaPipe** and **OpenCV**
* Detects eye presence and user attention
* Tracks screen engagement duration
* Helps identify unhealthy continuous screen exposure

###  Smart Break Reminder System

* Configurable work/break intervals
* Encourages healthy screen usage habits
* Supports productivity-focused eye care routines
* Helps implement the **20-20-20 rule** for reducing eye strain

###  Session Tracking & Analytics

* Logs monitoring sessions into a local SQLite database
* Stores user activity and tracking information
* Enables future analytics and usage insights

###  Desktop Application UI

* Built with **PyQt6**
* Lightweight desktop-native experience
* Clean and responsive interface
* Designed for long-running background usage

###  System Notifications

* Uses desktop notifications for reminders and alerts
* Non-intrusive productivity assistance
* Real-time eye health prompts

###  Standalone Executable Support

* Includes support for **PyInstaller**
* Can be packaged into a Windows executable
* Multiprocessing-safe application startup

---

# Screenshots
<img width=45% style="margin:10px; border-radius:8px" alt="Screenshot 2026-05-21 212646" src="https://github.com/user-attachments/assets/571634e6-2903-4a20-a275-8e5117d13982" />
<img width=45% style="margin:10px; border-radius:8px" alt="Screenshot 2026-05-21 212722" src="https://github.com/user-attachments/assets/7a1fe41e-0553-4ea8-b614-2333d83d6b68" />
<img width=45% style="margin:10px; border-radius:8px" alt="Screenshot 2026-05-21 212819" src="https://github.com/user-attachments/assets/5e75b656-c724-4209-9074-ea2b6a019494" />
<img width=45% style="margin:10px; border-radius:8px" alt="Screenshot 2026-05-21 222736" src="https://github.com/user-attachments/assets/018e4f84-fc25-4d06-ba80-d111908e7689" />
<img width=45% style="margin:10px; border-radius:8px" alt="Screenshot 2026-05-21 222910" src="https://github.com/user-attachments/assets/e80937f6-9fd0-473c-bbd5-cf3aafef2abb" />
<img width=45% style="margin:10px; border-radius:8px" alt="Screenshot 2026-05-21 222926" src="https://github.com/user-attachments/assets/5968deca-4b0b-4709-b128-35a013fa7442" />
<img width=45% style="margin:10px; border-radius:8px" alt="Screenshot 2026-05-21 222943" src="https://github.com/user-attachments/assets/c27da2f1-a7ab-4f25-9423-c0683a62fe8a" />
<img width=45% style="margin:10px; border-radius:8px" alt="Screenshot 2026-05-21 222954" src="https://github.com/user-attachments/assets/c03af988-97f8-40cf-96b8-f850b281a5b1" />


#  Project Architecture

```text
Ocular-Guard/
│
├── src/
│   ├── database/
│   ├── ui/
│   ├── vision/
│   ├── monitoring/
│   └── utilities/
│
├── run_ocularguard.py
├── requirements.txt
├── test_vision.py
├── ocularguard.spec
└── ocularguard.db
```

---

#  Tech Stack

| Category          | Technologies        |
| ----------------- | ------------------- |
| Language          | Python              |
| UI Framework      | PyQt6               |
| Computer Vision   | OpenCV              |
| Face/Eye Tracking | MediaPipe           |
| Data Analysis     | Pandas, NumPy       |
| Visualization     | Matplotlib          |
| Database          | SQLite + SQLAlchemy |
| Notifications     | Plyer               |
| Packaging         | PyInstaller         |
| Audio Utilities   | sounddevice         |

---

#  Installation

## 1. Clone the Repository

```bash
git clone https://github.com/Veebeeo/Ocular-Guard.git
cd Ocular-Guard
```

---

## 2. Create a Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

#  Running the Application

Launch Ocular Guard using:

```bash
python run_ocularguard.py
```

The launcher:

* Initializes the local database
* Loads application modules
* Starts the desktop interface
* Begins eye monitoring services

---

#  Testing Vision Components

To test webcam and vision modules:

```bash
python test_vision.py
```

This helps verify:

* Webcam access
* Face detection
* Eye-tracking pipeline
* OpenCV functionality
* MediaPipe integration

---

#  Database

Ocular Guard uses a local SQLite database:

```text
ocularguard.db
```

The database is initialized automatically on startup and is used to:

* Store monitoring sessions
* Save tracking metrics
* Maintain application records
* Support future analytics features

---

#  How It Works

## 1. Webcam Capture

The application captures webcam frames in real time using OpenCV.

## 2. Face & Eye Landmark Detection

MediaPipe analyzes facial landmarks and identifies eye regions.

## 3. Eye Activity Analysis

The system monitors:

* Eye presence
* Focus duration
* Attention consistency
* Screen engagement patterns

## 4. Session Monitoring

Continuous usage sessions are tracked and timed.

## 5. Reminder Triggering

When unhealthy usage thresholds are reached, Ocular Guard sends desktop notifications encouraging the user to take a break.

---

#  Building a Standalone Executable

The project includes a PyInstaller specification file:

```text
ocularguard.spec
```

To build the executable:

```bash
pyinstaller ocularguard.spec
```

Or:

```bash
pyinstaller --onefile --windowed run_ocularguard.py
```

Generated executables will appear inside:

```text
dist/
```

---

#  Important Dependencies

Some core dependencies used in the project include:

```text
PyQt6
opencv-python
opencv-contrib-python
mediapipe
numpy
pandas
matplotlib
SQLAlchemy
plyer
sounddevice
pyinstaller
```

Full dependency versions are available in:

```text
requirements.txt
```

---

#  Use Cases

Ocular Guard is useful for:

*  Software developers
*  Students
*  Designers
*  Office workers
*  Remote workers
*  Gamers
*  Anyone spending long hours in front of screens

---

#  Future Improvements

Potential future enhancements:

* AI-powered fatigue detection
* Blink-rate analysis
* Productivity scoring
* Multi-monitor support
* Cloud sync
* Cross-platform packaging
* Weekly health reports
* Focus analytics dashboard
* Mobile companion app
* Posture detection
* Advanced eye strain prediction

---

# Privacy

Ocular Guard is designed with privacy in mind.

* Webcam processing is performed locally
* No cloud-based image processing
* No user webcam footage is uploaded
* Local database storage only

---

# Contributing

Contributions are welcome.

## Steps to Contribute

1. Fork the repository
2. Create a new feature branch
3. Commit your changes
4. Push to your fork
5. Open a Pull Request

---

# License



Example:

```text
MIT License
```

---

Suggested sections:

* Main Dashboard
* Eye Tracking View
* Reminder Notifications
* Analytics Screen
* Session History

---

#  Acknowledgements

This project uses several amazing open-source technologies:

* OpenCV
* MediaPipe
* PyQt6
* SQLAlchemy
* NumPy
* Pandas
* PyInstaller

---


# 💡 Motivation

Digital eye strain and unhealthy screen exposure are increasingly common in modern work environments. Ocular Guard aims to provide a practical and lightweight desktop solution that helps users maintain healthier screen habits without interrupting productivity.

The project combines computer vision and desktop productivity tools to create a real-time eye health assistant for everyday computer users.
