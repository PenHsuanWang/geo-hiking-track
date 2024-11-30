from src.geo_objects.geo_points.basic_point import BasicPoint

class ImagePoint(BasicPoint):
    """
    ImagePoint represents a geographic point extracted from an image's EXIF data.

    :param file_name: The name of the image file.
    :param time: The timestamp when the photo was taken.
    :param lat: Latitude extracted from EXIF data.
    :param lon: Longitude extracted from EXIF data.
    :param elev: Elevation extracted from EXIF data, if available.
    :param additional_info: Any additional metadata or notes.
    """

    def __init__(self, file_name, time, lat, lon, elev=None, additional_info=None):
        super().__init__(time, lat, lon, elev)
        self._file_name = file_name
        self._additional_info = additional_info

    @property
    def file_name(self):
        return self._file_name

    @property
    def additional_info(self):
        return self._additional_info

    def get_popup_info(self):
        """
        Returns formatted information for display in map popups.
        """
        info = f"Image: {self._file_name}<br>"
        if self.time:
            info += f"Time: {self.time.strftime('%Y-%m-%d %H:%M:%S')}<br>"
        if self._additional_info:
            info += f"Info: {self._additional_info}<br>"
        return info
