# NSFW Image Detection API

A lightweight and production-ready **NSFW Image Classification API** built using:

* **FastAPI** — lightning-fast Python web framework
* **Hugging Face Transformers** — for image classification
* **Falconsai/nsfw_image_detection** — pretrained NSFW classification model
* **Uvicorn** — high-performance ASGI server

This project supports:

* 🔍 **Single Image Classification via REST API**
* 🌐 **CORS-enabled usage in browsers / extensions**
* 🚀 **Deployable on Heroku / Render / Docker / Local**

---

## 📁 Project Structure

```text
NSFW-Image-Detector/
├── .env.example         # Environment variable template
├── .gitignore
├── LICENSE
├── main.py              # FastAPI application
├── Procfile             # Deployment entrypoint (Heroku)
├── requirements.txt     # Python dependencies
└── test_client.py       # Local/remote API tester script
```

### Folder Purpose

* **main.py** — Core API logic
* **test_client.py** — Simple script to test API predictions
* **.env.example** — Configure model, CORS, max upload size
* **Procfile** — Required for Heroku deployment
* **requirements.txt** — Dependencies list

---

## 🚀 Installation

Use a virtual environment for clean dependency management:

```bash
python -m venv venv

# Linux / macOS:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

Install packages:

```bash
pip install -r requirements.txt
```

> ⚠️ **Note:**
> If PyTorch fails to install, install the correct version from [https://pytorch.org](https://pytorch.org) and then retry `pip install -r requirements.txt`.

---

## ▶️ Running the API

Start the FastAPI server:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Your API is now available at:

```
http://127.0.0.1:8000
```

---

## 🔌 Endpoints

### **1️⃣ GET /** — Health Check

Returns model name and device status.

Example:

```json
{
  "status": "ok",
  "model": "Falconsai/nsfw_image_detection",
  "device": "cpu"
}
```

---

### **2️⃣ GET /labels** — Model Labels

Shows all NSFW classification labels supported by the model.

---

### **3️⃣ POST /classify** — Classify an Image

Upload an image file (`file=@your_image.jpg`).

Example:

```bash
curl -X POST "http://127.0.0.1:8000/classify" \
     -F "file=@sample.jpg"
```

Response:

```json
{
  "predictions": {
    "safe": 0.98213,
    "nsfw": 0.01787
  }
}
```

---

## 🔬 Testing with test_client.py

Use this for quick local or deployed API testing.

Local API:

```bash
python test_client.py sample.jpg
```

Remote API:

```bash
python test_client.py sample.jpg https://your-app.onrender.com
```

---

## ⚙️ Environment Variables

Copy `.env.example` → `.env`.

Example content:

```
MODEL_NAME=Falconsai/nsfw_image_detection
ALLOW_ORIGINS=*
MAX_UPLOAD_SIZE=5242880    # 5 MB
PORT=8080
```

### Variable Meaning

| Variable            | Description                                                 |
| ------------------- | ----------------------------------------------------------- |
| **MODEL_NAME**      | HF model to load (change to a smaller NSFW model if needed) |
| **ALLOW_ORIGINS**   | CORS allowed domains (`*` for development)                  |
| **MAX_UPLOAD_SIZE** | Maximum allowed file upload size                            |
| **PORT**            | Optional. Default port for local/VM deployments (not required for Heroku/Render, which inject their own $PORT).                            |

---

## ☁️ Deployment

### **Heroku Deployment**

1. Ensure `Procfile` includes:

```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

2. Push code:

```bash
git add .
git commit -m "Initial deploy"
git push heroku main
```

3. Set environment variables in Heroku → Settings → Config Vars.

> ⚠️ Heroku free dynos may not have enough RAM for large HF models; consider smaller models or Render.

---

### **Render Deployment**

1. Create a **Web Service**
2. Start command:

```
uvicorn main:app --host 0.0.0.0 --port $PORT
```

3. Set environment variables in Render dashboard.

Render generally has fewer RAM limits compared to Heroku’s free tier.

---

## ⚠️ Notes & Gotchas

### ✔ Run server from project root

Relative paths may break otherwise.

### ✔ Large Models Need RAM

`Falconsai/nsfw_image_detection` can be heavy.

If you hit memory errors:

* Switch to a smaller NSFW model
* Use Hugging Face Inference API
* Deploy on higher-memory machine

### ✔ Never commit `.env` or tokens

Your `.gitignore` already protects `.env`.

### ✔ Browser Extensions Will Require CORS

Set proper CORS origins in production:

```
ALLOW_ORIGINS=https://your-extension.com
```

---

## 💡 Future Improvements

* Add a **Gradio UI** for drag-and-drop testing
* Add **batch image classification** endpoint
* Add **image blur / censor** endpoint
* Add **FastAPI + JWT authentication**
* Add **Dockerfile** and docker-based deployment

---

## 📄 License

This project is licensed under the **MIT License**.
See `LICENSE` for details.

