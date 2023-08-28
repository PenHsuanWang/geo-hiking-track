import datetime
import os

from xml.dom import minidom

from src.geoanalyzer.tracks import track_objects


def parse_gpx(input_gpx_file):
    xmldoc = minidom.parse(input_gpx_file)
    return xmldoc


def extract_waypoint_from_xmldoc(xmldoc, tag_name='wpt'):
    extract_waypoint = xmldoc.getElementsByTagName(tag_name)
    return extract_waypoint


def extract_track_point_from_xmldoc(xmldoc, tag_name='trkpt'):
    extract_track_point = xmldoc.getElementsByTagName(tag_name)
    return extract_track_point


def parse_time(input_time):
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

    def processing_waypoint_list(self, input_list_):

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

    def processing_track_point_list(self, input_list_):
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

    def get_raw_track_object(self):
        return self._target_track_object

    @staticmethod
    def _gpx_extract_point_time_str_utc(s):
        try:
            time_tag = s.getElementsByTagName("time")[0].firstChild.data
            return time_tag

        except:
            print("Error of get time from GPX, time tag not found!")
            return None

    @staticmethod
    def _gpx_extract_point_elevation(s):
        try:
            elevation = s.getElementsByTagName("ele")[0].firstChild.data
            elevation = float(elevation)
            return elevation
        except:
            print("Error of get elevation from GPX, ele tag not found!")
            return None

    @staticmethod
    def _gpx_extract_point_note(s):
        try:
            note = s.getElementsByTagName("name")[0].firstChild.data
            return note
        except:
            print("Error of get Note from GPX, name tag not found!")
            return None
