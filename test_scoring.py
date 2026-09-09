from pipeline import scoring
from pipeline import facial_matching


# ---------------------------------------------------------
# FILES USED FOR FACE MATCHING
# ---------------------------------------------------------

document_face_path = "uploads/document_face.jpg"
selfie_path = "uploads/selfie.jpg"


# ---------------------------------------------------------
# STEP 1: RUN REAL FACE MATCHING
# ---------------------------------------------------------
# Instead of manually saying MATCH or MISMATCH,
# we ask our facial_matching module to analyze
# the two images.
# ---------------------------------------------------------

face_result = facial_matching.compare_faces(
    document_face_path,
    selfie_path
)


# ---------------------------------------------------------
# DISPLAY FACE RESULT
# ---------------------------------------------------------

print("\n========================================")
print("           FACE MATCHING RESULT")
print("========================================")

print(face_result)


# ---------------------------------------------------------
# SAMPLE DOCUMENT IDENTIFICATION RESULT
# ---------------------------------------------------------
# This currently comes from our successful Aadhaar test.
#
# Later, Flask will generate this automatically.
# ---------------------------------------------------------

document_result = {
    "document_type": "AADHAAR",
    "confidence": 100,
    "clues": [
        "Aadhaar keyword detected after OCR normalization",
        "Found keyword: GOVERNMENT OF INDIA",
        "Found 12-digit Aadhaar number pattern"
    ]
}


# ---------------------------------------------------------
# SAMPLE FIELD VALIDATION RESULT
# ---------------------------------------------------------

validation_result = {

    "aadhaar_number": {
        "valid": True,
        "reason": "Aadhaar number has a valid format"
    },

    "date_of_birth": {
        "valid": True,
        "reason": "Date of birth is valid"
    },

    "gender": {
        "valid": True,
        "reason": "Gender value is valid"
    }
}


# ---------------------------------------------------------
# SAMPLE ELA RESULT
# ---------------------------------------------------------
# These values come from our clean synthetic Aadhaar test.
# ---------------------------------------------------------

ela_result = {

    "high_difference_percentage": 0.0,

    "suspicious_regions": []
}


# ---------------------------------------------------------
# STEP 2: SEND ALL RESULTS TO SCORING ENGINE
# ---------------------------------------------------------

final_result = scoring.calculate_score(

    document_result,

    validation_result,

    ela_result,

    face_result
)


# ---------------------------------------------------------
# STEP 3: DISPLAY FINAL RESULT
# ---------------------------------------------------------

print("\n========================================")
print("          FINAL SCREENING RESULT")
print("========================================")

print(
    "Overall Score:",
    final_result["total_score"],
    "/ 100"
)

print(
    "Risk Level:",
    final_result["risk_level"]
)


# ---------------------------------------------------------
# DISPLAY COMPONENT SCORES
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# DISPLAY WHY
# ---------------------------------------------------------

print("\nWHY:")

for reason in final_result["reasons"]:

    print("✓", reason)


print("\n========================================")