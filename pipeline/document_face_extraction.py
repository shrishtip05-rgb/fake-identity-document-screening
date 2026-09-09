# =========================================================
# DOCUMENT FACE EXTRACTION
# =========================================================
#
# This module finds the person's face directly inside the
# uploaded Aadhaar/document image using YuNet.
#
# Flow:
#
# Aadhaar image
#      ↓
# YuNet face detection
#      ↓
# Select detected face
#      ↓
# Crop face
#      ↓
# Save cropped face
#
# IMPORTANT:
# The face detected here will later be passed to SFace
# for comparison with the user's selfie.
# =========================================================


import os
import cv2


# =========================================================
# PROJECT PATH
# =========================================================

PROJECT_FOLDER = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


# =========================================================
# YUNET MODEL
# =========================================================

YUNET_MODEL = os.path.join(
    PROJECT_FOLDER,
    "models",
    "face_detection_yunet_2026may.onnx"
)


# =========================================================
# DETECT FACE
# =========================================================

def detect_document_face(document_path):
    """
    Detect a face inside the uploaded document.

    Parameters:
        document_path (str):
            Path to the Aadhaar/document image.

    Returns:
        dictionary containing detection information.
    """

    # -----------------------------------------------------
    # Check model
    # -----------------------------------------------------

    if not os.path.exists(YUNET_MODEL):

        return {
            "success": False,
            "reason": (
                "YuNet model not found: "
                + YUNET_MODEL
            )
        }


    # -----------------------------------------------------
    # Read document
    # -----------------------------------------------------

    image = cv2.imread(document_path)


    if image is None:

        return {
            "success": False,
            "reason": (
                "Could not read the document image."
            )
        }


    # -----------------------------------------------------
    # Get image dimensions
    # -----------------------------------------------------

    height, width = image.shape[:2]


    # -----------------------------------------------------
    # Create YuNet detector
    # -----------------------------------------------------

    detector = cv2.FaceDetectorYN.create(

        YUNET_MODEL,

        "",

        (width, height),

        0.6,       # score threshold

        0.3,       # NMS threshold

        5000       # maximum detections
    )


    # -----------------------------------------------------
    # Detect faces
    # -----------------------------------------------------

    _, faces = detector.detect(image)


    # -----------------------------------------------------
    # No face found
    # -----------------------------------------------------

    if faces is None or len(faces) == 0:

        return {
            "success": False,
            "reason": (
                "No face was detected inside "
                "the document."
            )
        }


    # -----------------------------------------------------
    # If multiple faces are detected
    #
    # For an identity document we expect one
    # person's photograph.
    #
    # Select the face with the highest confidence.
    # -----------------------------------------------------

    best_face = max(
        faces,
        key=lambda face: float(face[14])
    )


    # -----------------------------------------------------
    # Extract bounding box
    # -----------------------------------------------------

    x = max(
        0,
        int(best_face[0])
    )

    y = max(
        0,
        int(best_face[1])
    )

    w = int(best_face[2])
    h = int(best_face[3])


    # -----------------------------------------------------
    # Make sure bounding box stays inside image
    # -----------------------------------------------------

    x2 = min(
        width,
        x + w
    )

    y2 = min(
        height,
        y + h
    )


    # -----------------------------------------------------
    # Validate bounding box
    # -----------------------------------------------------

    if x2 <= x or y2 <= y:

        return {
            "success": False,
            "reason": (
                "Invalid face bounding box detected."
            )
        }


    # -----------------------------------------------------
    # Crop face
    # -----------------------------------------------------

    face_crop = image[
        y:y2,
        x:x2
    ]


    if face_crop.size == 0:

        return {
            "success": False,
            "reason": (
                "Face crop is empty."
            )
        }


    # -----------------------------------------------------
    # Save cropped face
    # -----------------------------------------------------

    output_folder = os.path.join(
        PROJECT_FOLDER,
        "uploads"
    )

    os.makedirs(
        output_folder,
        exist_ok=True
    )


    output_path = os.path.join(
        output_folder,
        "document_face_from_document.jpg"
    )


    cv2.imwrite(
        output_path,
        face_crop
    )


    # -----------------------------------------------------
    # Return result
    # -----------------------------------------------------

    return {

        "success": True,

        "face_path": output_path,

        "confidence": round(
            float(best_face[14]),
            4
        ),

        "bounding_box": {

            "left": x,

            "top": y,

            "width": x2 - x,

            "height": y2 - y
        }
    }
