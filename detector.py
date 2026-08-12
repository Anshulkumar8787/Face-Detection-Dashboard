import os
import cv2

# -------------------------------------------------------------------
# TWO DETECTORS, ONE FUNCTION
# -------------------------------------------------------------------
# 1) YuNet — a real, small deep-learning face detector from OpenCV's
#    own model zoo. It was actually TRAINED on thousands of photos
#    of real human faces, at every angle, so it understands what a
#    face genuinely looks like (eyes, nose, mouth, proportions) —
#    not just "a roughly square patch with contrast in the middle."
#
# 2) Haar Cascade — the older method we started with. We keep it as
#    a FALLBACK only, in case you haven't downloaded the YuNet model
#    file yet. It still works, just less accurately.
# -------------------------------------------------------------------

YUNET_MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "models",
    "face_detection_yunet_2023mar.onnx"
)

yunet_detector = None

if os.path.exists(YUNET_MODEL_PATH):
    # (320, 320) is just a starting size — we resize it per-image
    # inside detect_faces() below, based on the real photo's size.
    yunet_detector = cv2.FaceDetectorYN.create(
        YUNET_MODEL_PATH,
        "",
        (320, 320),
        score_threshold=0.75,   # how confident YuNet must be to count something as a face
        nms_threshold=0.3,      # merges duplicate/overlapping detections of the same face
        top_k=5000
    )

# Load the fallback Haar Cascade too (loading it is cheap, so we
# always have it ready even if YuNet is available).
cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
haar_detector = cv2.CascadeClassifier(cascade_path)


def _detect_with_yunet(image):
    """
    Runs the deep-learning YuNet detector on the image.
    Returns a list of (x, y, w, h, confidence) tuples.
    """
    height, width = image.shape[:2]

    # YuNet needs to know the exact size of the image you're feeding it
    # so it can scale its internal grid correctly.
    yunet_detector.setInputSize((width, height))

    # detect() returns (retval, faces). 'faces' is an array where each
    # row is: [x, y, w, h, then 5 pairs of facial landmark coordinates,
    # then a confidence score as the very last value].
    _, faces = yunet_detector.detect(image)

    boxes = []
    if faces is not None:
        for face in faces:
            x, y, w, h = face[0:4].astype(int)
            confidence = float(face[-1])

            # Clip negative coordinates — YuNet can occasionally predict
            # a box that starts slightly outside the image edge.
            x = max(0, x)
            y = max(0, y)

            boxes.append((x, y, w, h, confidence))

    return boxes


def _detect_with_haar(image):
    """
    Fallback detector. Same tuned logic as before: grayscale +
    histogram equalization + a photo-relative minimum face size +
    shape filtering, to keep false positives down.
    """
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_image = cv2.equalizeHist(gray_image)

    img_height, img_width = gray_image.shape[:2]
    min_face_dimension = int(min(img_height, img_width) * 0.08)
    min_face_dimension = max(min_face_dimension, 40)

    faces = haar_detector.detectMultiScale(
        gray_image,
        scaleFactor=1.08,
        minNeighbors=8,
        minSize=(min_face_dimension, min_face_dimension)
    )

    boxes = []
    for (x, y, w, h) in faces:
        aspect_ratio = w / float(h)
        if 0.75 <= aspect_ratio <= 1.35:
            # No real confidence score from Haar, so we store None.
            boxes.append((x, y, w, h, None))

    return boxes


def detect_faces(image_path, output_path):
    """
    Takes the path of an uploaded image, finds every face in it using
    whichever detector is available (YuNet preferred, Haar as backup),
    draws a blue box around each face, saves the result to
    output_path, and returns information about what it found.
    """

    image = cv2.imread(image_path)

    if image is None:
        return {
            "faces_found": 0,
            "boxes": [],
            "error": "Could not read the uploaded image.",
            "engine": None
        }

    if yunet_detector is not None:
        detections = _detect_with_yunet(image)
        engine = "YuNet (deep learning)"
    else:
        detections = _detect_with_haar(image)
        engine = "Haar Cascade (fallback — download the YuNet model for better accuracy)"

    output_image = image.copy()
    boxes = []

    for (x, y, w, h, confidence) in detections:
        cv2.rectangle(
            output_image,
            (x, y),
            (x + w, y + h),
            (255, 0, 0),
            2
        )

        entry = {"x": int(x), "y": int(y), "w": int(w), "h": int(h)}
        if confidence is not None:
            entry["confidence"] = round(confidence * 100, 1)
        boxes.append(entry)

    cv2.imwrite(output_path, output_image)

    return {
        "faces_found": len(boxes),
        "boxes": boxes,
        "error": None,
        "engine": engine
    }
