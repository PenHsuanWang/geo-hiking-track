"""
The analyzed geography point is on top of the raw point, it provide the displacement information
including the delta x, delta y, delta z, delta xy, delta time, speed x, speed y, speed z, speed xy,
and more other type of point like RestPoint and SeedPoint is designed to
specific function like clustering closing point while tracker in rest
"""

import math

import datetime

from src.geo_objects.geo_points.basic_point import BasicPoint


class AnalyzedTrkPoint(BasicPoint):
    """
    Analyzed track point object is the model to save track point
    """

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
    """
    Rest track point object is the model to save track point
    """
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
