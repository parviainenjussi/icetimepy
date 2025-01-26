import tkinter as tk
from tkinter import messagebox
from tkinter.ttk import Style
import time
import threading
import pygame

class IceHockeyTimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ice Hockey Game Timer")
        self.root.configure(bg="#f0f0f0")

        # Initialize pygame for sound playback
        pygame.mixer.init()

        # Variables
        self.offset_seconds = tk.IntVar(value=10)
        self.interval_seconds = tk.IntVar(value=120)
        self.total_minutes = tk.IntVar(value=24)
        self.clock_direction = tk.StringVar(value="down")

        self.running = False
        self.elapsed_time = 0
        self.next_horn_time = 0
        self.ten_min_horn_played = False

        # Style Configuration
        style = Style()
        style.configure("TLabel", background="#f0f0f0", font=("Arial", 12), foreground="#333")
        style.configure("TButton", font=("Arial", 12), padding=5)
        style.map("TButton", background=[("active", "#0056b3"), ("!active", "#007bff")], foreground=[("active", "white")])

        # GUI Layout
        container = tk.Frame(root, bg="#ffffff", bd=10, relief=tk.RIDGE)
        container.pack(pady=20, padx=20)

        tk.Label(container, text="Starting Offset (Seconds):", bg="#ffffff", fg="#333", font=("Arial", 10)).pack(anchor="w", pady=5)
        self.offset_entry = tk.Entry(container, textvariable=self.offset_seconds, font=("Arial", 10), bg="#e9ecef", relief=tk.GROOVE)
        self.offset_entry.pack(fill="x", pady=5)
        self.offset_entry.bind("<KeyRelease>", self.update_parameters)

        tk.Label(container, text="Horn Interval (Seconds):", bg="#ffffff", fg="#333", font=("Arial", 10)).pack(anchor="w", pady=5)
        self.interval_entry = tk.Entry(container, textvariable=self.interval_seconds, font=("Arial", 10), bg="#e9ecef", relief=tk.GROOVE)
        self.interval_entry.pack(fill="x", pady=5)
        self.interval_entry.bind("<KeyRelease>", self.update_parameters)

        tk.Label(container, text="Total Time (Minutes):", bg="#ffffff", fg="#333", font=("Arial", 10)).pack(anchor="w", pady=5)
        self.total_time_entry = tk.Entry(container, textvariable=self.total_minutes, font=("Arial", 10), bg="#e9ecef", relief=tk.GROOVE)
        self.total_time_entry.pack(fill="x", pady=5)
        self.total_time_entry.bind("<KeyRelease>", self.update_parameters)

        tk.Label(container, text="Clock Direction:", bg="#ffffff", fg="#333", font=("Arial", 10)).pack(anchor="w", pady=5)
        self.direction_menu = tk.OptionMenu(container, self.clock_direction, "down", "up", command=self.update_parameters)
        self.direction_menu.pack(fill="x", pady=5)

        self.start_button = tk.Button(container, text="Start", command=self.start_timer, bg="#007bff", fg="white", font=("Arial", 12), relief=tk.RAISED, activebackground="#0056b3")
        self.start_button.pack(fill="x", pady=10)

        self.stop_button = tk.Button(container, text="Stop", command=self.stop_timer, state=tk.DISABLED, bg="#dc3545", fg="white", font=("Arial", 12), relief=tk.RAISED, activebackground="#a71d2a")
        self.stop_button.pack(fill="x", pady=10)

        self.play_horn_button = tk.Button(container, text="Play Horn Sound", command=self.play_horn_sound, bg="#6c757d", fg="white", font=("Arial", 12), relief=tk.RAISED, activebackground="#5a6268")
        self.play_horn_button.pack(fill="x", pady=10)

        self.elapsed_time_label = tk.Label(container, text="00:00/24:00", bg="#e9ecef", fg="#333", font=("Arial", 14), relief=tk.SUNKEN, anchor="center")
        self.elapsed_time_label.pack(fill="x", pady=10)

        self.next_horn_label = tk.Label(container, text="Next Horn Sound at: --:--", bg="#e9ecef", fg="#333", font=("Arial", 12), relief=tk.SUNKEN, anchor="center")
        self.next_horn_label.pack(fill="x", pady=10)

        # Initialize display
        self.update_parameters()

    def start_timer(self):
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.direction_menu.config(state=tk.DISABLED)
        self.offset_entry.config(state=tk.DISABLED)
        self.interval_entry.config(state=tk.DISABLED)
        self.total_time_entry.config(state=tk.DISABLED)
        total_seconds = self.total_minutes.get() * 60

        if self.clock_direction.get() == "down":
            self.elapsed_time = total_seconds - self.offset_seconds.get()
        else:
            self.elapsed_time = self.offset_seconds.get()

        self.next_horn_time = ((self.elapsed_time // self.interval_seconds.get()) + 1) * self.interval_seconds.get()
        self.ten_min_horn_played = False
        threading.Thread(target=self.run_timer).start()

    def stop_timer(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.direction_menu.config(state=tk.NORMAL)
        self.offset_entry.config(state=tk.NORMAL)
        self.interval_entry.config(state=tk.NORMAL)
        self.total_time_entry.config(state=tk.NORMAL)
        self.elapsed_time = 0
        self.update_display(self.total_minutes.get() * 60)

    def run_timer(self):
        total_seconds = self.total_minutes.get() * 60
        interval = self.interval_seconds.get()

        while self.running and (self.elapsed_time <= total_seconds if self.clock_direction.get() == "up" else self.elapsed_time >= 0):
            self.update_display(total_seconds)

            # Specific horn at 10 minutes left
            if not self.ten_min_horn_played and self.clock_direction.get() == "down" and self.elapsed_time <= total_seconds - 600:
                self.play_horn_sound()
                self.ten_min_horn_played = True

            # Interval-based horns
            if self.elapsed_time >= self.next_horn_time:
                self.play_horn_sound()
                self.next_horn_time += interval

            time.sleep(1)
            self.elapsed_time += 1 if self.clock_direction.get() == "up" else -1

        self.stop_timer()

    def update_display(self, total_seconds):
        minutes, seconds = divmod(abs(self.elapsed_time), 60)
        total_minutes, total_secs = divmod(total_seconds, 60)
        self.elapsed_time_label.config(
            text=f"{minutes:02}:{seconds:02}/{total_minutes:02}:{total_secs:02}"
        )

        if self.next_horn_time > total_seconds:
            self.next_horn_label.config(text="Next Horn Sound at: --:--")
        else:
            next_minutes, next_seconds = divmod(self.next_horn_time, 60)
            self.next_horn_label.config(text=f"Next Horn Sound at: {next_minutes:02}:{next_seconds:02}")

    def play_horn_sound(self):
        try:
            pygame.mixer.music.load("horn.wav")
            pygame.mixer.music.play()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to play sound: {e}")

    def update_parameters(self, event=None):
        total_seconds = self.total_minutes.get() * 60
        if self.clock_direction.get() == "down":
            self.elapsed_time = total_seconds - self.offset_seconds.get()
        else:
            self.elapsed_time = self.offset_seconds.get()
        self.next_horn_time = ((self.elapsed_time // self.interval_seconds.get()) + 1) * self.interval_seconds.get()
        self.update_display(total_seconds)

if __name__ == "__main__":
    root = tk.Tk()
    app = IceHockeyTimerApp(root)
    root.mainloop()
