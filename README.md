# OriginScan AI — Starter Project

OriginScan AI is a web starter for inspecting images and videos for signals that may help assess whether media is AI-generated or edited.

## Important limitation
No detector can reliably prove that all media is AI-generated or authentic. This starter reports **inconclusive** by default unless a user-configured analysis service is connected. Metadata and content credentials are clues, not proof.

## Project layout
- `frontend/` — static upload interface
- `backend/` — FastAPI API with file validation and metadata inspection
- `.gitignore`

## Run locally
Requires Python 3.10+.

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open `frontend/index.html` in a browser. Set `API_BASE` in `frontend/app.js` if the backend is hosted elsewhere.

## Current capabilities
- Upload image/video files through the interface
- Backend validates supported file extensions and size
- Returns a cautious preliminary report
- Extracts basic file metadata (filename, size, MIME type)
- Does **not** claim to detect AI generation reliably yet

## Next steps
1. Deploy the backend to a hosting provider.
2. Connect a validated image/video forensic model.
3. Add C2PA Content Credentials verification.
4. Evaluate false-positive/false-negative rates on representative datasets before public launch.
5. Add rate limiting, malware scanning, retention controls, and privacy policy before accepting public uploads.
