# main.py
import os
import io
import logging
from typing import Dict, Any

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PIL import Image, UnidentifiedImageError
import torch

from transformers import AutoProcessor, AutoModelForImageClassification

# --- Config via env ---
MODEL_NAME = os.getenv("MODEL_NAME", "Falconsai/nsfw_image_detection")
ALLOW_ORIGINS = os.getenv("ALLOW_ORIGINS", "*")  # comma-separated or "*" for all
# optional: if you want to limit max upload size (bytes)
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", 5 * 1024 * 1024))  # default 5 MB

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nsfw-api")

# --- App ---
app = FastAPI(title="NSFW Image Detection API")

# CORS
origins = [o.strip() for o in ALLOW_ORIGINS.split(",")] if ALLOW_ORIGINS != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Device ---
device = "cuda" if torch.cuda.is_available() else "cpu"
logger.info(f"Using device: {device}")

# --- Load model & processor ---
# NOTE: Many models require `trust_remote_code=True`. If model fails, enable it.
try:
    processor = AutoProcessor.from_pretrained(MODEL_NAME, trust_remote_code=True)
    model = AutoModelForImageClassification.from_pretrained(MODEL_NAME, trust_remote_code=True).to(device)
except Exception as e:
    # fallback: try without trust_remote_code (some models don't need it)
    logger.warning(f"Model load with trust_remote_code raised: {e}. Retrying without it.")
    processor = AutoProcessor.from_pretrained(MODEL_NAME)
    model = AutoModelForImageClassification.from_pretrained(MODEL_NAME).to(device)

# expose labels
LABELS = model.config.id2label if hasattr(model.config, "id2label") else {}

@app.get("/", summary="Health check")
def home() -> Dict[str, Any]:
    return {"status": "ok", "model": MODEL_NAME, "device": device}

@app.get("/labels", summary="Return model labels")
def get_labels() -> Dict[str, Any]:
    return {"labels": LABELS}

@app.post("/classify", summary="Classify uploaded image")
async def classify_image(file: UploadFile = File(...)):
    # Basic protection: check file size (if content-length header not present, we read and check)
    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Empty file")

    if len(contents) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail=f"File too large (>{MAX_UPLOAD_SIZE} bytes)")

    try:
        image = Image.open(io.BytesIO(contents)).convert("RGB")
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="Invalid image file")

    # Run through processor and model
    try:
        inputs = processor(images=image, return_tensors="pt").to(device)
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probs = torch.nn.functional.softmax(logits, dim=-1)[0].cpu().numpy()
    except Exception as e:
        logger.exception("Model inference failed")
        raise HTTPException(status_code=500, detail=f"Inference error: {e}")

    # Build result mapping label -> score
    # model.config.id2label is a dict of {idx: label}
    labels = LABELS if LABELS else {i: str(i) for i in range(len(probs))}
    result = {labels.get(i, str(i)): float(round(float(probs[i]), 6)) for i in range(len(probs))}

    # Optionally sort descending by probability
    sorted_result = dict(sorted(result.items(), key=lambda x: x[1], reverse=True))

    return {"predictions": sorted_result}

# If using Uvicorn directly in-process (not recommended for production), you can enable:
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
