const API_BASE = "https://origin-scan-ai.onrender.com";

const input = document.getElementById("media");
const analyze = document.getElementById("analyze");
const fileRow = document.getElementById("file-row");
const fileName = document.getElementById("file-name");
const fileSize = document.getElementById("file-size");
const result = document.getElementById("result");
const resultTitle = document.getElementById("result-title");
const resultCopy = document.getElementById("result-copy");
const signals = document.getElementById("signals");

let selectedFile = null;
const maxSize = 25 * 1024 * 1024;

// Wake the free Render server as soon as the page opens
fetch(API_BASE + "/health").catch(function () {});

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
    fileSize.textContent = (file.size / 1024 / 1024).toFixed(2) + " MB";
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

function showError(title, message) {
    resultTitle.textContent = title;
    resultCopy.textContent = message;
    signals.replaceChildren();
    result.hidden = false;
}

analyze.addEventListener("click", async function () {
    if (!selectedFile) return;

    analyze.disabled = true;
    analyze.textContent = "Analyzing... (first try can take 1 minute)";

    const controller = new AbortController();
    const timer = setTimeout(function () { controller.abort(); }, 90000);

    try {
        const formData = new FormData();
        formData.append("file", selectedFile);

        const response = await fetch(API_BASE + "/analyze", {
            method: "POST",
            body: formData,
            signal: controller.signal
        });

        if (!response.ok) {
            showError(
                "Server error",
                "The server answered with status " + response.status + "."
            );
            return;
        }

        const data = await response.json();

        resultTitle.textContent = data.verdict || "Inconclusive";
        resultCopy.textContent = data.summary || "No conclusive result.";

        signals.replaceChildren();
        (data.signals || []).forEach(function (signal) {
            const item = document.createElement("li");
            item.textContent = signal;
            signals.appendChild(item);
        });

        result.hidden = false;

    } catch (error) {
        if (error.name === "AbortError") {
            showError(
                "Server too slow",
                "No answer after 90 seconds. The free server may still be waking up. Try again."
            );
        } else {
            showError(
                "Could not reach server",
                "Error: " + error.message
            );
        }
    } finally {
        clearTimeout(timer);
        analyze.disabled = !selectedFile;
        analyze.innerHTML = 'Analyze media <span>→</span>';
    }
});
