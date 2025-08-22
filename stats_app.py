import tkinter as tk
from tkinter import ttk
import webbrowser
from datetime import datetime
import config.settings as SETTINGS


class StatsApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Статистика откликов")
        self.root.geometry("700x400")
        self.root.config(bg="#f0f0f0")

        # Frame for table + scrollbars
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Table
        columns = ("date", "responded", "title", "link")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        # Headings
        self.tree.heading("date", text="Дата", command=lambda: self.sort_column("date", False))
        self.tree.heading("responded", text="Ответил", command=lambda: self.sort_column("responded", False))
        self.tree.heading("title", text="Задача", command=lambda: self.sort_column("title", False))
        self.tree.heading("link", text="Ссылка", command=lambda: self.sort_column("link", False))

        # Column widths
        self.tree.column("date", width=180, anchor="center")
        self.tree.column("responded", width=80, anchor="center")
        self.tree.column("title", width=250, anchor="w")
        self.tree.column("link", width=180, anchor="center")

        # Scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Grid layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        # Open link on double click
        self.tree.bind("<Double-1>", self.on_item_click)

        # Refresh button
        self.refresh_button = tk.Button(
            self.root,
            text="Перезагрузить",
            font=("Arial", 12, "bold"),
            bg="#2196F3",
            fg="white",
            relief="ridge",
            command=self.update_stats
        )
        self.refresh_button.pack(pady=5)

        # Initial load
        self.update_stats()

        self.root.mainloop()

    def update_stats(self):
        """Load stats array and update the table"""
        for row in self.tree.get_children():
            self.tree.delete(row)

        stats = SETTINGS.load_stats()
        for item in stats:
            self.tree.insert(
                "",
                "end",
                values=(
                    item["date"],
                    "Да" if item["responded"] else "Нет",
                    item["task"]["title"],
                    item["task"]["link"]
                )
            )

    def on_item_click(self, event):
        """Open link in browser on double click"""
        item_id = self.tree.selection()
        if not item_id:
            return
        values = self.tree.item(item_id, "values")
        link = values[3]
        if link.startswith("http"):
            webbrowser.open(link)

    def sort_column(self, col, reverse):
        """Sort table by column"""
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        if col == "date":
            items.sort(key=lambda x: datetime.strptime(x[0], "%Y-%m-%d %H:%M:%S"), reverse=reverse)
        else:
            items.sort(reverse=reverse)

        for index, (val, k) in enumerate(items):
            self.tree.move(k, "", index)

        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))


if __name__ == "__main__":
    StatsApp()
