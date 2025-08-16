import tkinter as tk
from tkinter import messagebox
import json
import os


class WordApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Сборник слов")
        self.root.geometry("400x400")
        self.root.config(bg="#f0f0f0")

        # Label above the input
        self.label = tk.Label(self.root, text="Введите слово:",
                              font=("Arial", 12), bg="#f0f0f0")
        self.label.pack(pady=10)

        # Input field
        self.entry = tk.Entry(self.root, font=("Arial", 12), width=25)
        self.entry.pack(pady=5)

        # Add button
        self.button = tk.Button(
            self.root, text="Добавить", font=("Arial", 12, "bold"),
            bg="#4CAF50", fg="white", relief="ridge", command=self.add_word
        )
        self.button.pack(pady=10)

        # Frame for Listbox + Scrollbar
        self.list_frame = tk.Frame(self.root)
        self.list_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        # Scrollbar
        self.scrollbar = tk.Scrollbar(self.list_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Listbox
        self.listbox = tk.Listbox(
            self.list_frame, font=("Arial", 12), yscrollcommand=self.scrollbar.set
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.listbox.yview)

        # Delete button
        self.del_button = tk.Button(
            self.root, text="× Удалить выбранное", font=("Arial", 12),
            bg="#f44336", fg="white", relief="ridge", command=self.delete_word
        )
        self.del_button.pack(pady=5)

        # JSON file for storing words
        self.filename = "./data/ban_words.json"
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
        if not os.path.exists(self.filename):
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)

        # Load existing words into listbox
        self.load_words()

        self.root.mainloop()

    def load_words(self):
        """Load words from JSON into the listbox."""
        with open(self.filename, "r", encoding="utf-8") as f:
            words = json.load(f)
        self.listbox.delete(0, tk.END)
        for w in words:
            self.listbox.insert(tk.END, w)

    def add_word(self):
        """Add a word to the JSON file and listbox."""
        word = self.entry.get().strip()
        if not word:
            messagebox.showwarning("Внимание", "Введите слово!")
            return

        with open(self.filename, "r", encoding="utf-8") as f:
            words = json.load(f)

        if word in words:
            messagebox.showinfo("Информация", f"Слово '{word}' уже существует!")
            return

        words.append(word)
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(words, f, ensure_ascii=False, indent=2)

        self.listbox.insert(tk.END, word)
        self.entry.delete(0, tk.END)

    def delete_word(self):
        """Delete selected word from JSON file and listbox."""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите слово для удаления!")
            return

        index = selection[0]
        word = self.listbox.get(index)

        with open(self.filename, "r", encoding="utf-8") as f:
            words = json.load(f)

        words.remove(word)
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(words, f, ensure_ascii=False, indent=2)

        self.listbox.delete(index)


if __name__ == "__main__":
    try:
        WordApp()
    except KeyboardInterrupt:
        print("\nBye Bye.")
