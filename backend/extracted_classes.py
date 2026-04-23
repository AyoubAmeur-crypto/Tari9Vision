import os, sys, time, json, warnings
warnings.filterwarnings('ignore')

import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict
from tqdm import tqdm

import torch
import torch.nn as nn
import torchvision.transforms as T
from torchvision.models.segmentation import deeplabv3_resnet101

from ultralytics import YOLO
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR        = Path('dataset/Japan/Japan')
TRAIN_IMG_DIR   = BASE_DIR / 'train' / 'images'
TRAIN_ANN_DIR   = BASE_DIR / 'train' / 'annotations' / 'xmls'
TEST_IMG_DIR    = BASE_DIR / 'test'  / 'images'

YOLO_MODELS = {
    
    'Yolo enhanced'  : 'bestv3.pt',
    'Yolo base'  : 'best1.pt',
}
UNET_PATH    = 'unet_best.pth'
DEEPLAB_PATH = 'deeplab_final.pth'
SAM_PATH     = 'sam_vit_b_01ec64.pth'

CLASS_NAMES  = {0: 'D00', 1: 'D10', 2: 'D20', 3: 'D40'}
CLASS_COLORS = {'D00':'#E74C3C','D10':'#2ECC71','D20':'#3498DB','D40':'#E67E22'}

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Device  : {DEVICE}")
print(f"PyTorch : {torch.__version__}")

# ── Verify paths ───────────────────────────────────────────────────────────
print("\nModel availability:")
for name, path in YOLO_MODELS.items():
    status = '✓' if Path(path).exists() else '✗'
    print(f"  {status} {name:12s} → {path}")
for label, path in [('U-Net', UNET_PATH), ('DeepLab', DEEPLAB_PATH), ('SAM', SAM_PATH)]:
    status = '✓' if Path(path).exists() else '✗'
    print(f"  {status} {label:12s} → {path}")

print("\nDataset:")
for label, d in [('Train imgs', TRAIN_IMG_DIR), ('Train anns', TRAIN_ANN_DIR), ('Test imgs', TEST_IMG_DIR)]:
    status = '✓' if d.exists() else '✗'
    print(f"  {status} {label:12s} → {d}")

# ── U-Net architecture definition (must match training) ────────────────────
class DoubleConv(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1), nn.BatchNorm2d(out_ch), nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, 3, padding=1), nn.BatchNorm2d(out_ch), nn.ReLU(inplace=True))
    def forward(self, x): return self.net(x)

class UNet(nn.Module):
    def __init__(self, in_channels=3, out_channels=1, features=[64,128,256,512]):
        super().__init__()
        self.downs, self.ups = nn.ModuleList(), nn.ModuleList()
        self.pool = nn.MaxPool2d(2, 2)
        # Encoder
        ch = in_channels
        for f in features:
            self.downs.append(DoubleConv(ch, f)); ch = f
        self.bottleneck = DoubleConv(features[-1], features[-1]*2)
        # Decoder
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

# ── Load U-Net ──────────────────────────────────────────────────────────────
unet_available = False
if Path(UNET_PATH).exists():
    try:
        unet = UNet(in_channels=3, out_channels=1).to(DEVICE)
        ckpt = torch.load(UNET_PATH, map_location=DEVICE)
        state = ckpt.get('model_state_dict', ckpt.get('state_dict', ckpt))
        unet.load_state_dict(state, strict=False)
        unet.eval()
        unet_available = True
        print("✓ U-Net loaded from", UNET_PATH)
    except Exception as e:
        print(f"⚠  U-Net load error: {e}")
else:
    print(f"⚠  U-Net checkpoint not found at {UNET_PATH}")

# ── Load DeepLab ────────────────────────────────────────────────────────────
deeplab_available = False
if Path(DEEPLAB_PATH).exists():
    try:
        deeplab = deeplabv3_resnet101(pretrained=False, num_classes=1)
        ckpt = torch.load(DEEPLAB_PATH, map_location=DEVICE)
        state = ckpt.get('state_dict', ckpt)
        deeplab.load_state_dict(state, strict=False)
        deeplab.to(DEVICE).eval()
        deeplab_available = True
        print("✓ DeepLab loaded from", DEEPLAB_PATH)
    except Exception as e:
        print(f"⚠  DeepLab load error: {e}")
else:
    print(f"⚠  DeepLab checkpoint not found at {DEEPLAB_PATH}")

# ── DeepLab evaluation ──────────────────────────────────────────────────────
deeplab_transform = T.Compose([
    T.ToTensor(),
    T.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
])

