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

# Initialize MiDaS runner (MiDaS_small for speed)
device = "cuda" if torch.cuda.is_available() else "cpu"
midas = MidasRunner(device=device)

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    # save upload
    uid = uuid.uuid4().hex
    filename = f"{uid}_{file.filename}"
    dest = os.path.join(UPLOAD_DIR, filename)
    await save_upload_file(file, dest)

    # infer depth
    depth = midas.infer(dest)  # numpy 2D array normalized 0..1
    depth_fname = f"depth_{uid}.png"
    depth_path = os.path.join(DEPTH_DIR, depth_fname)
    save_depth_png(depth, depth_path)

    # Return relative URLs for frontend
    image_url = f"/static/uploads/{filename}"
    depth_url = f"/static/depths/{depth_fname}"

    return JSONResponse({"image_url": image_url, "depth_url": depth_url})

# simple health endpoint
@app.get("/")
def root():
    return {"status": "ok"}

# For local dev: uvicorn backend.app.main:app --reload --port 8000
