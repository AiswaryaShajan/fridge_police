
import tkinter as tk
from PIL import Image, ImageTk
import cv2
import numpy as np
import tensorflow as tf

class ScanGroceriesScreen:
    def __init__(self, parent_frame):
        self.frame = tk.Frame(parent_frame, width=512, height=768)
        self.frame.pack_propagate(False)

        # Load background
        self.bg_img = ImageTk.PhotoImage(Image.open("inside_screen_resized.png"))
        self.canvas = tk.Canvas(self.frame, width=512, height=768, highlightthickness=0)
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_img)

        # Webcam feed placeholder
        self.video_label = tk.Label(self.frame)
        self.canvas.create_window(256, 300, window=self.video_label)

        # Prediction label
        self.prediction_text = tk.StringVar()
        self.prediction_text.set("I see you got ...")
        self.prediction_label = tk.Label(self.frame, textvariable=self.prediction_text,
                                         bg="#d8f0f7", font=("Arial", 14, "bold"))
        self.canvas.create_window(256, 580, window=self.prediction_label)

        # Load TM model
        self.model = tf.keras.models.load_model("keras_model.h5")
        with open("labels.txt", "r") as f:
            self.class_names = [line.strip() for line in f.readlines()]

        self.cap = cv2.VideoCapture(0)
        self.update_frame()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # Resize frame for model and prediction
            img_resized = cv2.resize(frame, (224, 224))
            img_array = np.asarray(img_resized, dtype=np.float32).reshape(1, 224, 224, 3)
            img_array = (img_array / 127.5) - 1

            prediction = self.model.predict(img_array)[0]
            idx = np.argmax(prediction)
            item = self.class_names[idx]
            self.prediction_text.set(f"I see you got {item}")

            # Convert BGR to RGB and show on GUI
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = ImageTk.PhotoImage(image=Image.fromarray(rgb_frame).resize((300, 200)))
            self.video_label.imgtk = img
            self.video_label.configure(image=img)

        self.frame.after(1000, self.update_frame)

    def stop(self):
        self.cap.release()
