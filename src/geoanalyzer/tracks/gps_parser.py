import datetime
import os
import logging
from typing import Optional, List

from xml.dom import minidom
from xml.dom.minidom import Node, Element, Text
# from src.geoanalyzer.tracks import track_objects


from src.geo_objects.geo_points.raw_geo_points import RawTrkPoint, WayPoint
from src.geo_objects.geo_tracks.raw_geo_tracks import RawTrackObject
# from src.geo_objects.geo_tracks.analyzed_geo_tracks import AnalyzedTrackObject


def parse_gpx(input_gpx_file: str) -> minidom.Document:
    """
    Parse a GPX file and return its XML document representation.

    Reads a GPX file from the given file path, parses it into an XML document using the
    `minidom` parser, and returns the document object for further processing. Raises a
    FileNotFoundError if the specified GPX file does not exist.

    :param input_gpx_file: The file path to the GPX file to be parsed.
    :type input_gpx_file: str
    :return: The parsed XML document object of the GPX file.
    :rtype: minidom.Document
    :raises FileNotFoundError: If the specified GPX file does not exist.
    """
    if not os.path.exists(input_gpx_file):
        raise FileNotFoundError("GPX file not found")
    xmldoc = minidom.parse(input_gpx_file)
    return xmldoc


def extract_waypoint_from_xmldoc(xmldoc: minidom.Document, tag_name='wpt') -> List[minidom.Node]:
    """
    Extracts all waypoints from the given GPX XML document.

    Finds all XML nodes corresponding to waypoints in the GPX document,
    based on the specified tag name, and returns them as a list. By default,
    it looks for 'wpt' tags, which represent waypoints in GPX files.

    :param xmldoc: The XML structure of the GPX file.
    :param tag_name: The tag name of waypoints. Default is 'wpt'.
    :type tag_name: str
    :return: A list of waypoints.
    :rtype: List[minidom.Node]
    """
    return list(xmldoc.getElementsByTagName(tag_name))


def extract_track_point_from_xmldoc(xmldoc: minidom.Document, tag_name: str = 'trkpt') -> List[minidom.Node]:
    """
    Extracts track points from the XML structure of a GPX file.

    :param xmldoc: The XML structure of the GPX file.
    :param tag_name: The tag name of track points. Default is 'trkpt'.
    :type tag_name: str
    :return: A list of track points.
    :rtype: List[minidom.Node]
    """
    return list(xmldoc.getElementsByTagName(tag_name))


def parse_time(input_time: str) -> datetime.datetime:
    """
    Parses a time string from a GPX file into a datetime object.

    Converts a time string in the format "%Y-%m-%dT%H:%M:%SZ" from the GPX file to
    a datetime object, adjusting for the timezone if necessary. The implementation
    should be adapted to handle timezone information more dynamically.

    :param input_time: The input time string in "%Y-%m-%dT%H:%M:%SZ" format.
    :type input_time: str
    :return: The parsed datetime object.
    :rtype: datetime.datetime
    :raises ValueError: If there is an error parsing the datetime.
    """
    try:
        parse_date_and_time = datetime.datetime.strptime(
            input_time,
            "%Y-%m-%dT%H:%M:%SZ"
        )
        parse_date_and_time = parse_date_and_time + datetime.timedelta(hours=8)
        return parse_date_and_time
    except Exception as e:
        raise ValueError from e


