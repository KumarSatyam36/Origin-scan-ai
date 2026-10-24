from io import BytesIO
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from PIL.ExifTags import TAGS

app = FastAPI(title="OriginScan AI API", version="0.2.0")

# For a public deployment, replace "*" with your exact frontend origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

MAX_BYTES = 25 * 1024 * 1024
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
VIDEO_EXTENSIONS = {".mp4", ".mov", ".webm", ".m4v"}
ALLOWED_EXTENSIONS = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS

AI_KEYWORDS = [
    "midjourney", "dall-e", "dalle", "stable diffusion", "stablediffusion",
    "firefly", "imagen", "gemini", "flux", "leonardo", "novelai",
    "comfyui", "automatic1111", "sdxl", "openai", "ai generated",
]


@app.get("/")
def root():
    return {"name": "OriginScan AI API", "status": "starter", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}


def inspect_image(content: bytes):
    signals = []
    ai_hits = []
    has_camera_info = False

    try:
        img = Image.open(BytesIO(content))
        signals.append(f"Image format: {img.format}, size {img.width}x{img.height}")

        text_blobs = []
        exif = img.getexif()
        exif_map = {}
        for tag_id, value in exif.items():
            exif_map[TAGS.get(tag_id, tag_id)] = value

        for key, value in img.info.items():
            if isinstance(value, (str, bytes)):
                text = value.decode("utf-8", "ignore") if isinstance(value, bytes) else value
                text_blobs.append(f"{key} {text}")

        make = exif_map.get("Make")
        model = exif_map.get("Model")
        software = exif_map.get("Software")
        taken = exif_map.get("DateTime")

        if make or model:
            has_camera_info = True
            signals.append(f"Camera info found: {make or ''} {model or ''}".strip())
        else:
            signals.append("No camera make or model in metadata.")

        if software:
            signals.append(f"Software tag: {software}")
            text_blobs.append(str(software))
        if taken:
            signals.append(f"Date in metadata: {taken}")
        if not exif_map:
            signals.append("No EXIF metadata found (social apps often strip it from real photos too).")

        combined = " ".join(text_blobs).lower()
        for word in AI_KEYWORDS:
            if word in combined:
                ai_hits.append(word)

    except Exception:
        signals.append("Could not read image metadata.")

    return signals, ai_hits, has_camera_info


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    filename = file.filename or "upload"
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Unsupported file type.")
    content = await file.read(MAX_BYTES + 1)
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    if len(content) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds the 25 MB limit.")

    media_type = "image" if ext in IMAGE_EXTENSIONS else "video"
    signals = [f"File extension: {ext}", f"Media type: {media_type}"]

    if media_type == "image":
        img_signals, ai_hits, has_camera = inspect_image(content)
        signals.extend(img_signals)

        if ai_hits:
            verdict = "AI signs found"
            summary = (
                "The file's metadata mentions AI tools: "
                + ", ".join(sorted(set(ai_hits)))
                + ". This is a strong clue, but metadata can be edited."
            )
        elif has_camera:
            verdict = "Camera info present"
            summary = (
                "The file carries camera details, which is typical of real photos. "
                "This is a clue, not proof, because metadata can be faked."
            )
        else:
            verdict = "Inconclusive"
            summary = (
                "No camera details and no AI tool names were found in the metadata. "
                "That does not show whether the image is real or AI-generated."
            )
    else:
        verdict = "Inconclusive"
        summary = "Video analysis is not available yet, only the upload was validated."

    signals.append("No pixel-level AI detection model has been run yet.")

    return {
        "filename": filename,
        "media_type": media_type,
        "size_bytes": len(content),
        "verdict": verdict,
        "summary": summary,
        "signals": signals,
        "confidence": None,
            }
