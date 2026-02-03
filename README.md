# Hologram MVP (Depth-based 3D illusion)

This repo contains a minimal MVP that creates a hologram-style 3D illusion from 1 image using MiDaS depth estimation.

## Structure

- backend/: FastAPI server that accepts image uploads, runs MiDaS, and serves the depth PNGs via `/static`.
- frontend/: React + Vite app that uploads images and renders a depth-displaced plane using Three.js.

## Quick start

### Backend

1. Create a venv and install dependencies (recommended):

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
```

2. Run the backend:

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

> Notes: MiDaS may download weights at first run. Use MiDaS_small for CPU-friendly operation. If you have a GPU, ensure CUDA-enabled PyTorch is installed.

### Frontend

1. Install deps and run:

```bash
cd frontend
npm install
npm run dev
```

2. Open the URL shown by Vite (usually http://localhost:5173) and upload an image.

## API

POST /upload
- form field: `file` (image)
- returns: `{ image_url: "/static/uploads/xxx.png", depth_url: "/static/depths/depth_xxx.png" }`

