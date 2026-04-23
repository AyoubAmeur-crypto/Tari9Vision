import streamlit as st
import numpy as np
import cv2
import tempfile
import os
import shutil
import subprocess
import base64
from pathlib import Path

from model_utils import DamageDetector, SAM_AVAILABLE

st.set_page_config(
    page_title="Damage Intelligence Studio",
    page_icon="TV.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Initialize Detector strictly once ────────────────────────────────────────
@st.cache_resource
def get_detector():
    return DamageDetector()

detector = get_detector()


# ── Logo loader ───────────────────────────────────────────────────────────────
def load_logo_b64():
    try:
        with open("TV.png", "rb") as f:
            return "data:image/png;base64," + base64.b64encode(f.read()).decode()
    except Exception:
        return ""

logo_src = load_logo_b64()


# ── UI Styles ─────────────────────────────────────────────────────────────────
def style_ui():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&display=swap');

        :root {
            --black:          #000000;
            --surface:        #09090B;
            --surface-2:      #121214;
            --surface-3:      #18181B;
            --accent:         #10B981;
            --accent-glow:    rgba(16, 185, 129, 0.1);
            --text-primary:   #FAFAFA;
            --text-secondary: #A1A1AA;
            --text-muted:     #52525B;
            --border:         #27272A;
            --border-bright:  #3F3F46;
            --font-display:   'Syne', sans-serif;
            --font-body:      'DM Sans', sans-serif;
        }

        html, body, [data-testid="stAppViewContainer"] {
            background-color: var(--black) !important;
            color: var(--text-primary);
            font-family: var(--font-body);
        }

        /* Hide Streamlit top toolbar */
        [data-testid="stToolbar"],
        [data-testid="stDecoration"],
        #MainMenu,
        footer {
            display: none !important;
        }

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {
            background-color: var(--surface) !important;
            border-right: 1px solid var(--border) !important;
        }
        [data-testid="stSidebar"] > div:first-child {
            padding-top: 0 !important;
        }

        /* ── Block container ── */
        div.block-container {
            padding: 0 2.5rem 3rem 2.5rem !important;
            max-width: 1400px;
        }

        /* ── Header band ── */
        .dis-header {
            display: flex;
            align-items: center;
            gap: 16px;
            padding: 24px 32px;
            background: var(--surface);
            border-bottom: 1px solid var(--border);
            margin: 0 -2.5rem 36px -2.5rem;
            position: relative;
        }
        .dis-header-logo {
            width: 44px;
            height: 44px;
            object-fit: contain;
            border-radius: 8px;
            flex-shrink: 0;
            opacity: 1;
        }
        .dis-header-title {
            font-family: var(--font-display);
            font-size: 22px;
            font-weight: 700;
            color: var(--text-primary);
            letter-spacing: -0.5px;
            line-height: 1.1;
            margin: 0 0 4px 0;
        }
        .dis-header-sub {
            font-family: var(--font-body);
            font-size: 11px;
            font-weight: 500;
            color: var(--text-secondary);
            letter-spacing: 1.5px;
            text-transform: uppercase;
            margin: 0;
        }
        .dis-header-badge {
            margin-left: auto;
            font-family: var(--font-body);
            font-size: 10px;
            font-weight: 600;
            color: var(--text-primary);
            background: var(--surface-2);
            border: 1px solid var(--border);
            padding: 6px 14px;
            border-radius: 20px;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            white-space: nowrap;
            transition: all 0.2s ease;
        }
        .dis-header-badge:hover {
            border-color: var(--accent);
            color: var(--accent);
        }

        /* ── Sidebar brand ── */
        .sidebar-brand {
            padding: 24px 20px 16px 20px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 24px;
        }
        .sidebar-logo-row {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
        }
        .sidebar-logo-row img {
            width: 28px;
            height: 28px;
            object-fit: contain;
            border-radius: 6px;
        }
        .sidebar-brand-name {
            font-family: var(--font-display);
            font-size: 15px;
            font-weight: 700;
            color: var(--text-primary);
            letter-spacing: -0.3px;
        }

        /* ── Field labels ── */
        .field-label {
            font-family: var(--font-body);
            font-size: 10px;
            font-weight: 600;
            color: var(--text-muted);
            letter-spacing: 1.5px;
            text-transform: uppercase;
            margin: 0 0 10px 0;
        }
        [data-testid="stSelectbox"] label,
        [data-testid="stSlider"] label {
            font-family: var(--font-body) !important;
            font-size: 10px !important;
            font-weight: 600 !important;
            color: var(--text-muted) !important;
            letter-spacing: 1.5px !important;
            text-transform: uppercase !important;
        }

        /* ── Selectbox ── */
        [data-testid="stSelectbox"] > div > div {
            background-color: var(--surface-2) !important;
            border: 1px solid var(--border) !important;
            border-radius: 8px !important;
            color: var(--text-primary) !important;
            font-family: var(--font-body) !important;
            transition: all 0.2s ease !important;
        }
        [data-testid="stSelectbox"] > div > div:hover {
            border-color: var(--border-bright) !important;
        }
        [data-testid="stSelectbox"] > div > div:focus-within {
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 2px var(--accent-glow) !important;
        }

        /* ── Slider ── */
        [data-testid="stSlider"] > div > div > div > div {
            background: var(--accent) !important;
        }

        /* ── Status panel ── */
        .status-panel {
            background: var(--surface-2);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 16px;
            margin-top: 12px;
            transition: border-color 0.3s ease;
        }
        .status-panel:hover {
            border-color: var(--border-bright);
        }
        .status-title {
            font-family: var(--font-display);
            font-size: 11px;
            font-weight: 700;
            color: var(--text-primary);
            letter-spacing: 1.5px;
            text-transform: uppercase;
            margin: 0 0 8px 0;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .status-dot {
            width: 6px;
            height: 6px;
            background: var(--accent);
            border-radius: 50%;
            flex-shrink: 0;
            animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
            50%      { opacity: 0.5; box-shadow: 0 0 0 4px rgba(16, 185, 129, 0); }
        }
        .status-detail {
            font-family: var(--font-body);
            font-size: 13px;
            color: var(--text-secondary);
            margin: 0;
            line-height: 1.6;
        }

        /* ── Divider ── */
        hr {
            border: none !important;
            border-top: 1px solid var(--border) !important;
            margin: 24px 0 !important;
        }

        /* ── Tabs ── */
        [data-testid="stTabs"] {
            border-bottom: 1px solid var(--border) !important;
            margin-bottom: 32px;
        }
        [data-testid="stTabs"] button {
            font-family: var(--font-body) !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            letter-spacing: 0.5px !important;
            color: var(--text-muted) !important;
            padding: 16px 20px !important;
            border: none !important;
            border-radius: 0 !important;
            background: transparent !important;
            transition: all 0.2s ease !important;
        }
        [data-testid="stTabs"] button:hover {
            color: var(--text-primary) !important;
        }
        [data-testid="stTabs"] button[aria-selected="true"] {
            color: var(--text-primary) !important;
            border-bottom: 2px solid var(--accent) !important;
            font-weight: 600 !important;
        }

        /* ── Buttons ── */
        .stButton > button {
            font-family: var(--font-body) !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            letter-spacing: 0.5px !important;
            background: var(--surface-2) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border) !important;
            border-radius: 8px !important;
            padding: 12px 24px !important;
            transition: all 0.2s ease !important;
            box-shadow: none !important;
            width: 100% !important;
        }
        .stButton > button:hover {
            border-color: var(--accent) !important;
            color: var(--accent) !important;
            background: var(--accent-glow) !important;
            transform: translateY(-1px) !important;
        }
        .stButton > button:active {
            transform: translateY(0px) !important;
        }

        /* ── File uploader ── */
        [data-testid="stFileUploadDropzone"] {
            background: var(--surface-2) !important;
            border: 1px dashed var(--border) !important;
            border-radius: 12px !important;
            transition: all 0.2s ease !important;
            padding: 40px 24px !important;
        }
        [data-testid="stFileUploadDropzone"]:hover {
            border-color: var(--accent) !important;
            background: var(--surface-3) !important;
        }
        [data-testid="stFileUploadDropzone"] p,
        [data-testid="stFileUploadDropzone"] span {
            font-family: var(--font-body) !important;
            color: var(--text-secondary) !important;
            font-size: 14px !important;
            font-weight: 500 !important;
        }

        /* ── Media frames ── */
        .media-frame {
            background: var(--surface-2);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 16px;
            transition: border-color 0.3s ease;
        }
        .media-frame:hover {
            border-color: var(--border-bright);
        }
        .media-frame-result {
            background: var(--surface-2);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 16px;
            position: relative;
            overflow: hidden;
        }
        .media-frame-result::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; height: 2px;
            background: var(--accent);
        }
        .media-label {
            font-family: var(--font-body);
            font-size: 11px;
            font-weight: 600;
            color: var(--text-muted);
            letter-spacing: 1.5px;
            text-transform: uppercase;
            margin: 0 0 12px 0;
        }
        .media-label-result {
            font-family: var(--font-body);
            font-size: 11px;
            font-weight: 600;
            color: var(--accent);
            letter-spacing: 1.5px;
            text-transform: uppercase;
            margin: 0 0 12px 0;
        }

        /* ── Section heading ── */
        .section-heading {
            font-family: var(--font-display);
            font-size: 24px;
            font-weight: 700;
            color: var(--text-primary);
            letter-spacing: -0.5px;
            margin: 0 0 8px 0;
        }
        .section-sub {
            font-family: var(--font-body);
            font-size: 14px;
            font-weight: 400;
            color: var(--text-secondary);
            margin: 0 0 24px 0;
            line-height: 1.6;
        }

        /* ── Progress bar ── */
        [data-testid="stProgressBar"] > div {
            background: var(--surface-3) !important;
            border-radius: 4px !important;
        }
        [data-testid="stProgressBar"] > div > div {
            background: var(--accent) !important;
        }

        /* ── Download button ── */
        [data-testid="stDownloadButton"] > button {
            font-family: var(--font-body) !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            background: var(--surface-2) !important;
            color: var(--text-primary) !important;
            border: 1px solid var(--border) !important;
            border-radius: 8px !important;
            padding: 10px 24px !important;
            transition: all 0.2s ease !important;
            width: auto !important;
        }
        [data-testid="stDownloadButton"] > button:hover {
            border-color: var(--accent) !important;
            color: var(--accent) !important;
            background: var(--accent-glow) !important;
        }

        /* ── Alerts ── */
        [data-testid="stAlert"] {
            background: var(--surface-2) !important;
            border: 1px solid var(--border) !important;
            border-radius: 10px !important;
            font-family: var(--font-body) !important;
            color: var(--text-primary) !important;
        }

        /* ── Spinner ── */
        [data-testid="stSpinner"] p {
            font-family: var(--font-body) !important;
            color: var(--text-secondary) !important;
            font-size: 14px !important;
        }

        /* ── Scrollbar ── */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: var(--black); }
        ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--border-bright); }

        [data-testid="column"] { padding: 0 12px !important; }
        </style>
    """, unsafe_allow_html=True)

style_ui()


# ── FFmpeg Resolver ───────────────────────────────────────────────────────────
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


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
    <div class="dis-header">
        {'<img class="dis-header-logo" src="' + logo_src + '" alt=""/>' if logo_src else ''}
        <div>
            <p class="dis-header-title">Damage Intelligence Studio</p>
            <p class="dis-header-sub">Road Infrastructure Analysis Platform</p>
        </div>
        <span class="dis-header-badge">Production</span>
    </div>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:

    st.markdown(f"""
        <div class="sidebar-brand">
            <div class="sidebar-logo-row">
                {'<img src="' + logo_src + '" alt=""/>' if logo_src else ''}
                <span class="sidebar-brand-name">DI Studio</span>
            </div>
            <p class="field-label">Configuration Panel</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<p class="field-label">Inference Model</p>', unsafe_allow_html=True)

    options = ["YOLO"]
    if SAM_AVAILABLE and os.path.exists("sam_vit_b_01ec64.pth"):
        options.append("YOLO + SAM")
    if os.path.exists("unet_best.pth"):
        options.append("YOLO + UNet")
    if os.path.exists("deeplab_final.pth"):
        options.append("YOLO + DeepLab")

    model_choice = st.selectbox("Model", options, label_visibility="collapsed")

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    st.markdown('<p class="field-label">Detection Sensitivity</p>', unsafe_allow_html=True)
    conf_threshold = st.slider("Confidence", 0.05, 1.0, 0.25, 0.05, label_visibility="collapsed")

    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown('<p class="field-label">System Status</p>', unsafe_allow_html=True)

    yolo_loaded = False
    with st.spinner("Initializing runtime..."):
        if os.path.exists("bestv3.pt"):
            detector.load_yolo("bestv3.pt")
            yolo_loaded = True

        detector.clear_unused_models(model_choice)

        if model_choice == "YOLO + SAM":
            detector.load_sam()
        elif model_choice == "YOLO + UNet":
            detector.load_unet()
        elif model_choice == "YOLO + DeepLab":
            detector.load_deeplab()

    st.markdown(f"""
        <div class="status-panel">
            <p class="status-title">
                <span class="status-dot"></span>Runtime Active
            </p>
            <p class="status-detail">
                Model &nbsp;&nbsp;{model_choice}<br/>
                Threshold &nbsp;&nbsp;{conf_threshold:.2f}
            </p>
        </div>
    """, unsafe_allow_html=True)


