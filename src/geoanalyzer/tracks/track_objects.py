import datetime
import math


class BasicPoint:
    def __init__(self, time=None, lat=None, lon=None, elev=None):
        if time is not None:
            self._time = time
            self._lat = lat
            self._lon = lon
            self._elev = elev
            self._is_empty = False
        else:
            self._time = None
            self._lat = None
            self._lon = None
            self._elev = None
            self._is_empty = True

    def get_point_time(self):
        return self._time

    def get_lat(self):
        return self._lat

    def get_lon(self):
        return self._lon

    def get_elev(self):
        return self._elev

    def is_enpty(self):
        return self._is_empty


class WayPoint(BasicPoint):
    def __init__(self, time=None, lat=None, lon=None, elev=None, note=None):
        super(WayPoint, self).__init__(time, lat, lon, elev)
        self._note = note

    def get_note(self):
        return self._note


class RawTrkPoint(BasicPoint):
    """
    Raw track point object is the model to save track point
    row information which extracting directory from gpx file.
    """


    def __init__(self, time=None, lat=None, lon=None, elev=None):
        super(RawTrkPoint, self).__init__(time, lat, lon, elev)


class AnalyzedTrkPoint(BasicPoint):

    def __init__(self, time, lat, lon, elev, dx, dy, dz, dt):
        super(AnalyzedTrkPoint, self).__init__(time, lat, lon, elev)
        self._dx = dx
        self._dy = dy
        self._dz = dz
        self._dt = dt
        self._integral_dst = 0

    def set_point_integral_dst(self, in_dst):
        self._integral_dst = in_dst

    #=====================================================#
    # get methods for return the value about displacement #
    #=====================================================#
    def get_delta_x(self):
        return self._dx

    def get_delta_y(self):
        return self._dy

    def get_delta_z(self):
        return self._dz

    def get_delta_xy(self):
        return math.sqrt(math.pow(self._dx, 2) + math.pow(self._dy, 2))

    def get_point_integral_dst(self):
        return self._integral_dst

    #============#
    # Delta time #
    #============#
    def get_point_delta_time(self):
        return self._dt

    #===========================================================#
    # get methods for return the value about speed and velocity #
    #===========================================================#

    def get_speed_x(self):
        return self._dx/self._dt

    def get_speed_y(self):
        return self._dy/self._dt

    def get_speed_z(self):
        return self._dz/self._dt

    def get_speed_xy(self):
        return self.get_delta_xy()/self._dt

    def get_velocity_xy(self):
        """
        Return a 2-D array [Vx, Vy], the vector about velocity
        :return: list[Vx, Vy]
        """
        return [self._dx/self._dt, self._dy/self._dt]

    def get_velocity_xyx(self):
        """
        Return a 3-D array [Vx, Vy, Vz], the vector about velocity
        :return: list[Vx, Vy, Vz]
        """
        return [self._dx/self._dt, self._dy/self._dt, self._dz/self._dt]


class RestTrkPoint(BasicPoint):
    def __init__(self, time, lat, lon, elev, start_time, end_time):
        super(RestTrkPoint, self).__init__(time, lat, lon, elev)
        self._start_time = start_time
        self._end_time = end_time

    def update_start_time(self, new_start_time):
        self._start_time = new_start_time

    def update_end_time(self, new_end_time):
        self._end_time = new_end_time

    def get_start_time(self):
        return self._start_time

    def get_end_time(self):
        return self._end_time

    def get_rest_time_spend(self):
        return (self._end_time - self._start_time).minutes


