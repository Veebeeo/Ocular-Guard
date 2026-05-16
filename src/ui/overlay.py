import sys
import os
from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor, QPixmap

class OverlayAlert(QDialog):
    def __init__(self, title, message, is_warning=False):
        super().__init__()
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                            Qt.WindowType.WindowStaysOnTopHint | 
                            Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        
        base_path = os.path.dirname(__file__)
        if is_warning:
            self.grad_start = "#7f1d1d" 
            self.grad_end = "#450a0a"
            self.border_color = "#991b1b"
            self.icon_path = os.path.join(base_path, "redness.png") 
        else:
            self.grad_start = "#334155"
            self.grad_end = "#1e293b"
            self.border_color = "#475569"
            self.icon_path = os.path.join(base_path, "hourglass.png") 

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.card = QFrame()
        self.card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {self.grad_start}, stop:1 {self.grad_end});
                border: 1px solid {self.border_color};
                border-radius: 12px;
            }}
        """)
        
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(12)
        layout.addWidget(self.card)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(24, 24) 
        self.icon_label.setStyleSheet("background: transparent; border: none;")
        

        if os.path.exists(self.icon_path):
            pixmap = QPixmap(self.icon_path)
            scaled_pixmap = pixmap.scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.icon_label.setPixmap(scaled_pixmap)
        else:
            self.icon_label.setText("⚠️" if is_warning else "🕒")
            self.icon_label.setFont(QFont("Segoe UI Emoji", 14))
            
        header_layout.addWidget(self.icon_label)

        self.title_label = QLabel(title)
        self.title_label.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
        self.title_label.setStyleSheet("color: rgba(255, 255, 255, 0.95); background: transparent; border: none; letter-spacing: 0.5px;")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()

        self.close_btn = QPushButton("✕")
        self.close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.close_btn.setFixedSize(20, 20)
        self.close_btn.clicked.connect(self.accept)
        self.close_btn.setStyleSheet("""
            QPushButton {
                color: rgba(255, 255, 255, 0.5);
                background: transparent;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover { color: white; }
        """)
        header_layout.addWidget(self.close_btn)
        
        card_layout.addLayout(header_layout)

   
        self.message_label = QLabel(message)
        self.message_label.setWordWrap(True)
        self.message_label.setFont(QFont("Segoe UI", 10))
        self.message_label.setStyleSheet("color: rgba(255, 255, 255, 0.8); background: transparent; border: none; line-height: 1.4;")
        card_layout.addWidget(self.message_label)

      
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.action_btn = QPushButton("OK")
        self.action_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.action_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        
        btn_color = "rgba(255, 255, 255, 0.1)"
        btn_hover = "rgba(255, 255, 255, 0.2)"
        
        self.action_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {btn_color};
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                padding: 6px 16px;
            }}
            QPushButton:hover {{
                background-color: {btn_hover};
            }}
        """)
        self.action_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.action_btn)
        
        card_layout.addLayout(btn_layout)

        self.resize(380, 140)
        self.move_to_bottom_right()

    def move_to_bottom_right(self):
        screen = QApplication.primaryScreen().availableGeometry()
        margin = 24 
        x = screen.width() - self.width() - margin
        y = screen.height() - self.height() - margin
        self.move(x, y)

def show_overlay_process(title, message, is_warning):
    # 1. Set the High DPI policy FIRST (Before the app is created)
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    # 2. Check if an app instance exists, if not, create it
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    # 3. Build and show the alert
    alert = OverlayAlert(title, message, is_warning)
    alert.show()
    app.exec()

if __name__ == "__main__":
    show_overlay_process("DRY EYE ALERT", "Test with image icon.", True)