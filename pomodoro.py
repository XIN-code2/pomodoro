#!/usr/bin/env python3
"""A multi-preset Pomodoro timer built with tkinter."""

import tkinter as tk
from tkinter import font as tkfont

FOCUS_PRESETS = [15, 25, 30, 45, 60]
BREAK_PRESETS = [3, 5, 10, 15]
DEFAULT_FOCUS = 25
DEFAULT_BREAK = 5

# Deep dark color palette
BG           = "#0f0f14"
FRAME_BG     = "#1a1a24"
TITLE_FG     = "#c4c8da"
SUBTLE_FG    = "#565970"
FOCUS_RED    = "#d64550"
BREAK_GREEN  = "#35a05d"
START_GREEN  = "#35a05d"
PAUSE_AMBER  = "#c78a1c"
RESET_RED    = "#c23b44"
PRESET_OFF   = "#252535"
PRESET_ON    = "#2961d5"
COUNTER_FG   = "#6e7290"
BTN_TEXT     = "#0f0f14"

FOCUS_HOVER  = "#2a9b50"
PAUSE_HOVER  = "#b07a15"
RESET_HOVER  = "#af313a"
PRESET_HOVER = "#33334a"


class PomodoroApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("番茄钟")
        self.root.resizable(False, False)

        self.mode = "focus"
        self.state = "idle"
        self.focus_minutes = DEFAULT_FOCUS
        self.break_minutes = DEFAULT_BREAK
        self.remaining = self.focus_minutes * 60
        self.tomatoes = 0
        self._job = None

        self._build_ui()
        self._center_window()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        self.root.configure(bg=BG)

        title_font = tkfont.Font(family="Helvetica", size=18, weight="bold")
        timer_font = tkfont.Font(family="Helvetica", size=56, weight="bold")
        label_font = tkfont.Font(family="Helvetica", size=13)
        small_font = tkfont.Font(family="Helvetica", size=11)
        preset_font = tkfont.Font(family="Helvetica", size=10, weight="bold")

        # Title
        tk.Label(
            self.root, text="🍅 番茄钟", font=title_font,
            fg=TITLE_FG, bg=BG
        ).pack(pady=(20, 6))

        # ---- Focus presets ----
        tk.Label(
            self.root, text="专注时长（分钟）", font=small_font,
            fg=SUBTLE_FG, bg=BG
        ).pack()

        focus_frame = tk.Frame(self.root, bg=BG)
        focus_frame.pack(pady=(4, 8))
        self.focus_btns = []
        for m in FOCUS_PRESETS:
            btn = tk.Button(
                focus_frame, text=str(m), font=preset_font, width=4,
                bg=PRESET_OFF, fg=TITLE_FG, activebackground=PRESET_HOVER,
                activeforeground=TITLE_FG,
                relief="flat", bd=0, padx=3, pady=3,
                command=lambda v=m: self._set_focus(v)
            )
            btn.pack(side="left", padx=3)
            self.focus_btns.append((m, btn))

        # ---- Break presets ----
        tk.Label(
            self.root, text="休息时长（分钟）", font=small_font,
            fg=SUBTLE_FG, bg=BG
        ).pack()

        break_frame = tk.Frame(self.root, bg=BG)
        break_frame.pack(pady=(4, 8))
        self.break_btns = []
        for m in BREAK_PRESETS:
            btn = tk.Button(
                break_frame, text=str(m), font=preset_font, width=4,
                bg=PRESET_OFF, fg=TITLE_FG, activebackground=PRESET_HOVER,
                activeforeground=TITLE_FG,
                relief="flat", bd=0, padx=3, pady=3,
                command=lambda v=m: self._set_break(v)
            )
            btn.pack(side="left", padx=3)
            self.break_btns.append((m, btn))

        # ---- Timer display ----
        self.timer_frame = tk.Frame(self.root, bg=FRAME_BG, highlightthickness=0)
        self.timer_frame.pack(padx=40, pady=4, ipadx=30, ipady=12)

        self.timer_label = tk.Label(
            self.timer_frame, text="25:00", font=timer_font,
            fg=FOCUS_RED, bg=FRAME_BG
        )
        self.timer_label.pack()

        self.mode_label = tk.Label(
            self.timer_frame, text="专注时间", font=label_font,
            fg=SUBTLE_FG, bg=FRAME_BG
        )
        self.mode_label.pack(pady=(0, 8))

        # ---- Control buttons ----
        ctrl_frame = tk.Frame(self.root, bg=BG)
        ctrl_frame.pack(pady=12)

        ctrl_font = tkfont.Font(family="Helvetica", size=12, weight="bold")

        self.start_btn = tk.Button(
            ctrl_frame, text="开始", font=ctrl_font, width=6,
            bg=START_GREEN, fg=BTN_TEXT, activebackground=FOCUS_HOVER,
            relief="flat", bd=0, padx=4, pady=6,
            command=self.start
        )
        self.start_btn.pack(side="left", padx=6)

        self.pause_btn = tk.Button(
            ctrl_frame, text="暂停", font=ctrl_font, width=6,
            bg=PAUSE_AMBER, fg=BTN_TEXT, activebackground=PAUSE_HOVER,
            relief="flat", bd=0, padx=4, pady=6,
            command=self.pause
        )
        self.pause_btn.pack(side="left", padx=6)

        self.reset_btn = tk.Button(
            ctrl_frame, text="重置", font=ctrl_font, width=6,
            bg=RESET_RED, fg=BTN_TEXT, activebackground=RESET_HOVER,
            relief="flat", bd=0, padx=4, pady=6,
            command=self.reset
        )
        self.reset_btn.pack(side="left", padx=6)

        # ---- Counter ----
        self.counter_label = tk.Label(
            self.root, text="已完成: 0 个番茄", font=small_font,
            fg=COUNTER_FG, bg=BG
        )
        self.counter_label.pack(pady=(2, 16))

        self._update_preset_highlights()
        self._update_display()

    def _center_window(self):
        w, h = 420, 480
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        x = (ws - w) // 2
        y = (hs - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _set_focus(self, minutes):
        if self.state != "idle":
            return
        self.focus_minutes = minutes
        if self.mode == "focus":
            self.remaining = minutes * 60
        self._update_preset_highlights()
        self._update_display()

    def _set_break(self, minutes):
        if self.state != "idle":
            return
        self.break_minutes = minutes
        if self.mode == "break":
            self.remaining = minutes * 60
        self._update_preset_highlights()
        self._update_display()

    def _update_preset_highlights(self):
        for m, btn in self.focus_btns:
            btn.config(bg=PRESET_ON if m == self.focus_minutes else PRESET_OFF)
        for m, btn in self.break_btns:
            btn.config(bg=PRESET_ON if m == self.break_minutes else PRESET_OFF)

    def _fmt_time(self):
        m = self.remaining // 60
        s = self.remaining % 60
        return f"{m:02d}:{s:02d}"

    def _update_display(self):
        self.timer_label.config(text=self._fmt_time())
        self.mode_label.config(
            text="专注时间" if self.mode == "focus" else "休息时间"
        )
        if self.mode == "focus":
            self.timer_label.config(fg=FOCUS_RED)
        else:
            self.timer_label.config(fg=BREAK_GREEN)

    def tick(self):
        if self.remaining > 0:
            self.remaining -= 1
            self._update_display()
        if self.remaining == 0:
            self._switch_mode()
            self.start()
        else:
            self._job = self.root.after(1000, self.tick)

    def _switch_mode(self):
        if self.mode == "focus":
            self.mode = "break"
            self.remaining = self.break_minutes * 60
            self.tomatoes += 1
            self.counter_label.config(text=f"已完成: {self.tomatoes} 个番茄")
        else:
            self.mode = "focus"
            self.remaining = self.focus_minutes * 60
        self.state = "idle"
        self._job = None
        self._update_display()

    def start(self):
        if self.state == "running":
            return
        if self._job is not None:
            self.root.after_cancel(self._job)
        self.state = "running"
        self._update_display()
        self._job = self.root.after(1000, self.tick)

    def pause(self):
        if self.state != "running":
            return
        if self._job is not None:
            self.root.after_cancel(self._job)
            self._job = None
        self.state = "paused"

    def reset(self):
        if self._job is not None:
            self.root.after_cancel(self._job)
            self._job = None
        self.state = "idle"
        self.mode = "focus"
        self.remaining = self.focus_minutes * 60
        self._update_display()

    def _on_close(self):
        if self._job is not None:
            self.root.after_cancel(self._job)
        self.root.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = PomodoroApp()
    app.run()
