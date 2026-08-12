const imageInput = document.getElementById("imageInput");
const preview = document.getElementById("preview");
const browseBtn = document.getElementById("browseBtn");
const dropArea = document.getElementById("dropArea");
const loading = document.getElementById("loading");
const form = document.getElementById("uploadForm");
const predictBtn = document.getElementById("predictBtn");
const clearBtn = document.getElementById("clearBtn");

// Clicking "Choose Photo" opens the normal file picker
browseBtn.addEventListener("click", () => imageInput.click());

// When a file is chosen, show a live preview of it
imageInput.addEventListener("change", () => {
    const file = imageInput.files[0];
    if (!file) return;
    preview.src = URL.createObjectURL(file);
    preview.style.display = "block";
});

// Drag-and-drop support
dropArea.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropArea.style.background = "#dbeafe";
});

dropArea.addEventListener("dragleave", () => {
    dropArea.style.background = "#eff6ff";
});

dropArea.addEventListener("drop", (e) => {
    e.preventDefault();
    dropArea.style.background = "#eff6ff";
    const file = e.dataTransfer.files[0];
    if (!file) return;
    imageInput.files = e.dataTransfer.files;
    preview.src = URL.createObjectURL(file);
    preview.style.display = "block";
});

// Show a loading message while the server processes the image
form.addEventListener("submit", (e) => {
    if (imageInput.files.length === 0) {
        e.preventDefault();
        alert("⚠ Please upload a photo first.");
        return;
    }
    loading.style.display = "block";
    predictBtn.disabled = true;
    predictBtn.innerHTML = "Detecting...";
});

// ==============================
// Webcam Capture
// ==============================
const startCameraBtn = document.getElementById("startCameraBtn");
const captureBtn = document.getElementById("captureBtn");
const retakeBtn = document.getElementById("retakeBtn");
const video = document.getElementById("camera");
const cameraCanvas = document.getElementById("cameraCanvas");

let cameraStream = null;

function stopCamera() {
    if (cameraStream) {
        cameraStream.getTracks().forEach((track) => track.stop());
        cameraStream = null;
    }
}

startCameraBtn.addEventListener("click", async () => {
    stopCamera();
    try {
        cameraStream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = cameraStream;
        video.style.display = "block";
        captureBtn.style.display = "inline-block";
        startCameraBtn.style.display = "none";
    } catch (err) {
        alert("Unable to access camera. Please allow camera permission.");
    }
});

captureBtn.addEventListener("click", () => {
    cameraCanvas.width = video.videoWidth;
    cameraCanvas.height = video.videoHeight;
    const ctx = cameraCanvas.getContext("2d");
    ctx.drawImage(video, 0, 0);

    cameraCanvas.toBlob((blob) => {
        const file = new File([blob], "camera.jpg", { type: "image/jpeg" });
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        imageInput.files = dataTransfer.files;

        preview.src = URL.createObjectURL(file);
        preview.style.display = "block";
    });

    stopCamera();
    video.style.display = "none";
    captureBtn.style.display = "none";
    retakeBtn.style.display = "inline-block";
});

retakeBtn.addEventListener("click", async () => {
    preview.src = "";
    preview.style.display = "none";
    imageInput.value = "";

    try {
        cameraStream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = cameraStream;
        video.style.display = "block";
        captureBtn.style.display = "inline-block";
        retakeBtn.style.display = "none";
    } catch (err) {
        alert("Unable to access camera.");
    }
});

// Reset the form (and camera UI) back to its starting state
clearBtn.addEventListener("click", () => {
    imageInput.value = "";
    preview.src = "";
    preview.style.display = "none";
    loading.style.display = "none";
    predictBtn.disabled = false;
    predictBtn.innerHTML = "Detect Faces";

    stopCamera();
    video.style.display = "none";
    captureBtn.style.display = "none";
    retakeBtn.style.display = "none";
    startCameraBtn.style.display = "inline-block";

    const result = document.querySelector(".result");
    if (result) result.remove();

    const warning = document.querySelector(".warning");
    if (warning) warning.remove();
});

// ==============================
// Search Detection History
// ==============================
const historySearch = document.getElementById("historySearch");
const noResultsMsg = document.getElementById("noResultsMsg");

if (historySearch) {
    historySearch.addEventListener("keyup", function () {
        const query = this.value.toLowerCase();
        const rows = document.querySelectorAll("#historyTableBody tr");
        let visibleCount = 0;

        rows.forEach((row) => {
            const text = row.innerText.toLowerCase();
            const matches = text.indexOf(query) > -1;
            row.style.display = matches ? "" : "none";
            if (matches) visibleCount++;
        });

        if (noResultsMsg) {
            noResultsMsg.style.display = visibleCount === 0 ? "block" : "none";
        }
    });
}
