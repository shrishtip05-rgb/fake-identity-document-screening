# =========================================================
# AADHAAR FIELD EXTRACTION
# =========================================================

import re


# =========================================================
# FIND 12-DIGIT AADHAAR NUMBER
# =========================================================

def find_aadhaar_number(text):
    """
    Extract a 12-digit Aadhaar-like number from OCR text.

    OCR may represent the number in different formats:

        1234 5678 9012
        123456789012
        1234-5678-9012

    The extraction does NOT depend on any person's name
    or any particular Aadhaar number.
    """

    if not text:
        return None


    # -----------------------------------------------------
    # Method 1:
    # Look for a number containing spaces/hyphens.
    # -----------------------------------------------------

    candidates = re.findall(
        r"\d[\d\s\-]{9,}\d",
        text
    )


    for candidate in candidates:

        digits = re.sub(
            r"\D",
            "",
            candidate
        )


        if len(digits) == 12:

            return digits


    # -----------------------------------------------------
    # Method 2:
    # Remove non-digit characters and search for
    # exactly 12 consecutive digits.
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
# FIND DATE OF BIRTH
# =========================================================

def find_dob(text):
    """
    Extract a date of birth from OCR text.

    Supports common formats such as:

        20-06-1986
        20/06/1986
        20.06.1986
    """

    if not text:
        return None


    dob_pattern = (
        r"\b\d{2}[-/.]\d{2}[-/.]\d{4}\b"
    )


    match = re.search(
        dob_pattern,
        text
    )


    if match:

        # Convert separators to '-'
        dob = re.sub(
            r"[-/.]",
            "-",
            match.group()
        )

        return dob


    return None


# =========================================================
# FIND GENDER
# =========================================================

def find_gender(text):
    """
    Detect gender from OCR text.

    This is intentionally simple because OCR may contain
    unrelated text.
    """

    if not text:
        return None


    upper_text = text.upper()


    if re.search(
        r"\bFEMALE\b",
        upper_text
    ):

        return "Female"


    if re.search(
        r"\bMALE\b",
        upper_text
    ):

        return "Male"


    return None


# =========================================================
# MAIN AADHAAR EXTRACTION
# =========================================================

def extract_aadhaar_fields(ocr_text):
    """
    Extract Aadhaar-specific fields from OCR text.

    The function works with arbitrary names and numbers.
    """

    return {

        "aadhaar_number":
            find_aadhaar_number(
                ocr_text
            ),

        "date_of_birth":
            find_dob(
                ocr_text
            ),

        "gender":
            find_gender(
                ocr_text
            )
    }