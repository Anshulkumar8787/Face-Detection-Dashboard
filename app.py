from flask import Flask, render_template, request, send_from_directory, redirect
import os
import csv
from datetime import datetime
from werkzeug.utils import secure_filename
from detector import detect_faces

app = Flask(__name__)

# ------------------------------
# Folders
# ------------------------------
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def allowed_file(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# ------------------------------
# History (CSV file, same idea as your other 2 projects)
# ------------------------------
HISTORY_FOLDER = "history"
HISTORY_FILE = os.path.join(HISTORY_FOLDER, "history.csv")
os.makedirs(HISTORY_FOLDER, exist_ok=True)


def save_history(original_name, result_name, faces_found):
    current_time = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
    with open(HISTORY_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([original_name, result_name, faces_found, current_time])


def load_history():
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            history = list(reader)
    history.reverse()
    return history


def count_total_faces(history):
    return sum(int(item["Faces Found"]) for item in history if item["Faces Found"].isdigit())


@app.route("/", methods=["GET", "POST"])
def home():

    warning = ""
    result = None
    original_filename = ""

    if request.method == "POST":

        if "image" not in request.files or request.files["image"].filename == "":
            warning = "⚠ Please upload an image first."
            history = load_history()
            return render_template("index.html", warning=warning, result=None,
                                    original_filename="", history=history,
                                    total_faces=count_total_faces(history))

        file = request.files["image"]

        if not allowed_file(file.filename):
            warning = "⚠ Only JPG, JPEG and PNG images are allowed."
            history = load_history()
            return render_template("index.html", warning=warning, result=None,
                                    original_filename="", history=history,
                                    total_faces=count_total_faces(history))

        # Save the uploaded photo with a safe filename.
        # We add a timestamp prefix so repeated webcam captures (which
        # all arrive named "camera.jpg") don't overwrite each other.
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
        safe_name = secure_filename(file.filename)
        original_filename = f"{timestamp}_{safe_name}"
        original_path = os.path.join(app.config["UPLOAD_FOLDER"], original_filename)
        file.save(original_path)

        # Build a filename for the "boxed" output image
        result_filename = "detected_" + original_filename
        result_path = os.path.join(app.config["UPLOAD_FOLDER"], result_filename)

        # Run the actual face detection
        detection = detect_faces(original_path, result_path)

        result = {
            "original": original_filename,
            "detected": result_filename,
            "faces_found": detection["faces_found"],
            "boxes": detection["boxes"],
            "error": detection["error"],
            "engine": detection["engine"]
        }

        if detection["error"] is None:
            save_history(original_filename, result_filename, detection["faces_found"])

    history = load_history()

    return render_template(
        "index.html",
        warning=warning,
        result=result,
        original_filename=original_filename,
        history=history,
        total_faces=count_total_faces(history)
    )


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/clear_history")
def clear_history():
    with open(HISTORY_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Original Image", "Detected Image", "Faces Found", "Time"])
    return redirect("/")


@app.route("/delete_history/<int:index>")
def delete_history(index):
    # 'index' here refers to the row's position in the REVERSED list
    # shown on the page (newest first) — the same order the person
    # sees on screen, since that's what the delete link was built from.
    rows = []

    with open(HISTORY_FILE, "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        rows = list(reader)

    if len(rows) > 1:
        header = rows[0]
        data_rows = rows[1:]

        # The page displays history newest-first (load_history reverses
        # it), so we reverse here too before deleting, to make sure we
        # remove the exact row the person clicked on.
        data_rows.reverse()

        if 0 <= index < len(data_rows):
            del data_rows[index]

        data_rows.reverse()

        with open(HISTORY_FILE, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(data_rows)

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
