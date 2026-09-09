# =========================================================
# PAN FIELD VALIDATION
# =========================================================

import re

from datetime import datetime


def validate_pan_number(pan_number):
    """
    Validate the structural format of a PAN number.

    Standard structure:
        AAAAA9999A
    """

    if not pan_number:

        return {
            "valid": False,
            "reason": "PAN number is missing"
        }

    pan = (
        pan_number
        .upper()
        .replace(" ", "")
    )

    # Basic PAN format.
    if not re.fullmatch(
        r"[A-Z]{5}[0-9]{4}[A-Z]",
        pan
    ):

        return {
            "valid": False,
            "reason": (
                "PAN must contain "
                "5 letters, 4 digits and 1 letter"
            )
        }

    # Fourth character represents the holder category.
    category = pan[3]

    valid_categories = {
        "P",  # Individual
        "C",  # Company
        "H",  # Hindu Undivided Family
        "F",  # Firm / LLP
        "A",  # Association of Persons
        "T",  # Trust
        "B",  # Body of Individuals
        "L",  # Local Authority
        "J",  # Artificial Juridical Person
        "G"   # Government
    }

    if category not in valid_categories:

        return {
            "valid": False,
            "reason": (
                "PAN contains an unexpected "
                "holder-category character"
            )
        }

    return {
        "valid": True,
        "reason": (
            "PAN number has a valid "
            "structural format"
        )
    }


def validate_name(name):
    """
    Basic validation of the OCR-extracted name.

    This checks format only.
    It does NOT verify the real identity.
    """

    if not name:

        return {
            "valid": False,
            "reason": (
                "PAN holder name was not extracted"
            )
        }

    cleaned_name = re.sub(
        r"\s+",
        " ",
        name
    ).strip()

    if not re.fullmatch(
        r"[A-Za-z][A-Za-z .'-]{1,49}",
        cleaned_name
    ):

        return {
            "valid": False,
            "reason": (
                "Extracted name contains "
                "unexpected characters"
            )
        }

    return {
        "valid": True,
        "reason": (
            "Extracted name has a valid text format"
        )
    }


def validate_date_of_birth(date_of_birth):
    """
    Validate DOB.

    Checks:
        - correct date
        - date is not in the future
    """

    if not date_of_birth:

        return {
            "valid": False,
            "reason": "Date of birth is missing"
        }

    try:

        dob = datetime.strptime(
            date_of_birth,
            "%d-%m-%Y"
        )

    except ValueError:

        return {
            "valid": False,
            "reason": (
                "Invalid date format or date"
            )
        }

    if dob.date() > datetime.today().date():

        return {
            "valid": False,
            "reason": (
                "Date of birth cannot be in the future"
            )
        }

    return {
        "valid": True,
        "reason": "Date of birth is valid"
    }


def validate_pan_fields(fields):
    """
    Validate all extracted PAN fields.
    """

    pan_result = validate_pan_number(
        fields.get("pan_number")
    )

    name_result = validate_name(
        fields.get("name")
    )

    dob_result = validate_date_of_birth(
        fields.get("date_of_birth")
    )

    return {
        "pan_number": pan_result,
        "name": name_result,
        "date_of_birth": dob_result
    }