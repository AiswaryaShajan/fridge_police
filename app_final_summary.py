    
import cv2
import numpy as np
import tensorflow as tf
import datetime
import sys, os
def resource_path(filename):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.abspath("."), filename)

import json
import os

# Load model and labels
model = tf.keras.models.load_model(resource_path("keras_model.h5"))
with open(resource_path("labels.txt"), "r") as f:
    class_names = [line.strip().split(" ", 1)[1] for line in f.readlines()]

# Load shelf life
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

def check_expiries(log):
    print("\n📦 Items in fridge:")
    unique = {}
    for entry in log:
        name = entry["item"]
        added = entry["added_on"]
        if name not in unique:
            unique[name] = added
    for item, added_on in unique.items():
        print(f"- {item} (added: {added_on})")

def list_cameras(max_tested=5):
    print("🔌 Available Cameras:")
    for i in range(max_tested):
        cap = cv2.VideoCapture(i)
        if cap.read()[0]:
            print(f"{i} - Camera available")
        cap.release()

def main():
    list_cameras()
    try:
        cam_index = int(input("Select camera index: "))
    except ValueError:
        cam_index = 0
        print("Invalid input. Defaulting to camera 0.")

    cap = cv2.VideoCapture(cam_index)
    log = load_log()

    last_label = None
    stable_counter = 0
    detection_threshold = 5
    confidence_threshold = 0.85
    logged_items = set()

    print("🔍 Starting Fridge Police Scanner... Press 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Failed to read from camera.")
            break

        item, confidence = predict(frame)
        print(f"[DEBUG] Prediction: {item}, Confidence: {confidence:.2f}")

        if confidence > confidence_threshold and item != "not_fridge_item":
            if item == last_label:
                stable_counter += 1
            else:
                stable_counter = 0
                last_label = item

            if stable_counter == detection_threshold and item not in logged_items:
                print(f"🆕 Detected: {item} ({confidence*100:.1f}%)")
                log.append({
                    "item": item,
                    "added_on": str(datetime.date.today())
                })
                save_log(log)
                logged_items.add(item)
                stable_counter = 0
        else:
            stable_counter = 0
            last_label = None

        cv2.imshow("Fridge Police - Press 'q' to Quit", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    check_expiries(log)

if __name__ == "__main__":
    main()