from pathlib import Path
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="OriginScan AI API", version="0.1.0")

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

@app.get("/")
def root():
    return {"name": "OriginScan AI API", "status": "starter", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}

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

    # This starter deliberately does not pretend that metadata proves provenance.
    # Add a validated forensic model and C2PA verification before making claims.
    media_type = "image" if ext in IMAGE_EXTENSIONS else "video"
    return {
        "filename": filename,
        "media_type": media_type,
        "size_bytes": len(content),
        "verdict": "Inconclusive",
        "summary": (
            "This starter has validated the upload format and size, but no "
            "AI-media detection model is connected. It cannot determine whether "
            "this file is AI-generated or authentic."
        ),
        "signals": [
            f"File extension: {ext}",
            f"Detected category from extension: {media_type}",
            "No validated AI-generation classifier has been run.",
            "A file extension and metadata are not proof of authenticity."
        ],
        "confidence": None
    }
