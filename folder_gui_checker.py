import os
import hashlib
import json
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

# Calculate SHA-256 hash of a file
def calculate_file_hash(file_path):
    sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        return None

# Scan a folder and return a dictionary of file hashes
def scan_folder(folder_path):
    hash_dict = {}
    for root, _, files in os.walk(folder_path):
        for filename in files:
            full_path = os.path.join(root, filename)
            relative_path = os.path.relpath(full_path, folder_path)

            if "hash_store.json" in relative_path:
                continue  # Skip our own hash file

            file_hash = calculate_file_hash(full_path)
            if file_hash:
                hash_dict[relative_path] = file_hash
    return hash_dict

# Save current hashes to file
def save_hashes(folder_path, hash_data):
    with open(os.path.join(folder_path, "hash_store.json"), "w") as f:
        json.dump(hash_data, f, indent=4)

# Load previously stored hashes
def load_hashes(folder_path):
    try:
        with open(os.path.join(folder_path, "hash_store.json"), "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

# GUI Functions
def browse_folder():
    folder = filedialog.askdirectory()
    folder_entry.delete(0, tk.END)
    folder_entry.insert(0, folder)

def check_integrity():
    folder = folder_entry.get()
    if not os.path.isdir(folder):
        messagebox.showerror("Error", "Please select a valid folder.")
        return

    current_hashes = scan_folder(folder)
    stored_hashes = load_hashes(folder)

    result_text.delete(1.0, tk.END)

    if stored_hashes:
        modified = []
        added = []
        deleted = []

        for file in current_hashes:
            if file not in stored_hashes:
                added.append(file)
            elif current_hashes[file] != stored_hashes[file]:
                modified.append(file)

        for file in stored_hashes:
            if file not in current_hashes:
                deleted.append(file)

        if not (modified or added or deleted):
            result_text.insert(tk.END, "✅ No changes detected.\n")
        else:
            if modified:
                result_text.insert(tk.END, "⚠️ Modified files:\n" + "\n".join(modified) + "\n\n")
            if added:
                result_text.insert(tk.END, "🆕 New files:\n" + "\n".join(added) + "\n\n")
            if deleted:
                result_text.insert(tk.END, "❌ Deleted files:\n" + "\n".join(deleted) + "\n\n")
    else:
        result_text.insert(tk.END, "🔐 First-time scan. Saving current hashes.\n")

    save_hashes(folder, current_hashes)

# GUI Setup
root = tk.Tk()
root.title("Folder Integrity Checker")
root.geometry("600x400")

folder_entry = tk.Entry(root, width=60)
folder_entry.pack(pady=10)

browse_button = tk.Button(root, text="Browse Folder", command=browse_folder)
browse_button.pack()

check_button = tk.Button(root, text="Check Folder Integrity", command=check_integrity)
check_button.pack(pady=10)

result_text = scrolledtext.ScrolledText(root, width=70, height=15)
result_text.pack(pady=10)

root.mainloop()
