from pipeline import facial_matching


# --------------------------------------------------
# TEST IMAGES
# --------------------------------------------------

document_path = "uploads/document_face.jpg"
selfie_path = "uploads/selfie.jpg"


# --------------------------------------------------
# FACE MATCHING
# --------------------------------------------------

result = facial_matching.compare_faces(
    document_path,
    selfie_path
)


# --------------------------------------------------
# DISPLAY RESULT
# --------------------------------------------------

print("----- FACE MATCHING -----")

if result["success"]:

    print("Similarity Score:", result["similarity"])
    print("Threshold:", result["threshold"])
    print("Result:", result["result"])

else:

    print("Face matching failed.")
    print("Reason:", result["reason"])

print("-------------------------")