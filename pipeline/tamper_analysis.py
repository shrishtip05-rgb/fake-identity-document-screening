from PIL import Image, ImageChops, ImageEnhance
import os
import cv2
import numpy as np


def perform_ela(file_path, quality=90):
    """
    Perform Error Level Analysis (ELA).

    ELA compares the original image with a JPEG
    recompressed version and finds pixel differences.

    IMPORTANT:
    ELA is evidence of possible manipulation,
    not proof of tampering.
    """

    # -----------------------------------------
    # 1. Open original image
    # -----------------------------------------

    original = Image.open(file_path).convert("RGB")

    # -----------------------------------------
    # 2. Create JPEG-compressed copy
    # -----------------------------------------

    temp_path = "uploads/ela_temp.jpg"

    original.save(
        temp_path,
        "JPEG",
        quality=quality
    )

    compressed = Image.open(
        temp_path
    ).convert("RGB")

    # -----------------------------------------
    # 3. Calculate pixel differences
    # -----------------------------------------

    difference = ImageChops.difference(
        original,
        compressed
    )

    # Create visible ELA image
    enhanced = ImageEnhance.Brightness(
        difference
    ).enhance(10)

    ela_path = "uploads/ela_result.jpg"

    enhanced.save(
        ela_path
    )

    # Convert difference image to NumPy array
    difference_array = np.array(
        difference
    )

    # Calculate average difference
    # for every pixel
    difference_values = (
        difference_array.mean(axis=2)
    )

    # -----------------------------------------
    # 4. Overall ELA measurements
    # -----------------------------------------

    mean_difference = (
        difference_values.mean()
    )

    max_difference = (
        difference_values.max()
    )

    # Temporary measurement threshold.
    #
    # IMPORTANT:
    # This is NOT a "fake document" threshold.
    # It only identifies pixels with larger
    # ELA differences.
    high_difference_threshold = 10

    # Find suspicious pixels
    suspicious_pixels = (
        difference_values
        > high_difference_threshold
    )

    high_difference_pixels = np.sum(
        suspicious_pixels
    )

    total_pixels = (
        difference_values.size
    )

    high_difference_percentage = (
        high_difference_pixels
        / total_pixels
    ) * 100

    # -----------------------------------------
    # 5. Create suspicious-pixel mask
    # -----------------------------------------

    mask = np.zeros(
        difference_values.shape,
        dtype=np.uint8
    )

    mask[suspicious_pixels] = 255

    # -----------------------------------------
    # 6. Remove isolated noise
    # -----------------------------------------

    # Small isolated pixels can occur because
    # of normal JPEG compression or image edges.
    #
    # Morphological opening helps remove
    # these tiny isolated points.

    noise_kernel = np.ones(
        (3, 3),
        np.uint8
    )

    cleaned_mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        noise_kernel
    )

    # -----------------------------------------
    # 7. Group nearby suspicious pixels
    # -----------------------------------------

    # This kernel helps join suspicious pixels
    # that are close to each other.

    grouping_kernel = np.ones(
        (7, 7),
        np.uint8
    )

    grouped_mask = cv2.morphologyEx(
        cleaned_mask,
        cv2.MORPH_CLOSE,
        grouping_kernel
    )

    # Expand the grouped region slightly
    # so nearby suspicious pixels become
    # part of the same region.

    expanded_mask = cv2.dilate(
        grouped_mask,
        grouping_kernel,
        iterations=2
    )

    # -----------------------------------------
    # 8. Find connected suspicious regions
    # -----------------------------------------

    num_labels, labels, stats, centroids = (
        cv2.connectedComponentsWithStats(
            expanded_mask,
            connectivity=8
        )
    )

    suspicious_regions = []

    # Ignore label 0 because it represents
    # the background.

    for label in range(
        1,
        num_labels
    ):

        # Get bounding box coordinates
        x = stats[
            label,
            cv2.CC_STAT_LEFT
        ]

        y = stats[
            label,
            cv2.CC_STAT_TOP
        ]

        width = stats[
            label,
            cv2.CC_STAT_WIDTH
        ]

        height = stats[
            label,
            cv2.CC_STAT_HEIGHT
        ]

        area = stats[
            label,
            cv2.CC_STAT_AREA
        ]

        # -------------------------------------
        # Count original suspicious pixels
        # -------------------------------------
        #
        # The region has been expanded for
        # grouping, so we don't want the
        # expanded pixels themselves to be
        # considered evidence.
        #
        # Instead, count how many pixels from
        # the ORIGINAL suspicious mask are
        # inside this region.

        region_mask = (
            labels == label
        )

        original_suspicious_pixels = np.sum(
            suspicious_pixels
            & region_mask
        )

        # -------------------------------------
        # Remove very weak regions
        # -------------------------------------

        # Ignore regions containing very few
        # original suspicious pixels.

        if original_suspicious_pixels < 20:
            continue

        # -------------------------------------
        # Store region information
        # -------------------------------------

        suspicious_regions.append({

            "left": int(x),

            "top": int(y),

            "right": int(
                x + width
            ),

            "bottom": int(
                y + height
            ),

            "width": int(width),

            "height": int(height),

            "area": int(area),

            "suspicious_pixels": int(
                original_suspicious_pixels
            )
        })

    # -----------------------------------------
    # 9. Remove temporary JPEG file
    # -----------------------------------------

    if os.path.exists(temp_path):
        os.remove(temp_path)

    # -----------------------------------------
    # 10. Return results
    # -----------------------------------------

    return {

        "ela_image": ela_path,

        "mean_difference": round(
            float(mean_difference),
            2
        ),

        "max_difference": round(
            float(max_difference),
            2
        ),

        "high_difference_percentage": round(
            float(high_difference_percentage),
            2
        ),

        "suspicious_regions":
            suspicious_regions
    }

