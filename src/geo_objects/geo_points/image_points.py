from src.geo_objects.geo_points.basic_point import BasicPoint

class ImagePoint(BasicPoint):
    """
    ImagePoint represents a geographic point extracted from an image's EXIF data.

    :param file_name: The name of the image file.
    :param time: The timestamp when the photo was taken.
    :param lat: Latitude extracted from EXIF data.
    :param lon: Longitude extracted from EXIF data.
    :param elev: Elevation extracted from EXIF data, if available.
    :param image_url: URL of the image accessible on the web.
    :param additional_info: Any additional metadata or notes.
    """

    def __init__(self, file_name, time, lat, lon, elev=None, image_url=None, additional_info=None):
        super().__init__(time, lat, lon, elev)
        self._file_name = file_name
        self._image_url = image_url
        self._additional_info = additional_info

    @property
    def file_name(self):
        return self._file_name

    @property
    def image_url(self):
        return self._image_url

    @property
    def additional_info(self):
        return self._additional_info

    def get_note(self):
        """
        Returns additional info or file name as a note.
        """
        return self.additional_info or self.file_name

    def get_popup_info(self):
        """
        Returns formatted information for display in map pop-ups, including the image if available.
        """
        info = f"<strong>Image:</strong> {self._file_name}<br>"
        if self.time:
            info += f"<strong>Time:</strong> {self.time.strftime('%Y-%m-%d %H:%M:%S')}<br>"
        if self._additional_info:
            info += f"<strong>Info:</strong> {self._additional_info}<br>"
        if self._image_url:
            # Include the image in the pop-up using HTML
            info += f'<img src="{self._image_url}" alt="{self._file_name}" style="width:200px;"><br>'
        return info