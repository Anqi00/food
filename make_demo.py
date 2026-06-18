"""Generate demo.gif and demo.mp4 showing the full app workflow."""

from PIL import Image, ImageDraw, ImageFont
import os
import subprocess

W, H = 520, 700
BG        = (245, 245, 245)
WHITE     = (255, 255, 255)
BLUE      = (79, 142, 247)
BLUE_LT   = (240, 246, 255)
GRAY      = (204, 204, 204)
GRAY_LT   = (238, 238, 238)
TEXT_DK   = (34, 34, 34)
TEXT_MD   = (100, 100, 100)
TEXT_LT   = (170, 170, 170)
RED       = (229, 85, 85)
GREEN     = (52, 199, 89)
ORANGE    = (255, 149, 0)


def font(size=14, bold=False):
    candidates = [
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc" if bold else
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def rr(draw, xy, r=12, fill=WHITE, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)


# ── shared chrome ────────────────────────────────────────────────────────────

def draw_chrome(draw):
    draw.rectangle([0, 0, W, H], fill=BG)
    # top bar
    draw.rectangle([0, 0, W, 68], fill=WHITE)
    draw.line([0, 68, W, 68], fill=GRAY_LT, width=1)
    draw.text((W//2, 18), "食物热量识别", font=font(20, True), fill=TEXT_DK, anchor="mt")
    draw.text((W//2, 46), "上传食物图片，AI 自动识别并估算热量",
              font=font(12), fill=TEXT_MD, anchor="mt")
    # card
    rr(draw, (14, 78, W-14, H-14), r=16, fill=WHITE)


# ── upload zone ──────────────────────────────────────────────────────────────

def draw_dropzone_empty(draw, y0=96):
    rr(draw, (34, y0, W-34, y0+190), r=12, fill=WHITE, outline=GRAY, width=2)
    draw.text((W//2, y0+70), "📷", font=font(38), fill=TEXT_MD, anchor="mm")
    draw.text((W//2, y0+118), "点击或拖拽图片到此处",
              font=font(13), fill=TEXT_MD, anchor="mm")
    draw.text((W//2, y0+140), "支持 JPG / PNG / WEBP",
              font=font(11), fill=TEXT_LT, anchor="mm")


_PHOTO = None

def load_photo():
    global _PHOTO
    if _PHOTO is None:
        path = os.path.join(os.path.dirname(__file__), "demo_photo.jpeg")
        if os.path.exists(path):
            img = Image.open(path).convert("RGB")
            # crop center square then resize to fit
            w, h = img.size
            s = min(w, h)
            img = img.crop(((w-s)//2, (h-s)//2, (w+s)//2, (h+s)//2))
            _PHOTO = img.resize((188, 154), Image.LANCZOS)
    return _PHOTO


def draw_dropzone_image(draw, canvas, y0=96):
    rr(draw, (34, y0, W-34, y0+190), r=12, fill=BLUE_LT, outline=BLUE, width=2)
    photo = load_photo()
    if photo:
        # paste real photo with rounded mask
        px, py = (W - 188) // 2, y0 + 18
        mask = Image.new("L", photo.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, 188, 154], radius=10, fill=255)
        canvas.paste(photo, (px, py), mask)
    else:
        rr(draw, (160, y0+12, 360, y0+178), r=10, fill=(200, 225, 255))
        draw.text((260, y0+95), "🍣", font=font(56), fill=TEXT_DK, anchor="mm")


# ── weight row ───────────────────────────────────────────────────────────────

def draw_weight_row(draw, weight="100", estimate_enabled=False,
                    hint="", y0=300):
    draw.text((48, y0+14), "食物重量", font=font(12), fill=TEXT_MD, anchor="lm")
    rr(draw, (128, y0+4, 310, y0+26), r=7, fill=WHITE, outline=GRAY, width=1)
    draw.text((140, y0+15), weight, font=font(13), fill=TEXT_DK, anchor="lm")
    draw.text((320, y0+14), "克 (g)", font=font(12), fill=TEXT_MD, anchor="lm")

    # estimate button
    btn_fill    = BLUE    if estimate_enabled else WHITE
    btn_outline = BLUE    if estimate_enabled else GRAY
    btn_txt_c   = WHITE   if estimate_enabled else GRAY
    rr(draw, (380, y0+2, W-34, y0+28), r=7,
       fill=btn_fill, outline=btn_outline, width=1)
    draw.text(((380 + W-34)//2, y0+15), "估计重量",
              font=font(11, bold=estimate_enabled), fill=btn_txt_c, anchor="mm")

    if hint:
        draw.text((48, y0+38), hint, font=font(10), fill=ORANGE, anchor="lm")


# ── submit button ─────────────────────────────────────────────────────────────

def draw_submit(draw, label="请先选择图片", enabled=True, loading=False, y0=348):
    c = BLUE if enabled else (160, 190, 248)
    rr(draw, (34, y0, W-34, y0+38), r=10, fill=c)
    if loading:
        cx = W//2
        draw.ellipse([cx-11, y0+9, cx+11, y0+29], outline=WHITE, width=2)
        draw.arc([cx-11, y0+9, cx+11, y0+29], start=0, end=240, fill=WHITE, width=2)
        draw.text((cx+18, y0+19), "识别中…", font=font(13), fill=WHITE, anchor="lm")
    else:
        draw.text((W//2, y0+19), label, font=font(14, bold=enabled),
                  fill=WHITE, anchor="mm")


# ── result cards ─────────────────────────────────────────────────────────────

RESULTS_DATA = [
    ("烤鱼",     "grilled salmon",  89.4, 206, True),
    ("烤三文鱼", "peking duck",      5.2, 338, False),
    ("西班牙海鲜饭", "paella",       2.7, 179, False),
    ("炸鱿鱼",   "fried calamari",   1.5, 175, False),
    ("炸鱼薯条", "fish and chips",   1.2, 265, False),
]


def draw_results(draw, weight=100, y0=400):
    draw.text((48, y0), "识别结果（Top 5）",
              font=font(12, True), fill=TEXT_DK, anchor="lm")
    y = y0 + 16
    for i, (zh, en, conf, cal100, hi) in enumerate(RESULTS_DATA):
        total = round(cal100 * weight / 100)
        fill    = BLUE_LT if hi else WHITE
        outline = BLUE    if hi else GRAY_LT
        rr(draw, (34, y, W-34, y+62), r=9, fill=fill, outline=outline, width=1)

        draw.text((48, y+18), zh,  font=font(13, True), fill=TEXT_DK, anchor="lm")
        draw.text((48, y+36), en,  font=font(10),       fill=TEXT_MD, anchor="lm")

        bx0, bx1 = 170, 290
        by = y + 20
        rr(draw, [bx0, by, bx1, by+6], r=3, fill=GRAY_LT)
        fw = int((bx1-bx0) * conf/100)
        if fw > 0:
            rr(draw, [bx0, by, bx0+fw, by+6], r=3, fill=BLUE)
        draw.text((bx0, by+14), f"{conf}%", font=font(10), fill=TEXT_MD, anchor="lm")

        draw.text((W-48, y+20), f"{total}",
                  font=font(16, True), fill=RED, anchor="rm")
        draw.text((W-48, y+38), "kcal",
                  font=font(10), fill=TEXT_MD, anchor="rm")
        draw.text((W-48, y+52), f"{cal100}/100g",
                  font=font(9), fill=TEXT_LT, anchor="rm")
        y += 68


# ── highlight overlay (flash effect) ─────────────────────────────────────────

def flash_overlay(img, alpha=60):
    overlay = Image.new("RGBA", img.size, (79, 142, 247, alpha))
    base = img.convert("RGBA")
    return Image.alpha_composite(base, overlay).convert("RGB")


# ── individual scene builders ─────────────────────────────────────────────────

def scene_idle():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    draw_chrome(d)
    draw_dropzone_empty(d, y0=96)
    draw_weight_row(d, weight="100", estimate_enabled=False, y0=300)
    draw_submit(d, label="请先选择图片", enabled=False, y0=348)
    return img


def scene_selected():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    draw_chrome(d)
    draw_dropzone_image(d, img, y0=96)
    draw_weight_row(d, weight="100", estimate_enabled=False, y0=300)
    draw_submit(d, label="识别食物 →", enabled=True, y0=348)
    return img


def scene_loading():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    draw_chrome(d)
    draw_dropzone_image(d, img, y0=96)
    draw_weight_row(d, weight="100", estimate_enabled=False, y0=300)
    draw_submit(d, enabled=True, loading=True, y0=348)
    return img


def scene_results(weight=100):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    draw_chrome(d)
    draw_dropzone_image(d, img, y0=96)
    draw_weight_row(d, weight=str(weight), estimate_enabled=True,
                    hint="烤鱼 典型份量约 500g（参考值）", y0=300)
    draw_submit(d, label="重新识别 →", enabled=True, y0=352)
    draw_results(d, weight=weight, y0=402)
    return img


def scene_estimate_click():
    """Button highlighted — about to fill weight."""
    img = scene_results(weight=100)
    d = ImageDraw.Draw(img)
    # highlight the estimate button with pressed state
    rr(d, (380, 302, W-34, 328), r=7, fill=(45, 110, 224))
    d.text(((380 + W-34)//2, 315), "估计重量",
           font=font(11, True), fill=WHITE, anchor="mm")
    return img


def scene_estimated():
    """Weight filled in as 500g, results updated."""
    img = scene_results(weight=500)
    d = ImageDraw.Draw(img)
    rr(d, (128, 304, 310, 326), r=7, fill=(230, 255, 235), outline=GREEN, width=2)
    d.text((140, 315), "500", font=font(13, True), fill=GREEN, anchor="lm")
    return img


# ── assemble frames ───────────────────────────────────────────────────────────

def build_frames():
    frames = []

    # 1. idle  (1.5s)
    frames += [scene_idle()] * 45

    # 2. image selected  (1s)
    frames += [scene_selected()] * 30

    # 3. loading  (0.8s, 3 rotation states)
    for _ in range(8):
        frames.append(scene_loading())

    # 4. results appear  (2s)
    frames += [scene_results(100)] * 60

    # 5. estimate button click flash  (0.4s)
    frames += [scene_estimate_click()] * 12

    # 6. weight auto-filled → recalculate  (0.5s)
    frames += [scene_loading()] * 10

    # 7. updated results  (3s)
    frames += [scene_estimated()] * 90

    return frames


def make_gif(frames, path="demo.gif"):
    frames[0].save(
        path,
        save_all=True,
        append_images=frames[1:],
        duration=33,
        loop=0,
        optimize=False,
    )
    print(f"Saved {path}  ({os.path.getsize(path)//1024} KB)")


def make_mp4(frames, path="demo.mp4"):
    import tempfile, shutil
    tmp = tempfile.mkdtemp()
    for i, f in enumerate(frames):
        f.save(f"{tmp}/{i:04d}.png")
    subprocess.run([
        "ffmpeg", "-y",
        "-framerate", "30",
        "-i", f"{tmp}/%04d.png",
        "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
        path,
    ], check=True, capture_output=True)
    shutil.rmtree(tmp)
    print(f"Saved {path}  ({os.path.getsize(path)//1024} KB)")


if __name__ == "__main__":
    frames = build_frames()
    make_gif(frames, "demo.gif")
    make_mp4(frames, "demo.mp4")
