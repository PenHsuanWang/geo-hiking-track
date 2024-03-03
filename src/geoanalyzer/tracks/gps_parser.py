import datetime
import os
import logging
from typing import Optional

from xml.dom import minidom
from xml.dom.minidom import Node
from xml.dom.minidom import Element
# from src.geoanalyzer.tracks import track_objects


from src.geo_objects.geo_points.raw_geo_points import RawTrkPoint, WayPoint
from src.geo_objects.geo_tracks.raw_geo_tracks import RawTrackObject
# from src.geo_objects.geo_tracks.analyzed_geo_tracks import AnalyzedTrackObject


def parse_gpx(input_gpx_file: str) -> minidom.Document:
    """
    Parse a GPX file into an XML document object.

    :param input_gpx_file: The path to the GPX file to be parsed.
    :return: The parsed XML document object.
    """
    if not os.path.exists(input_gpx_file):
        raise FileNotFoundError("GPX file not found")
    xmldoc = minidom.parse(input_gpx_file)
    return xmldoc


def extract_waypoint_from_xmldoc(xmldoc: minidom.Document, tag_name='wpt') -> [minidom.Node]:
    """
    Extract waypoints from the XML structure of a GPX file.

    :param xmldoc: The XML structure of the GPX file.
    :param tag_name: The tag name of waypoints. Default is 'wpt'.
    :return: A list of waypoints.
    """
    return xmldoc.getElementsByTagName(tag_name)


def extract_track_point_from_xmldoc(xmldoc: minidom.Document, tag_name: str = 'trkpt') -> [minidom.Node]:
    """
    Extract track points from the XML structure of a GPX file.

    :param xmldoc: The XML structure of the GPX file.
    :param tag_name: The tag name of track points. Default is 'trkpt'.
    :return: A list of track points.
    """
    return xmldoc.getElementsByTagName(tag_name)


def parse_time(input_time: str) -> datetime.datetime:
    """
    Parse a time string into a datetime object.

    :param input_time: The input time string in "%Y-%m-%dT%H:%M:%SZ" format.
    :return: The parsed datetime object.
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
    """GpxParser for extraction of row GPX file

    Extracting GPX by looping xml structure of GPX file
    Getting information from GPX and saving into defined model (class:TrackObject)

    Author: {Pen Hsuan Wang}

    """

    def __init__(self, gpx_file):

        self._infile = gpx_file

        self._target_track_object = RawTrackObject()

        xmldoc = parse_gpx(self._infile)

        self._extract_waypoint = extract_waypoint_from_xmldoc(xmldoc)
        self._extract_track_point = extract_track_point_from_xmldoc(xmldoc)

        self.processing_waypoint_list(self._extract_waypoint)
        self.processing_track_point_list(self._extract_track_point)

    def processing_waypoint_list(self, input_list_: [minidom.Node]) -> None:
        """Processing the list of waypoints and adding them to the track object."""

        for s in input_list_:
            point_time_str_utc = self._gpx_extract_point_time_str_utc(s)
            point_parsed_datetime = parse_time(point_time_str_utc)

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

    def processing_track_point_list(self, input_list_: [minidom.Node]) -> None:
        """Processing the list of track points and adding them to the track object."""
        for s in input_list_:
            point_time_str_utc = self._gpx_extract_point_time_str_utc(s)
            point_parsed_datetime = parse_time(point_time_str_utc)

            elevation = self._gpx_extract_point_elevation(s)

            extract_point = RawTrkPoint(
                point_parsed_datetime,
                float(s.getAttribute("lat")),
                float(s.getAttribute("lon")),
                elevation
            )
            self._target_track_object.add_track_point(extract_point)

    def get_raw_track_object(self) -> RawTrackObject:
        """Return the populated RawTrackObject."""
        return self._target_track_object

    @staticmethod
    def _gpx_extract_point_time_str_utc(s: Node) -> Optional[str]:
        """
        Extracts the time string from a GPX point element.

        This method attempts to find and return the time string from a provided GPX point.
        It logs an error if the provided node is not an Element or if the time tag is missing.
        """
        if isinstance(s, Element):
            try:
                time_tag = s.getElementsByTagName("time")[0].firstChild.data
                return time_tag
            except IndexError:
                logging.error("Time tag not found in GPX point.")
        else:
            logging.error("Provided node is not an Element.")
        return None

    @staticmethod
    def _gpx_extract_point_elevation(s: Node) -> Optional[float]:
        """
        Extracts the elevation float value from a GPX point element.

        Attempts to extract and return the elevation value from a provided GPX point.
        Logs errors if the node is not an Element, the elevation tag is missing, or
        if the elevation value is not a valid float.
        """
        if isinstance(s, Element):
            try:
                elevation = s.getElementsByTagName("ele")[0].firstChild.data
                return float(elevation)
            except IndexError:
                logging.error("Elevation tag not found in GPX point.")
            except ValueError:
                logging.error("Elevation value is not a valid float.")
        else:
            logging.error("Provided node is not an Element.")
        return None

    @staticmethod
    def _gpx_extract_point_note(s: Node) -> Optional[str]:
        """
        Extracts the note string from a GPX point element.

        This method looks for and returns the note (name tag) from a provided GPX point.
        It logs an error if the node is not an Element or if the note tag is absent.
        """
        if isinstance(s, Element):
            try:
                note = s.getElementsByTagName("name")[0].firstChild.data
                return note
            except IndexError:
                logging.error("Note tag not found in GPX point.")
        else:
            logging.error("Provided node is not an Element.")
        return None
