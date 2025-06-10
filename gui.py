import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import tensorflow as tf
import datetime

# Load model and labels
model = tf.keras.models.load_model("keras_model.h5")
with open("labels.txt", "r") as f:
    class_names = [line.strip() for line in f.readlines()]

def calculate_days_left(expiry_date):
    today = datetime.date.today()
    expiry = datetime.datetime.strptime(expiry_date, "%Y-%m-%d").date()
    return (expiry - today).days

def predict_from_frame(frame):
    img = cv2.resize(frame, (224, 224))
    img = np.asarray(img, dtype=np.float32).reshape(1, 224, 224, 3)
    img = (img / 127.5) - 1
    prediction = model.predict(img)[0]
    max_index = np.argmax(prediction)
    return class_names[max_index]

class FridgePoliceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Fridge Police")
        self.root.geometry("400x300")

        self.label = ttk.Label(root, text="Expiry Date (YYYY-MM-DD):")
        self.label.pack(pady=5)

        self.entry = ttk.Entry(root)
        self.entry.pack()

        self.predict_btn = ttk.Button(root, text="Start Detection", command=self.start_detection)
        self.predict_btn.pack(pady=10)

        self.result_label = ttk.Label(root, text="", font=("Arial", 14))
        self.result_label.pack(pady=10)

    def start_detection(self):
        expiry_date = self.entry.get()
        try:
            days_left = calculate_days_left(expiry_date)
        except:
            messagebox.showerror("Invalid Date", "Please enter a valid date in YYYY-MM-DD format")
            return

        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()

        if ret:
            label = predict_from_frame(frame)
            result_text = f"Detected: {label} | Days left: {days_left}"
            if days_left <= 2:
                result_text += " ⚠️"
            self.result_label.config(text=result_text)
        else:
            self.result_label.config(text="Camera error")

root = tk.Tk()
app = FridgePoliceApp(root)
root.mainloop()
