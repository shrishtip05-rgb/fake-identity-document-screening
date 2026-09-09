from pipeline import document_face_extraction


# =========================================================
# DOCUMENT PATH
# =========================================================

document_path = "uploads/dummy_aadhaar.png"


# =========================================================
# RUN FACE EXTRACTION
# =========================================================

result = (
    document_face_extraction.detect_document_face(
        document_path
    )
)


# =========================================================
# DISPLAY RESULT
# =========================================================

print("\n========================================")
print("       DOCUMENT FACE EXTRACTION")
print("========================================")


if result["success"]:

    print("Face detected: YES")

    print(
        "Confidence:",
        result["confidence"]
    )

    print(
        "Face image saved at:",
        result["face_path"]
    )

    print(
        "Bounding box:",
        result["bounding_box"]
    )

else:

    print("Face detected: NO")

    print(
        "Reason:",
        result["reason"]
    )


print("\n========================================")
print("              COMPLETE")
print("========================================")