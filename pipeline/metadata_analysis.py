import os
from PIL import Image
from PIL.ExifTags import TAGS


def analyze(file_path):
    """
    Analyze basic file properties and available EXIF metadata.

    Parameters:
        file_path (str): Path of the uploaded image.

    Returns:
        dict: Metadata findings.
    """

    # Get the size of the file in bytes
    file_size = os.path.getsize(file_path)

    # Open the uploaded image
    image = Image.open(file_path)

    # Get basic image information
    width, height = image.size
    image_format = image.format

    # Create an empty dictionary for EXIF information
    exif_data = {}

    # Try to read EXIF metadata
    exif = image.getexif()

    # Check whether EXIF metadata exists
    if exif:

        # Go through every metadata item
        for tag_id, value in exif.items():

            # Convert the numeric tag ID into a readable name
            tag_name = TAGS.get(tag_id, tag_id)

            # Store the readable name and value
            exif_data[tag_name] = str(value)

    # Store all findings in one dictionary
    findings = {
        "file_name": os.path.basename(file_path),
        "file_size_bytes": file_size,
        "width": width,
        "height": height,
        "format": image_format,
        "exif": exif_data
    }

    # Return the results to app.py
    return findings