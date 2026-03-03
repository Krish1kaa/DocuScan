# 📄 DocuScan

DocuScan is a Python-based OCR (Optical Character Recognition) application that extracts text from images using the EasyOCR deep learning model developed by Jaided AI.

---

## 🚀 Features

* 📷 Image-to-text extraction
* 🧠 Powered by EasyOCR (Jaided AI)
* ⚡ Lightweight and efficient
* 🔍 Supports multiple languages
* 🛠 Simple command-line execution

---

## 🧠 Model Used

DocuScan uses:

* **EasyOCR**
* Developed by **Jaided AI**
* Deep learning-based text detection and recognition
* Supports 80+ languages

EasyOCR internally uses:

* CRAFT (text detection)
* CRNN (text recognition)
* PyTorch backend

---

## 🏗 Project Structure

```
DocuScan/
│── ocr_app.py
│── requirements.txt
│── README.md
│── .gitignore
```

---

## 🔧 Installation

1️⃣ Clone the repository:

```
git clone https://github.com/yourusername/DocuScan.git
cd DocuScan
```

2️⃣ Create virtual environment (recommended):

```
python -m venv .venv
.\.venv\Scripts\activate
```

3️⃣ Install dependencies:

```
pip install -r requirements.txt
```

---

## ▶️ Run the Application

```
python ocr_app.py
```

---

## 📦 Requirements

* Python 3.8+
* PyTorch
* EasyOCR
* OpenCV (if used)

All dependencies are listed in `requirements.txt`.

---

## 📌 Future Improvements

* PDF OCR support
* GUI / Web interface
* Cloud deployment
* Real-time camera scanning

---

## 👩‍💻 Author

Krishikaa Mathi Bharathi

---

## 📜 License

For academic and development purposes.
