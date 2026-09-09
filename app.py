# =========================================================
# FLASK APPLICATION
# =========================================================

from flask import (
    Flask,
    render_template,
    request
)

from werkzeug.utils import secure_filename

import os
import uuid


# =========================================================
# PIPELINE MODULES
# =========================================================

from pipeline import metadata_analysis
from pipeline import ocr
from pipeline import document_identification
from pipeline import field_extraction
from pipeline import field_validation

from pipeline import pan_extraction
from pipeline import pan_validation

from pipeline import tamper_analysis
from pipeline import region_comparison
from pipeline import document_face_extraction
from pipeline import facial_matching
from pipeline import scoring


# =========================================================
# CREATE APP
# =========================================================

app = Flask(__name__)


# =========================================================
# UPLOAD CONFIGURATION
# =========================================================

PROJECT_FOLDER = os.path.dirname(
    os.path.abspath(__file__)
)


UPLOAD_FOLDER = os.path.join(
    PROJECT_FOLDER,
    "uploads"
)


app.config["UPLOAD_FOLDER"] = (
    UPLOAD_FOLDER
)


# Maximum upload size = 10 MB

app.config["MAX_CONTENT_LENGTH"] = (
    10 * 1024 * 1024
)


# =========================================================
# ALLOWED FILE TYPES
# =========================================================

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}


def allowed_file(filename):
    """
    Check whether the uploaded file extension
    is supported.
    """

    return (
        "."
        in filename
        and filename.rsplit(
            ".",
            1
        )[1].lower()
        in ALLOWED_EXTENSIONS
    )


# =========================================================
# CREATE UPLOAD FOLDER
# =========================================================

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# ANALYZE
# =========================================================