class RestTrkPointCandidate:
    def __init__(self, first_point: AnalyzedTrkPoint):

        if not isinstance(first_point, AnalyzedTrkPoint):
            print("Using Rest Point finder should provided Analyzed point")
            raise TypeError

        self._start_time = first_point.get_point_time()
        self._point_count = 1

        self._accumulated_lat = first_point.get_lat()
        self._accumulated_lon = first_point.get_lon()
        self._accumulated_elev = first_point.get_elev()

        self._tot_delta_x = 0
        self._tot_delta_y = 0
        self._last_point_time = None

    def calculate_time_spend(self, input_point) -> float:
        """Calculating time spend across starting point to input_point timestamp
        :param input_point: AnalyzedTrkPoint
        :return: seconds
        """
        time_spend = input_point.get_point_time() - self._start_time
        return time_spend.seconds

    def add_candidate(self, input_point: AnalyzedTrkPoint):
        if isinstance(input_point, AnalyzedTrkPoint):
            self._point_count += 1
            self._tot_delta_x += input_point.get_delta_x()
            self._tot_delta_y += input_point.get_delta_y()
            self._last_point_time = input_point.get_point_time()

            self._accumulated_lat += input_point.get_lat()
            self._accumulated_lon += input_point.get_lon()
            self._accumulated_elev += input_point.get_elev()

        else:
            raise TypeError

    def get_point_count(self) -> int:
        return self._point_count

    def get_tot_delta_x(self) -> float:
        return self._tot_delta_x

    def get_tot_delta_y(self) -> float:
        return self._tot_delta_y

    def get_average_lat(self) -> float:
        return self._accumulated_lat/self._point_count

    def get_average_lon(self) -> float:
        return self._accumulated_lon/self._point_count

    def get_average_elev(self) -> float:
        return self._accumulated_elev/self._point_count

    def get_start_time(self) -> datetime.datetime:
        return self._start_time

    def get_tot_time_spend(self) -> float:
        """provided total time spend from start point to last point
        :return: float time in second
        """
        tot_time_spend = self._last_point_time - self._start_time
        return tot_time_spend.seconds

    def flush_to_rest_seed(self):

        rest_seed = SeedRestPoint(
            self.get_average_lat(),
            self.get_average_lon(),
            self.get_average_elev(),
            self.get_start_time()
        )
        return rest_seed


class SeedRestPoint:
    def __init__(self, lat, lon, elev, start_time):
        self._lat = lat
        self._lon = lon
        self._elev = elev
        self._start_time = start_time

    def get_lat(self):
        return self._lat

    def get_lon(self):
        return self._lon

    def get_elev(self):
        return self._elev

    def get_start_time(self):
        return self._start_time



class BasicTracks:

    def __init__(self):
        """

        """
        self._main_track_points_list = []

    def add_track_point(self, BasicPoint):
        self._main_track_points_list.append(BasicPoint)

    def get_track_point(self, i):
        return self._main_track_points_list[i]

    def get_start_point(self):
        return self._main_track_points_list[0]

    def get_end_point(self):
        return self._main_track_points_list[-1]

    def get_start_time(self):
        return self.get_start_point().get_point_time()

    def get_end_time(self):
        return self.get_end_point().get_point_time()

    def get_total_time_spend(self):
        """
        Provided the End point time: time2 - Start point time: time1
        :return: time:hours
        """
        return (self.get_end_point() - self.get_start_point()).hours

    def get_main_tracks_points_list(self):
        return self._main_track_points_list


class RawTracks(BasicTracks):

    def __init__(self):
        """
        Container for hold a Track, composed by the list of RowTrkPoints
        """

        self._main_track_points_list = []

    def add_track_point(self, raw_track_point):

        if isinstance(raw_track_point, RawTrkPoint):
            self._main_track_points_list.append(raw_track_point)
        else:
            print("error, have to append RawTrkPoint in this class")
            pass

class AnalyzedTracks(BasicTracks):

    def __init__(self):
        """
        Container for hold a Track, composed by the list of AnalyzedTrkPoints.
        Is also can be used for placing certain TrkPoints composed Segments that involved special information.
        like continuously elevation change, or low velocity section.

        """

        self._main_track_points_list = []

    def add_track_point(self, analyzed_trk_point):
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


class RawTrackObject:

    def __init__(self):

        self._main_tracks = RawTracks()
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


class TrackPointVector:

    def __init__(self, track_point_1, track_point_2):
        """
        Provide two track points and get the vector (point2 - point1)
        :param track_point_1: vector start point
        :param track_point_2: vector end point
        """

        self._track_point_1 = track_point_1
        self._track_point_2 = track_point_2

    def get_x_component(self):
        return(self._track_point_2.get_lon() - self._track_point_1.get_lon()) * 101751

    def get_y_component(self):
        return(self._track_point_2.get_lat() - self._track_point_1.get_lat()) * 110757

    def get_x_component(self):
        return(self._track_point_2.get_elev() - self._track_point_1.get_elev())

    def get_length(self):
        return math.sqrt( math.pow(self.get_x_component(), 2) + math.pow(self.get_y_component(), 2) )

    def get_vector(self):
        return [self.get_x_component(), self.get_y_component()]

    def get_init_point(self):
        return self._track_point_1

    def get_end_point(self):
        return self._track_point_2
