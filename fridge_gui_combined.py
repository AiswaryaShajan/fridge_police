import tkinter as tk
from PIL import Image, ImageTk
import subprocess
import sys
import json
import os
import datetime
import winsound
import cv2
import numpy as np
import tensorflow as tf

# Window settings
WINDOW_WIDTH = 512  # Match your logo's width
WINDOW_HEIGHT = 740  # Adjusted for logo + compact buttons

def resource_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.abspath("."), filename)

class FridgePoliceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fridge Police")
        self.root.geometry("512x768")
        self.root.resizable(False, False)

        # Load background logo (the main image)
        self.bg_home = ImageTk.PhotoImage(Image.open(resource_path("final_home_screen.png")))

        # Main frame and canvas
        self.home_frame = tk.Frame(self.root, width=512, height=768)
        self.home_frame.pack()
        self.canvas = tk.Canvas(self.home_frame, width=512, height=768, highlightthickness=0)
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_home)

        # Button parameters: smaller size, tighter spacing
        btn_width = 250
        btn_height = 35
        btn_font = ("Arial", 12, "bold")

        # The three buttons
        self.btn_groceries = tk.Button(self.home_frame, text="SHOW GROCERIES", command=self.scan_items,
                                       bg="#2d2d2d", fg="white", font=btn_font)
        self.btn_fridge = tk.Button(self.home_frame, text="SHOW FRIDGE", command=self.show_fridge,
                                    bg="#2d2d2d", fg="white", font=btn_font)
        self.btn_expiring = tk.Button(self.home_frame, text="SHOW EXPIRES", command=self.show_expires,
                                      bg="#2d2d2d", fg="white", font=btn_font)

        # Place buttons closer together, higher up (near the logo)
        self.canvas.create_window(256, 420, window=self.btn_groceries, width=btn_width, height=btn_height)
        self.canvas.create_window(256, 470, window=self.btn_fridge, width=btn_width, height=btn_height)
        self.canvas.create_window(256, 520, window=self.btn_expiring, width=btn_width, height=btn_height)

    def scan_items(self):
        import threading
        self.root.withdraw()
        def scanner_thread():
            try:
                run_scanner()
            except Exception as e:
                print("[ERROR]", e)
            finally:
                self.root.deiconify()
        threading.Thread(target=scanner_thread, daemon=True).start()

    def show_fridge(self):
        self.home_frame.pack_forget()
        self.fridge_frame = tk.Frame(self.root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="white")
        self.fridge_frame.pack()

        title = tk.Label(self.fridge_frame, text="🧊 Items in Your Fridge", font=("Arial", 16, "bold"), bg="white")
        title.pack(pady=(20, 10))

        self.log_text = tk.Text(self.fridge_frame, wrap="word", font=("Arial", 12), width=45, height=18)
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
        log_path = resource_path("fridge_log.json")
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
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
        log_path = resource_path("fridge_log.json")
        if os.path.exists(log_path):
            os.remove(log_path)
        self.load_fridge_log()

    def go_home(self):
        if hasattr(self, 'fridge_frame'):
            self.fridge_frame.pack_forget()
        if hasattr(self, 'expiry_frame'):
            self.expiry_frame.pack_forget()
        self.home_frame.pack()

    def show_expires(self):
        self.home_frame.pack_forget()
        self.expiry_frame = tk.Frame(self.root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="white")
        self.expiry_frame.pack()

        title = tk.Label(self.expiry_frame, text="⏳ Items Nearing Expiry", font=("Arial", 16, "bold"), bg="white")
        title.pack(pady=(20, 10))

        self.expiry_text = tk.Text(self.expiry_frame, wrap="word", font=("Arial", 12), width=45, height=18)
        self.expiry_text.pack(padx=20, pady=10)

        self.load_expiry_list()

        btn_frame = tk.Frame(self.expiry_frame, bg="white")
        btn_frame.pack(pady=10)

        back_btn = tk.Button(btn_frame, text="← BACK", command=self.go_home,
                             bg="#2d2d2d", fg="white", font=("Arial", 11))
        back_btn.pack(padx=10)

    def load_expiry_list(self):
        self.expiry_text.delete("1.0", "end")
        log_path = resource_path("fridge_log.json")
        shelf_path = resource_path("shelf_life.json")
        if not os.path.exists(log_path) or not os.path.exists(shelf_path):
            self.expiry_text.insert("end", "No data found.")
            return

        with open(log_path, "r") as f:
            log = json.load(f)
        with open(shelf_path, "r") as f:
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
                elif days_left == 1:
                    status = "⚠️ expires in 1 day"
                else:
                    status = f"⚠️ expires in {days_left} days"
                self.expiry_text.insert("end", f"- {item} (added: {entry['added_on']}, {status})\n")

        if not shown:
            self.expiry_text.insert("end", "✅ No items nearing expiry!")

