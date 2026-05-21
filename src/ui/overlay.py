"""
overlay.py — Notification popup for OcularGuard.



WHY: PyQt6 dialogs MUST be created and shown on the main thread.
When called from a background camera thread (even via threading.Thread),
PyQt6 performs an immediate abort in a frozen PyInstaller exe because
Qt detects the GUI call is not on the main thread.

tkinter Toplevels are safe to *schedule* from any thread via
root.after(0, callback) — the callback executes on the main thread
in the next event-loop tick. The app.py camera loop already uses
root.after() for this pattern, so we follow the same approach here.

The _root reference is set once by app.py when the window is created.
"""

import tkinter as tk

# Module-level reference to the main Tk root — set by app.py at startup.
_root = None


def set_root(root):
    """Called once from app.py after Tk() is created."""
    global _root
    _root = root


# Colour tokens (match app.py palette)
_WARN_BG     = "#2D0A0A"
_WARN_BORDER = "#991b1b"
_WARN_ACCENT = "#FF6B6B"

_INFO_BG     = "#0D1B2A"
_INFO_BORDER = "#475569"
_INFO_ACCENT = "#00D4AA"

_TEXT = "#E8ECF1"


class _OverlayPopup:
    """
    Frameless, always-on-top toast notification.
    Positioned in the bottom-right corner of the screen.
    Auto-dismisses after timeout_ms milliseconds.
    """

    def __init__(self, root, title, message, is_warning, timeout_ms=8000):
        self.root = root

        bg     = _WARN_BG     if is_warning else _INFO_BG
        border = _WARN_BORDER if is_warning else _INFO_BORDER
        accent = _WARN_ACCENT if is_warning else _INFO_ACCENT
        icon   = "⚠" if is_warning else "🕒"

        # Window setup
        self.win = tk.Toplevel(root)
        self.win.overrideredirect(True)       # frameless
        self.win.attributes("-topmost", True) # always on top
        self.win.configure(bg=border)         # 1-px border via bg colour

        # Outer border frame
        outer = tk.Frame(self.win, bg=border, padx=1, pady=1)
        outer.pack(fill=tk.BOTH, expand=True)

        inner = tk.Frame(outer, bg=bg, padx=16, pady=12)
        inner.pack(fill=tk.BOTH, expand=True)

        # Header row
        header = tk.Frame(inner, bg=bg)
        header.pack(fill=tk.X, pady=(0, 6))

        tk.Label(header, text=icon, bg=bg, fg=accent,
                 font=("Segoe UI Emoji", 14)).pack(side=tk.LEFT, padx=(0, 8))

        tk.Label(header, text=title, bg=bg, fg=accent,
                 font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT)

        tk.Button(header, text="✕", bg=bg, fg="#4A5568",
                  activebackground=bg, activeforeground=_TEXT,
                  font=("Segoe UI", 10, "bold"),
                  bd=0, cursor="hand2",
                  command=self._dismiss).pack(side=tk.RIGHT)

        # Message
        tk.Label(inner, text=message, bg=bg, fg=_TEXT,
                 font=("Segoe UI", 10), justify=tk.LEFT,
                 wraplength=320).pack(anchor="w", pady=(0, 10))

        # OK button
        btn_row = tk.Frame(inner, bg=bg)
        btn_row.pack(fill=tk.X)

        tk.Button(btn_row, text="OK", bg="#1E2633", fg=_TEXT,
                  activebackground="#2A3444", activeforeground=_TEXT,
                  font=("Segoe UI", 9, "bold"),
                  bd=0, padx=20, pady=5, cursor="hand2",
                  command=self._dismiss,
                  highlightthickness=1,
                  highlightbackground=border,
                  highlightcolor=accent).pack(side=tk.RIGHT)

        # Position bottom-right
        self.win.update_idletasks()
        sw = self.win.winfo_screenwidth()
        sh = self.win.winfo_screenheight()
        w  = self.win.winfo_reqwidth()
        h  = self.win.winfo_reqheight()
        margin = 24
        self.win.geometry(f"{w}x{h}+{sw - w - margin}+{sh - h - margin - 48}")

        # Auto-dismiss
        self._after_id = self.win.after(timeout_ms, self._dismiss)

    def _dismiss(self):
        try:
            self.win.after_cancel(self._after_id)
        except Exception:
            pass
        try:
            self.win.destroy()
        except Exception:
            pass


def show_overlay(title, message, is_warning):
    """
    Schedule a popup on the main tkinter thread.
    Safe to call from any background thread.
    """
    if _root is None:
        print(f"[OcularGuard] Popup skipped (no root): {title}")
        return

    def _create():
        try:
            _OverlayPopup(_root, title, message, is_warning)
        except Exception as e:
            print(f"[OcularGuard] Popup error: {e}")

    # after(0, ...) posts to the main event loop — safe from any thread
    _root.after(0, _create)


def show_overlay_process(title, message, is_warning):
    """Backwards-compatible name used by alerts.py."""
    show_overlay(title, message, is_warning)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Overlay Test")
    set_root(root)
    root.after(300,  lambda: show_overlay(
        "DRY EYE ALERT",
        "Your blink rate is critically low (2 BPM).\nSTOP and blink 5 times now.",
        is_warning=True))
    root.after(1200, lambda: show_overlay(
        "20-20-20 Rule",
        "Time to look away!\n\nLook 20 feet away for 20 seconds.",
        is_warning=False))
    root.mainloop()
