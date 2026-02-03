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


Frontend served by backend

- The backend now serves the frontend static files directly. After starting the backend you can open:
  - http://localhost:8000/            → main landing page (index)
  - http://localhost:8000/dashboard   → dashboard page
  - http://localhost:8000/login       → login-only page

If you are developing the frontend separately you can still open `frontend/index.html` directly in your browser or use the static server scripts in `/frontend/test`.

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
- form field: `files` (1 or 2 image files)
- optional form fields: `edge_sharpen` (boolean), `background_blur` (boolean)
- returns: `{ image_url: "/static/uploads/xxx.png", depth_url: "/static/depths/depth_xxx.png" }`

## Features added in this scaffold

- 2-image support: pass up to 2 images — the backend computes depth for each and averages them for a more robust depth cue.
- Edge sharpening: toggleable option that detects depth edges and enhances them in the depth map, improving wireframe/hologram contours.
- Background blur: toggleable option that blurs far background regions of the original image using the depth map and returns the processed image for rendering.
- Frontend toggles: Auto-rotate and Bloom (postprocessing) toggles are available in the UI.

