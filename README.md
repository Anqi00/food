---
title: 食物热量识别
emoji: 🍱
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# 🍱 食物热量识别

上传一张食物照片，AI 自动识别食物种类并根据重量估算热量。

**在线体验：[huggingface.co/spaces/alex0027/food-calories](https://huggingface.co/spaces/alex0027/food-calories)**

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green) ![License](https://img.shields.io/badge/License-MIT-yellow)

## 效果预览

![demo](demo.gif)

## 技术栈

| 模块 | 技术 |
|------|------|
| 食物识别 | [nateraw/food](https://huggingface.co/nateraw/food)（ViT-base，Food-101 微调） |
| 热量数据 | USDA FoodData Central，覆盖 101 种食物 |
| 后端 | Python + FastAPI |
| 前端 | 原生 HTML/CSS/JS，拖拽上传 |
| 部署 | Hugging Face Spaces（Docker） |

## 在线使用

直接访问 [https://huggingface.co/spaces/alex0027/food-calories](https://huggingface.co/spaces/alex0027/food-calories)，无需安装任何环境。

> 首次访问冷启动约需 1 分钟（模型加载），之后响应正常。

## 本地运行

```bash
git clone https://github.com/Anqi00/food.git
cd food

python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt
uvicorn app:app --reload
```

打开浏览器访问 [http://localhost:8000](http://localhost:8000)

国内网络下载模型较慢时：

```bash
export HF_ENDPOINT=https://hf-mirror.com
uvicorn app:app --reload
```

## 项目结构

```
food/
├── app.py              # FastAPI 路由
├── model.py            # 模型加载与推理
├── calories_db.json    # 热量数据库（101 种食物 + 中文名）
├── Dockerfile          # 容器化部署配置
├── requirements.txt
└── templates/
    └── index.html      # 前端页面
```

## API

### `POST /predict`

**请求参数（multipart/form-data）**

| 字段 | 类型 | 说明 |
|------|------|------|
| `file` | File | 图片文件（JPG / PNG / WEBP） |
| `weight` | float | 食物重量（克），默认 100 |

**返回示例**

```json
{
  "predictions": [
    {
      "label": "peking_duck",
      "name_zh": "北京烤鸭",
      "confidence": 92.3,
      "calories_per_100g": 338,
      "total_calories": 338,
      "weight": 100.0
    }
  ]
}
```

## 支持的食物

共 101 种，包括：

> 披萨、汉堡、寿司、拉面、炒饭、饺子、春卷、章鱼小丸子、北京烤鸭、韩式拌饭、
> 牛排、三文鱼、薯条、甜甜圈、芝士蛋糕、马卡龙、提拉米苏 ……

完整列表见 `calories_db.json`。

## 热量计算

```
总热量 (kcal) = 食物重量 (g) × 每 100g 热量 (kcal) ÷ 100
```

数据来源：USDA FoodData Central，为典型制作方式的参考值，仅供估算。

## License

MIT
