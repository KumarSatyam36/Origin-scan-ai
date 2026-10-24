from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from io import BytesIO
from PIL import Image
import base64

app = FastAPI(title="OriginScan AI")

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>OriginScan AI</title>
<style>
* { box-sizing: border-box; }
body {
    margin: 0;
    padding: 24px;
    font-family: Arial, sans-serif;
    background: #080d19;
    color: white;
}
.container {
    max-width: 520px;
    margin: 40px auto;
    padding: 25px;
    background: #131c2e;
    border: 1px solid #26344b;
    border-radius: 18px;
}
h1 { color: #57e6b1; text-align: center; }
p { color: #b5c2d6; text-align: center; }
.upload {
    display: block;
    width: 100%;
    padding: 20px;
    margin: 20px 0;
    border: 1px dashed #57e6b1;
    border-radius: 10px;
}
button {
    width: 100%;
    padding: 14px;
    border: 0;
    border-radius: 9px;
    background: #57e6b1;
    color: #08111b;
    font-weight: bold;
    font-size: 16px;
}
#preview {
    display: none;
    width: 100%;
    max-height: 350px;
    object-fit: contain;
    margin: 15px 0;
    border-radius: 10px;
}
#result {
    margin-top: 20px;
    padding: 12px;
    overflow-wrap: anywhere;
    line-height: 1.6;
}
.small { font-size: 12px; }
</style>
</head>
<body>
<div class="container">
    <h1>OriginScan AI</h1>
    <p>Upload an image to inspect its properties.</p>

    <input class="upload" id="file" type="file" accept="image/*">
    <img id="preview" alt="Selected image preview">
    <button id="analyze">Analyze Image</button>
    <div id="result"></div>
    <p class="small">Image inspection is available. AI-origin detection
    is not yet connected.</p>
</div>

<script>
const fileInput = document.getElementById("file");
const preview = document.getElementById("preview");
const result = document.getElementById("result");

fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];

    if (!file) return;

    preview.src = URL.createObjectURL(file);
    preview.style.display = "block";
    result.textContent = "";
});

document.getElementById("analyze").addEventListener("click", async () => {
    const file = fileInput.files[0];

    if (!file) {
        result.textContent = "Please select an image first.";
        return;
    }

    result.textContent = "Analyzing image...";

    const data = new FormData();
    data.append("file", file);

    try {
        const response = await fetch("/analyze", {
            method: "POST",
            body: data
        });

        const answer = await response.json();

        if (!response.ok) {
            throw new Error(answer.detail || "Analysis failed.");
        }

        result.textContent =
            "Filename: " + answer.filename +
            " | Format: " + answer.format +
            " | Dimensions: " + answer.width + " × " + answer.height +
            " | Size: " + answer.size_kb + " KB";

    } catch (error) {
        result.textContent = "Error: " + error.message;
    }
});
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Please upload an image.")

    contents = await file.read()

    if not contents:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="The file is empty.")

    if len(contents) > 10 * 1024 * 1024:
        from fastapi import HTTPException
        raise HTTPException(status_code=413, detail="Maximum image size is 10 MB.")

    try:
        image = Image.open(BytesIO(contents))
        image.verify()

        image = Image.open(BytesIO(contents))

        return {
            "filename": file.filename or "image",
            "format": image.format or "Unknown",
            "width": image.width,
            "height": image.height,
            "size_kb": round(len(contents) / 1024, 2)
        }

    except Exception:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail="Invalid or unsupported image."
    )
