
from scan_groceries_screen import ScanGroceriesScreen
import tkinter as tk
from PIL import Image, ImageTk
import subprocess
import sys
import json
import os
import datetime
import winsound

class FridgePoliceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fridge Police")
        self.root.geometry("512x768")
        self.root.resizable(False, False)

        self.bg_home = ImageTk.PhotoImage(Image.open("final_home_screen.png"))

        self.home_frame = tk.Frame(self.root, width=512, height=768)
        self.home_frame.pack()
        self.canvas = tk.Canvas(self.home_frame, width=512, height=768, highlightthickness=0)
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_home)

        self.btn_groceries = tk.Button(self.home_frame, text="SHOW GROCERIES", command=self.scan_items,
                                       bg="#2d2d2d", fg="white", font=("Arial", 14, "bold"))
        self.btn_fridge = tk.Button(self.home_frame, text="SHOW FRIDGE", command=self.show_fridge,
                                    bg="#2d2d2d", fg="white", font=("Arial", 14, "bold"))
        self.btn_expiring = tk.Button(self.home_frame, text="SHOW EXPIRES", command=self.show_expires,
                                      bg="#2d2d2d", fg="white", font=("Arial", 14, "bold"))

        self.canvas.create_window(256, 570, window=self.btn_groceries, width=300, height=50)
        self.canvas.create_window(256, 640, window=self.btn_fridge, width=300, height=50)
        self.canvas.create_window(256, 710, window=self.btn_expiring, width=300, height=50)

    def scan_items(self):
        self.root.withdraw()
        subprocess.run([sys.executable, "app_final_summary.py"])
        self.root.deiconify()

    def show_fridge(self):
        self.home_frame.pack_forget()
        self.fridge_frame = tk.Frame(self.root, width=512, height=768, bg="white")
        self.fridge_frame.pack()

        title = tk.Label(self.fridge_frame, text="🧊 Items in Your Fridge", font=("Arial", 16, "bold"), bg="white")
        title.pack(pady=(20, 10))

        self.log_text = tk.Text(self.fridge_frame, wrap="word", font=("Arial", 12), width=50, height=25)
        self.log_text.pack(padx=20, pady=10)

        self.load_fridge_log()

        btn_frame = tk.Frame(self.fridge_frame, bg="white")
        btn_frame.pack(pady=10)

        clear_btn = tk.Button(btn_frame, text="🗑️ Clear Fridge", command=self.clear_fridge_log,
                              bg="#aa0000", fg="white", font=("Arial", 11, "bold"))
        clear_btn.pack(side="left", padx=10)

        back_btn = tk.Button(btn_frame, text="← BACK", command=self.go_home,
                             bg="#2d2d2d", fg="white", font=("Arial", 11))
        back_btn.pack(side="right", padx=10)

    def load_fridge_log(self):
        self.log_text.delete("1.0", "end")
        if os.path.exists("fridge_log.json"):
            with open("fridge_log.json", "r") as f:
                log = json.load(f)
            unique = {}
            for entry in log:
                name = entry["item"]
                added = entry["added_on"]
                if name not in unique:
                    unique[name] = added
            if unique:
                for item, date in unique.items():
                    self.log_text.insert("end", f"- {item} (added: {date})\n")

            else:
                self.log_text.insert("end", "Fridge is currently empty.")
        else:
            self.log_text.insert("end", "No fridge log found.")

    def clear_fridge_log(self):
        if os.path.exists("fridge_log.json"):
            os.remove("fridge_log.json")
        self.load_fridge_log()

    def go_home(self):
        if hasattr(self, 'fridge_frame'):
            self.fridge_frame.pack_forget()
        if hasattr(self, 'expiry_frame'):
            self.expiry_frame.pack_forget()
        self.home_frame.pack()

    def show_expires(self):
        self.home_frame.pack_forget()
        self.expiry_frame = tk.Frame(self.root, width=512, height=768, bg="white")
        self.expiry_frame.pack()

        title = tk.Label(self.expiry_frame, text="⏳ Items Nearing Expiry", font=("Arial", 16, "bold"), bg="white")
        title.pack(pady=(20, 10))

        self.expiry_text = tk.Text(self.expiry_frame, wrap="word", font=("Arial", 12), width=50, height=25)
        self.expiry_text.pack(padx=20, pady=10)

        self.load_expiry_list()

        btn_frame = tk.Frame(self.expiry_frame, bg="white")
        btn_frame.pack(pady=10)

        back_btn = tk.Button(btn_frame, text="← BACK", command=self.go_home,
                             bg="#2d2d2d", fg="white", font=("Arial", 11))
        back_btn.pack(padx=10)

    def load_expiry_list(self):
        self.expiry_text.delete("1.0", "end")

        if not os.path.exists("fridge_log.json") or not os.path.exists("shelf_life.json"):
            self.expiry_text.insert("end", "No data found.")
            return

        with open("fridge_log.json", "r") as f:
            log = json.load(f)

        with open("shelf_life.json", "r") as f:
            shelf_life = json.load(f)
            
        today = datetime.date.today()
        shown = False
        checked = set()

        for entry in log:
            item = entry["item"]
            if item in checked:
                continue
            checked.add(item)

            added = datetime.datetime.strptime(entry["added_on"], "%Y-%m-%d").date()
            days_left = shelf_life.get(item, 0) - (today - added).days

            if days_left <= 2:
                shown = True
                if days_left < 0:
                    status = "❌ expired"
                elif days_left == 0:
                    status = "⚠️ expires today!"
                    self.show_notification(item)
                elif days_left == 1:
                    status = f"⚠️ expires in 1 day(s)"
                    self.show_notification(item)
                else:
                    status = f"⚠️ expires in {days_left} day(s)"
                self.expiry_text.insert("end", f"- {item} (added: {entry['added_on']}, {status})\n")


        if not shown:
            self.expiry_text.insert("end", "✅ No items nearing expiry!")

    def show_notification(self, item_name):
        toast = tk.Toplevel(self.root)
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)
        toast.configure(bg="#ffcc00")

        x = self.root.winfo_rootx() + 106
        toast.geometry(f"300x0+{x}+0")

        label = tk.Label(toast, text=f"🔔 {item_name} expires soon!", font=("Arial", 11, "bold"),
                         bg="#ffcc00", fg="black")
        label.pack(fill="both", expand=True, padx=10, pady=10)

        def slide_in():
            h = toast.winfo_height()
            if h < 50:
                toast.geometry(f"300x{h + 5}+{x}+0")
                toast.after(10, slide_in)
            else:
                toast.after(2500, slide_out)

        def slide_out():
            h = toast.winfo_height()
            if h > 0:
                toast.geometry(f"300x{h - 5}+{x}+0")
                toast.after(10, slide_out)
            else:
                toast.destroy()

        try:
            winsound.MessageBeep()
        except:
            pass

        slide_in()

if __name__ == "__main__":
    root = tk.Tk()
    app = FridgePoliceApp(root)
    root.mainloop()
