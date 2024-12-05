import os
import datetime
import json
from typing import List, Tuple, Dict, Optional, Any
from PIL import Image, ExifTags
from src.geo_objects.geo_points.image_points import ImagePoint


class ImageParser:
    """
    Parses images in a directory to extract GPS data.

    :param image_folder: Path to the folder containing images.
    """

    def __init__(self, image_folder: str):
        self._image_folder = image_folder
        self._image_url_mapping = self._load_image_url_mapping()
        self._image_points: List[ImagePoint] = []
        self._processed_files: int = 0
        self._skipped_files_non_jpg: int = 0
        self._skipped_files_no_gps: int = 0
        self._errors: List[str] = []
        self._parse_images()

    def _load_image_url_mapping(self) -> Dict[str, str]:
        """
        Loads the image URL mapping from a JSON file.

        :return: A dictionary mapping file names to image URLs.
        """
        mapping: Dict[str, str] = {}
        mapping_file = os.path.join(self._image_folder, 'picture_name_url_mapping.json')

        if os.path.exists(mapping_file):
            try:
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        file_name = item.get('filename')
                        image_url = item.get('image_url')
                        if file_name and image_url:
                            mapping[file_name] = image_url
                        else:
                            print(f"Invalid entry in mapping file: {item}")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON mapping file: {e}")
        else:
            print("No image URL mapping file found in the picture folder.")

        return mapping

    def _parse_images(self):
        """
        Parses all JPEG images in the specified folder.
        """
        for root, _, files in os.walk(self._image_folder):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg')):
                    file_path = os.path.join(root, file)
                    self._processed_files += 1
                    image_point = self._extract_gps_data(file_path)
                    if image_point:
                        self._image_points.append(image_point)
                    else:
                        self._skipped_files_no_gps += 1
                else:
                    self._skipped_files_non_jpg += 1

    def _extract_gps_data(self, file_path: str) -> Optional[ImagePoint]:
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

            exif: Dict[str, Any] = {}
            for tag, value in exif_data.items():
                decoded_tag = ExifTags.TAGS.get(tag, tag)
                exif[decoded_tag] = value

            gps_info = exif.get('GPSInfo')
            if not gps_info:
                return None

            gps_data: Dict[str, Any] = {}
            for key in gps_info.keys():
                decoded_key = ExifTags.GPSTAGS.get(key, key)
                gps_data[decoded_key] = gps_info[key]

            # Decode references if they are bytes
            lat_ref = gps_data.get('GPSLatitudeRef')
            lon_ref = gps_data.get('GPSLongitudeRef')
            if isinstance(lat_ref, bytes):
                lat_ref = lat_ref.decode('utf-8')
            if isinstance(lon_ref, bytes):
                lon_ref = lon_ref.decode('utf-8')

            lat = self._convert_to_degrees(gps_data.get('GPSLatitude'))
            lon = self._convert_to_degrees(gps_data.get('GPSLongitude'))

            if lat is None or lon is None or not lat_ref or not lon_ref:
                return None

            if lat_ref in ['S']:
                lat = -lat
            if lon_ref in ['W']:
                lon = -lon

            # Extract time and elevation if available
            time_str = exif.get('DateTimeOriginal') or exif.get('DateTime')
            time: Optional[datetime.datetime] = None
            if time_str:
                try:
                    time = datetime.datetime.strptime(time_str, '%Y:%m:%d %H:%M:%S')
                except ValueError:
                    print(f"Invalid date/time format in {file_path}: {time_str}")
                    # time remains None

            elev = gps_data.get('GPSAltitude')
            if elev:
                elev = self._convert_rational_to_float(elev)

            file_name = os.path.basename(file_path)
            image_url = self._image_url_mapping.get(file_name)

            return ImagePoint(
                file_name=file_name,
                time=time,
                lat=lat,
                lon=lon,
                elev=elev,
                image_url=image_url,
                additional_info=None
            )
        except Exception as e:
            error_message = f"Error processing {file_path}: {e}"
            self._errors.append(error_message)
            print(error_message)
            return None

    def _convert_to_degrees(self, value: Optional[Tuple[Any, Any, Any]]) -> Optional[float]:
        """
        Helper function to convert GPS coordinates to degrees.

        :param value: The GPS coordinate as a tuple of rationals.
        :return: Coordinate in decimal degrees.
        """
        if not value:
            return None

        try:
            d = self._convert_rational_to_float(value[0])
            m = self._convert_rational_to_float(value[1])
            s = self._convert_rational_to_float(value[2])

            if d is None or m is None or s is None:
                return None

            result = d + (m / 60.0) + (s / 3600.0)
            return result
        except Exception as e:
            print(f"Error converting to degrees: {e}")
            return None

    def _convert_rational_to_float(self, rational: Any) -> Optional[float]:
        """
        Convert a rational number to float.

        :param rational: The rational number to convert.
        :return: The float representation of the rational number.
        """
        try:
            if isinstance(rational, (int, float)):
                return float(rational)
            elif isinstance(rational, tuple) and len(rational) == 2:
                return rational[0] / rational[1]
            else:
                return float(rational)
        except Exception as e:
            print(f"Error converting rational to float: {e}")
            return None

    def get_image_points(self) -> List[ImagePoint]:
        """
        Returns the list of ImagePoint instances.

        :return: List of ImagePoint objects.
        """
        return self._image_points

    def get_summary(self) -> Tuple[int, int, int, List[str]]:
        """
        Returns a summary of the parsing process.

        :return: A tuple containing:
            - processed_files: Number of JPG files processed.
            - skipped_files_non_jpg: Number of files skipped because they are not JPG.
            - skipped_files_no_gps: Number of JPG files skipped due to missing GPS data.
            - errors: List of error messages encountered during parsing.
        """
        return (
            self._processed_files,
            self._skipped_files_non_jpg,
            self._skipped_files_no_gps,
            self._errors
        )