class GpxParser:
    """
    Parser class for extracting data from GPX files.

    Takes a path to a GPX file, parses it, and extracts geographical data, including waypoints and
    track points. The extracted data is used to populate a RawTrackObject with instances of WayPoint
    and RawTrkPoint, which can then be further processed or analyzed.

    :ivar _infile: Path to the input GPX file.
    :ivar _target_track_object: Container for the extracted waypoints and track points.

    :param gpx_file: The file path to the GPX file to be processed.
    :type gpx_file: str
    """

    def __init__(self, gpx_file):

        self._infile = gpx_file

        self._target_track_object = RawTrackObject()

        xmldoc = parse_gpx(self._infile)

        self._extract_waypoint = extract_waypoint_from_xmldoc(xmldoc)
        self._extract_track_point = extract_track_point_from_xmldoc(xmldoc)

        self.processing_waypoint_list(self._extract_waypoint)
        self.processing_track_point_list(self._extract_track_point)

    def processing_waypoint_list(self, input_list_: List[minidom.Node]) -> None:
        """
        Processes a list of waypoint nodes and adds them to the track object.

        :param input_list_: List of waypoint nodes to be processed.
        :type input_list_: List[minidom.Node]
        """
        for s in input_list_:
            if not isinstance(s, Element):
                logging.error("Node is not an Element.")
                continue

            point_time_str_utc = self._gpx_extract_point_time_str_utc(s)
            point_parsed_datetime = None if point_time_str_utc is None else parse_time(point_time_str_utc)
            elevation = self._gpx_extract_point_elevation(s)
            waypoint_note = self._gpx_extract_point_note(s)

            # Creating the point object
            extract_waypoint = WayPoint(
                point_parsed_datetime,
                float(s.getAttribute("lat")),
                float(s.getAttribute("lon")),
                elevation,
                waypoint_note
            )
            self._target_track_object.add_way_point(extract_waypoint)

    def processing_track_point_list(self, input_list_: List[minidom.Node]) -> None:
        """
        Processes a list of track point nodes and adds them to the track object.

        :param input_list_: List of track point nodes to be processed.
        :type input_list_: List[minidom.Node]
        """
        for s in input_list_:

            if not isinstance(s, Element):
                logging.error("Node is not an Element.")
                continue

            point_time_str_utc = self._gpx_extract_point_time_str_utc(s)
            point_parsed_datetime = None if point_time_str_utc is None else parse_time(point_time_str_utc)
            elevation = self._gpx_extract_point_elevation(s)

            extract_point = RawTrkPoint(
                point_parsed_datetime,
                float(s.getAttribute("lat")),
                float(s.getAttribute("lon")),
                elevation
            )
            self._target_track_object.add_track_point(extract_point)

    def get_raw_track_object(self) -> RawTrackObject:
        """
        Returns the populated RawTrackObject with GPX data.

        :return: The populated RawTrackObject.
        :rtype: RawTrackObject
        """
        return self._target_track_object

    @staticmethod
    def _gpx_extract_point_time_str_utc(s: Node) -> Optional[str]:
        """
        Extracts the time string from a GPX point element and returns it.

        :param s: GPX point element from which to extract the time string.
        :type s: Node
        :return: The extracted time string, or None if not found.
        :rtype: Optional[str]
        """
        if not isinstance(s, Element):
            logging.error("Provided node is not an Element.")
            return None

        time_elements = s.getElementsByTagName("time")
        if not time_elements:
            logging.error("Time tag not found in GPX point.")
            return None

        time_node = time_elements[0].firstChild
        if not time_node or not isinstance(time_node, Text):
            logging.error("Time element's first child is not text.")
            return None

        return time_node.data

    @staticmethod
    def _gpx_extract_point_elevation(s: Node) -> Optional[float]:
        """
        Extracts and returns the elevation float value from a GPX point element.

        :param s: GPX point element from which to extract the elevation.
        :type s: Node
        :return: The elevation value, or None if not found or invalid.
        :rtype: Optional[float]
        """
        if not isinstance(s, Element):
            logging.error("Provided node is not an Element.")
            return None

        elevation_elements = s.getElementsByTagName("ele")
        if not elevation_elements:
            logging.error("Elevation tag not found in GPX point.")
            return None

        elevation_node = elevation_elements[0].firstChild
        if not elevation_node or not isinstance(elevation_node, Text):
            logging.error("Elevation element's first child is not text.")
            return None

        try:
            return float(elevation_node.data)
        except ValueError:
            logging.error("Elevation value is not a valid float.")
            return None

    @staticmethod
    def _gpx_extract_point_note(s: Node) -> Optional[str]:
        """
        Extracts and returns the note string from a GPX point element.

        :param s: GPX point element from which to extract the note.
        :type s: Node
        :return: The note string, or None if not found.
        :rtype: Optional[str]
        """
        if not isinstance(s, Element):
            logging.error("Provided node is not an Element.")
            return None

        note_elements = s.getElementsByTagName("name")
        if not note_elements:
            logging.error("Note tag not found in GPX point.")
            return None

        note_node = note_elements[0].firstChild
        if not isinstance(note_node, Text):
            logging.error("Note element's first child is not text.")
            return None

        return note_node.data
