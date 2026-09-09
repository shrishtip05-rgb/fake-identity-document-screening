def calculate_overlap(ela_region, ocr_box):
    """
    Calculate how much an ELA suspicious region
    overlaps with an OCR bounding box.

    ELA region:
        {
            "left": ...,
            "top": ...,
            "right": ...,
            "bottom": ...
        }

    OCR box:
        {
            "left": ...,
            "top": ...,
            "right": ...,
            "bottom": ...
        }

    Returns:
        Overlap percentage and whether
        the two regions overlap.
    """

    # -----------------------------------------
    # 1. Find intersection coordinates
    # -----------------------------------------

    left = max(
        ela_region["left"],
        ocr_box["left"]
    )

    top = max(
        ela_region["top"],
        ocr_box["top"]
    )

    right = min(
        ela_region["right"],
        ocr_box["right"]
    )

    bottom = min(
        ela_region["bottom"],
        ocr_box["bottom"]
    )

    # -----------------------------------------
    # 2. Check whether they overlap
    # -----------------------------------------

    if right <= left or bottom <= top:
        return {
            "overlap": False,
            "overlap_percentage": 0.0
        }

    # -----------------------------------------
    # 3. Calculate intersection area
    # -----------------------------------------

    intersection_width = right - left
    intersection_height = bottom - top

    intersection_area = (
        intersection_width
        * intersection_height
    )

    # -----------------------------------------
    # 4. Calculate ELA region area
    # -----------------------------------------

    ela_width = (
        ela_region["right"]
        - ela_region["left"]
    )

    ela_height = (
        ela_region["bottom"]
        - ela_region["top"]
    )

    ela_area = (
        ela_width
        * ela_height
    )

    # Prevent division by zero
    if ela_area <= 0:
        return {
            "overlap": False,
            "overlap_percentage": 0.0
        }

    # -----------------------------------------
    # 5. Calculate overlap percentage
    # -----------------------------------------

    overlap_percentage = (
        intersection_area
        / ela_area
    ) * 100

    # -----------------------------------------
    # 6. Return result
    # -----------------------------------------

    return {
        "overlap": True,
        "overlap_percentage": round(
            overlap_percentage,
            2
        )
    }


def compare_ela_with_ocr(
    suspicious_regions,
    ocr_data
):
    """
    Compare every ELA suspicious region
    with every OCR text bounding box.

    Returns fields that have overlapping
    suspicious regions.
    """

    results = []

    # -----------------------------------------
    # Compare every ELA region
    # with every OCR box
    # -----------------------------------------

    for ela_region in suspicious_regions:

        for item in ocr_data:

            text = item["text"].strip()

            # Ignore empty OCR results
            if not text:
                continue

            ocr_box = {
                "left": item["left"],
                "top": item["top"],
                "right": (
                    item["left"]
                    + item["width"]
                ),
                "bottom": (
                    item["top"]
                    + item["height"]
                )
            }

            result = calculate_overlap(
                ela_region,
                ocr_box
            )

            # ---------------------------------
            # Only keep actual overlaps
            # ---------------------------------

            if result["overlap"]:

                results.append({

                    "text": text,

                    "overlap_percentage":
                        result[
                            "overlap_percentage"
                        ],

                    "ela_region":
                        ela_region,

                    "ocr_box":
                        ocr_box
                })

    return results