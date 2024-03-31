from typing import Union
from src.geo_objects.geo_points.basic_point import BasicPoint
from src.geo_objects.geo_points.analyzed_geo_points import AnalyzedTrkPoint
from src.geo_objects.geo_points.raw_geo_points import RawTrkPoint


class BasicTracks:
    """
    The BasicTracks class serves as a base class for other track classes.
    It provides basic functionality for managing a list of track points.

    :ivar _main_track_points_list: List of track points
    :vartype _main_track_points_list: list
    """

    def __init__(self):
        """
        Initializes a new instance of the BasicTracks class.
        """
        self._main_track_points_list = []

    def __iter__(self):
        """
        Returns an iterator for the list of track points.
        This allows instances of this class to be used in a for loop.

        :return: Iterator for the list of track points
        :rtype: iter
        """
        return iter(self._main_track_points_list)

    def add_track_point(self, trk_point: Union[BasicPoint, RawTrkPoint, AnalyzedTrkPoint]):
        self._main_track_points_list.append(trk_point)

    def get_track_point(self, i):
        return self._main_track_points_list[i]

    def get_start_point(self):
        return self._main_track_points_list[0]

    def get_end_point(self):
        return self._main_track_points_list[-1]

    def get_start_time(self):
        return self.get_start_point().time

    def get_end_time(self):
        return self.get_end_point().time

    def get_total_time_spend(self):
        """
        Provided the End point time: time2 - Start point time: time1
        :return: time:hours
        """
        return (self.get_end_point() - self.get_start_point()).hours

    def get_main_tracks_points_list(self):
        return self._main_track_points_list
