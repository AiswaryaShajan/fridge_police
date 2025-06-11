import tkinter as tk
from tkinter import messagebox
import cv2
import numpy as np
import tensorflow as tf

# Load model and labels
model = tf.keras.models.load_model("keras_model.h5")
with open("labels.txt", "r") as f:
    class_names = [line.strip() for line in f.readlines()]

def predict_carrot():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Error", "Webcam not detected!")
        return

    ret, frame = cap.read()
    cap.release()

    if ret:
        img = cv2.resize(frame, (224, 224))
        img = np.asarray(img, dtype=np.float32).reshape(1, 224, 224, 3)
        img = (img / 127.5) - 1  # Normalize
        prediction = model.predict(img)[0]
        max_index = np.argmax(prediction)
        label = class_names[max_index]
        confidence = prediction[max_index]
        result_text = f"{label.upper()} detected with {confidence:.2%} confidence"
        result_label.config(text=result_text)
    else:
        result_label.config(text="Could not capture image.")

# GUI
root = tk.Tk()
root.title("Fridge Police - Carrot Detector")
root.geometry("400x200")

tk.Label(root, text="Carrot Detection", font=("Arial", 16)).pack(pady=10)
tk.Button(root, text="Scan with Webcam", command=predict_carrot).pack(pady=10)
result_label = tk.Label(root, text="", font=("Arial", 14))
result_label.pack(pady=10)

root.mainloop()
