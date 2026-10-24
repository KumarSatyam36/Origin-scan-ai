import os
import httpx
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for your GitHub Pages frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fetch Sightengine API credentials from environment variables
SIGHTENGINE_API_USER = os.getenv("SIGHTENGINE_API_USER")
SIGHTENGINE_API_SECRET = os.getenv("SIGHTENGINE_API_SECRET")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "OriginScan AI Backend is running"}

@app.post("/analyze")
async def analyze_media(file: UploadFile = File(...)):
    if not SIGHTENGINE_API_USER or not SIGHTENGINE_API_SECRET:
        raise HTTPException(
            status_code=500,
            detail="API credentials not configured on backend."
        )

    # Read file content from upload
    file_bytes = await file.read()

    # Call Sightengine Deepfake/AI-generated detection API
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.sightengine.com/1.0/check.json",
                data={
                    "models": "genai",  # Checks for AI-generated / deepfake images
                    "api_user": SIGHTENGINE_API_USER,
                    "api_secret": SIGHTENGINE_API_SECRET,
                },
                files={"media": (file.filename, file_bytes, file.content_type)}
            )
            data = response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error contacting forensic service: {str(e)}")

    if response.status_code != 200 or data.get("status") != "success":
        raise HTTPException(status_code=400, detail=data.get("error", {}).get("message", "Analysis failed"))

    # Extract score from Sightengine response
    # 'genai' score ranges from 0.0 (real) to 1.0 (AI generated)
    ai_score = data.get("type", {}).get("ai_generated", 0.0)
    is_ai = ai_score > 0.5

    return {
        "is_ai_generated": is_ai,
        "confidence_score": round(ai_score * 100, 2),
        "details": {
            "ai_generated_probability": ai_score,
            "raw_response": data
        }
    }
    
