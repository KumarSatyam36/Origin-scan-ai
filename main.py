from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from io import BytesIO
from PIL import Image

app = FastAPI(
    title="OriginScan AI",
    description="AI Image Inspection",
    version="1.0.0"
)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OriginScan AI</title>
    <style>
        * { box-sizing: border-box; }

        body {
            margin: 0;
            padding: 20px;
            background: #080d19;
            color: white;
            font-family: Arial, sans-serif;
        }

        .container {
            max-width: 520px;
            margin: 40px auto;
            padding: 25px;
            background: #131c2e;
            border-radius: 18px;
            border: 1px solid #26344b;
        }

        h1 {
            color: #57e6b1;
            text-align: center;
        }

        p {
            color: #b5c2d6;
            text-align: center;
        }

        input {
            width: 100%;
            margin: 20px 0;
            padding: 14px;
            background: #202c42;
            color: white;
            border: 1px solid #57e6b1;
            border-radius: 10px;
        }

        button {
            width: 100%;
            padding: 15px;
            background: #57e6b1;
            color: #08111b;
            font-size: 16px;
            font-weight: bold;
            border: none;
            border-radius: 9px;
        }

        #preview {
            display: none;
            max-width: 100%;
            max-height: 350px;
            margin: 15px auto;
            border-radius: 10px;
        }

        #result {
            margin-top: 20px;
            padding: 12px;
            overflow-wrap: anywhere;
            line-height: 1.7;
        }
    </style>
</head>

<body>
    <div class="container">
        <h1>OriginScan AI</h1>
        <p>Inspect your image in seconds.</p>

        <input id="file" type="file" accept="image/*">

        <img id="preview" alt="Selected image preview">

        <button id="analyze">Analyze Image</button>

        <div id="result"></div>

        <p>
            Image inspection is available.
            AI-origin detection is not yet connected.
        </p>
    </div>

    <script>
        const fileInput = document.getElementById("file");
        const preview = document.getElementById("preview");
        const result = document.getElementById("result");

        fileInput.addEventListener("change", () => {
            const file = fileInput.files[0];

            if (!file) {
                preview.style.display = "none";
                return;
            }

            preview.src = URL.createObjectURL(file);
            preview.style.display = "block";
            result.textContent = "";
        });

        document.getElementById("analyze").addEventListener(
            "click", async () => {
                const file = fileInput.files[0];

                if (!file) {
                    result.textContent = "Please select an image first.";
                    return;
                }

                result.textContent = "Analyzing image...";

                const formData = new FormData();
                formData.append("file", file);

                try {
                    const response = await fetch("/analyze", {
                        method: "POST",
                        body: formData
                    });

                    const data = await response.json();

                    if (!response.ok) {
                        throw new Error(
                            data.detail || "Analysis failed."
                        );
                    }

                    result.textContent =
                        "Filename: " + data.filename +
                        " | Format: " + data.format +
                        " | Dimensions: " + data.width + " × " +
                        data.height +
                        " | Size: " + data.size_kb + " KB";

                } catch (error) {
                    result.textContent = "Error: " + error.message;
                }
            }
        );
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML


@app.get("/health")
async def health():
    return {"status": "ok", "app": "OriginScan AI"}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Please upload an image file."
        )

    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty."
        )

    if len(contents) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="Maximum image size is 10 MB."
        )

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
        raise HTTPException(
            status_code=400,
            detail="Invalid or unsupported image."
        )
