import os
import datetime
from typing import List
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from src.geo_objects.geo_points.image_points import ImagePoint

class ImageParser:
    """
    Parses images in a directory to extract GPS data.

    :param image_folder: Path to the folder containing images.
    """

    def __init__(self, image_folder: str):
        self._image_folder = image_folder
        self._image_points: List[ImagePoint] = []
        self._parse_images()

    def _parse_images(self):
        """
        Parses all JPEG images in the specified folder.
        """
        for root, _, files in os.walk(self._image_folder):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg')):
                    file_path = os.path.join(root, file)
                    image_point = self._extract_gps_data(file_path)
                    if image_point:
                        self._image_points.append(image_point)

    def _extract_gps_data(self, file_path: str) -> ImagePoint:
        """
        Extracts GPS data from an image file.

        :param file_path: Path to the image file.
        :return: ImagePoint with extracted data, or None if GPS data is unavailable.
        """
        try:
            image = Image.open(file_path)
            exif_data = image._getexif()
            if not exif_data:
                return None

            exif = {
                TAGS.get(tag): value
                for tag, value in exif_data.items()
                if tag in TAGS
            }

            gps_info = exif.get('GPSInfo')
            if not gps_info:
                return None

            gps_data = {
                GPSTAGS.get(tag): value
                for tag, value in gps_info.items()
                if tag in GPSTAGS
            }

            lat = self._convert_to_degrees(gps_data.get('GPSLatitude'), gps_data.get('GPSLatitudeRef'))
            lon = self._convert_to_degrees(gps_data.get('GPSLongitude'), gps_data.get('GPSLongitudeRef'))

            # Extract time and elevation if available
            time_str = exif.get('DateTimeOriginal') or exif.get('DateTime')
            time = datetime.datetime.strptime(time_str, '%Y:%m:%d %H:%M:%S') if time_str else None
            elev = gps_data.get('GPSAltitude')
            if elev:
                elev = elev[0] / elev[1]

            return ImagePoint(
                file_name=os.path.basename(file_path),
                time=time,
                lat=lat,
                lon=lon,
                elev=elev
            )
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return None

    def _convert_to_degrees(self, value, ref):
        """
        Helper function to convert GPS coordinates to degrees.

        :param value: The GPS coordinate tuple.
        :param ref: Reference direction ('N', 'S', 'E', 'W').
        :return: Coordinate in decimal degrees.
        """
        if not value:
            return None

        d = value[0][0] / value[0][1]
        m = value[1][0] / value[1][1]
        s = value[2][0] / value[2][1]

        result = d + (m / 60.0) + (s / 3600.0)
        if ref in ['S', 'W']:
            result *= -1
        return result

    def get_image_points(self) -> List[ImagePoint]:
        """
        Returns the list of ImagePoint instances.

        :return: List of ImagePoint objects.
        """
        return self._image_points
