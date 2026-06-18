import base64
import io
import json
import os

from dotenv import load_dotenv
import dashscope
from dashscope import MultiModalConversation
from PIL import Image

load_dotenv()
dashscope.api_key = os.environ["DASHSCOPE_API_KEY"]

PROMPT = (
    "你是一位食物识别和营养专家。"
    "仔细观察图片中的食物，只返回一个 JSON 数组，不要有任何其他文字或 markdown。"
    "数组包含 5 个对象，每个对象有以下字段：\n"
    "- label: 英文食物名（snake_case，如 grilled_fish）\n"
    "- name_zh: 中文食物名（如 烤鱼）\n"
    "- confidence: 置信度 0-100 的浮点数，最匹配的最高\n"
    "- calories_per_100g: 每100克热量（整数 kcal）\n"
    "- typical_serving_g: 典型单次份量克数（整数）\n"
    "按置信度从高到低排序。注意烹饪方式和菜系风格。"
)


def predict_food(image: Image.Image, top_k: int = 5) -> list[dict]:
    """Return top_k food prediction dicts from Qwen-VL."""
    buf = io.BytesIO()
    image.save(buf, format="JPEG")
    b64 = base64.b64encode(buf.getvalue()).decode()

    messages = [
        {
            "role": "user",
            "content": [
                {"image": f"data:image/jpeg;base64,{b64}"},
                {"text": PROMPT},
            ],
        }
    ]

    response = MultiModalConversation.call(
        model="qwen-vl-plus",
        messages=messages,
    )

    text = response.output.choices[0].message.content[0]["text"].strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()

    results = json.loads(text)
    return results[:top_k]
