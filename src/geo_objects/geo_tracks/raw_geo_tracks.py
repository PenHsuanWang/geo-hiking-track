from typing import Union
from src.geo_objects.geo_tracks.basic_track import BasicTracks
from src.geo_objects.geo_points.basic_point import BasicPoint
from src.geo_objects.geo_points.raw_geo_points import RawTrkPoint, WayPoint


class RawTracks(BasicTracks):

    def __init__(self):
        """
        Container for hold a Track, composed by the list of RowTrkPoints
        """

        super().__init__()
        self._main_track_points_list = []

    def add_track_point(self, raw_track_point: Union[BasicPoint, RawTrkPoint]):

        if isinstance(raw_track_point, RawTrkPoint):
            self._main_track_points_list.append(raw_track_point)
        else:
            print("error, have to append RawTrkPoint in this class")
            pass


class RawTrackObject:

    def __init__(self):

        self._main_tracks: BasicTracks = RawTracks()
        self._waypoint_list = []

    def add_track_point(self, new_track_point):
        if isinstance(new_track_point, RawTrkPoint):
            self._main_tracks.add_track_point(
                new_track_point
            )
        else:
            print("Error, input object is not a RawTrackPoint")

    def add_way_point(self, new_waypoint):
        if isinstance(new_waypoint, WayPoint):
            self._waypoint_list.append(
                new_waypoint
            )
        else:
            print("Error, input object is not a WayPoint")

    def get_track_point(self, i):
        return self._main_tracks.get_track_point(i)

    def get_waypoint_list(self):
        return self._waypoint_list

    def get_main_tracks(self):
        return self._main_tracks
