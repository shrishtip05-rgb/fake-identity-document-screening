# =========================================================
# PAN FIELD EXTRACTION
# =========================================================

import re


def extract_pan_number(text):
    """
    Extract a PAN number from OCR text.

    Standard PAN structure:
        5 letters + 4 digits + 1 letter

    Example:
        ABCDE1234F
    """

    if not text:
        return None

    text = text.upper()

    # First try the normal format.
    pan_pattern = r"\b[A-Z]{5}[0-9]{4}[A-Z]\b"

    match = re.search(
        pan_pattern,
        text
    )

    if match:
        return match.group()

    # OCR may insert spaces.
    compact_text = re.sub(
        r"\s+",
        "",
        text
    )

    match = re.search(
        r"[A-Z]{5}[0-9]{4}[A-Z]",
        compact_text
    )

    if match:
        return match.group()

    return None


def extract_date_of_birth(text):
    """
    Extract DOB from OCR text.

    Supported formats:
        DD-MM-YYYY
        DD/MM/YYYY
        DD.MM.YYYY
    """

    if not text:
        return None

    date_pattern = (
        r"\b(?:"
        r"\d{2}[-/]\d{2}[-/]\d{4}"
        r"|"
        r"\d{2}\.\d{2}\.\d{4}"
        r")\b"
    )

    match = re.search(
        date_pattern,
        text
    )

    if not match:
        return None

    date_value = match.group()

    date_value = (
        date_value
        .replace("/", "-")
        .replace(".", "-")
    )

    return date_value


def extract_name(text):
    """
    Best-effort extraction of the PAN holder's name.

    This is an OCR-based heuristic.
    It does NOT verify the person's actual identity.
    """

    if not text:
        return None

    lines = text.upper().splitlines()

    ignored_phrases = [
        "INCOME TAX",
        "INCOME TAX DEPARTMENT",
        "PERMANENT ACCOUNT NUMBER",
        "GOVERNMENT OF INDIA",
        "GOVT OF INDIA",
        "SIGNATURE",
        "DATE OF BIRTH",
        "DOB",
        "PAN"
    ]

    candidates = []

    for line in lines:

        line = re.sub(
            r"\s+",
            " ",
            line
        ).strip()

        if not line:
            continue

        # Ignore known labels.
        if any(
            phrase in line
            for phrase in ignored_phrases
        ):
            continue

        # Ignore PAN number.
        if re.fullmatch(
            r"[A-Z]{5}[0-9]{4}[A-Z]",
            line
        ):
            continue

        # Ignore dates.
        if re.fullmatch(
            r"\d{2}[-/.]\d{2}[-/.]\d{4}",
            line
        ):
            continue

        # Possible person's name.
        if re.fullmatch(
            r"[A-Z][A-Z .'-]{1,49}",
            line
        ):
            candidates.append(line)

    if candidates:
        return candidates[0]

    return None


def extract_pan_fields(ocr_text):
    """
    Extract all supported PAN fields.
    """

    return {
        "pan_number": extract_pan_number(
            ocr_text
        ),

        "name": extract_name(
            ocr_text
        ),

        "date_of_birth": extract_date_of_birth(
            ocr_text
        )
    }