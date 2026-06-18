from transformers import pipeline
import torch

_pipe = None


def get_pipeline():
    global _pipe
    if _pipe is None:
        device = 0 if torch.cuda.is_available() else -1
        _pipe = pipeline(
            "image-classification",
            model="nateraw/food",
            device=device,
        )
    return _pipe


def predict_food(image, top_k: int = 5) -> list[tuple[str, float]]:
    """Return top_k (label, confidence) pairs for a PIL image."""
    results = get_pipeline()(image, top_k=top_k)
    return [(r["label"], r["score"]) for r in results]
