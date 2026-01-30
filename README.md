# Skin Tone Classifier API

API that classifies skin tone from images and optionally detects dark circles and eye bags. Returns fine labels (e.g. CA, CF), coarse labels (Light, Medium, Dark), and hex skin color per face.

---

## How to run

### Option 1: Setup script (recommended)

**Mac / Linux**

```bash
./setup_and_run.sh
```

**Windows**

```cmd
setup_and_run.bat
```

These scripts create a virtual environment (`.venv`), install dependencies from `requirements.txt`, and start the API at `http://0.0.0.0:8000`.

### Option 2: Manual

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate.bat
pip install -r requirements.txt
export PYTHONPATH=./src     # Windows: set PYTHONPATH=%CD%\src
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Option 3: Docker

```bash
docker build -t skin-tone-api .
docker run -p 8000:8000 -e ROBOFLOW_API_KEY=N984HNwXaGBLQB7lGlga skin-tone-api
```

---

## Environment

| Variable | Required | Description |
|----------|----------|-------------|
| `ROBOFLOW_API_KEY` | No | When set, `/classify` also returns eye detection (darkcircle, eyebag). Skin-tone works without it. |

---

## Endpoints

### `GET /`

Root; returns API info and link to docs.

**Response**

```json
{
  "message": "Skin Tone Classifier API",
  "docs": "/docs",
  "endpoints": {
    "classify": "POST /classify — skin tone (label, color, confidence) + eyes (darkcircle, eyebag + confidence)"
  }
}
```

---

### `POST /classify`

Upload an image; get skin-tone classification per face and (if `ROBOFLOW_API_KEY` is set) eye detection.

**Request**

- **Body:** `multipart/form-data` with one image file.
- **Query parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `tone_palette` | string | `perla` | Palette: `perla`, `monk`, `yadon-ostfeld`, `proder`, `bw` |
| `confidence_min` | float | `0.30` | Min confidence (0.0–1.0) for eye detections |

**Allowed file types:** `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.tif`

**Response**

```json
{
  "results": [
    {
      "label": "Light",
      "color": "#e8c4a8",
      "confidence": 0.95
    }
  ],
  "eyes": {
    "darkcircle": true,
    "darkcircle_confidence": 0.72,
    "eyebag": false,
    "eyebag_confidence": 0.0
  }
}
```

- **`results`:** One entry per detected face: `label` (Light/Medium/Dark), `color` (hex), `confidence` (0–100 scale).
- **`eyes`:** Present when `ROBOFLOW_API_KEY` is set: `darkcircle`, `darkcircle_confidence`, `eyebag`, `eyebag_confidence`.

**Example (curl)**

```bash
curl -X POST "http://localhost:8000/classify" \
  -F "image_file=@photo.jpg"
```

---

## Interactive docs

When the API is running, open:

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
