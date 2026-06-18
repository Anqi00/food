---
title: 食物热量识别
emoji: 🍱
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# 🍱 食物热量识别 | Food Calorie Estimator

> 上传一张食物照片，AI 自动识别食物种类并估算热量。
> Upload a food photo — AI identifies the dish and estimates its calories.

**在线体验 / Live Demo：[huggingface.co/spaces/alex0027/food-calories](https://huggingface.co/spaces/alex0027/food-calories)**

**开源代码 / Source Code：[github.com/Anqi00/food](https://github.com/Anqi00/food)**

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 效果预览

![demo](demo.gif)

---

## 功能

- **食物识别**：基于 ViT 视觉模型，支持 101 种常见食物
- **热量估算**：识别后输入克重，自动计算总热量
- **估计重量**：不知道重量？点击「估计重量」按钮，自动填入该食物的典型份量
- **拖拽上传**：支持拖拽或点击上传 JPG / PNG / WEBP

---

## 技术栈

| 模块 | 技术 |
|------|------|
| 食物识别 | [nateraw/food](https://huggingface.co/nateraw/food)（ViT-base，Food-101 微调） |
| 热量数据 | USDA FoodData Central，覆盖 101 种食物 |
| 后端 | Python + FastAPI |
| 前端 | 原生 HTML / CSS / JS |
| 部署 | Hugging Face Spaces（Docker） |

---

## 在线使用

直接访问 👉 **[https://huggingface.co/spaces/alex0027/food-calories](https://huggingface.co/spaces/alex0027/food-calories)**

无需安装，打开即用。首次访问冷启动约 1 分钟（模型加载）。

---

## 本地运行

```bash
git clone https://github.com/Anqi00/food.git
cd food

python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt
uvicorn app:app --reload
```

打开 [http://localhost:8000](http://localhost:8000)

> 国内网络下载模型较慢时，先执行：
> ```bash
> export HF_ENDPOINT=https://hf-mirror.com
> ```

---

## 项目结构

```
food/
├── app.py              # FastAPI 路由
├── model.py            # 模型加载与推理
├── calories_db.json    # 热量数据库（101 种食物 + 中文名 + 典型份量）
├── Dockerfile
├── requirements.txt
└── templates/
    └── index.html      # 前端页面
```

---

## 热量计算

```
总热量 (kcal) = 食物重量 (g) × 每 100g 热量 (kcal) ÷ 100
```

热量数据来源：USDA FoodData Central，为典型制作方式参考值，仅供估算。

---

## License

MIT
