import cv2
import torch
import numpy as np
from ultralytics import YOLO
from segment_anything import sam_model_registry, SamPredictor

# ── Config ───────────────────────────────────────────────────
DEVICE     = 'cuda' if torch.cuda.is_available() else 'cpu'
YOLO_PATH  = 'bestv3.pt'
SAM_PATH   = 'sam_vit_b_01ec64.pth'
IMAGE_PATH = 'image1.png'        # ← change to your image path
OUTPUT     = 'output.jpg'

CLASS_NAMES = {0: 'D00', 1: 'D10', 2: 'D20', 3: 'D40'}
INST_COLORS = {
    0: (255, 80,  80),
    1: (80,  200, 80),
    2: (80,  120, 255),
    3: (255, 200, 50),
}

print(f'Using: {DEVICE}')

# ── Load models ──────────────────────────────────────────────
print('Loading YOLO...')
yolo = YOLO(YOLO_PATH)

print('Loading SAM...')
sam       = sam_model_registry["vit_b"](checkpoint=SAM_PATH)
sam.to(DEVICE)
predictor = SamPredictor(sam)
print('Models ready ✅')

# ── Inference ────────────────────────────────────────────────
def predict(img_path, conf=0.25):
    img_bgr = cv2.imread(img_path)
    if img_bgr is None:
        print(f'❌ Could not read image: {img_path}')
        return
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    H, W    = img_rgb.shape[:2]
    result  = img_rgb.copy().astype(np.float32)

    # YOLO detection
    yolo_res = yolo.predict(source=img_path, conf=conf, verbose=False)[0]

    if yolo_res.boxes is None or len(yolo_res.boxes) == 0:
        print('No damage detected in this image.')
        cv2.imwrite(OUTPUT, img_bgr)
        return img_rgb

    print(f'Found {len(yolo_res.boxes)} damage region(s)')

    # SAM setup
    predictor.set_image(img_rgb)

    for box in yolo_res.boxes:
        cls      = int(box.cls)
        conf_val = float(box.conf)
        x1, y1, x2, y2 = box.xyxy[0].int().tolist()
        color     = INST_COLORS[cls]
        color_bgr = tuple(reversed(color))

        print(f'  → {CLASS_NAMES[cls]} ({conf_val:.2f}) at [{x1},{y1},{x2},{y2}]')

        # SAM precise mask
        try:
            masks_sam, _, _ = predictor.predict(
                box=np.array([x1, y1, x2, y2])[None, :],
                multimask_output=False,
            )
            mask = masks_sam[0].astype(np.uint8) * 255
        except Exception as e:
            print(f'    SAM failed: {e} — skipping')
            continue

        # Color fill
        colored         = np.zeros((H, W, 3), dtype=np.float32)
        colored[mask>0] = color
        result          = np.where(
            np.stack([mask>0]*3, axis=-1),
            0.45 * result + 0.55 * colored,
            result
        )

        # Contour
        result_u8   = np.clip(result, 0, 255).astype(np.uint8)
        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(result_u8, contours, -1, color_bgr, 2)

        # Corner accents
        length, thick = 20, 3
        for (px, py), (dx, dy) in [
            ((x1,y1),(+1,+1)), ((x2,y1),(-1,+1)),
            ((x1,y2),(+1,-1)), ((x2,y2),(-1,-1))
        ]:
            cv2.line(result_u8, (px,py), (px+dx*length, py), color_bgr, thick)
            cv2.line(result_u8, (px,py), (px, py+dy*length), color_bgr, thick)

        # Label
        label = f"{CLASS_NAMES[cls]} {conf_val:.2f}"
        (tw, th), _ = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(result_u8,
                      (x1, y1-th-10), (x1+tw+6, y1), (0,0,0), -1)
        cv2.rectangle(result_u8,
                      (x1, y1-th-10), (x1+tw+6, y1), color_bgr, 1)
        cv2.putText(result_u8, label, (x1+3, y1-4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_bgr, 2)

        result = result_u8.astype(np.float32)

    # Save
    final     = np.clip(result, 0, 255).astype(np.uint8)
    final_bgr = cv2.cvtColor(final, cv2.COLOR_RGB2BGR)
    cv2.imwrite(OUTPUT, final_bgr)
    print(f'\nSaved → {OUTPUT}')
    return final


# ── Run ───────────────────────────────────────────────────────
predict(IMAGE_PATH)