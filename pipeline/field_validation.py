import re
from datetime import datetime


def validate_aadhaar_number(aadhaar_number):
    """
    Validate the extracted Aadhaar number.

    Rules:
    1. Aadhaar must contain exactly 12 digits.
    2. Spaces are allowed because OCR may extract:
       1234 5678 9012
    3. Alphabets and special characters are not allowed.
    """

    if not aadhaar_number:
        return {
            "valid": False,
            "reason": "Aadhaar number is missing"
        }

    # Remove spaces from the OCR result
    number = aadhaar_number.replace(" ", "")

    # Check whether the result contains exactly 12 digits
    if not re.fullmatch(r"\d{12}", number):
        return {
            "valid": False,
            "reason": "Aadhaar number must contain exactly 12 digits"
        }

    return {
        "valid": True,
        "reason": "Aadhaar number has a valid format"
    }


def validate_dob(date_of_birth):
    """
    Validate the extracted date of birth.

    Rules:
    1. Must follow DD-MM-YYYY.
    2. Must be a real calendar date.
    3. Cannot be a future date.
    """

    if not date_of_birth:
        return {
            "valid": False,
            "reason": "Date of birth is missing"
        }

    try:
        dob = datetime.strptime(date_of_birth, "%d-%m-%Y")

    except ValueError:
        return {
            "valid": False,
            "reason": "Invalid date format or date"
        }

    # A person's DOB cannot be in the future
    if dob.date() > datetime.today().date():
        return {
            "valid": False,
            "reason": "Date of birth cannot be in the future"
        }

    return {
        "valid": True,
        "reason": "Date of birth is valid"
    }


def validate_gender(gender):
    """
    Validate the extracted gender.

    Expected values:
    Male or Female
    """

    if not gender:
        return {
            "valid": False,
            "reason": "Gender is missing"
        }

    if gender not in ["Male", "Female"]:
        return {
            "valid": False,
            "reason": "Unexpected gender value"
        }

    return {
        "valid": True,
        "reason": "Gender value is valid"
    }


def validate_aadhaar_fields(fields):
    """
    Validate all extracted Aadhaar fields together.

    Input:
        fields - dictionary returned by field_extraction.py

    Output:
        Dictionary containing validation results.
    """

    aadhaar_result = validate_aadhaar_number(
        fields["aadhaar_number"]
    )

    dob_result = validate_dob(
        fields["date_of_birth"]
    )

    gender_result = validate_gender(
        fields["gender"]
    )

    return {
        "aadhaar_number": aadhaar_result,
        "date_of_birth": dob_result,
        "gender": gender_result
    }

def validate_pan_number(pan_number):
    """
    Validate the basic structural format of a PAN number.

    This checks format only.
    It does NOT verify the PAN against a government database.
    """

    if not pan_number:
        return {
            "valid": False,
            "reason": "PAN number is missing"
        }

    pan_number = pan_number.upper().strip()

    if not re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", pan_number):
        return {
            "valid": False,
            "reason": "PAN number does not follow the expected format"
        }

    return {
        "valid": True,
        "reason": "PAN number follows the expected format"
    }


def validate_pan_fields(fields):
    """
    Validate extracted PAN fields.
    """

    pan_result = validate_pan_number(fields["pan_number"])

    return {
        "pan_number": pan_result
    }