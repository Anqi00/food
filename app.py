import io
import json
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from PIL import Image

from model import predict_food

app = FastAPI(title="Food Calorie Estimator")

BASE = Path(__file__).parent
templates = Jinja2Templates(directory=BASE / "templates")

with open(BASE / "calories_db.json", encoding="utf-8") as f:
    CALORIES_DB: dict = json.load(f)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.post("/predict")
async def predict(
    file: UploadFile = File(...),
    weight: float = Form(default=100.0),
):
    if not file.content_type.startswith("image/"):
        return JSONResponse({"error": "请上传图片文件"}, status_code=400)

    data = await file.read()
    image = Image.open(io.BytesIO(data)).convert("RGB")

    raw_results = predict_food(image, top_k=5)

    predictions = []
    for label, confidence in raw_results:
        info = CALORIES_DB.get(label, {})
        cal_per_100g = info.get("calories_per_100g")
        name_zh = info.get("name_zh", label.replace("_", " ").title())
        total_calories = round(cal_per_100g * weight / 100) if cal_per_100g else None
        predictions.append(
            {
                "label": label,
                "name_zh": name_zh,
                "confidence": round(confidence * 100, 1),
                "calories_per_100g": cal_per_100g,
                "total_calories": total_calories,
                "weight": weight,
            }
        )

    return {"predictions": predictions}
