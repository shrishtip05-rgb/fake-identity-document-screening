# =========================================================
# DOCUMENT IDENTIFICATION
# =========================================================
#
# Supported documents:
#
#     1. AADHAAR
#     2. PAN
#
# IMPORTANT:
# The filename is NEVER used to identify the document.
#
# Identification is based on OCR CONTENT.
# =========================================================

import re

from pipeline import ocr


# =========================================================
# HELPER
# =========================================================

def normalize_for_matching(text):
    """
    Prepare OCR text for document identification.

    Converts:
        lowercase -> uppercase
        punctuation -> spaces
        multiple spaces -> one space

    This makes OCR matching more tolerant.
    """

    if not text:
        return ""

    text = text.upper()

    # Replace punctuation with spaces.
    text = re.sub(
        r"[^A-Z0-9]+",
        " ",
        text
    )

    # Remove repeated spaces.
    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


# =========================================================
# FIND AADHAAR-LIKE 12 DIGIT NUMBER
# =========================================================

def find_aadhaar_number(text):
    """
    Look for a 12-digit number while allowing OCR to
    insert spaces, hyphens or other separators.

    Examples that can be detected:

        1234 5678 9012
        123456789012
        12-0011 11111
        1234-5678-9012

    We only return the candidate number.
    Actual field validation is handled separately.
    """

    if not text:
        return None

    # Find digit-containing chunks.
    chunks = re.findall(
        r"\d[\d\s\-]{9,}\d",
        text
    )

    for chunk in chunks:

        # Keep only digits.
        digits = re.sub(
            r"\D",
            "",
            chunk
        )

        if len(digits) == 12:
            return digits

    # -----------------------------------------------------
    # Second approach:
    # Find any 12 consecutive digits after removing
    # separators from the entire OCR text.
    # -----------------------------------------------------

    digit_text = re.sub(
        r"[^0-9]",
        "",
        text
    )

    match = re.search(
        r"\d{12}",
        digit_text
    )

    if match:
        return match.group()

    return None


# =========================================================
# MAIN IDENTIFICATION
# =========================================================

def identify_document(ocr_text):
    """
    Identify Aadhaar or PAN from OCR text.

    Returns:

        {
            "document_type": "PAN",
            "confidence": 100,
            "clues": [...]
        }
    """

    if not ocr_text:

        return {
            "document_type": "UNKNOWN",
            "confidence": 0,
            "clues": [
                "No OCR text was extracted from the document."
            ]
        }


    # -----------------------------------------------------
    # Keep raw OCR text.
    # -----------------------------------------------------

    raw_text = ocr_text.upper()


    # -----------------------------------------------------
    # OCR normalization.
    #
    # This also attempts to correct small OCR errors such
    # as slightly misspelled AADHAAR.
    # -----------------------------------------------------

    normalized_ocr = ocr.normalize_text(
        ocr_text
    )


    # -----------------------------------------------------
    # Additional normalization for keyword matching.
    # -----------------------------------------------------

    text = normalize_for_matching(
        normalized_ocr
    )


    # =====================================================
    # SCORES
    # =====================================================

    aadhaar_score = 0
    pan_score = 0


    aadhaar_clues = []
    pan_clues = []


    # =====================================================
    # AADHAAR DETECTION
    # =====================================================

    # -----------------------------------------------------
    # Aadhaar keyword
    # -----------------------------------------------------

    if "AADHAAR" in text:

        aadhaar_score += 45

        aadhaar_clues.append(
            "Aadhaar keyword detected"
        )


    # -----------------------------------------------------
    # Government of India
    # -----------------------------------------------------

    if (
        "GOVERNMENT OF INDIA"
        in text
    ):

        aadhaar_score += 20

        aadhaar_clues.append(
            "Found keyword: GOVERNMENT OF INDIA"
        )


    # -----------------------------------------------------
    # Aadhaar 12-digit candidate
    # -----------------------------------------------------

    aadhaar_number = find_aadhaar_number(
        raw_text
    )


    if aadhaar_number:

        aadhaar_score += 35

        # Do NOT display the complete number in the
        # identification clue.
        #
        # This keeps the identification result cleaner
        # and reduces unnecessary exposure of sensitive data.

        aadhaar_clues.append(
            "Found a 12-digit Aadhaar-like number pattern"
        )


    # =====================================================
    # PAN DETECTION
    # =====================================================

    # -----------------------------------------------------
    # Income Tax Department
    # -----------------------------------------------------

    if (
        "INCOME TAX DEPARTMENT"
        in text
    ):

        pan_score += 35

        pan_clues.append(
            "Found keyword: INCOME TAX DEPARTMENT"
        )


    # -----------------------------------------------------
    # Permanent Account Number
    # -----------------------------------------------------

    if (
        "PERMANENT ACCOUNT NUMBER"
        in text
    ):

        pan_score += 25

        pan_clues.append(
            "Found keyword: PERMANENT ACCOUNT NUMBER"
        )


    # -----------------------------------------------------
    # Income Tax
    # -----------------------------------------------------

    if (
        "INCOME TAX"
        in text
    ):

        pan_score += 10

        pan_clues.append(
            "Found keyword: INCOME TAX"
        )


    # -----------------------------------------------------
    # PAN number pattern
    #
    # Standard structure:
    #
    # AAAAA9999A
    # -----------------------------------------------------

    pan_pattern = (
        r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"
    )


    pan_match = re.search(
        pan_pattern,
        raw_text
    )


    if pan_match:

        pan_score += 40

        pan_clues.append(
            "Found PAN number pattern"
        )


    # -----------------------------------------------------
    # OCR sometimes inserts spaces inside a PAN number.
    #
    # Example:
    #
    # ABCDE 1234 F
    # -----------------------------------------------------

    compact_text = re.sub(
        r"\s+",
        "",
        raw_text
    )


    compact_pan_match = re.search(
        r"[A-Z]{5}[0-9]{4}[A-Z]",
        compact_text
    )


    if (
        compact_pan_match
        and not pan_match
    ):

        pan_score += 40

        pan_clues.append(
            "Found PAN number pattern after OCR "
            "spacing normalization"
        )


    # =====================================================
    # FINAL DECISION
    # =====================================================

    # -----------------------------------------------------
    # PAN
    # -----------------------------------------------------

    if (
        pan_score > aadhaar_score
        and pan_score > 0
    ):

        return {

            "document_type": "PAN",

            "confidence": min(
                pan_score,
                100
            ),

            "clues": pan_clues
        }


    # -----------------------------------------------------
    # AADHAAR
    # -----------------------------------------------------

    if (
        aadhaar_score > pan_score
        and aadhaar_score > 0
    ):

        return {

            "document_type": "AADHAAR",

            "confidence": min(
                aadhaar_score,
                100
            ),

            "clues": aadhaar_clues
        }


    # =====================================================
    # UNKNOWN
    # =====================================================

    return {

        "document_type": "UNKNOWN",

        "confidence": 0,

        "clues": [
            "No strong Aadhaar or PAN indicators found"
        ]
    }