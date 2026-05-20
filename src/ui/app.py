"""
OcularGuard Desktop Application
Main GUI window with Control Panel + Analytics Dashboard
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import cv2
import numpy as np
from datetime import datetime, timedelta
from collections import deque

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

from src.database.db_connection import get_db_session
from src.database.models import WorkSession, BlinkLog, Event
from src.engine.vision import EyeTracker
from src.ui.alerts import NotificationManager


# ─── Color Palette ───────────────────────────────────────────────────────────
BG_DARK      = "#0B0E11"
BG_CARD      = "#141820"
BG_CARD_ALT  = "#1A1F2B"
ACCENT       = "#00D4AA"
ACCENT_DIM   = "#00A88A"
ACCENT_WARN  = "#FF6B6B"
ACCENT_AMBER = "#FFB347"
TEXT_PRIMARY  = "#E8ECF1"
TEXT_SECONDARY= "#7A8599"
TEXT_MUTED    = "#4A5568"
BORDER       = "#1E2633"


class OcularGuardApp:
    """Main application window."""

    def __init__(self, root):
        self.root = root
        self.root.title("OcularGuard")
        self.root.geometry("1280x820")
        self.root.minsize(1100, 700)
        self.root.configure(bg=BG_DARK)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # ── State ────────────────────────────────────────────────────────
        self.tracker = EyeTracker()
        self.db = next(get_db_session())
        self.current_session = None
        self.running = False
        self.camera_thread = None

        # Toggles
        self.enable_blink_alert = tk.BooleanVar(value=True)
        self.enable_20_20_20   = tk.BooleanVar(value=True)

        # Runtime counters
        self.blinks = 0
        self.blink_status = False
        self.ear_history = []
        self.last_blink_time = 0
        self.EAR_THRESHOLD = 0.22
        self.BLINK_COOLDOWN = 0.1

        self.minute_start_time = 0
        self.last_break_time = 0
        self.BREAK_INTERVAL = 30  # seconds — overwritten at start_monitoring from the UI input

        self.smart_check_start = 0
        self.smart_blinks = 0
        self.SMART_CHECK_INTERVAL = 15

        # Live data for mini-chart
        self.live_bpm_history = deque(maxlen=30)
        self.live_ear_history = deque(maxlen=30)
        self.live_time_labels = deque(maxlen=30)

        # Current page
        self.current_page = "control"

        # ── Styles ───────────────────────────────────────────────────────
        self._setup_styles()

        # ── Layout ───────────────────────────────────────────────────────
        self._build_sidebar()
        self._build_main_area()

        # Show control panel by default
        self._show_control_panel()

    # =====================================================================
    #  STYLES
    # =====================================================================
    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Dark.TFrame", background=BG_DARK)
        style.configure("Card.TFrame", background=BG_CARD)
        style.configure("CardAlt.TFrame", background=BG_CARD_ALT)

        style.configure("Title.TLabel", background=BG_DARK, foreground=TEXT_PRIMARY,
                         font=("Segoe UI", 22, "bold"))
        style.configure("Subtitle.TLabel", background=BG_DARK, foreground=TEXT_SECONDARY,
                         font=("Segoe UI", 11))
        style.configure("CardTitle.TLabel", background=BG_CARD, foreground=TEXT_PRIMARY,
                         font=("Segoe UI", 13, "bold"))
        style.configure("CardBody.TLabel", background=BG_CARD, foreground=TEXT_SECONDARY,
                         font=("Segoe UI", 10))
        style.configure("StatValue.TLabel", background=BG_CARD, foreground=ACCENT,
                         font=("Consolas", 28, "bold"))
        style.configure("StatLabel.TLabel", background=BG_CARD, foreground=TEXT_SECONDARY,
                         font=("Segoe UI", 9))
        style.configure("Status.TLabel", background=BG_DARK, foreground=TEXT_MUTED,
                         font=("Segoe UI", 9))

        # Checkbutton
        style.configure("Toggle.TCheckbutton", background=BG_CARD, foreground=TEXT_PRIMARY,
                         font=("Segoe UI", 11), indicatorsize=16)
        style.map("Toggle.TCheckbutton",
                  background=[("active", BG_CARD)],
                  foreground=[("active", ACCENT)])

    # =====================================================================
    #  SIDEBAR
    # =====================================================================
    def _build_sidebar(self):
        self.sidebar = tk.Frame(self.root, bg=BG_CARD, width=220)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # Logo area
        logo_frame = tk.Frame(self.sidebar, bg=BG_CARD)
        logo_frame.pack(fill=tk.X, padx=20, pady=(28, 8))

        # Animated dot
        self.logo_dot = tk.Canvas(logo_frame, width=12, height=12,
                                  bg=BG_CARD, highlightthickness=0)
        self.logo_dot.pack(side=tk.LEFT, padx=(0, 10))
        self.logo_dot_id = self.logo_dot.create_oval(2, 2, 10, 10, fill=TEXT_MUTED, outline="")

        tk.Label(logo_frame, text="OcularGuard", bg=BG_CARD, fg=TEXT_PRIMARY,
                 font=("Segoe UI", 15, "bold")).pack(side=tk.LEFT)

        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(fill=tk.X, padx=16, pady=16)

        # Nav buttons
        self.nav_buttons = {}
        self._add_nav_button("control", "⚙  Control Panel", self._show_control_panel)
        self._add_nav_button("dashboard", "📊  Dashboard", self._show_dashboard)

        # Bottom status
        self.status_label = tk.Label(self.sidebar, text="● Idle", bg=BG_CARD,
                                     fg=TEXT_MUTED, font=("Segoe UI", 9), anchor="w")
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=24, pady=20)

    def _add_nav_button(self, key, text, command):
        btn = tk.Button(self.sidebar, text=text, anchor="w",
                        bg=BG_CARD, fg=TEXT_SECONDARY, activebackground=BG_CARD_ALT,
                        activeforeground=TEXT_PRIMARY, font=("Segoe UI", 11),
                        bd=0, padx=24, pady=10, cursor="hand2",
                        command=command, relief=tk.FLAT)
        btn.pack(fill=tk.X)
        btn.bind("<Enter>", lambda e, b=btn: b.config(bg=BG_CARD_ALT))
        btn.bind("<Leave>", lambda e, b=btn, k=key:
                 b.config(bg=ACCENT_DIM if self.current_page == k else BG_CARD))
        self.nav_buttons[key] = btn

    def _highlight_nav(self, key):
        for k, btn in self.nav_buttons.items():
            if k == key:
                btn.config(bg=ACCENT_DIM, fg=TEXT_PRIMARY)
            else:
                btn.config(bg=BG_CARD, fg=TEXT_SECONDARY)

    # =====================================================================
    #  MAIN AREA
    # =====================================================================
    def _build_main_area(self):
        self.main_frame = tk.Frame(self.root, bg=BG_DARK)
        self.main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Container that switches between pages
        self.page_container = tk.Frame(self.main_frame, bg=BG_DARK)
        self.page_container.pack(fill=tk.BOTH, expand=True, padx=28, pady=20)

    def _clear_page(self):
        for w in self.page_container.winfo_children():
            w.destroy()

    # =====================================================================
    #  CONTROL PANEL PAGE
    # =====================================================================
    def _show_control_panel(self):
        self.current_page = "control"
        self._highlight_nav("control")
        self._clear_page()

        # Header
        ttk.Label(self.page_container, text="Control Panel", style="Title.TLabel").pack(anchor="w")
        ttk.Label(self.page_container, text="Configure monitoring features and start a session",
                  style="Subtitle.TLabel").pack(anchor="w", pady=(2, 20))

        # ── Feature Toggles Card ─────────────────────────────────────────
        toggles_card = self._make_card(self.page_container, "Feature Toggles")

        self.chk_blink = ttk.Checkbutton(toggles_card, text="  Blink Rate Alert",
                                          variable=self.enable_blink_alert,
                                          style="Toggle.TCheckbutton")
        self.chk_blink.pack(anchor="w", padx=20, pady=(10, 4))

        ttk.Label(toggles_card, text="Notifies you when your blink rate drops below safe levels "
                  "(< 3 blinks per 15 seconds)", style="CardBody.TLabel").pack(anchor="w", padx=44, pady=(0, 12))

        self.chk_202020 = ttk.Checkbutton(toggles_card, text="  20-20-20 Rule Timer",
                                           variable=self.enable_20_20_20,
                                           style="Toggle.TCheckbutton")
        self.chk_202020.pack(anchor="w", padx=20, pady=(4, 4))

        ttk.Label(toggles_card, text="Every N minutes, reminds you to look 20 feet away "
                  "for 20 seconds", style="CardBody.TLabel").pack(anchor="w", padx=44, pady=(0, 6))

        interval_row = tk.Frame(toggles_card, bg=BG_CARD)
        interval_row.pack(anchor="w", padx=44, pady=(0, 16))

        tk.Label(interval_row, text="Break interval:", bg=BG_CARD, fg=TEXT_SECONDARY,
                 font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 8))

        self.break_interval_var = tk.StringVar(value="20")
        interval_entry = tk.Entry(interval_row, textvariable=self.break_interval_var,
                                  width=5, bg=BG_CARD_ALT, fg=TEXT_PRIMARY,
                                  insertbackground=ACCENT, font=("Consolas", 11),
                                  relief=tk.FLAT, bd=4,
                                  highlightthickness=1, highlightcolor=ACCENT,
                                  highlightbackground=BORDER)
        interval_entry.pack(side=tk.LEFT, padx=(0, 6))
        tk.Label(interval_row, text="minutes", bg=BG_CARD, fg=TEXT_MUTED,
                 font=("Segoe UI", 10)).pack(side=tk.LEFT)

        # ── Session Controls Card ────────────────────────────────────────
        session_card = self._make_card(self.page_container, "Session")

        btn_frame = tk.Frame(session_card, bg=BG_CARD)
        btn_frame.pack(fill=tk.X, padx=20, pady=(10, 16))

        self.start_btn = tk.Button(
            btn_frame, text="▶  Start Monitoring", font=("Segoe UI", 12, "bold"),
            bg=ACCENT, fg=BG_DARK, activebackground=ACCENT_DIM, activeforeground=BG_DARK,
            bd=0, padx=28, pady=10, cursor="hand2", command=self._start_monitoring
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 12))

        self.stop_btn = tk.Button(
            btn_frame, text="■  Stop", font=("Segoe UI", 12, "bold"),
            bg=ACCENT_WARN, fg=TEXT_PRIMARY, activebackground="#CC5555",
            bd=0, padx=28, pady=10, cursor="hand2", state=tk.DISABLED,
            command=self._stop_monitoring
        )
        self.stop_btn.pack(side=tk.LEFT)

        # Live info
        self.live_frame = tk.Frame(session_card, bg=BG_CARD)
        self.live_frame.pack(fill=tk.X, padx=20, pady=(0, 16))

        self.live_blinks_label = tk.Label(self.live_frame, text="Blinks: --", bg=BG_CARD,
                                          fg=ACCENT, font=("Consolas", 14, "bold"))
        self.live_blinks_label.pack(side=tk.LEFT, padx=(0, 30))

        self.live_ear_label = tk.Label(self.live_frame, text="EAR: --", bg=BG_CARD,
                                       fg=ACCENT, font=("Consolas", 14, "bold"))
        self.live_ear_label.pack(side=tk.LEFT, padx=(0, 30))

        self.live_elapsed_label = tk.Label(self.live_frame, text="Elapsed: --", bg=BG_CARD,
                                            fg=TEXT_SECONDARY, font=("Segoe UI", 11))
        self.live_elapsed_label.pack(side=tk.LEFT)

        # ── Live Mini-Chart Card ─────────────────────────────────────────
        chart_card = self._make_card(self.page_container, "Live Blink Rate")

        self.live_fig = Figure(figsize=(8, 2.2), dpi=100, facecolor=BG_CARD)
        self.live_ax = self.live_fig.add_subplot(111)
        self._style_axis(self.live_ax)
        self.live_ax.set_ylabel("BPM", color=TEXT_SECONDARY, fontsize=9)
        self.live_ax.set_ylim(0, 30)
        self.live_line, = self.live_ax.plot([], [], color=ACCENT, linewidth=2)
        self.live_threshold = self.live_ax.axhline(y=10, color=ACCENT_WARN,
                                                    linestyle="--", linewidth=1, alpha=0.6)
        self.live_fig.tight_layout(pad=1.5)

        self.live_canvas = FigureCanvasTkAgg(self.live_fig, master=chart_card)
        self.live_canvas.get_tk_widget().pack(fill=tk.X, padx=10, pady=(0, 10))

    # =====================================================================
    #  DASHBOARD PAGE
    # =====================================================================
    def _show_dashboard(self):
        self.current_page = "dashboard"
        self._highlight_nav("dashboard")
        self._clear_page()

        ttk.Label(self.page_container, text="Analytics Dashboard", style="Title.TLabel").pack(anchor="w")
        ttk.Label(self.page_container, text="Eye health insights from your recorded sessions",
                  style="Subtitle.TLabel").pack(anchor="w", pady=(2, 16))

        # Scrollable area
        canvas = tk.Canvas(self.page_container, bg=BG_DARK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.page_container, orient="vertical", command=canvas.yview)
        self.dash_scroll_frame = tk.Frame(canvas, bg=BG_DARK)

        self.dash_scroll_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.dash_scroll_frame, anchor="nw",
                             tags="inner")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Make the inner frame resize with the canvas
        def _resize_inner(event):
            canvas.itemconfig("inner", width=event.width)
        canvas.bind("<Configure>", _resize_inner)

        # Mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._populate_dashboard()

    def _populate_dashboard(self):
        parent = self.dash_scroll_frame

        # ── Fetch Data ───────────────────────────────────────────────────
        sessions = self.db.query(WorkSession).order_by(WorkSession.start_time.desc()).all()

        if not sessions:
            tk.Label(parent, text="No sessions recorded yet.\nStart a monitoring session first.",
                     bg=BG_DARK, fg=TEXT_MUTED, font=("Segoe UI", 14), justify="center").pack(pady=60)
            return

        all_logs = self.db.query(BlinkLog).order_by(BlinkLog.timestamp).all()
        all_events = self.db.query(Event).order_by(Event.timestamp).all()

        # Calculate statistics
        total_sessions = len(sessions)
        total_logs = len(all_logs)
        blink_rates = [l.blink_rate for l in all_logs]
        ear_values = [l.avg_ear for l in all_logs]

        avg_blink_rate = np.mean(blink_rates) if blink_rates else 0
        min_blink_rate = min(blink_rates) if blink_rates else 0
        max_blink_rate = max(blink_rates) if blink_rates else 0
        avg_ear = np.mean(ear_values) if ear_values else 0

        # Total monitoring time
        total_minutes = 0
        for s in sessions:
            if s.end_time and s.start_time:
                total_minutes += (s.end_time - s.start_time).total_seconds() / 60
            elif s.start_time:
                # Estimate from log count for the session
                s_logs = [l for l in all_logs if l.session_id == s.id]
                total_minutes += len(s_logs)

        # Dry eye risk minutes (blink rate < 10)
        dry_eye_minutes = len([r for r in blink_rates if r < 10])
        dry_eye_pct = (dry_eye_minutes / total_logs * 100) if total_logs > 0 else 0

        # ── Summary Stats Row ────────────────────────────────────────────
        stats_row = tk.Frame(parent, bg=BG_DARK)
        stats_row.pack(fill=tk.X, pady=(0, 16))

        stat_data = [
            ("Avg Blink Rate", f"{avg_blink_rate:.1f}", "blinks/min"),
            ("Avg EAR", f"{avg_ear:.3f}", "eye aspect ratio"),
            ("Sessions", str(total_sessions), "recorded"),
            ("Monitor Time", f"{total_minutes:.0f}", "minutes total"),
            ("Dry Eye Risk", f"{dry_eye_pct:.0f}%", f"{dry_eye_minutes} low-rate mins"),
        ]
        for i, (label, value, sub) in enumerate(stat_data):
            self._make_stat_card(stats_row, label, value, sub, i)

        # Configure columns to expand
        for i in range(len(stat_data)):
            stats_row.columnconfigure(i, weight=1)

        # ── Chart 1: Blink Rate Over Time (latest session) ──────────────
        latest = sessions[0]
        latest_logs = self.db.query(BlinkLog).filter_by(session_id=latest.id)\
                          .order_by(BlinkLog.timestamp).all()

        if latest_logs:
            chart1_card = self._make_card(parent, f"Blink Rate — Latest Session  "
                                          f"({latest.start_time.strftime('%b %d, %H:%M')})")

            fig1 = Figure(figsize=(9, 3), dpi=100, facecolor=BG_CARD)
            ax1 = fig1.add_subplot(111)
            self._style_axis(ax1)

            times = [l.timestamp for l in latest_logs]
            rates = [l.blink_rate for l in latest_logs]

            ax1.fill_between(times, rates, alpha=0.15, color=ACCENT)
            ax1.plot(times, rates, color=ACCENT, linewidth=2, marker="o", markersize=4)
            ax1.axhline(y=10, color=ACCENT_WARN, linestyle="--", linewidth=1, alpha=0.7,
                        label="Dry Eye Threshold")
            ax1.set_ylabel("Blinks / min", color=TEXT_SECONDARY, fontsize=9)
            ax1.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            ax1.legend(loc="upper right", fontsize=8, facecolor=BG_CARD,
                       edgecolor=BORDER, labelcolor=TEXT_SECONDARY)
            fig1.tight_layout(pad=1.5)

            canvas1 = FigureCanvasTkAgg(fig1, master=chart1_card)
            canvas1.get_tk_widget().pack(fill=tk.X, padx=10, pady=(0, 10))

        # ── Chart 2: EAR Over Time (latest session) ─────────────────────
        if latest_logs:
            chart2_card = self._make_card(parent, "Eye Openness (EAR) — Latest Session")

            fig2 = Figure(figsize=(9, 3), dpi=100, facecolor=BG_CARD)
            ax2 = fig2.add_subplot(111)
            self._style_axis(ax2)

            ears = [l.avg_ear for l in latest_logs]
            ax2.fill_between(times, ears, alpha=0.15, color="#6C63FF")
            ax2.plot(times, ears, color="#6C63FF", linewidth=2, marker="s", markersize=3)
            ax2.axhline(y=0.22, color=ACCENT_AMBER, linestyle="--", linewidth=1, alpha=0.7,
                        label="Fatigue Threshold")
            ax2.set_ylabel("Avg EAR", color=TEXT_SECONDARY, fontsize=9)
            ax2.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
            ax2.legend(loc="upper right", fontsize=8, facecolor=BG_CARD,
                       edgecolor=BORDER, labelcolor=TEXT_SECONDARY)
            fig2.tight_layout(pad=1.5)

            canvas2 = FigureCanvasTkAgg(fig2, master=chart2_card)
            canvas2.get_tk_widget().pack(fill=tk.X, padx=10, pady=(0, 10))

        # ── Chart 3: Blink Rate Distribution Histogram ──────────────────
        if blink_rates:
            chart3_card = self._make_card(parent, "Blink Rate Distribution — All Sessions")

            fig3 = Figure(figsize=(9, 2.8), dpi=100, facecolor=BG_CARD)
            ax3 = fig3.add_subplot(111)
            self._style_axis(ax3)

            bins = np.arange(0, max(blink_rates) + 3, 2)
            colors_hist = [ACCENT_WARN if b < 10 else ACCENT for b in bins[:-1]]
            n, _, patches = ax3.hist(blink_rates, bins=bins, edgecolor=BG_CARD, linewidth=0.8)
            for patch, c in zip(patches, colors_hist):
                patch.set_facecolor(c)
                patch.set_alpha(0.8)

            ax3.axvline(x=10, color=ACCENT_WARN, linestyle="--", linewidth=1, alpha=0.7)
            ax3.set_xlabel("Blinks / min", color=TEXT_SECONDARY, fontsize=9)
            ax3.set_ylabel("Frequency", color=TEXT_SECONDARY, fontsize=9)
            fig3.tight_layout(pad=1.5)

            canvas3 = FigureCanvasTkAgg(fig3, master=chart3_card)
            canvas3.get_tk_widget().pack(fill=tk.X, padx=10, pady=(0, 10))

        # ── Chart 4: Session-by-Session Average Blink Rate ──────────────
        if len(sessions) > 1:
            chart4_card = self._make_card(parent, "Average Blink Rate Across Sessions")

            fig4 = Figure(figsize=(9, 2.8), dpi=100, facecolor=BG_CARD)
            ax4 = fig4.add_subplot(111)
            self._style_axis(ax4)

            session_avgs = []
            session_labels = []
            for s in reversed(sessions):
                s_logs = [l for l in all_logs if l.session_id == s.id]
                if s_logs:
                    session_avgs.append(np.mean([l.blink_rate for l in s_logs]))
                    session_labels.append(s.start_time.strftime("%b %d\n%H:%M"))

            if session_avgs:
                bar_colors = [ACCENT_WARN if v < 10 else ACCENT for v in session_avgs]
                ax4.bar(range(len(session_avgs)), session_avgs, color=bar_colors, alpha=0.85,
                        width=0.6, edgecolor=BG_CARD)
                ax4.set_xticks(range(len(session_labels)))
                ax4.set_xticklabels(session_labels, fontsize=7, color=TEXT_MUTED)
                ax4.axhline(y=10, color=ACCENT_WARN, linestyle="--", linewidth=1, alpha=0.5)
                ax4.set_ylabel("Avg BPM", color=TEXT_SECONDARY, fontsize=9)
            fig4.tight_layout(pad=1.5)

            canvas4 = FigureCanvasTkAgg(fig4, master=chart4_card)
            canvas4.get_tk_widget().pack(fill=tk.X, padx=10, pady=(0, 10))

        # ── Chart 5: Fatigue Trend (EAR decline over session) ───────────
        if latest_logs and len(latest_logs) > 3:
            chart5_card = self._make_card(parent, "Fatigue Trend — Eye Openness Decline")

            fig5 = Figure(figsize=(9, 2.8), dpi=100, facecolor=BG_CARD)
            ax5 = fig5.add_subplot(111)
            self._style_axis(ax5)

            ears_arr = np.array([l.avg_ear for l in latest_logs])
            minutes = np.arange(len(ears_arr))

            # Rolling average
            window = min(5, len(ears_arr))
            rolling = np.convolve(ears_arr, np.ones(window) / window, mode="valid")
            roll_x = minutes[:len(rolling)]

            ax5.scatter(minutes, ears_arr, color="#6C63FF", alpha=0.4, s=18, zorder=3)
            ax5.plot(roll_x, rolling, color=ACCENT_AMBER, linewidth=2.5,
                     label=f"Rolling avg ({window}-min)", zorder=4)

            # Trend line
            if len(minutes) > 1:
                z = np.polyfit(minutes, ears_arr, 1)
                p = np.poly1d(z)
                ax5.plot(minutes, p(minutes), color=ACCENT_WARN, linewidth=1.5,
                         linestyle=":", alpha=0.7, label="Trend")

            ax5.set_xlabel("Minutes into session", color=TEXT_SECONDARY, fontsize=9)
            ax5.set_ylabel("Avg EAR", color=TEXT_SECONDARY, fontsize=9)
            ax5.legend(loc="upper right", fontsize=8, facecolor=BG_CARD,
                       edgecolor=BORDER, labelcolor=TEXT_SECONDARY)
            fig5.tight_layout(pad=1.5)

            canvas5 = FigureCanvasTkAgg(fig5, master=chart5_card)
            canvas5.get_tk_widget().pack(fill=tk.X, padx=10, pady=(0, 10))

        # ── Chart 6: Hourly Heatmap — when are eyes most strained ───────
        if len(all_logs) > 5:
            chart6_card = self._make_card(parent, "Hourly Eye Strain Heatmap")

            fig6 = Figure(figsize=(9, 2.2), dpi=100, facecolor=BG_CARD)
            ax6 = fig6.add_subplot(111)
            self._style_axis(ax6)

            hourly_rates = {}
            for l in all_logs:
                h = l.timestamp.hour
                hourly_rates.setdefault(h, []).append(l.blink_rate)

            hours = sorted(hourly_rates.keys())
            avg_rates = [np.mean(hourly_rates[h]) for h in hours]
            bar_colors6 = [ACCENT_WARN if v < 10 else ACCENT for v in avg_rates]

            ax6.bar(hours, avg_rates, color=bar_colors6, alpha=0.85, width=0.7)
            ax6.axhline(y=10, color=ACCENT_WARN, linestyle="--", linewidth=1, alpha=0.5)
            ax6.set_xlabel("Hour of Day", color=TEXT_SECONDARY, fontsize=9)
            ax6.set_ylabel("Avg BPM", color=TEXT_SECONDARY, fontsize=9)
            ax6.set_xticks(hours)
            ax6.set_xticklabels([f"{h}:00" for h in hours], fontsize=7, color=TEXT_MUTED)
            fig6.tight_layout(pad=1.5)

            canvas6 = FigureCanvasTkAgg(fig6, master=chart6_card)
            canvas6.get_tk_widget().pack(fill=tk.X, padx=10, pady=(0, 10))

        # ── Event Log Table ──────────────────────────────────────────────
        if all_events:
            events_card = self._make_card(parent, "Alert History")

            for i, ev in enumerate(all_events[-15:]):  # last 15 events
                color = ACCENT_WARN if "dry" in (ev.event_type or "").lower() else ACCENT_AMBER
                row = tk.Frame(events_card, bg=BG_CARD if i % 2 == 0 else BG_CARD_ALT)
                row.pack(fill=tk.X, padx=10, pady=1)
                tk.Label(row, text=ev.timestamp.strftime("%b %d %H:%M"),
                         bg=row["bg"], fg=TEXT_MUTED, font=("Consolas", 9),
                         width=14, anchor="w").pack(side=tk.LEFT, padx=(10, 6))
                tk.Label(row, text=ev.event_type or "—",
                         bg=row["bg"], fg=color, font=("Segoe UI", 9, "bold"),
                         width=20, anchor="w").pack(side=tk.LEFT)
                tk.Label(row, text=ev.action_taken or "",
                         bg=row["bg"], fg=TEXT_SECONDARY, font=("Segoe UI", 9),
                         anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)

            tk.Frame(events_card, bg=BG_CARD, height=10).pack()

    # =====================================================================
    #  MONITORING CONTROL
    # =====================================================================
    def _start_monitoring(self):
        if not self.enable_blink_alert.get() and not self.enable_20_20_20.get():
            messagebox.showwarning("OcularGuard",
                                   "Please enable at least one feature before starting.")
            return

        self.running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text="● Monitoring", fg=ACCENT)
        self.logo_dot.itemconfig(self.logo_dot_id, fill=ACCENT)

        # Reset counters
        self.blinks = 0
        self.blink_status = False
        self.ear_history = []
        self.last_blink_time = 0
        now = time.time()
        self.minute_start_time = now
        self.last_break_time = now
        self.smart_check_start = now
        self.smart_blinks = 0
        self.live_bpm_history.clear()
        self.live_ear_history.clear()
        self.live_time_labels.clear()
        self.session_start_wall = time.time()

        # Read break interval from UI (fallback to 20 minutes if invalid)
        try:
            minutes = float(self.break_interval_var.get())
            if minutes <= 0:
                raise ValueError
            self.BREAK_INTERVAL = minutes * 60
        except (ValueError, AttributeError):
            self.BREAK_INTERVAL = 20 * 60

        # Create DB session
        new_session = WorkSession()
        self.db.add(new_session)
        self.db.commit()
        self.db.refresh(new_session)
        self.current_session = new_session

        # Start camera in thread
        self.camera_thread = threading.Thread(target=self._camera_loop, daemon=True)
        self.camera_thread.start()

        # Start UI update loop
        self._update_live_ui()

    def _stop_monitoring(self):
        self.running = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="● Idle", fg=TEXT_MUTED)
        self.logo_dot.itemconfig(self.logo_dot_id, fill=TEXT_MUTED)

        if self.current_session:
            self.current_session.end_time = datetime.utcnow()
            self.db.commit()
            self.current_session = None

    def _camera_loop(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.root.after(0, lambda: messagebox.showerror(
                "OcularGuard", "Could not open camera. Check permissions."))
            self.root.after(0, self._stop_monitoring)
            return

        while self.running:
            ret, frame = cap.read()
            if not ret:
                break

            result = self.tracker.process_frame(frame)
            if result:
                left, right, avg = result
                self.ear_history.append(avg)

                # Blink detection
                if avg < self.EAR_THRESHOLD:
                    self.blink_status = True
                else:
                    if self.blink_status:
                        if (time.time() - self.last_blink_time) > self.BLINK_COOLDOWN:
                            self.blinks += 1
                            self.smart_blinks += 1
                            self.last_blink_time = time.time()
                        self.blink_status = False

            current_time = time.time()

            # Smart blink alert
            if self.enable_blink_alert.get():
                if current_time - self.smart_check_start >= self.SMART_CHECK_INTERVAL:
                    if self.smart_blinks < 3:
                        estimated_bpm = self.smart_blinks * (60 / self.SMART_CHECK_INTERVAL)
                        NotificationManager.alert_dry_eyes(int(estimated_bpm))
                        # Log event
                        self._log_event("Dry Eye Alert",
                                        f"Low blink rate: {int(estimated_bpm)} BPM")
                    self.smart_blinks = 0
                    self.smart_check_start = current_time

            # 20-20-20 rule
            if self.enable_20_20_20.get():
                if current_time - self.last_break_time >= self.BREAK_INTERVAL:
                    NotificationManager.alert_20_20_20()
                    self._log_event("20-20-20 Reminder", "Break prompted")
                    self.last_break_time = current_time

            # Per-minute DB logging
            if current_time - self.minute_start_time >= 60:
                bpm = self.blinks
                avg_ear = float(np.mean(self.ear_history)) if self.ear_history else 0.0

                self.live_bpm_history.append(bpm)
                self.live_ear_history.append(avg_ear)
                self.live_time_labels.append(datetime.now().strftime("%H:%M"))

                self._log_minute_data(bpm, avg_ear)
                self.blinks = 0
                self.minute_start_time = current_time
                self.ear_history = []

            time.sleep(0.01)  # Small sleep to avoid CPU spin

        cap.release()

    def _log_minute_data(self, bpm, avg_ear):
        if not self.current_session:
            return
        log = BlinkLog(
            session_id=self.current_session.id,
            blink_rate=bpm,
            avg_ear=float(avg_ear)
        )
        self.db.add(log)
        self.db.commit()

    def _log_event(self, event_type, action):
        if not self.current_session:
            return
        ev = Event(
            session_id=self.current_session.id,
            event_type=event_type,
            action_taken=action
        )
        self.db.add(ev)
        self.db.commit()

    def _update_live_ui(self):
        if not self.running:
            return

        # Update labels
        current_ear = self.ear_history[-1] if self.ear_history else 0
        self.live_blinks_label.config(text=f"Blinks: {self.blinks}")
        self.live_ear_label.config(text=f"EAR: {current_ear:.3f}")
        elapsed = int(time.time() - self.session_start_wall)
        m, s = divmod(elapsed, 60)
        self.live_elapsed_label.config(text=f"Elapsed: {m:02d}:{s:02d}")

        # Update live chart
        if self.live_bpm_history and self.current_page == "control":
            self.live_line.set_data(range(len(self.live_bpm_history)),
                                    list(self.live_bpm_history))
            self.live_ax.set_xlim(0, max(len(self.live_bpm_history), 10))
            y_max = max(max(self.live_bpm_history), 15)
            self.live_ax.set_ylim(0, y_max + 5)
            try:
                self.live_canvas.draw_idle()
            except Exception:
                pass

        self.root.after(500, self._update_live_ui)

    # =====================================================================
    #  HELPERS
    # =====================================================================
    def _make_card(self, parent, title):
        outer = tk.Frame(parent, bg=BORDER, padx=1, pady=1)
        outer.pack(fill=tk.X, pady=(0, 14))

        card = tk.Frame(outer, bg=BG_CARD)
        card.pack(fill=tk.BOTH, expand=True)

        tk.Label(card, text=title, bg=BG_CARD, fg=TEXT_PRIMARY,
                 font=("Segoe UI", 13, "bold"), anchor="w").pack(
            fill=tk.X, padx=20, pady=(14, 4))

        return card

    def _make_stat_card(self, parent, label, value, sub, col):
        outer = tk.Frame(parent, bg=BORDER, padx=1, pady=1)
        outer.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else 6, 0))

        card = tk.Frame(outer, bg=BG_CARD)
        card.pack(fill=tk.BOTH, expand=True)

        tk.Label(card, text=label, bg=BG_CARD, fg=TEXT_SECONDARY,
                 font=("Segoe UI", 9)).pack(anchor="w", padx=16, pady=(12, 0))
        tk.Label(card, text=value, bg=BG_CARD, fg=ACCENT,
                 font=("Consolas", 24, "bold")).pack(anchor="w", padx=16)
        tk.Label(card, text=sub, bg=BG_CARD, fg=TEXT_MUTED,
                 font=("Segoe UI", 8)).pack(anchor="w", padx=16, pady=(0, 12))

    def _style_axis(self, ax):
        ax.set_facecolor(BG_CARD)
        ax.tick_params(colors=TEXT_MUTED, labelsize=8)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_color(BORDER)
        ax.spines["left"].set_color(BORDER)
        ax.grid(axis="y", color=BORDER, linewidth=0.5, alpha=0.5)

    def _on_close(self):
        self.running = False
        if self.current_session:
            self.current_session.end_time = datetime.utcnow()
            self.db.commit()
        self.root.destroy()


def launch():
    root = tk.Tk()
    app = OcularGuardApp(root)
    root.mainloop()


if __name__ == "__main__":
    launch()
