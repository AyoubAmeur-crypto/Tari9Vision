import os
import cv2
import torch
import torch.nn as nn
import torchvision.transforms as T
from torchvision.models.segmentation import deeplabv3_resnet101
import numpy as np
from ultralytics import YOLO

# Attempt SAM import
try:
    from segment_anything import sam_model_registry, SamPredictor
    SAM_AVAILABLE = True
except ImportError:
    SAM_AVAILABLE = False


# ── Configuration ────────────────────────────────────────────────────────
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

CLASS_NAMES = {0: 'D00', 1: 'D10', 2: 'D20', 3: 'D40'}
INST_COLORS = {
    0: (255, 80,  80),
    1: (80,  200, 80),
    2: (80,  120, 255),
    3: (255, 200, 50),
}


# ── U-Net Architecture ───────────────────────────────────────────────────
class DoubleConv(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1), nn.BatchNorm2d(out_ch), nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, 3, padding=1), nn.BatchNorm2d(out_ch), nn.ReLU(inplace=True))
    def forward(self, x): return self.net(x)

class UNet(nn.Module):
    def __init__(self, in_channels=3, out_channels=1, features=[64, 128, 256, 512]):
        super().__init__()
        self.downs, self.ups = nn.ModuleList(), nn.ModuleList()
        self.pool = nn.MaxPool2d(2, 2)
        ch = in_channels
        for f in features:
            self.downs.append(DoubleConv(ch, f)); ch = f
        self.bottleneck = DoubleConv(features[-1], features[-1]*2)
        for f in reversed(features):
            self.ups.append(nn.ConvTranspose2d(f*2, f, 2, 2))
            self.ups.append(DoubleConv(f*2, f))
        self.final = nn.Conv2d(features[0], out_channels, 1)

    def forward(self, x):
        skips = []
        for down in self.downs:
            x = down(x); skips.append(x); x = self.pool(x)
        x = self.bottleneck(x)
        skips = skips[::-1]
        for i in range(0, len(self.ups), 2):
            x = self.ups[i](x)
            skip = skips[i//2]
            if x.shape != skip.shape:
                x = nn.functional.interpolate(x, size=skip.shape[2:])
            x = torch.cat([skip, x], dim=1)
            x = self.ups[i+1](x)
        return self.final(x)


# ── Model Wrapper Class ──────────────────────────────────────────────────
class DamageDetector:
    def __init__(self):
        self.yolo = None
        self.sam_predictor = None
        self.unet = None
        self.deeplab = None

    def clear_unused_models(self, active_choice):
        import gc
        if active_choice != "YOLO + SAM" and self.sam_predictor is not None:
            self.sam_predictor = None
        if active_choice != "YOLO + UNet" and self.unet is not None:
            self.unet = None
        if active_choice != "YOLO + DeepLab" and self.deeplab is not None:
            self.deeplab = None
        
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    def load_yolo(self, path='bestv3.pt'):
        if not self.yolo and os.path.exists(path):
            self.yolo = YOLO(path)

    def load_sam(self, path='sam_vit_b_01ec64.pth'):
        if not self.sam_predictor and os.path.exists(path) and SAM_AVAILABLE:
            sam = sam_model_registry["vit_b"](checkpoint=path)
            sam.to(DEVICE)
            self.sam_predictor = SamPredictor(sam)

    def load_unet(self, path='unet_best.pth'):
        if not self.unet and os.path.exists(path):
            self.unet = UNet(in_channels=3, out_channels=1).to(DEVICE)
            ckpt = torch.load(path, map_location=DEVICE)
            state = ckpt.get('model_state_dict', ckpt.get('state_dict', ckpt))
            self.unet.load_state_dict(state, strict=False)
            self.unet.eval()

    def load_deeplab(self, path='deeplab_final.pth'):
        if not self.deeplab and os.path.exists(path):
            self.deeplab = deeplabv3_resnet101(pretrained=False, num_classes=1)
            ckpt = torch.load(path, map_location=DEVICE)
            state = ckpt.get('state_dict', ckpt)
            self.deeplab.load_state_dict(state, strict=False)
            self.deeplab.to(DEVICE).eval()

    def process_frame(self, img_bgr, model_choice, conf=0.25):
        # Clear unused cache elements before processing
        self.clear_unused_models(model_choice)
        
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        H, W = img_rgb.shape[:2]
        
        # Downscale if the image is astronomically large to prevent basic memory blowouts
        max_dim = 1200
        if max(H, W) > max_dim:
            scale = max_dim / max(H, W)
            img_rgb = cv2.resize(img_rgb, (int(W * scale), int(H * scale)))
            H, W = img_rgb.shape[:2]
            
        result = img_rgb.copy().astype(np.float32)

        # Baseline: YOLO detections if loaded
        boxes = []
        if self.yolo:
            res = self.yolo.predict(source=img_bgr, conf=conf, verbose=False)[0]
            if res.boxes is not None and len(res.boxes) > 0:
                boxes = res.boxes

        if len(boxes) == 0 and model_choice == "YOLO + SAM":
            # Just return original if nothing
            return img_rgb
            
        if model_choice == "YOLO + SAM" and self.sam_predictor:
            try:
                self.sam_predictor.set_image(img_rgb)
            except RuntimeError as e:
                print(f"SAM Memory Error: {e}. Falling back to YOLO.")
                self.sam_predictor = None
            for box in boxes:
                cls = int(box.cls)
                conf_val = float(box.conf)
                x1, y1, x2, y2 = box.xyxy[0].int().tolist()
                color = INST_COLORS.get(cls, (255, 255, 255))
                
                try:
                    with torch.no_grad():
                        masks_sam, _, _ = self.sam_predictor.predict(
                            box=np.array([x1, y1, x2, y2])[None, :],
                            multimask_output=False,
                        )
                    mask = masks_sam[0].astype(np.uint8) * 255
                except:
                    continue
                
                # Blend mask
                colored = np.zeros((H, W, 3), dtype=np.float32)
                colored[mask > 0] = color
                result = np.where(
                    np.stack([mask > 0]*3, axis=-1),
                    0.45 * result + 0.55 * colored,
                    result
                )

                # Draw
                result_u8 = np.clip(result, 0, 255).astype(np.uint8)
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cv2.drawContours(result_u8, contours, -1, color, 2)
                
                # Box Label
                self._draw_label_box(result_u8, x1, y1, x2, y2, cls, conf_val, color)
                result = result_u8.astype(np.float32)
                
        elif model_choice == "YOLO + UNet" and self.unet:
            transform = T.Compose([
                T.ToTensor(), T.Resize((512, 512))
            ])
            tensor = transform(img_rgb).unsqueeze(0).to(DEVICE)
            with torch.no_grad():
                out = self.unet(tensor)
            mask_512 = (torch.sigmoid(out).squeeze().cpu().numpy() > 0.5).astype(np.uint8) * 255
            mask = cv2.resize(mask_512, (W, H), interpolation=cv2.INTER_NEAREST)
            result = self._apply_global_mask(result, mask, (80, 200, 80))

            # Still overlay YOLO boxes for context if desired
            result_u8 = np.clip(result, 0, 255).astype(np.uint8)
            for box in boxes:
                self._draw_only_label(result_u8, box)
            result = result_u8.astype(np.float32)

        elif model_choice == "YOLO + DeepLab" and self.deeplab:
            transform = T.Compose([
                T.ToTensor(),
                T.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225]),
                T.Resize((512, 512))
            ])
            tensor = transform(img_rgb).unsqueeze(0).to(DEVICE)
            with torch.no_grad():
                out = self.deeplab(tensor)['out']
            mask_512 = (torch.sigmoid(out).squeeze().cpu().numpy() > 0.5).astype(np.uint8) * 255
            mask = cv2.resize(mask_512, (W, H), interpolation=cv2.INTER_NEAREST)
            result = self._apply_global_mask(result, mask, (255, 80, 80))
            
            result_u8 = np.clip(result, 0, 255).astype(np.uint8)
            for box in boxes:
                self._draw_only_label(result_u8, box)
            result = result_u8.astype(np.float32)
        else:
            # Fallback to just Draw YOLO boxes
            result_u8 = np.clip(result, 0, 255).astype(np.uint8)
            for box in boxes:
                cls = int(box.cls)
                conf_val = float(box.conf)
                x1, y1, x2, y2 = box.xyxy[0].int().tolist()
                color = INST_COLORS.get(cls, (255, 255, 255))
                self._draw_label_box(result_u8, x1, y1, x2, y2, cls, conf_val, color)
            result = result_u8.astype(np.float32)

        return np.clip(result, 0, 255).astype(np.uint8)

    def _apply_global_mask(self, result, mask, color):
        colored = np.zeros_like(result, dtype=np.float32)
        colored[mask > 0] = color
        result = np.where(
            np.stack([mask > 0]*3, axis=-1),
            0.45 * result + 0.55 * colored,
            result
        )
        return result

    def _draw_only_label(self, result_u8, box):
        cls = int(box.cls)
        conf_val = float(box.conf)
        x1, y1, x2, y2 = box.xyxy[0].int().tolist()
        color = tuple(INST_COLORS.get(cls, (255,255,255)))
        self._draw_label_box(result_u8, x1, y1, x2, y2, cls, conf_val, color, draw_mask_borders=False)

    def _draw_label_box(self, img_u8, x1, y1, x2, y2, cls, conf_val, color_rgb, draw_mask_borders=True):
        if draw_mask_borders:
            length, thick = 20, 3
            for (px, py), (dx, dy) in [
                ((x1,y1),(+1,+1)), ((x2,y1),(-1,+1)),
                ((x1,y2),(+1,-1)), ((x2,y2),(-1,-1))
            ]:
                cv2.line(img_u8, (px,py), (px+dx*length, py), color_rgb, thick)
                cv2.line(img_u8, (px,py), (px, py+dy*length), color_rgb, thick)

        label = f"{CLASS_NAMES.get(cls, 'Unk')} {conf_val:.2f}"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(img_u8, (x1, y1-th-10), (x1+tw+6, y1), (0,0,0), -1)
        cv2.rectangle(img_u8, (x1, y1-th-10), (x1+tw+6, y1), color_rgb, 1)
        cv2.putText(img_u8, label, (x1+3, y1-4), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color_rgb, 2)
