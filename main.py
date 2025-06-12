
import tkinter as tk
from tkinter import PhotoImage
import subprocess
import os
from PIL import Image, ImageTk
import sys


def launch_scanner():
    subprocess.Popen([sys.executable, "gui.py"])
    root.destroy()

root = tk.Tk()
root.title("Fridge Police")
root.geometry("800x600")
root.configure(bg="#d8f0f7")  # Light blue background


img = Image.open("fridge_police_logo.png")
img = img.resize((200, 300), Image.Resampling.LANCZOS)
logo = ImageTk.PhotoImage(img)
logo_label = tk.Label(root, image=logo, bg="#d8f0f7")
logo_label.image = logo
logo_label.pack(pady=40)

# Title label
title = tk.Label(root, text="Got new groceries? Let me see!", font=("Helvetica", 18, "bold"), bg="#d8f0f7")
title.pack(pady=10)

# Start button
start_btn = tk.Button(root, text="Start Scanning", font=("Helvetica", 14), bg="#002b45", fg="white",
                      padx=20, pady=10, command=launch_scanner)
start_btn.pack(pady=30)

root.mainloop()