if deeplab_available:
    dl_pa, dl_iou, dl_dice, dl_prec, dl_rec, dl_times = [], [], [], [], [], []
    eval_dl_imgs = img_list[:100]
    print(f"Evaluating DeepLab on {len(eval_dl_imgs)} images …")
    with torch.no_grad():
        for img_path in tqdm(eval_dl_imgs, desc='DeepLab'):
            img_name = img_path.name
            if img_name not in ground_truth: continue
            gt_boxes = ground_truth[img_name]

            img_bgr = cv2.imread(str(img_path))
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            img_res = cv2.resize(img_rgb, (512, 512))

            tensor   = deeplab_transform(img_res).unsqueeze(0).to(DEVICE)
            t0       = time.time()
            out      = deeplab(tensor)['out']
            dl_times.append(time.time()-t0)
            pred_mask= (torch.sigmoid(out).squeeze().cpu().numpy() > 0.5).astype(np.uint8)
            gt_mask  = make_gt_mask(gt_boxes, 512, 512)

            tp_ = np.sum((pred_mask==1)&(gt_mask==1))
            fp_ = np.sum((pred_mask==1)&(gt_mask==0))
            fn_ = np.sum((pred_mask==0)&(gt_mask==1))
            tn_ = np.sum((pred_mask==0)&(gt_mask==0))

            dl_pa.append((tp_+tn_)/(tp_+fp_+fn_+tn_+1e-8))
            dl_iou.append(tp_/(tp_+fp_+fn_+1e-8))
            dl_dice.append(2*tp_/(2*tp_+fp_+fn_+1e-8))
            dl_prec.append(tp_/(tp_+fp_+1e-8))
            dl_rec.append(tp_/(tp_+fn_+1e-8))

    deeplab_metrics = {
        'pixel_accuracy': np.mean(dl_pa),
        'mean_iou'      : np.mean(dl_iou),
        'dice'          : np.mean(dl_dice),
        'precision'     : np.mean(dl_prec),
        'recall'        : np.mean(dl_rec),
        'avg_time'      : np.mean(dl_times),
    }
    print("\n─── DeepLab Segmentation Metrics ───")
    for k, v in deeplab_metrics.items():
        print(f"  {k:20s}: {v:.4f}")
else:
    print("DeepLab not available — skipping.")
    deeplab_metrics = None

# ── Aggregate all segmentation metrics ────────────────────────────────────
seg_rows = []

# YOLO (box IoU as proxy)
for name, m in yolo_results.items():
    seg_rows.append({'Model': f'YOLO {name}', 'Type': 'Detection',
                     'Pixel Acc': '—', 'Mean IoU': round(m['avg_iou'],4),
                     'Dice/F1' : round(m['f1'],4),
                     'Precision': round(m['precision'],4),
                     'Recall'  : round(m['recall'],4),
                     'Time (ms)': round(m['avg_time']*1000,1)})

# U-Net
if unet_metrics:
    seg_rows.append({'Model': 'U-Net', 'Type': 'Segmentation',
                     'Pixel Acc': round(unet_metrics['pixel_accuracy'],4),
                     'Mean IoU' : round(unet_metrics['mean_iou'],4),
                     'Dice/F1'  : round(unet_metrics['dice'],4),
                     'Precision': round(unet_metrics['precision'],4),
                     'Recall'   : round(unet_metrics['recall'],4),
                     'Time (ms)': round(unet_metrics['avg_time']*1000,1)})

# DeepLab
if deeplab_metrics:
    seg_rows.append({'Model': 'DeepLab', 'Type': 'Segmentation',
                     'Pixel Acc': round(deeplab_metrics['pixel_accuracy'],4),
                     'Mean IoU' : round(deeplab_metrics['mean_iou'],4),
                     'Dice/F1'  : round(deeplab_metrics['dice'],4),
                     'Precision': round(deeplab_metrics['precision'],4),
                     'Recall'   : round(deeplab_metrics['recall'],4),
                     'Time (ms)': round(deeplab_metrics['avg_time']*1000,1)})

# SAM
if sam_metrics:
    seg_rows.append({'Model': 'SAM ViT-B', 'Type': 'Foundation',
                     'Pixel Acc': '—',
                     'Mean IoU' : round(sam_metrics['mean_mask_iou'],4),
                     'Dice/F1'  : round(sam_metrics['mean_dice'],4),
                     'Precision': '—', 'Recall': '—',
                     'Time (ms)': round(sam_metrics['avg_time']*1000,1)})

df_seg = pd.DataFrame(seg_rows)
print("=" * 95)
print("FULL MODEL COMPARISON — RDD2022 Japan")
print("=" * 95)
print(df_seg.to_string(index=False))
df_seg.to_csv('all_models_comparison.csv', index=False)
print("\n✓ Saved → all_models_comparison.csv")

# ── Final summary printout ──────────────────────────────────────────────────
print("=" * 80)
print("FINAL METRICS SUMMARY — RDD2022 Japan Dataset")
print("=" * 80)

print("\n▸ YOLO DETECTION MODELS")
print(f"  {'Model':<14} {'Precision':>10} {'Recall':>8} {'F1':>8} {'mAP@0.5':>10} {'ms/img':>8}")
print("  " + "─"*62)
for name, m in yolo_results.items():
    print(f"  {name:<14} {m['precision']:>10.4f} {m['recall']:>8.4f} "
          f"{m['f1']:>8.4f} {m['map50']:>10.4f} {m['avg_time']*1000:>8.1f}")

print("\n▸ U-NET SEGMENTATION")
if unet_metrics:
    for k,v in unet_metrics.items():
        print(f"  {k:<22}: {v:.4f}")
else:
    print("  Not evaluated.")

print("\n▸ DEEPLAB SEGMENTATION")
if deeplab_metrics:
    for k,v in deeplab_metrics.items():
        print(f"  {k:<22}: {v:.4f}")
else:
    print("  Not evaluated.")

print("\n▸ SAM ViT-B SEGMENTATION")
if sam_metrics:
    for k,v in sam_metrics.items():
        if isinstance(v, float):
            print(f"  {k:<22}: {v:.4f}")
        else:
            print(f"  {k:<22}: {v}")
else:
    print("  Not evaluated.")

print("\n" + "=" * 80)
print("✓ Outputs: yolo_metrics.csv, all_models_comparison.csv,")
print("           fig1 … fig9 (PNG figures)")
print("=" * 80)