def run_scanner():
    model_path = resource_path("rebuilt_model.h5")
    print("Model path:", model_path)
    print("Exists?", os.path.exists(model_path))
    model = tf.keras.models.load_model(model_path, compile=False)    
    with open(resource_path("labels.txt"), "r") as f:
        class_names = [line.strip().split(" ", 1)[1] for line in f.readlines()]
    with open(resource_path("shelf_life.json"), "r") as f:
        shelf_life = json.load(f)
    log_file = resource_path("fridge_log.json")

    def load_log():
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                return json.load(f)
        return []

    def save_log(data):
        with open(log_file, "w") as f:
            json.dump(data, f, indent=4)

    def predict(frame):
        img = cv2.resize(frame, (224, 224))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = np.asarray(img, dtype=np.float32) / 255.0
        img = np.expand_dims(img, axis=0)
        prediction = model.predict(img)[0]
        idx = np.argmax(prediction)
        return class_names[idx], prediction[idx]

    # Increased window height for visibility
    scanner = tk.Toplevel()
    scanner.title("Fridge Scanner")
    scanner.geometry("600x700")  # Increased height
    scanner.configure(bg="white")

    top_frame = tk.Frame(scanner, bg="white")
    top_frame.pack(pady=10)

    # Shrink video label if desired, e.g., width=500, height=375 for 4:3 ratio
    video_label = tk.Label(top_frame)
    video_label.pack()

    bottom_frame = tk.Frame(scanner, bg="white")
    bottom_frame.pack(pady=30)  # Increased padding to give room for the button

    status_label = tk.Label(bottom_frame, text="Scanning...", font=("Arial", 16), bg="white")
    status_label.pack(pady=5)

    stop_btn = tk.Button(bottom_frame, text="🛑 Stop Scan", font=("Arial", 12), command=scanner.destroy,
                         bg="#d9534f", fg="white")
    stop_btn.pack(pady=8)  # Add vertical padding for comfort

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    print("[INFO] Camera opened:", cap.isOpened())
    log = load_log()

    last_label = None
    stable_counter = 0
    detection_threshold = 5
    confidence_threshold = 0.85
    logged_items = set()

    def update_frame():
        nonlocal last_label, stable_counter
        ret, frame = cap.read()
        if not ret or frame is None or frame.size == 0:
            status_label.config(text="⚠️ Failed to read from camera.")
            print("[ERROR] Blank or failed frame.")
            return
        if not ret:
            status_label.config(text="⚠️ Camera read failed")
            return

        try:
            item, confidence = predict(frame)
        except Exception as e:
                status_label.config(text=f"Prediction error: {e}")
                print("[ERROR]", e)
                return
        if confidence > confidence_threshold and item != "not_fridge_item":
            if item == last_label:
                stable_counter += 1
            else:
                stable_counter = 0
                last_label = item

            if stable_counter == detection_threshold and item not in logged_items:
                status_label.config(text=f"✅ Got: {item} ({confidence*100:.1f}%)")
                log.append({"item": item, "added_on": str(datetime.date.today())})
                save_log(log)
                logged_items.add(item)
                stable_counter = 0
        else:
            status_label.config(text=f"🔍 {item} ({confidence*100:.1f}%)")
            stable_counter = 0
            last_label = None

        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)

        if scanner.winfo_exists():
            scanner.after(10, update_frame)
        else:
            cap.release()

    update_frame()
    scanner.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = FridgePoliceApp(root)
    root.mainloop()