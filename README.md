# Damage Intelligence Studio

![Damage Analysis Interface](./frontend/src/assets/TV.png)

## Elevating Infrastructure Intelligence

Damage Intelligence Studio is a production-grade computer vision solution designed to improve how structural damage is detected and analyzed. It combines object detection and semantic segmentation into a unified interface, giving engineering and maintenance teams clear and actionable visual insights.

![Studio Preview](./frontend/src/assets/cover.jpg)

## Architecture

This project is split into a backend API and a frontend interface.

- **Backend Engine**: Built with FastAPI, it handles model inference and manages YOLO, SAM, UNet, and DeepLab.
- **Frontend Interface**: A React + Vite application focused on performance and clean UI, with responsive design and smooth interactions.

## Core Capabilities

- **Detection**: Real-time damage detection using YOLO.
- **Segmentation**: Pixel-level analysis using SAM, UNet, and DeepLab.
- **Media Support**: Works with both images and videos.
- **Performance Handling**: Efficient memory usage with caching and cleanup mechanisms.

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- PyTorch (CUDA recommended)
- FFmpeg

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn api:app --host 0.0.0.0 --port 8000