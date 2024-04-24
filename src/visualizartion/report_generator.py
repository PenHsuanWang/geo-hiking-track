from typing import List
import os

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from src.geoanalyzer.tracks.track_analyzer import TrackAnalyzer


class ReportGenerator:
    """
    The report generator class takes the recorded note in tracks from gpx file and generates a report.
    That is the important information recorded by the user during the trip.
    Taking the time and note of the waypoint to organize the report of the trip.
    """
    def __init__(self, track_object: TrackAnalyzer):
        """
        Initializes a ReportGenerator object.

        :param track_object: The track object to generate the report from.
        :type track_object: TrackObject
        """
        self._track_object = track_object

    def _parsing_waypoint_list(self) -> List[List[str]]:
        """
        Parses a list of waypoint nodes and extracts the time and note.

        This method retrieves a list of waypoints from the track object and iterates over each waypoint.
        For each waypoint, it extracts the time and note and appends them as a list to the waypoint_time_note_dict list.
        The method returns the waypoint_time_note_dict list, which is a list of lists,
        where each inner list contains the time and note of a waypoint.

        :return: A list of lists, where each inner list contains the time and note of a waypoint.
        :rtype: List[List]
        """
        waypoint_list = self._track_object.get_waypoint_list()

        waypoint_time_note_dict = []

        for point in waypoint_list:
            waypoint_time_note_dict.append([point.time, point.get_note()])

        return waypoint_time_note_dict

    def generate_report(self, saved_file: str = 'default_report.txt', saved_format: str = 'txt', **kwargs):
        """
        Generates a report from the track object and saves it as a text file or a PDF.

        :param saved_file: The file path to save the report. Defaults to 'default_report.txt'.
        :type saved_file: str
        :param saved_format: The format of the report to be saved. Defaults to 'txt'.
        :type saved_format: str
        """

        if saved_format is None:
            saved_format = 'txt'
        elif saved_format not in ['txt', 'pdf']:
            raise ValueError(f"Invalid format: {saved_format}. Supported formats are 'txt' and 'pdf'.")

        waypoint_time_note_dict = self._parsing_waypoint_list()

        # Check if the file extension matches the desired format
        if saved_file is not None:
            _, ext = os.path.splitext(saved_file)
            if ext[1:] != saved_format:
                saved_file = f"{saved_file}.{saved_format}"
        else:
            saved_file = f"default_report.{saved_format}"

        if saved_format == 'txt':
            with open(saved_file, 'w') as f:
                for point in waypoint_time_note_dict:
                    f.write(f"{point[0]} {point[1]}\n")
        elif saved_format == 'pdf':
            c = canvas.Canvas(saved_file, pagesize=letter)
            width, height = letter
            for i, point in enumerate(waypoint_time_note_dict):
                c.drawString(10, height - 10 * (i + 1), f"{point[0]} {point[1]}")
            c.save()

        print(f"Report successfully generated at {saved_file}")
