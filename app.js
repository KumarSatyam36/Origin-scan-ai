const API_BASE = "https://origin-scan-ai.onrender.com";

const input = document.getElementById("media");
const analyze = document.getElementById("analyze");
const fileRow = document.getElementById("file-row");
const fileName = document.getElementById("file-name");
const fileSize = document.getElementById("file-size");
const result = document.getElementById("result");

let selectedFile = null;

const maxSize = 25 * 1024 * 1024;

input.addEventListener("change", function () {
    const file = input.files[0];

    if (!file) return;

    if (file.size > maxSize) {
        alert("File must be smaller than 25 MB.");
        input.value = "";
        return;
    }

    selectedFile = file;

    fileName.textContent = file.name;
    fileSize.textContent =
        (file.size / 1024 / 1024).toFixed(2) + " MB";

    fileRow.hidden = false;
    analyze.disabled = false;
});

document.getElementById("remove").addEventListener("click", function () {
    selectedFile = null;
    input.value = "";
    fileRow.hidden = true;
    analyze.disabled = true;
    result.hidden = true;
});

analyze.addEventListener("click", async function () {
    if (!selectedFile) return;

    analyze.disabled = true;
    analyze.textContent = "Analyzing...";

    try {
        const formData = new FormData();
        formData.append("file", selectedFile);

        const response = await fetch(
            `${API_BASE}/analyze`,
            {
                method: "POST",
                body: formData
            }
        );

        if (!response.ok) {
            throw new Error("Analysis server returned an error.");
        }

        const data = await response.json();

        document.getElementById("result-title").textContent =
            data.verdict || "Inconclusive";

        document.getElementById("result-copy").textContent =
            data.summary || "No conclusive result.";

        const signals = document.getElementById("signals");
        signals.replaceChildren();

        (data.signals || []).forEach(function (signal) {
            const item = document.createElement("li");
            item.textContent = signal;
            signals.appendChild(item);
        });

        result.hidden = false;

    } catch (error) {
        document.getElementById("result-title").textContent =
            "Analysis unavailable";

        document.getElementById("result-copy").textContent =
            "The analysis server is not connected. The file was selected, but AI detection could not be completed.";

        result.hidden = false;

    } finally {
        analyze.disabled = !selectedFile;
        analyze.innerHTML = 'Analyze media <span>→</span>';
    }
});
