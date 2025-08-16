import tkinter as tk
import json
import os


class StatsApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Статистика откликов")
        self.root.geometry("400x120")
        self.root.config(bg="#f0f0f0")

        # JSON file with data
        self.filename = "./data/monitoring_tasks.json"
        if not os.path.exists(self.filename):
            os.makedirs(os.path.dirname(self.filename), exist_ok=True)
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)

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
        with open(self.filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        count = len(data)
        self.stats_label.config(text=f"Общее количество откликов: {count}")


if __name__ == "__main__":
    try:
        StatsApp()
    except KeyboardInterrupt:
        print("\nBye Bye.")
