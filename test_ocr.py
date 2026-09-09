from pipeline import ocr
from pipeline import document_identification
from pipeline import field_extraction
from pipeline import field_validation
from pipeline import tamper_analysis
from pipeline import region_comparison

# Path of the document we want to test
image_path = "uploads/dummy_aadhaar.png"


# -----------------------------
# STEP 1: Extract text using OCR
# -----------------------------

text = ocr.extract_text(image_path)

print("----- OCR RESULT -----")
print(text)
print("----------------------")

ocr_data = ocr.extract_data(image_path)
print("\n----- OCR DATA -----")

for i in range(len(ocr_data["text"])):

    if ocr_data["text"][i].strip():

        print(
            ocr_data["text"][i],
            "| X:", ocr_data["left"][i],
            "| Y:", ocr_data["top"][i],
            "| Width:", ocr_data["width"][i],
            "| Height:", ocr_data["height"][i],
            "| Confidence:", ocr_data["conf"][i]
        )

print("--------------------")


# ------------------------------------
# STEP 2: Identify the document type
# ------------------------------------

result = document_identification.identify_document(text)

print("\n----- DOCUMENT IDENTIFICATION -----")
print("Document Type:", result["document_type"])
print("Confidence:", result["confidence"])
print("Clues:")

for clue in result["clues"]:
    print("-", clue)

print("------------------------------------")


# -----------------------------
# STEP 3: Extract fields
# -----------------------------

fields = field_extraction.extract_aadhaar_fields(text)

print("\n----- EXTRACTED FIELDS -----")
print("Aadhaar Number:", fields["aadhaar_number"])
print("Date of Birth:", fields["date_of_birth"])
print("Gender:", fields["gender"])
print("----------------------------")
# -----------------------------
# STEP 4: Validate extracted fields
# -----------------------------

validation = field_validation.validate_aadhaar_fields(fields)

print("\n----- FIELD VALIDATION -----")

print(
    "Aadhaar Number:",
    validation["aadhaar_number"]["valid"],
    "-",
    validation["aadhaar_number"]["reason"]
)

print(
    "Date of Birth:",
    validation["date_of_birth"]["valid"],
    "-",
    validation["date_of_birth"]["reason"]
)

print(
    "Gender:",
    validation["gender"]["valid"],
    "-",
    validation["gender"]["reason"]
)

print("----------------------------")

# -----------------------------
# STEP 5: Tamper Analysis
# -----------------------------

tamper_result = tamper_analysis.perform_ela(image_path)

print("\n----- TAMPER ANALYSIS -----")
print("ELA image:", tamper_result["ela_image"])
print("Mean Difference:", tamper_result["mean_difference"])
print("Maximum Difference:", tamper_result["max_difference"])
print(
    "High Difference Pixels:",
    tamper_result["high_difference_percentage"],
    "%"
)

print("\nSuspicious Regions:")

for region in tamper_result["suspicious_regions"]:

    print(region)
print("---------------------------")

# -----------------------------------------
# STEP 6: Compare ELA with OCR regions
# -----------------------------------------

# Convert Tesseract OCR data into a simpler
# list of dictionaries.

ocr_boxes = []

for i in range(len(ocr_data["text"])):

    text_value = ocr_data["text"][i].strip()

    # Ignore empty OCR results
    if not text_value:
        continue

    ocr_boxes.append({
        "text": text_value,
        "left": int(ocr_data["left"][i]),
        "top": int(ocr_data["top"][i]),
        "width": int(ocr_data["width"][i]),
        "height": int(ocr_data["height"][i])
    })


# Compare suspicious ELA regions
# with OCR bounding boxes.

comparison_results = (
    region_comparison.compare_ela_with_ocr(
        tamper_result["suspicious_regions"],
        ocr_boxes
    )
)


print("\n----- ELA ↔ OCR COMPARISON -----")


if comparison_results:

    for result in comparison_results:

        print(
            "OCR Text:",
            result["text"]
        )

        print(
            "Overlap:",
            result["overlap_percentage"],
            "%"
        )

        print(
            "Potentially affected field:",
            result["text"]
        )

        print(
            "ELA Region:",
            result["ela_region"]
        )

        print(
            "OCR Box:",
            result["ocr_box"]
        )

        print("----------------------------")

else:

    print(
        "No OCR field overlaps "
        "with a significant ELA region."
    )


print("-------------------------------")

