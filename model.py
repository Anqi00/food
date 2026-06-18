import io
import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

load_dotenv()

_client = None

SYSTEM_PROMPT = (
    "You are a food recognition and nutrition expert. "
    "Given a food image, return ONLY a valid JSON array with exactly 5 items, no markdown. "
    "Each item must have: "
    "label (English snake_case, e.g. grilled_fish), "
    "name_zh (Chinese name, e.g. 烤鱼), "
    "confidence (float 0-100, highest for best match), "
    "calories_per_100g (integer kcal), "
    "typical_serving_g (integer grams for one serving). "
    "Sort by confidence descending. Be specific about cooking method and cuisine style."
)


def get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
    return _client


def predict_food(image: Image.Image, top_k: int = 5) -> list[dict]:
    """Return top_k food prediction dicts from Gemini vision."""
    buf = io.BytesIO()
    image.save(buf, format="JPEG")
    buf.seek(0)

    response = get_client().models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            SYSTEM_PROMPT,
            types.Part.from_bytes(data=buf.getvalue(), mime_type="image/jpeg"),
        ],
    )

    text = response.text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()

    results = json.loads(text)
    return results[:top_k]
