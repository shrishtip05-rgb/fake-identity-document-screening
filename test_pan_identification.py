from pipeline import document_identification


# =========================================================
# FICTIONAL PAN OCR TEXT
# =========================================================

ocr_text = """
INCOME TAX DEPARTMENT 2 GOVT. OF INDIA
Permanent Account Number Card
ABCDE1234F
APPLICANT NAME
APPLICANT'S FATHER NAME
01/06/1995
"""


# =========================================================
# IDENTIFY DOCUMENT
# =========================================================

result = (
    document_identification.identify_document(
        ocr_text
    )
)


# =========================================================
# DISPLAY RESULT
# =========================================================

print("\n========================================")
print("       DOCUMENT IDENTIFICATION")
print("========================================")

print(
    "Document Type:",
    result["document_type"]
)

print(
    "Confidence:",
    result["confidence"]
)

print("\nClues:")

for clue in result["clues"]:

    print(
        "-",
        clue
    )

print("\n========================================")
