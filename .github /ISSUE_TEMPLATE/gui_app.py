import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import webbrowser
import urllib.request
import json
import urllib.parse
import os

def open_url(url):
    webbrowser.open_new(url)

# --- ГЛАВНОЕ ОКНО ---
root = tk.Tk()
root.title("shadPS4 Compatibility Explorer")
root.geometry("650x900")
root.configure(bg="#1e1e1e")

issues_data, links = [], []

# --- ОКНО ОТЧЕТА ---
def open_registration_window():
    reg_window = tk.Toplevel(root)
    reg_window.title("New Compatibility Report")
    reg_window.geometry("620x980")
    reg_window.configure(bg="#1e1e1e")

    main_frame = tk.Frame(reg_window, bg="#1e1e1e")
    main_frame.pack(fill=tk.BOTH, expand=1, padx=25, pady=15)

    tk.Label(main_frame, text="COMPATIBILITY REPORT FORM", font=("Arial", 14, "bold"), bg="#1e1e1e", fg="#00ff00").pack(pady=10)

    # ГАЛОЧКА СОГЛАСИЯ
    confirm_var = tk.BooleanVar()
    check_frame = tk.Frame(main_frame, bg="#2d2d2d", padx=10, pady=10)
    check_frame.pack(fill=tk.X, pady=10)
    tk.Checkbutton(check_frame, text="I understand this is a Community list and all data types\n(dumps/pirated) are accepted *", 
                   variable=confirm_var, bg="#2d2d2d", fg="#ffcc00", selectcolor="#1e1e1e", font=("Arial", 9, "bold"), justify=tk.LEFT).pack(anchor="w")

    # ВЫБОР ТИПА КОПИИ
    tk.Label(main_frame, text="Copy Type (Select one): *", bg="#1e1e1e", fg="#cccccc", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0))
    copy_type = tk.StringVar(value="None")
    radio_frame = tk.Frame(main_frame, bg="#1e1e1e")
    radio_frame.pack(fill=tk.X, pady=5)
    tk.Radiobutton(radio_frame, text="Pirated (Downloaded)", variable=copy_type, value="Pirated", bg="#1e1e1e", fg="white", selectcolor="#007acc").pack(side=tk.LEFT, padx=10)
    tk.Radiobutton(radio_frame, text="Digital Dump (Own)", variable=copy_type, value="Digital Dump (Own)", bg="#1e1e1e", fg="white", selectcolor="#007acc").pack(side=tk.LEFT, padx=10)

    entries = {}
    def create_field(label_text, key, default=""):
        tk.Label(main_frame, text=label_text, bg="#1e1e1e", fg="#cccccc").pack(anchor="w", pady=(5, 0))
        e = tk.Entry(main_frame, width=70, bg="#2d2d2d", fg="white", insertbackground="white", borderwidth=0)
        if default: e.insert(0, default)
        e.pack(pady=5, ipady=3)
        entries[key] = e

    create_field("1. Game Name:", "name")
    create_field("2. Game ID (CUSA):", "id", "CUSA")

    # ВЕРСИЯ И СТАТУС
    tk.Label(main_frame, text="4. shadPS4 Version:", bg="#1e1e1e", fg="#cccccc").pack(anchor="w")
    ver_combo = ttk.Combobox(main_frame, values=["Main Build (Nightly)", "v0.5.0", "v0.4.0", "v0.3.1"], state="readonly")
    ver_combo.set("v0.5.0")
    ver_combo.pack(pady=5, fill=tk.X)

    tk.Label(main_frame, text="5. Status:", bg="#1e1e1e", fg="#cccccc").pack(anchor="w")
    status_combo = ttk.Combobox(main_frame, values=["Platinum", "Playable", "Orange", "In-Game", "Crashes"], state="readonly")
    status_combo.set("In-Game")
    status_combo.pack(pady=5, fill=tk.X)

    tk.Label(main_frame, text="6. Error Summary:", bg="#1e1e1e", fg="#cccccc").pack(anchor="w")
    error_text = tk.Text(main_frame, width=52, height=6, bg="#2d2d2d", fg="#e0e0e0", font=("Consolas", 10))
    error_text.pack(pady=5)

    def generate_and_send():
        if not confirm_var.get():
            messagebox.showwarning("Warning", "Check the 'Dumps/Pirated' box first!")
            return
        if copy_type.get() == "None":
            messagebox.showwarning("Warning", "Please select Copy Type!")
            return

        title = f"{entries['id'].get()} - {entries['name'].get()}"
        body = (
            f"- [x] I understand this is a Community list...\n\n"
            f"### Game Name: {entries['name'].get()}\n"
            f"### Game ID: {entries['id'].get()}\n"
            f"### Copy Type: {copy_type.get()}\n"
            f"### Version: {ver_combo.get()}\n"
            f"### Status: {status_combo.get()}\n"
            f"### Details:\n{error_text.get(1.0, tk.END)}"
        )
        
        url = f"https://github.com/bestrigyn/shadPS4-Community-Compatibility/issues/new?title={urllib.parse.quote(title)}&body={urllib.parse.quote(body)}"
        open_url(url)
        reg_window.destroy()

    tk.Button(main_frame, text="GENERATE & SEND", command=generate_and_send, bg="#007acc", fg="white", font=("Arial", 11, "bold"), height=2).pack(pady=20, fill=tk.X)

# --- ИНТЕРФЕЙС ГЛАВНОГО ОКНА ---
def load_data():
    listbox.delete(0, tk.END)
    url = "https://api.github.com/repos/bestrigyn/shadPS4-Community-Compatibility/issues"
    try:
        with urllib.request.urlopen(url) as res:
            data = json.loads(res.read().decode())
            for issue in data:
                issues_data.append(issue)
                listbox.insert(tk.END, issue['title'])
    except: pass

tk.Label(root, text="🎮 shadPS4 DATABASE", font=("Arial", 18, "bold"), bg="#1e1e1e", fg="white").pack(pady=15)
listbox = tk.Listbox(root, width=80, height=15, bg="#252526", fg="#cccccc", font=("Consolas", 10))
listbox.pack(pady=5, padx=20)

tk.Button(root, text="➕ CREATE NEW REPORT", command=open_registration_window, bg="#007acc", fg="white", height=2, font=("Arial", 11, "bold")).pack(pady=20, padx=20, fill=tk.X)

load_data()
root.mainloop()
