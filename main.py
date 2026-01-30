import tempfile
import os
from typing import Optional

import stone
from fastapi import FastAPI, UploadFile, HTTPException, Query
from inference_sdk import InferenceHTTPClient, InferenceConfiguration

app = FastAPI(
    title="Skin Tone Classifier API",
    description="Classify skin tone from images. Returns fine labels (e.g. CA, CF) and coarse labels (Light, Medium, Dark).",
    version="1.0.0",
)

# Roboflow client configuration
ROBOFLOW_API_KEY = os.environ.get("ROBOFLOW_API_KEY", "N984HNwXaGBLQB7lGlga")
ROBOFLOW_MODEL_ID = "dark_circle/1"
ROBOFLOW_CLIENT = InferenceHTTPClient(
    api_url="https://detect.roboflow.com",
    api_key=ROBOFLOW_API_KEY,
)
ROBOFLOW_CONFIG = InferenceConfiguration(
    confidence_threshold=0.30,  # Lower threshold to catch more detections
    iou_threshold=0.50          # Match model overlap threshold (50%)
)


@app.get("/")
async def root():
    return {
        "message": "Skin Tone Classifier API",
        "docs": "/docs",
        "endpoints": {
            "classify": "POST /classify — skin tone (label, color, confidence) + eyes (darkcircle, eyebag + confidence)",
        },
    }


ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".tif"}


@app.post("/classify")
async def classify(
    image_file: UploadFile,
    tone_palette: Optional[str] = Query("perla", description="Palette: perla, monk, yadon-ostfeld, proder, bw"),
    confidence_min: float = Query(0.30, ge=0.0, le=1.0, description="Eyes: min confidence (0.0-1.0)"),
):
    """
    **Input:** image file (multipart/form-data).

    **Output:** Skin tone classification + eye classification in one response.

    - `results`: Skin tone per face — `label` (Light/Medium/Dark), `color` (hex), `confidence` (0-100)
    - `eyes`: `darkcircle`, `darkcircle_confidence`, `eyebag`, `eyebag_confidence` — present when ROBOFLOW_API_KEY is set
    """
    content = await image_file.read()
    ext = os.path.splitext(image_file.filename or "")[1].lower()
    if ext not in ALLOWED_EXT:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXT)}")
    fd, tmp_path = tempfile.mkstemp(suffix=ext)
    try:
        os.write(fd, content)
    except Exception as e:
        os.close(fd)
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise HTTPException(status_code=400, detail=str(e))
    os.close(fd)

    try:
        # Skin tone (classify)
        result = stone.process(
            tmp_path,
            tone_palette=tone_palette or "perla",
        )
    except Exception as e:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=str(e))

    try:
        faces = result.get("faces", [])
        results = []
        for face in faces:
            label = face.get("coarse_tone_label") or ""
            color = face.get("skin_tone") or ""
            confidence = face.get("accuracy")
            if confidence is not None:
                confidence = round(float(confidence), 2)
            results.append({
                "label": label,
                "color": color,
                "confidence": confidence,
            })

        response = {"results": results}

        # Eyes (darkcircle, eyebag) when Roboflow is configured
        if ROBOFLOW_API_KEY:
            try:
                with ROBOFLOW_CLIENT.use_configuration(ROBOFLOW_CONFIG):
                    rf_result = ROBOFLOW_CLIENT.infer(tmp_path, model_id=ROBOFLOW_MODEL_ID)
                predictions = [
                    p for p in rf_result.get("predictions", [])
                    if p.get("confidence", 0) >= confidence_min
                    and p.get("class") in {"Eyebag", "darkcircle"}
                ]
                darkcircle_preds = [p for p in predictions if p.get("class") == "darkcircle"]
                eyebag_preds = [p for p in predictions if p.get("class") == "Eyebag"]
                response["eyes"] = {
                    "darkcircle": bool(darkcircle_preds),
                    "darkcircle_confidence": round(max((p.get("confidence", 0) for p in darkcircle_preds), default=0), 2),
                    "eyebag": bool(eyebag_preds),
                    "eyebag_confidence": round(max((p.get("confidence", 0) for p in eyebag_preds), default=0), 2),
                }
            except Exception:
                response["eyes"] = {
                    "darkcircle": False, "darkcircle_confidence": 0,
                    "eyebag": False, "eyebag_confidence": 0,
                }

        return response
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
