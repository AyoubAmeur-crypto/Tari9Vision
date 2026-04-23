<<<<<<< HEAD
# Damage Intelligence Studio

![Damage Analysis Interface](./frontend/src/assets/TV.png)
=======
![Damage Analysis Interface](/frontend/src/assets/TV.png)
>>>>>>> 095eb3d6a84caf1f9de82d499068e52a5aab4c4b

## Elevating Infrastructure Intelligence

Damage Intelligence Studio is a production-grade, high-performance computer vision solution designed to revolutionize the way structural damage is detected and analyzed. By combining state-of-the-art object detection and semantic segmentation algorithms into a seamless, unified interface, we provide engineering and maintenance teams with unparalleled visual intelligence.

<<<<<<< HEAD
![Studio Preview](./frontend/src/assets/cover.jpg)
=======
![interface](/frontend/src/assets/cover.jpg)
>>>>>>> 095eb3d6a84caf1f9de82d499068e52a5aab4c4b

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

### Prerequisites

Ensure you have the following installed on your system:
- Python 3.10+
- Node.js 18+ and npm
- PyTorch (with CUDA support recommended for optimal performance)
- FFmpeg (for video processing support)

### Backend Initialization

1. Navigate to the `backend` directory.
2. Ensure you have the model weights in the `backend/models/` directory.
   *(Note: These files are ignored by Git due to their size. You must manually place `bestv3.pt`, `sam_vit_b_01ec64.pth`, `unet_best.pth`, and `deeplab_final.pth` in that folder.)*
3. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI server:
   ```bash
   uvicorn api:app --host 0.0.0.0 --port 8000
   ```

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

## Licensing

Damage Intelligence Studio is proprietary software. All rights reserved.
