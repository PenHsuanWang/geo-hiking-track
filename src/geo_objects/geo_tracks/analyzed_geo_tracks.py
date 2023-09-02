
from src.geo_objects.geo_tracks.basic_track import BasicTracks
from src.geo_objects.geo_tracks.raw_geo_tracks import RawTrackObject
from src.geo_objects.geo_points.analyzed_geo_points import AnalyzedTrkPoint


class AnalyzedTracks(BasicTracks):

    def __init__(self):
        """
        Container for hold a Track, composed by the list of AnalyzedTrkPoints.
        Is also can be used for placing certain TrkPoints composed Segments that involved special information.
        like continuously elevation change, or low velocity section.

        """

        self._main_track_points_list = []

    def add_track_point(self, analyzed_trk_point: AnalyzedTrkPoint):
        if isinstance(analyzed_trk_point, AnalyzedTrkPoint):
            self._main_track_points_list.append(analyzed_trk_point)
        else:
            print("error, have to append analyzedTrkPoint in this class")
            pass

    def get_total_integral_xy_displacement(self):
        tot_dist_integration = 0
        for i in self._main_track_points_list:
            tot_dist_integration += i.get_delta_xy()
        return tot_dist_integration


class AnalyzedTrackObject(RawTrackObject):

    def __init__(self):
        super(AnalyzedTrackObject, self).__init__()

        self._main_tracks = AnalyzedTracks()

        self._waypoint_list = []

        #===================================================#
        # Attributes of track, which get from advance calc. #
        #===================================================#

        # List of Rest Point
        self._rest_point_list = []
        self._first_point_hours_list = []
        self._great_turn_point_list = []
        self._great_turn_vector_list = []

        # In analyzed tracks object, setting waypoint list directly,
        # Inheritance from RawTrkObject, get_waypoint_list function() is defined already

    def set_waypoint_list(self, waypoint_list):
        self._waypoint_list = waypoint_list

    def add_track_point(self, new_point):
        self._main_tracks.add_track_point(new_point)


    #=====================#
    # Set function series #
    #=====================#
    def set_rest_point_list(self, input_list):
        self._rest_point_list = input_list

    def set_every_hour_first_point_list(self, input_list):
        self._first_point_hours_list = input_list

    def set_great_turn_point_list(self, input_list):
        self._great_turn_point_list = input_list

    def set_great_turn_vector_list(self, input_list):
        self._great_turn_vector_list = input_list

    #=====================#
    # Get function series #
    #=====================#

    def get_rest_point_list(self):
        return self._rest_point_list

    def get_every_hour_first_point_list(self):
        return self._first_point_hours_list

    def get_great_turn_point_list(self):
        return self._great_turn_point_list

    def get_great_turn_vector_list(self):
        return self._great_turn_vector_list

    def get_total_integral_distance(self):
        return [i.get_point_integral_dst for i in self._main_tracks]

