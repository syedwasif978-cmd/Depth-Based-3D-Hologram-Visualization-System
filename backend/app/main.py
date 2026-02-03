from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import torch
from .model import MidasRunner
from .utils import save_upload_file, save_depth_png

BASE_STATIC = os.path.join(os.path.dirname(__file__), "..", "static")
UPLOAD_DIR = os.path.join(BASE_STATIC, "uploads")
DEPTH_DIR = os.path.join(BASE_STATIC, "depths")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DEPTH_DIR, exist_ok=True)

app = FastAPI(title="Hologram Depth MVP")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
# Serve static files at /static
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "..", "static")), name="static")

# Serve frontend static files (single-page fallback and pages)
# FRONTEND_DIR is the workspace-level frontend folder created by the UI work
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'frontend'))
if os.path.isdir(FRONTEND_DIR):
    app.mount('/', StaticFiles(directory=FRONTEND_DIR, html=True), name='frontend')

# Dedicated routes for convenience (dashboard, login) that return the appropriate page files
from fastapi.responses import FileResponse

@app.get('/dashboard')
def dashboard_page():
    p = os.path.join(FRONTEND_DIR, 'pages', 'dashboard.html')
    if os.path.exists(p):
        return FileResponse(p, media_type='text/html')
    # fallback to root index
    return FileResponse(os.path.join(FRONTEND_DIR, 'index.html'), media_type='text/html')

@app.get('/login')
def login_page():
    p = os.path.join(FRONTEND_DIR, 'pages', 'login.html')
    if os.path.exists(p):
        return FileResponse(p, media_type='text/html')
    return FileResponse(os.path.join(FRONTEND_DIR, 'index.html'), media_type='text/html')

# Initialize MiDaS runner (MiDaS_small for speed)
device = "cuda" if torch.cuda.is_available() else "cpu"
midas = MidasRunner(device=device)

from fastapi import Form
from typing import List
from .utils import save_upload_file, save_depth_png, apply_edge_sharpen, apply_background_blur_to_image

@app.post("/upload")
async def upload(files: List[UploadFile] = File(...), edge_sharpen: bool = Form(False), background_blur: bool = Form(False)):
    """Accept 1 or 2 image files, optional edge sharpening and background blur.
    Returns processed image (maybe blurred) and a generated depth map.
    """
    if len(files) == 0 or len(files) > 2:
        raise HTTPException(status_code=400, detail="Provide 1 or 2 image files")

    saved_paths = []
    for file in files:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Files must be images")
        uid = uuid.uuid4().hex
        filename = f"{uid}_{file.filename}"
        dest = os.path.join(UPLOAD_DIR, filename)
        await save_upload_file(file, dest)
        saved_paths.append(dest)

    # Run MiDaS on each saved image
    depths = [midas.infer(p) for p in saved_paths]
    if len(depths) == 2:
        depth = (depths[0] + depths[1]) / 2.0
    else:
        depth = depths[0]

    # Optional edge sharpening to enhance contours
    if edge_sharpen:
        depth = apply_edge_sharpen(depth, weight=0.25)

    # Save depth map
    depth_fname = f"depth_{uuid.uuid4().hex}.png"
    depth_path = os.path.join(DEPTH_DIR, depth_fname)
    save_depth_png(depth, depth_path)

    # Optionally produce a blurred background image using the depth map
    # Use the first uploaded image as the source for image-based effects
    source_image = saved_paths[0]
    processed_image_url = f"/static/uploads/{os.path.basename(source_image)}"
    if background_blur:
        proc_fname = f"proc_{uuid.uuid4().hex}_{os.path.basename(source_image)}"
        proc_path = os.path.join(UPLOAD_DIR, proc_fname)
        apply_background_blur_to_image(source_image, depth, proc_path, blur_sigma=15, depth_threshold=0.45)
        processed_image_url = f"/static/uploads/{proc_fname}"

    return JSONResponse({"image_url": processed_image_url, "depth_url": f"/static/depths/{depth_fname}"})

# simple health endpoint
@app.get("/")
def root():
    return {"status": "ok"}

# For local dev: uvicorn backend.app.main:app --reload --port 8000
