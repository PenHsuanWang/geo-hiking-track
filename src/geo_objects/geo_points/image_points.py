# src/geo_objects/geo_points/image_points.py

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
        html = '<div style="width: 50vw; height: auto; max-height: 70vh; overflow-y: auto; padding: 20px; box-sizing: border-box; font-size: 1.2rem;">'
        html += '<strong style="font-size: 1.5rem; margin-bottom: 10px;">Image Details</strong><br>'
        if self.time:
            html += f'<span style="display: block; margin-top: 10px;">Time: {self.time.strftime("%H:%M:%S")}</span>'
        html += f'<span style="display: block; margin-top: 5px;">Filename: {self._file_name}</span>'
        if self.elev:
            html += f'<span style="display: block; margin-top: 5px;">Elevation: {round(self.elev, 1)} M</span>'
        if self._additional_info:
            html += f'<span style="display: block; margin-top: 5px;">Info: {self._additional_info}</span>'
        if self._image_url:
            html += f'<img src="{self._image_url}" alt="{self._file_name}" style="width: 100%; max-width: 48vw; height: auto; border-radius: 10px; margin-top: 20px;">'
        html += '</div>'
        return html