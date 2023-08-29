import datetime
import os

from typing import Optional

from xml.dom import minidom
from xml.dom.minidom import Document, Node

from src.geoanalyzer.tracks import track_objects


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


def extract_track_point_from_xmldoc(xmldoc: minidom.Document, tag_name: str ='trkpt') -> [minidom.Node]:
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

        self._target_track_object = track_objects.RawTrackObject()

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
            extract_waypoint = track_objects.WayPoint(
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

            extract_point = track_objects.RawTrkPoint(
                point_parsed_datetime,
                float(s.getAttribute("lat")),
                float(s.getAttribute("lon")),
                elevation
            )
            self._target_track_object.add_track_point(extract_point)

    def get_raw_track_object(self) -> track_objects.RawTrackObject:
        """Return the populated RawTrackObject."""
        return self._target_track_object

    @staticmethod
    def _gpx_extract_point_time_str_utc(s: Node) -> Optional[str]:
        """Extract the time string from a GPX point. Returns None if not found."""
        try:
            time_tag = s.getElementsByTagName("time")[0].firstChild.data
            return time_tag

        except:
            print("Error of get time from GPX, time tag not found!")
            return None

    @staticmethod
    def _gpx_extract_point_elevation(s: Node) -> Optional[float]:
        """Extract the elevation from a GPX point. Returns None if not found."""
        try:
            elevation = s.getElementsByTagName("ele")[0].firstChild.data
            elevation = float(elevation)
            return elevation
        except:
            print("Error of get elevation from GPX, ele tag not found!")
            return None

    @staticmethod
    def _gpx_extract_point_note(s: Node) -> Optional[str]:
        """Extract the note from a GPX point. Returns None if not found."""
        try:
            note = s.getElementsByTagName("name")[0].firstChild.data
            return note
        except:
            print("Error of get Note from GPX, name tag not found!")
            return None
