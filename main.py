from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from PIL import Image
from io import BytesIO

app = FastAPI(title="OriginScan AI")

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OriginScan AI</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #0b1020;
            color: white;
            text-align: center;
            padding: 30px 15px;
        }
        .container {
            max-width: 500px;
            margin: 40px auto;
            padding: 25px;
            background: #171f35;
            border-radius: 16px;
        }
        h1 { color: #54e6b1; }
        input, button {
            margin: 15px 0;
            padding: 12px;
            max-width: 100%;
        }
        button {
            background: #54e6b1;
            border: none;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
        }
        #preview {
            max-width: 100%;
            max-height: 300px;
            margin-top: 15px;
            border-radius: 10px;
            display: none;
        }
        #result {
            margin-top: 20px;
            overflow-wrap: anywhere;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>OriginScan AI</h1>
        <p>Upload an image to inspect it.</p>

        <input type="file" id="imageInput" accept="image/*">
        <br>
        <img id="preview" alt="Selected image preview">
        <br>
        <button onclick="uploadImage()">Analyze Image</button>
        <div id="result"></div>
    </div>

    <script>
        const input = document.getElementById("imageInput");
        const preview = document.getElementById("preview");
        const result = document.getElementById("result");

        input.addEventListener("change", function() {
            const file = input.files[0];

            if (!file) return;

            preview.src = URL.createObjectURL(file);
            preview.style.display = "block";
            result.textContent = "";
        });

        async function uploadImage() {
            const file = input.files[0];

            if (!file) {
                result.textContent = "Please select an image first.";
                return;
            }

            const formData = new FormData();
            formData.append("file", file);

            result.textContent = "Uploading image...";

            try {
                const response = await fetch("/analyze", {
                    method: "POST",
                    body: formData
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.detail || "Upload failed");
                }

                result.textContent =
                    "Image uploaded successfully. Format: " +
                    data.format + ", Dimensions: " +
                    data.width + " × " + data.height +
                    ". AI detection is not enabled yet.";

            } catch (error) {
                result.textContent = "Error: " + error.message;
            }
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_PAGE

@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        return {"detail": "Please upload a valid image file."}

    contents = await file.read()

    if len(contents) > 10 * 1024 * 1024:
        return {"detail": "Image must be smaller than 10 MB."}

    try:
        image = Image.open(BytesIO(contents))
        image.verify()

        image = Image.open(BytesIO(contents))

        return {
            "filename": file.filename,
            "format": image.format,
            "width": image.width,
            "height": image.height
        }

    except Exception:
        return {"detail": "The uploaded file is not a valid image."}
