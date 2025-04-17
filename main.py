# main.py
from fastapi import FastAPI, UploadFile, File
from transformers import AutoProcessor, AutoModelForImageClassification
from PIL import Image
import torch
import io

app = FastAPI()

model_name = "Falconsai/nsfw_image_detection"
processor = AutoProcessor.from_pretrained(model_name)
model = AutoModelForImageClassification.from_pretrained(model_name)

@app.get("/")
def home():
    return {"message": "NSFW Detection API is running"}

@app.post("/classify")
async def classify_image(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    inputs = processor(images=image, return_tensors="pt")

    with torch.no_grad():
        outputs = model(**inputs)

    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]
    labels = model.config.id2label
    result = {labels[i]: float(probs[i]) for i in range(len(labels))}

    return result