@app.route(
    "/analyze",
    methods=["POST"]
)
def analyze():

    # -----------------------------------------------------
    # Get uploaded files
    # -----------------------------------------------------

    document = request.files.get(
        "document"
    )


    selfie = request.files.get(
        "selfie"
    )


    # -----------------------------------------------------
    # Basic validation
    # -----------------------------------------------------

    if not document:

        return (
            "Identity document is required.",
            400
        )


    if not selfie:

        return (
            "Selfie is required.",
            400
        )


    if document.filename == "":

        return (
            "Please select an identity document.",
            400
        )


    if selfie.filename == "":

        return (
            "Please select a selfie.",
            400
        )


    if not allowed_file(
        document.filename
    ):

        return (
            "Unsupported document format.",
            400
        )


    if not allowed_file(
        selfie.filename
    ):

        return (
            "Unsupported selfie format.",
            400
        )


    # =====================================================
    # SAFE UNIQUE FILE NAMES
    # =====================================================

    document_original_name = (
        secure_filename(
            document.filename
        )
    )


    selfie_original_name = (
        secure_filename(
            selfie.filename
        )
    )


    unique_id = uuid.uuid4().hex


    document_filename = (
        unique_id
        + "_document_"
        + document_original_name
    )


    selfie_filename = (
        unique_id
        + "_selfie_"
        + selfie_original_name
    )


    document_path = os.path.join(
        UPLOAD_FOLDER,
        document_filename
    )


    selfie_path = os.path.join(
        UPLOAD_FOLDER,
        selfie_filename
    )


    # =====================================================
    # SAVE FILES
    # =====================================================

    document.save(
        document_path
    )


    selfie.save(
        selfie_path
    )


    # =====================================================
    # STEP 1: METADATA
    # =====================================================

    try:

        metadata_result = (
            metadata_analysis.analyze(
                document_path
            )
        )

    except Exception as error:

        metadata_result = {
            "error": str(error)
        }


    # =====================================================
    # STEP 2: OCR
    # =====================================================

    try:

        ocr_text = ocr.extract_text(
            document_path
        )

    except Exception as error:

        ocr_text = ""

        print(
            "OCR ERROR:",
            error
        )


    # =====================================================
    # STEP 3: DOCUMENT IDENTIFICATION
    # =====================================================

    document_result = (
        document_identification.identify_document(
            ocr_text
        )
    )


    document_type = (
        document_result[
            "document_type"
        ]
    )


    # =====================================================
    # STEP 4 + 5:
    # DOCUMENT-SPECIFIC EXTRACTION + VALIDATION
    # =====================================================

    fields = {}


    validation_result = {}


    # -----------------------------------------------------
    # AADHAAR
    # -----------------------------------------------------

    if document_type == "AADHAAR":

        fields = (
            field_extraction
            .extract_aadhaar_fields(
                ocr_text
            )
        )


        validation_result = (
            field_validation
            .validate_aadhaar_fields(
                fields
            )
        )


    # -----------------------------------------------------
    # PAN
    # -----------------------------------------------------

    elif document_type == "PAN":

        fields = (
            pan_extraction
            .extract_pan_fields(
                ocr_text
            )
        )


        validation_result = (
            pan_validation
            .validate_pan_fields(
                fields
            )
        )


    # -----------------------------------------------------
    # UNKNOWN
    # -----------------------------------------------------

    else:

        fields = {}

        validation_result = {}


    # =====================================================
    # STEP 6: ELA / TAMPER ANALYSIS
    # =====================================================

    try:

        ela_result = (
            tamper_analysis.perform_ela(
                document_path
            )
        )

    except Exception as error:

        ela_result = {

            "ela_image": None,

            "mean_difference": 0,

            "max_difference": 0,

            "high_difference_percentage": 0,

            "suspicious_regions": [],

            "error": str(error)
        }


    # =====================================================
    # STEP 7: OCR REGION DATA
    # =====================================================

    try:

        ocr_data = (
            ocr.extract_data(
                document_path
            )
        )

    except Exception:

        ocr_data = {
            "text": [],
            "left": [],
            "top": [],
            "width": [],
            "height": []
        }


    ocr_boxes = []


    for i in range(
        len(
            ocr_data["text"]
        )
    ):

        text = (
            ocr_data["text"][i]
            .strip()
        )


        if not text:
            continue


        ocr_boxes.append({

            "text": text,

            "left": int(
                ocr_data["left"][i]
            ),

            "top": int(
                ocr_data["top"][i]
            ),

            "width": int(
                ocr_data["width"][i]
            ),

            "height": int(
                ocr_data["height"][i]
            )
        })


    # =====================================================
    # STEP 8:
    # ELA + OCR COMPARISON
    # =====================================================

    comparison_result = (
        region_comparison
        .compare_ela_with_ocr(

            ela_result.get(
                "suspicious_regions",
                []
            ),

            ocr_boxes
        )
    )


    # =====================================================
    # STEP 9:
    # DOCUMENT FACE EXTRACTION
    # =====================================================

    document_face_result = (
        document_face_extraction
        .detect_document_face(
            document_path
        )
    )


    # =====================================================
    # STEP 10:
    # FACE MATCHING
    # =====================================================

    if document_face_result[
        "success"
    ]:

        face_result = (
            facial_matching
            .compare_faces(

                document_face_result[
                    "face_path"
                ],

                selfie_path
            )
        )

    else:

        face_result = {

            "success": False,

            "similarity": None,

            "threshold": 0.363,

            "result": "UNAVAILABLE",

            "reason":
                document_face_result[
                    "reason"
                ]
        }


    # =====================================================
    # STEP 11:
    # FINAL SCORE
    # =====================================================

    final_result = (
        scoring.calculate_score(

            document_result,

            validation_result,

            ela_result,

            face_result
        )
    )


    # =====================================================
    # STEP 12:
    # RESULT PAGE
    # =====================================================

    return render_template(

        "result.html",

        original_document_name=(
            document.filename
        ),

        original_selfie_name=(
            selfie.filename
        ),

        metadata_result=(
            metadata_result
        ),

        ocr_text=(
            ocr_text
        ),

        document_result=(
            document_result
        ),

        fields=(
            fields
        ),

        validation_result=(
            validation_result
        ),

        ela_result=(
            ela_result
        ),

        comparison_result=(
            comparison_result
        ),

        document_face_result=(
            document_face_result
        ),

        face_result=(
            face_result
        ),

        final_result=(
            final_result
        )
    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )