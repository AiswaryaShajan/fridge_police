# Fridge Police

Fridge Police is a desktop app that helps monitor perishable fridge items using a webcam and a custom-trained machine learning model. Originally inspired by everyday challenges faced at home, it aims to reduce food waste by detecting items and alerting users about upcoming expiry.

## 🔧 How It Works

- Uses a **Logitech webcam** to capture real-time images
- A **Teachable Machine** image classifier predicts the item (e.g., Carrot, Cucumber, Milk)
- User inputs expiry date manually
- App displays how many days are left and alerts when close to expiry

## 🛠️ Tech Stack

- **Teachable Machine** (No-code ML training)
- **Python + TensorFlow** (Model integration)
- **OpenCV** (Webcam input)
- **Tkinter** (GUI)
- **Pillow, NumPy** (Image processing)

## 🚀 Getting Started

1. Clone the repo  
2. Install dependencies: pip install -r requirements.txt
3. 3. Ensure `keras_model.h5` and `labels.txt` are in the same folder  
4. Run python3 gui.py


## 📦 Status

Core functionality is in place:
- Item detection ✅
- Expiry tracking ✅
- Basic UI ✅

Future enhancements will include:
- More item categories
- Automated expiry logic
- Notifications or reminders

## 🔗 Challenge

Built for the [Decoding Data Science AI Challenge](https://decodingdatascience.com/ai-challenge)