# ── Main Tabs ─────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["Image Analysis", "Video Analysis"])


# ── Tab 1 — Image ─────────────────────────────────────────────────────────────
with tab1:
    st.markdown("""
        <p class="section-heading">Image Analysis</p>
        <p class="section-sub">
            Upload a road surface image to run damage detection and segmentation inference.
            Supported formats: JPG, JPEG, PNG.
        </p>
    """, unsafe_allow_html=True)

    uploaded_image = st.file_uploader(
        "Drop image here or click to browse",
        type=["jpg", "jpeg", "png"],
        key="img",
    )

    if uploaded_image is not None:
        col1, col2 = st.columns(2, gap="large")

        file_bytes = np.asarray(bytearray(uploaded_image.read()), dtype=np.uint8)
        img_bgr    = cv2.imdecode(file_bytes, 1)
        img_rgb    = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

        with col1:
            st.markdown('<div class="media-frame"><p class="media-label">Source Image</p>', unsafe_allow_html=True)
            st.image(img_rgb, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

        if st.button("Run Detection", use_container_width=True):
            with st.spinner("Running inference..."):
                processed_img = detector.process_frame(img_bgr, model_choice, conf_threshold)
            with col2:
                st.markdown('<div class="media-frame-result"><p class="media-label-result">Detection Output</p>', unsafe_allow_html=True)
                st.image(processed_img, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)


# ── Tab 2 — Video ─────────────────────────────────────────────────────────────
with tab2:
    st.markdown("""
        <p class="section-heading">Video Analysis</p>
        <p class="section-sub">
            Upload a video file to process every frame through the active detection model.
            Output is transcoded to H.264 for browser-compatible playback and download.
        </p>
    """, unsafe_allow_html=True)

    uploaded_video = st.file_uploader(
        "Drop video here or click to browse",
        type=["mp4", "avi", "mov"],
        key="vid",
    )

    if uploaded_video is not None:
        st.markdown('<div class="media-frame"><p class="media-label">Source Video</p>', unsafe_allow_html=True)
        st.video(uploaded_video)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

        if st.button("Process Video", use_container_width=True):
            tfile_path = None
            avi_path   = None
            mp4_path   = None

            try:
                # 1. Save upload to disk
                tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                tfile.write(uploaded_video.read())
                tfile.close()
                tfile_path = tfile.name

                cap = cv2.VideoCapture(tfile_path)
                if not cap.isOpened():
                    st.error("Could not open the uploaded video file.")
                    st.stop()

                fps          = cap.get(cv2.CAP_PROP_FPS) or 25
                width        = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height       = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

                # 2. Write processed frames — MJPEG AVI (OpenCV-native, no FFmpeg backend needed)
                avi_path = tempfile.mktemp(suffix=".avi")
                fourcc   = cv2.VideoWriter_fourcc(*"MJPG")
                out      = cv2.VideoWriter(avi_path, fourcc, fps, (width, height))

                if not out.isOpened():
                    st.error("VideoWriter failed to open. Verify your OpenCV installation.")
                    cap.release()
                    st.stop()

                progress_bar     = st.progress(0)
                status_text      = st.empty()
                frames_processed = 0

                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break

                    processed = detector.process_frame(frame, model_choice, conf_threshold)

                    if processed.shape[:2] != (height, width):
                        processed = cv2.resize(processed, (width, height))

                    processed_bgr = cv2.cvtColor(processed, cv2.COLOR_RGB2BGR)
                    out.write(processed_bgr)

                    frames_processed += 1
                    if frames_processed % 5 == 0 or frames_processed == total_frames:
                        progress_bar.progress(min(frames_processed / total_frames, 1.0))
                        status_text.text(f"Processing  {frames_processed} / {total_frames}  frames")

                cap.release()
                out.release()

                # 3. Transcode AVI to H.264 MP4
                ffmpeg_exe = get_ffmpeg_path()

                if ffmpeg_exe:
                    status_text.text("Transcoding to web format...")
                    mp4_path = tempfile.mktemp(suffix="_result.mp4")

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

                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

                    if result.returncode == 0 and os.path.getsize(mp4_path) > 0:
                        final_output = mp4_path
                        output_ext   = "mp4"
                        output_mime  = "video/mp4"
                    else:
                        st.warning(f"Transcoding failed — serving AVI directly.\n{result.stderr[:300]}")
                        final_output = avi_path
                        output_ext   = "avi"
                        output_mime  = "video/x-msvideo"
                else:
                    st.warning(
                        "FFmpeg not found — serving raw AVI. "
                        "Run `pip install imageio[ffmpeg]` and restart to enable MP4 output."
                    )
                    final_output = avi_path
                    output_ext   = "avi"
                    output_mime  = "video/x-msvideo"

                # 4. Display result
                status_text.text("Processing complete.")

                if os.path.exists(final_output) and os.path.getsize(final_output) > 0:
                    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
                    st.markdown('<div class="media-frame-result"><p class="media-label-result">Detection Output</p>', unsafe_allow_html=True)
                    st.video(final_output)
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
                    with open(final_output, "rb") as f:
                        st.download_button(
                            label="Download Processed Video",
                            data=f,
                            file_name=f"dis_output.{output_ext}",
                            mime=output_mime,
                        )
                else:
                    st.error("Output file is empty or missing. Processing may have failed.")

            except subprocess.TimeoutExpired:
                st.error("Transcoding timed out. Try a shorter or lower-resolution clip.")
            except Exception as e:
                st.error(f"Video processing error: {e}")
            finally:
                for p in [tfile_path, avi_path, mp4_path]:
                    if p and os.path.exists(p):
                        try:
                            os.unlink(p)
                        except Exception:
                            pass