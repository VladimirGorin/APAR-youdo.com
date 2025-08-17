import tkinter as tk
import json
import os
import config.settings as SETTINGS


class StatsApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Статистика откликов")
        self.root.geometry("400x120")
        self.root.config(bg="#f0f0f0")

        # Label to show the count
        self.stats_label = tk.Label(self.root, text="Общее количество откликов: 0",
                                    font=("Arial", 12), bg="#f0f0f0")
        self.stats_label.pack(pady=20)

        # Refresh button
        self.refresh_button = tk.Button(self.root, text="Перезагрузить", font=("Arial", 12, "bold"),
                                        bg="#2196F3", fg="white", relief="ridge",
                                        command=self.update_stats)
        self.refresh_button.pack(pady=10)

        # Initial load
        self.update_stats()

        self.root.mainloop()

    def update_stats(self):
        """Update the count and slider"""

        count = SETTINGS.load_stats().get("all", 0)
        self.stats_label.config(text=f"Общее количество откликов: {count}")


if __name__ == "__main__":
    try:
        StatsApp()
    except KeyboardInterrupt:
        print("\nBye Bye.")
