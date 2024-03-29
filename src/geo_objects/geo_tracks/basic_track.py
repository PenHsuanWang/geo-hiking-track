
from src.geo_objects.geo_points.basic_point import BasicPoint


class BasicTracks:

    def __init__(self):
        """

        """
        self._main_track_points_list = []

    def add_track_point(self, trk_point: BasicPoint):
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

