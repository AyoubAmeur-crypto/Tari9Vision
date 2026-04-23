import os
import cv2
import numpy as np
import tempfile
import shutil
import subprocess
from fastapi import FastAPI, File, UploadFile, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, FileResponse

from model_utils import DamageDetector, SAM_AVAILABLE

app = FastAPI(title="Damage Intelligence API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

detector = DamageDetector()

def prepare_models(model_choice: str):
    models_dir = os.path.join(os.path.dirname(__file__), "models")

    if detector.yolo is None:
        yolo_path = os.path.join(models_dir, "bestv3.pt")
        if os.path.exists(yolo_path):
            detector.load_yolo(yolo_path)
            
    detector.clear_unused_models(model_choice)

    if model_choice == "YOLO + SAM" and SAM_AVAILABLE:
        detector.load_sam(os.path.join(models_dir, "sam_vit_b_01ec64.pth"))
    elif model_choice == "YOLO + UNet":
        detector.load_unet(os.path.join(models_dir, "unet_best.pth"))
    elif model_choice == "YOLO + DeepLab":
        detector.load_deeplab(os.path.join(models_dir, "deeplab_final.pth"))

def get_ffmpeg_path():
    try:
        import imageio_ffmpeg
        path = imageio_ffmpeg.get_ffmpeg_exe()
        if path and os.path.exists(path):
            return path
    except Exception:
        pass

    path = shutil.which("ffmpeg")
    if path:
        return path

    candidates = [
        r"C:\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"ffmpeg\bin\ffmpeg.exe"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c

    return None

def cleanup_files(*filepaths):
    for path in filepaths:
        if path and os.path.exists(path):
            try:
                os.unlink(path)
            except Exception:
                pass

@app.post("/api/analyze-image")
async def analyze_image(
    file: UploadFile = File(...),
    model: str = Form("YOLO"),
    confidence: float = Form(0.25)
):
    prepare_models(model)
    
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    processed_img = detector.process_frame(img_bgr, model, confidence)
    
    processed_bgr = cv2.cvtColor(processed_img, cv2.COLOR_RGB2BGR)
    _, encoded_img = cv2.imencode('.png', processed_bgr)
    
    return Response(content=encoded_img.tobytes(), media_type="image/png")

@app.post("/api/analyze-video")
async def analyze_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    model: str = Form("YOLO"),
    confidence: float = Form(0.25)
):
    prepare_models(model)
    
    # Save upload to temporary file
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    tfile.write(await file.read())
    tfile.close()
    tfile_path = tfile.name

    cap = cv2.VideoCapture(tfile_path)
    if not cap.isOpened():
        return Response(status_code=400, content="Could not open video file.")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    avi_path = tempfile.mktemp(suffix=".avi")
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    out = cv2.VideoWriter(avi_path, fourcc, fps, (width, height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        processed = detector.process_frame(frame, model, confidence)
        if processed.shape[:2] != (height, width):
            processed = cv2.resize(processed, (width, height))
        processed_bgr = cv2.cvtColor(processed, cv2.COLOR_RGB2BGR)
        out.write(processed_bgr)

    cap.release()
    out.release()

    mp4_path = tempfile.mktemp(suffix="_result.mp4")
    ffmpeg_exe = get_ffmpeg_path()
    
    final_output = avi_path
    output_mime = "video/x-msvideo"
    output_ext = "avi"

    if ffmpeg_exe:
        cmd = [
            ffmpeg_exe, "-y",
            "-i", avi_path,
            "-vcodec", "libx264",
            "-crf", "28",
            "-preset", "ultrafast",
            "-movflags", "+faststart",
            "-an",
            mp4_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0 and os.path.getsize(mp4_path) > 0:
            final_output = mp4_path
            output_mime = "video/mp4"
            output_ext = "mp4"

    # Cleanup the input and intermediate AVI in background
    background_tasks.add_task(cleanup_files, tfile_path, avi_path if final_output == mp4_path else None)
    
    # We ideally should cleanup final_output after response is returned, but let OS handle temp or rely on FileResponse's behavior.
    # FileResponse handles simple files, we can also delete via background task:
    background_tasks.add_task(cleanup_files, final_output)

    return FileResponse(final_output, media_type=output_mime, filename=f"processed_video.{output_ext}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
