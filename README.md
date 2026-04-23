![Damage Analysis Interface](/frontend/src/assets/TV.png)

## Elevating Infrastructure Intelligence

Damage Intelligence Studio is a production-grade, high-performance computer vision solution designed to revolutionize the way structural damage is detected and analyzed. By combining state-of-the-art object detection and semantic segmentation algorithms into a seamless, unified interface, we provide engineering and maintenance teams with unparalleled visual intelligence.

![interface](/frontend/src/assets/cover.jpg)

## Architecture

This project is decoupled into a robust backend API and a minimalist, lightning-fast frontend.

- **Backend Engine**: A high-concurrency FastAPI REST API powering the inference pipeline. It orchestrates dynamic model loading and memory management for YOLO, SAM (Segment Anything Model), UNet, and DeepLab.
- **Frontend Interface**: A premium, React/Vite-based application with a startup-inspired aesthetic. It delivers a seamless user experience, complete with dynamic animations and a highly responsive media analysis dashboard.


## Core Capabilities

- **Precision Detection**: Utilizing YOLO architecture for real-time, highly accurate bounding box identification of structural anomalies.
- **Granular Segmentation**: Advanced pixel-perfect masking using SAM, UNet, and DeepLab to quantify damage extent with surgical precision.
- **Adaptive Processing**: Support for both static imagery and continuous video streams, applying frame-by-frame analysis with robust performance scaling.
- **Intelligent Resource Management**: Built-in garbage collection and dynamic caching ensure smooth, continuous operation without memory degradation during intensive workloads.

## Getting Started

Everything required to deploy Damage Intelligence Studio is self-contained within this directory. The necessary machine learning weights and parameters are bundled in the `backend/models` directory.

### Prerequisites

Ensure you have the following installed on your system:
- Python 3.10+
- Node.js 18+ and npm
- PyTorch (with CUDA support recommended for optimal performance)
- FFmpeg (for video processing support)

### Backend Initialization

1. Navigate to the `backend` directory.
2. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: Ensure torch and torchvision are correctly configured for your hardware environment)*
3. Start the FastAPI server:
   ```bash
   uvicorn api:app --host 0.0.0.0 --port 8000
   ```
   The backend will initialize and await incoming media analysis requests.

### Frontend Initialization

1. Open a new terminal and navigate to the `frontend` directory.
2. Install the Node modules:
   ```bash
   npm install
   ```
3. Launch the development server:
   ```bash
   npm run dev
   ```
4. Access the application interface via the provided local URL (typically `http://localhost:5173`).

## GitHub Deployment & Large Files

This repository contains large machine learning model files (such as `sam_vit_b_01ec64.pth`). To successfully push and pull these assets via GitHub, ensure that **Git Large File Storage (Git LFS)** is installed and configured on your local machine before pushing.

From the root of your project:
```bash
git lfs install
git lfs track "*.pth"
git lfs track "*.pt"
git add .gitattributes
```

## Licensing

Damage Intelligence Studio is proprietary software. All rights reserved.
