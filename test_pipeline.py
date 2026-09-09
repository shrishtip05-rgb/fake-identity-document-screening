from pipeline import ocr
from pipeline import document_identification
from pipeline import field_extraction
from pipeline import field_validation
from pipeline import tamper_analysis
from pipeline import region_comparison
from pipeline import facial_matching
from pipeline import scoring


# =========================================================
# FILE PATHS
# =========================================================

# Our synthetic Aadhaar document
document_path = "uploads/dummy_aadhaar.png"

# Temporary face extracted from / associated with the
# document for testing the face-matching module
document_face_path = "uploads/document_face.jpg"

# Selfie provided by the user
selfie_path = "uploads/selfie.jpg"


# =========================================================
# STEP 1: OCR
# =========================================================

print("\n========================================")
print("                OCR")
print("========================================")

ocr_text = ocr.extract_text(document_path)

print(ocr_text)


# =========================================================
# STEP 2: DOCUMENT IDENTIFICATION
# =========================================================

print("\n========================================")
print("        DOCUMENT IDENTIFICATION")
print("========================================")

document_result = document_identification.identify_document(
    ocr_text
)

print(
    "Document Type:",
    document_result["document_type"]
)

print(
    "Confidence:",
    document_result["confidence"]
)

print("Clues:")

for clue in document_result["clues"]:
    print("-", clue)


# =========================================================
# STEP 3: AADHAAR FIELD EXTRACTION
# =========================================================

print("\n========================================")
print("          FIELD EXTRACTION")
print("========================================")

# We are currently supporting Aadhaar only.

if document_result["document_type"] == "AADHAAR":

    fields = field_extraction.extract_aadhaar_fields(
        ocr_text
    )

    print(
        "Aadhaar Number:",
        fields["aadhaar_number"]
    )

    print(
        "Date of Birth:",
        fields["date_of_birth"]
    )

    print(
        "Gender:",
        fields["gender"]
    )

else:

    fields = {}

    print(
        "Document was not identified as Aadhaar."
    )


# =========================================================
# STEP 4: AADHAAR FIELD VALIDATION
# =========================================================

print("\n========================================")
print("          FIELD VALIDATION")
print("========================================")

if document_result["document_type"] == "AADHAAR":

    validation_result = (
        field_validation.validate_aadhaar_fields(
            fields
        )
    )

    for field_name, result in validation_result.items():

        print(
            field_name,
            ":",
            result["valid"],
            "-",
            result["reason"]
        )

else:

    validation_result = {}


# =========================================================
# STEP 5: ELA / TAMPER ANALYSIS
# =========================================================

print("\n========================================")
print("          TAMPER ANALYSIS")
print("========================================")

ela_result = tamper_analysis.perform_ela(
    document_path
)

print(
    "Mean Difference:",
    ela_result["mean_difference"]
)

print(
    "Maximum Difference:",
    ela_result["max_difference"]
)

print(
    "High Difference Percentage:",
    ela_result["high_difference_percentage"],
    "%"
)

print(
    "Suspicious Regions:",
    len(
        ela_result["suspicious_regions"]
    )
)


# =========================================================
# STEP 6: OCR POSITION DATA
# =========================================================

print("\n========================================")
print("          OCR REGION DATA")
print("========================================")

ocr_data = ocr.extract_data(
    document_path
)

ocr_boxes = []


for i in range(len(ocr_data["text"])):

    text = ocr_data["text"][i].strip()

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


print(
    "OCR text regions detected:",
    len(ocr_boxes)
)


# =========================================================
# STEP 7: ELA + OCR REGION COMPARISON
# =========================================================

print("\n========================================")
print("        ELA + OCR COMPARISON")
print("========================================")

comparison_result = (
    region_comparison.compare_ela_with_ocr(
        ela_result["suspicious_regions"],
        ocr_boxes
    )
)


if comparison_result:

    print(
        "Suspicious ELA regions overlap "
        "with OCR text:"
    )

    for item in comparison_result:

        print(
            "- Text:",
            item["text"],
            "| Overlap:",
            item["overlap_percentage"],
            "%"
        )

else:

    print(
        "No significant overlap between "
        "ELA regions and OCR text."
    )


# =========================================================
# STEP 8: FACE MATCHING
# =========================================================
#
# IMPORTANT:
# For this test, document_face.jpg is a separate
# temporary face image.
#
# Later, we will build the actual step that extracts
# the person's face from the uploaded Aadhaar image.
# =========================================================

print("\n========================================")
print("            FACE MATCHING")
print("========================================")

face_result = facial_matching.compare_faces(
    document_face_path,
    selfie_path
)


if face_result["success"]:

    print(
        "Similarity:",
        face_result["similarity"]
    )

    print(
        "Threshold:",
        face_result["threshold"]
    )

    print(
        "Result:",
        face_result["result"]
    )

else:

    print(
        "Face matching failed."
    )

    print(
        "Reason:",
        face_result["reason"]
    )


# =========================================================
# STEP 9: FINAL SCORING
# =========================================================

print("\n========================================")
print("          FINAL DECISION")
print("========================================")

final_result = scoring.calculate_score(

    document_result,

    validation_result,

    ela_result,

    face_result
)


print(
    "Overall Score:",
    final_result["total_score"],
    "/ 100"
)

print(
    "Risk Level:",
    final_result["risk_level"]
)


# =========================================================
# STEP 10: COMPONENT SCORES
# =========================================================

print("\nComponent Scores:")

for component, score in final_result[
    "component_scores"
].items():

    print(
        "-",
        component,
        ":",
        score
    )


# =========================================================
# STEP 11: WHY / EXPLANATION
# =========================================================

print("\nWHY:")

for reason in final_result["reasons"]:

    print(
        "✓",
        reason
    )


# =========================================================
# PIPELINE COMPLETE
# =========================================================

print("\n========================================")
print("          PIPELINE COMPLETE")
print("========================================")