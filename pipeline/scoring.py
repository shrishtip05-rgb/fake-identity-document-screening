# =========================================================
# SCORING / DECISION ENGINE
# =========================================================
#
# Prototype scoring model:
#
#   Document identification = 20
#   Field validation        = 30
#   Tamper analysis         = 25
#   Face matching           = 25
#
# Total = 100
#
# IMPORTANT:
# This is a screening score.
# It does NOT prove that a document is genuine or fake.
#
# Face states are treated separately:
#
#   MATCH       -> positive identity evidence
#   MISMATCH    -> negative identity evidence
#   UNAVAILABLE -> insufficient evidence, NOT mismatch
# =========================================================


# =========================================================
# DOCUMENT IDENTIFICATION
# =========================================================

def score_document_identification(document_result):
    """
    Convert document identification confidence
    into a maximum of 20 points.
    """

    confidence = document_result.get(
        "confidence",
        0
    )

    score = (
        confidence / 100
    ) * 20

    return round(score, 2)


# =========================================================
# FIELD VALIDATION
# =========================================================

def score_field_validation(validation_result):
    """
    Give equal weight to all available validated fields.

    Maximum contribution = 30 points.
    """

    if not validation_result:
        return 0

    total_fields = len(
        validation_result
    )

    if total_fields == 0:
        return 0

    valid_fields = 0

    for result in validation_result.values():

        if result.get(
            "valid",
            False
        ):
            valid_fields += 1

    score = (
        valid_fields / total_fields
    ) * 30

    return round(
        score,
        2
    )


# =========================================================
# TAMPER ANALYSIS
# =========================================================

def score_tamper_analysis(ela_result):
    """
    Convert ELA findings into a prototype score.

    Maximum contribution = 25 points.

    ELA is evidence of possible manipulation,
    not proof of tampering.
    """

    suspicious_regions = ela_result.get(
        "suspicious_regions",
        []
    )

    high_difference_percentage = ela_result.get(
        "high_difference_percentage",
        0
    )

    if (
        len(suspicious_regions) == 0
        and high_difference_percentage <= 1
    ):

        return 25

    elif (
        len(suspicious_regions) <= 2
        and high_difference_percentage <= 5
    ):

        return 15

    else:

        return 5


# =========================================================
# FACE MATCHING
# =========================================================

def score_face_matching(face_result):
    """
    Score the identity-matching result.

    MATCH:
        25 points

    MISMATCH:
        0 points

    UNAVAILABLE:
        0 points

    IMPORTANT:
    UNAVAILABLE is not treated as MISMATCH.
    """

    result = face_result.get(
        "result"
    )

    if result == "MATCH":
        return 25

    if result == "MISMATCH":
        return 0

    return 0


# =========================================================
# FIELD VALIDATION EXPLANATION
# =========================================================

def get_field_reason(
    document_type,
    validation_result
):
    """
    Produce a human-readable explanation
    of document-specific field validation.
    """

    if not validation_result:

        return (
            "No document-specific fields "
            "were available for validation."
        )

    total_fields = len(
        validation_result
    )

    valid_fields = 0

    for result in validation_result.values():

        if result.get(
            "valid",
            False
        ):
            valid_fields += 1

    if valid_fields == total_fields:

        return (
            f"All extracted {document_type} "
            "fields passed format validation."
        )

    return (
        f"{valid_fields} of {total_fields} "
        f"extracted {document_type} fields "
        "passed format validation."
    )


# =========================================================
# FINAL DECISION
# =========================================================

def calculate_score(
    document_result,
    validation_result,
    ela_result,
    face_result
):
    """
    Calculate the complete screening result.
    """

    # -----------------------------------------------------
    # Component scores
    # -----------------------------------------------------

    document_score = (
        score_document_identification(
            document_result
        )
    )

    field_score = (
        score_field_validation(
            validation_result
        )
    )

    tamper_score = (
        score_tamper_analysis(
            ela_result
        )
    )

    face_score = (
        score_face_matching(
            face_result
        )
    )


    # -----------------------------------------------------
    # Overall score
    # -----------------------------------------------------

    total_score = (
        document_score
        + field_score
        + tamper_score
        + face_score
    )

    total_score = round(
        total_score,
        2
    )


    # -----------------------------------------------------
    # Risk level
    # -----------------------------------------------------

    if total_score >= 85:

        risk_level = "LOW RISK"

    elif total_score >= 60:

        risk_level = "NEEDS REVIEW"

    else:

        risk_level = "HIGH RISK"


    # =====================================================
    # WHY EXPLANATION
    # =====================================================

    reasons = []


    document_type = document_result.get(
        "document_type",
        "UNKNOWN"
    )


    # -----------------------------------------------------
    # Document identification
    # -----------------------------------------------------

    if document_type in [
        "AADHAAR",
        "PAN"
    ]:

        reasons.append(
            f"{document_type} document structure "
            "was detected."
        )

    else:

        reasons.append(
            "The uploaded document could not be "
            "confidently identified as Aadhaar or PAN."
        )


    # -----------------------------------------------------
    # Field validation
    # -----------------------------------------------------

    reasons.append(
        get_field_reason(
            document_type,
            validation_result
        )
    )


    # -----------------------------------------------------
    # Tamper analysis
    # -----------------------------------------------------

    suspicious_regions = ela_result.get(
        "suspicious_regions",
        []
    )

    high_difference_percentage = ela_result.get(
        "high_difference_percentage",
        0
    )


    if (
        len(suspicious_regions) == 0
        and high_difference_percentage <= 1
    ):

        reasons.append(
            "No significant suspicious ELA "
            "regions were detected."
        )

    else:

        reasons.append(
            "Potentially suspicious image regions "
            "were detected by ELA analysis."
        )


    # -----------------------------------------------------
    # Face result
    # -----------------------------------------------------

    face_status = face_result.get(
        "result",
        "UNAVAILABLE"
    )


    if face_status == "MATCH":

        reasons.append(
            "The document face matched "
            "the provided selfie."
        )


    elif face_status == "MISMATCH":

        reasons.append(
            "The document face did not match "
            "the provided selfie."
        )


    else:

        reasons.append(
            "Identity matching could not be completed "
            "because a usable document face was unavailable."
        )


    # =====================================================
    # RETURN RESULT
    # =====================================================

    return {

        "total_score": total_score,

        "risk_level": risk_level,

        "component_scores": {

            "document_identification":
                document_score,

            "field_validation":
                field_score,

            "tamper_analysis":
                tamper_score,

            "face_matching":
                face_score
        },

        "reasons": reasons
    }