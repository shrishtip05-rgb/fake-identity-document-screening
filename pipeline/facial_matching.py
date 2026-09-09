# =========================================================
# FACIAL MATCHING MODULE
# =========================================================
#
# Uses:
#   1. YuNet  -> face detection
#   2. SFace  -> face recognition
#
# OpenCV 5 compatibility:
# We force the classic DNN engine because the new OpenCV 5
# graph engine currently has compatibility issues with the
# SFace feature extraction call.
# =========================================================


# IMPORTANT:
# This must be set BEFORE importing cv2.
import os

os.environ["OPENCV_FORCE_DNN_ENGINE"] = "1"


import cv2
import numpy as np


# =========================================================
# MODEL PATHS
# =========================================================

PROJECT_FOLDER = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


YUNET_MODEL = os.path.join(
    PROJECT_FOLDER,
    "models",
    "face_detection_yunet_2026may.onnx"
)


SFACE_MODEL = os.path.join(
    PROJECT_FOLDER,
    "models",
    "face_recognition_sface_2021dec.onnx"
)


# =========================================================
# FACE DETECTION
# =========================================================

def detect_faces(image):
    """
    Detect faces in an image using YuNet.

    Returns:
        list of detected faces
    """

    height, width = image.shape[:2]

    detector = cv2.FaceDetectorYN.create(
        YUNET_MODEL,
        "",
        (width, height),
        0.9,
        0.3,
        5000
    )

    _, faces = detector.detect(image)

    if faces is None:
        return []

    detected_faces = []

    for face in faces:

        x = int(face[0])
        y = int(face[1])
        w = int(face[2])
        h = int(face[3])

        detected_faces.append({
            "x": x,
            "y": y,
            "width": w,
            "height": h,
            "raw_face": face
        })

    return detected_faces


# =========================================================
# FACE COMPARISON
# =========================================================

def compare_faces(
    document_path,
    selfie_path
):
    """
    Compare the face in the document image with
    the face in the selfie.

    Returns:
        dictionary containing similarity and result.
    """

    # -----------------------------------------------------
    # Check model files
    # -----------------------------------------------------

    if not os.path.exists(YUNET_MODEL):

        return {
            "success": False,
            "reason": (
                "YuNet model not found: "
                + YUNET_MODEL
            )
        }


    if not os.path.exists(SFACE_MODEL):

        return {
            "success": False,
            "reason": (
                "SFace model not found: "
                + SFACE_MODEL
            )
        }


    # -----------------------------------------------------
    # Read images
    # -----------------------------------------------------

    document_image = cv2.imread(
        document_path
    )

    selfie_image = cv2.imread(
        selfie_path
    )


    if document_image is None:

        return {
            "success": False,
            "reason": (
                "Could not read document face image."
            )
        }


    if selfie_image is None:

        return {
            "success": False,
            "reason": (
                "Could not read selfie image."
            )
        }


    # -----------------------------------------------------
    # Detect faces
    # -----------------------------------------------------

    document_faces = detect_faces(
        document_image
    )

    selfie_faces = detect_faces(
        selfie_image
    )


    # -----------------------------------------------------
    # Check document face
    # -----------------------------------------------------

    if len(document_faces) == 0:

        return {
            "success": False,
            "reason": (
                "No face detected in document image."
            )
        }


    if len(document_faces) > 1:

        return {
            "success": False,
            "reason": (
                "Multiple faces detected in document image."
            )
        }


    # -----------------------------------------------------
    # Check selfie face
    # -----------------------------------------------------

    if len(selfie_faces) == 0:

        return {
            "success": False,
            "reason": (
                "No face detected in selfie."
            )
        }


    if len(selfie_faces) > 1:

        return {
            "success": False,
            "reason": (
                "Multiple faces detected in selfie."
            )
        }


    # -----------------------------------------------------
    # Create SFace recognizer
    # -----------------------------------------------------

    try:

        recognizer = cv2.FaceRecognizerSF.create(
            SFACE_MODEL,
            ""
        )

    except cv2.error as error:

        return {
            "success": False,
            "reason": (
                "Could not initialize SFace model: "
                + str(error)
            )
        }


    # -----------------------------------------------------
    # Get YuNet face information
    # -----------------------------------------------------

    document_face = document_faces[0][
        "raw_face"
    ]

    selfie_face = selfie_faces[0][
        "raw_face"
    ]


    # -----------------------------------------------------
    # Align and crop faces
    # -----------------------------------------------------

    try:

        document_crop = recognizer.alignCrop(
            document_image,
            document_face
        )

        selfie_crop = recognizer.alignCrop(
            selfie_image,
            selfie_face
        )

    except cv2.error as error:

        return {
            "success": False,
            "reason": (
                "Face alignment failed: "
                + str(error)
            )
        }


    # -----------------------------------------------------
    # Extract SFace features
    # -----------------------------------------------------

    try:

        document_feature = recognizer.feature(
            document_crop
        )

        selfie_feature = recognizer.feature(
            selfie_crop
        )

    except cv2.error as error:

        return {
            "success": False,
            "reason": (
                "SFace feature extraction failed. "
                "This is usually an OpenCV 5 DNN "
                "engine compatibility issue.\n"
                + str(error)
            )
        }


    # -----------------------------------------------------
    # Compare face embeddings
    # -----------------------------------------------------

    try:

        similarity = recognizer.match(
            document_feature,
            selfie_feature,
            cv2.FaceRecognizerSF_FR_COSINE
        )

    except cv2.error as error:

        return {
            "success": False,
            "reason": (
                "Face comparison failed: "
                + str(error)
            )
        }


    # Convert NumPy result to normal Python float
    similarity = float(similarity)


    # -----------------------------------------------------
    # Similarity threshold
    # -----------------------------------------------------
    #
    # OpenCV's SFace example uses approximately 0.363
    # as the cosine similarity threshold.
    #
    # This is a prototype threshold and should be tuned
    # using representative test data later.
    # -----------------------------------------------------

    threshold = 0.363


    if similarity >= threshold:

        result = "MATCH"

    else:

        result = "MISMATCH"


    # -----------------------------------------------------
    # Final result
    # -----------------------------------------------------

    return {

        "success": True,

        "similarity": round(
            similarity,
            4
        ),

        "threshold": threshold,

        "result": result
    }