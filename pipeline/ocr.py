# =========================================================
# OCR MODULE
# =========================================================

import re
import difflib
import os
import shutil

import cv2
import pytesseract
from PIL import Image


# =========================================================
# TESSERACT CONFIGURATION
# =========================================================

# Try to find Tesseract automatically.
# This works when Tesseract is available in the system PATH.
tesseract_path = shutil.which("tesseract")

if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

else:
    # Windows fallback.
    # This is the standard installation location on your laptop.
    windows_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

    if os.path.exists(windows_tesseract):
        pytesseract.pytesseract.tesseract_cmd = windows_tesseract


# =========================================================
# RUN TESSERACT
# =========================================================

def run_tesseract(image, config="--psm 6"):
    """
    Run Tesseract OCR on an image.
    """

    return pytesseract.image_to_string(
        image,
        config=config
    )


# =========================================================
# IMAGE PREPROCESSING
# =========================================================

def preprocess_variants(file_path):
    """
    Create multiple image versions so that OCR has
    several chances to read the document correctly.
    """

    image = cv2.imread(file_path)

    if image is None:
        return []


    variants = []


    # Original
    variants.append(
        ("original", image)
    )


    # Upscaled
    upscaled = cv2.resize(
        image,
        None,
        fx=3,
        fy=3,
        interpolation=cv2.INTER_CUBIC
    )

    variants.append(
        ("upscaled", upscaled)
    )


    # Grayscale
    gray = cv2.cvtColor(
        upscaled,
        cv2.COLOR_BGR2GRAY
    )

    variants.append(
        ("grayscale", gray)
    )


    # Contrast enhancement
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(gray)

    variants.append(
        ("contrast_enhanced", enhanced)
    )


    # OTSU
    _, otsu = cv2.threshold(
        enhanced,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    variants.append(
        ("otsu", otsu)
    )


    # Adaptive threshold
    adaptive = cv2.adaptiveThreshold(
        enhanced,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11
    )

    variants.append(
        ("adaptive", adaptive)
    )


    # Sharpening
    blurred = cv2.GaussianBlur(
        enhanced,
        (0, 0),
        3
    )

    sharpened = cv2.addWeighted(
        enhanced,
        1.5,
        blurred,
        -0.5,
        0
    )

    variants.append(
        ("sharpened", sharpened)
    )


    return variants


# =========================================================
# OCR QUALITY SCORE
# =========================================================

def calculate_ocr_score(text):
    """
    Score an OCR result based on useful document evidence.

    IMPORTANT:
    We do NOT simply choose the result containing the most
    characters.

    PAN/Aadhaar evidence gets higher priority than random
    OCR characters or QR-code noise.
    """

    if not text:
        return -1


    upper_text = text.upper()


    # Remove punctuation only for matching.
    normalized = re.sub(
        r"[^A-Z0-9\s]",
        " ",
        upper_text
    )

    normalized = re.sub(
        r"\s+",
        " ",
        normalized
    ).strip()


    score = 0


    # =====================================================
    # PAN EVIDENCE
    # =====================================================

    if "INCOME TAX DEPARTMENT" in normalized:
        score += 150


    if "PERMANENT ACCOUNT NUMBER" in normalized:
        score += 150


    if "INCOME TAX" in normalized:
        score += 50


    # Standard PAN pattern.
    if re.search(
        r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
        upper_text
    ):
        score += 180


    # OCR may put spaces in PAN.
    compact = re.sub(
        r"\s+",
        "",
        upper_text
    )

    if re.search(
        r"[A-Z]{5}[0-9]{4}[A-Z]",
        compact
    ):
        score += 160


    # =====================================================
    # AADHAAR EVIDENCE
    # =====================================================

    if "AADHAAR" in normalized:
        score += 120


    if "GOVERNMENT OF INDIA" in normalized:
        score += 40


    # A 12-digit number is useful, but NOT enough to strongly
    # identify Aadhaar because other document regions and QR
    # codes can produce numbers.

    if re.search(
        r"\b\d{4}\s?\d{4}\s?\d{4}\b",
        upper_text
    ):
        score += 30


    # =====================================================
    # GENERAL OCR QUALITY
    # =====================================================

    alphanumeric_count = len(
        re.findall(
            r"[A-Z0-9]",
            upper_text
        )
    )


    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]


    # General OCR quality contributes only modestly.
    score += min(
        alphanumeric_count,
        100
    )

    score += len(lines) * 3


    return score


# =========================================================
# OCR TEXT EXTRACTION
# =========================================================

def extract_text(file_path):
    """
    Extract the most useful OCR result.

    The selection is based on document evidence rather
    than simply selecting the longest OCR output.
    """

    variants = preprocess_variants(
        file_path
    )


    if not variants:
        return ""


    best_text = ""

    best_score = -1


    configs = [
    "--psm 6",
    "--psm 11"
]
    

    for variant_name, image in variants:

        for config in configs:

            try:

                text = run_tesseract(
                    image,
                    config
                )

            except Exception as error:

                print(
                    "OCR ERROR:",
                    error
                )

                continue


            cleaned_text = text.strip()


            if not cleaned_text:
                continue


            score = calculate_ocr_score(
                cleaned_text
            )


            print(
                f"OCR candidate: "
                f"{variant_name}, "
                f"{config}, "
                f"score={score}"
            )


            if score > best_score:

                best_score = score

                best_text = cleaned_text


    print(
        "\nBest OCR score:",
        best_score
    )


    return best_text


# =========================================================
# OCR BOUNDING BOX DATA
# =========================================================

def extract_data(file_path):
    """
    Extract OCR text and bounding boxes.

    Used by ELA + OCR region comparison.
    """

    image = Image.open(
        file_path
    )


    data = pytesseract.image_to_data(
        image,
        output_type=pytesseract.Output.DICT,
        config="--psm 6"
    )


    return data


# =========================================================
# OCR NORMALIZATION
# =========================================================

def normalize_text(text):
    """
    Normalize OCR text for document identification.
    """

    if not text:
        return ""


    normalized = text.upper()


    normalized = normalized.replace(
        '"',
        " "
    )

    normalized = normalized.replace(
        "'",
        " "
    )


    words = normalized.split()


    corrected_words = []


    for word in words:

        clean_word = re.sub(
            r"[^A-Z0-9]",
            "",
            word
        )


        if not clean_word:
            continue


        # Correct small OCR variations of AADHAAR.

        similarity = difflib.SequenceMatcher(
            None,
            clean_word,
            "AADHAAR"
        ).ratio()


        if (
            similarity >= 0.60
            and
            abs(
                len(clean_word)
                - len("AADHAAR")
            ) <= 2
        ):

            clean_word = "AADHAAR"


        corrected_words.append(
            clean_word
        )


    return " ".join(
        corrected_words
    )