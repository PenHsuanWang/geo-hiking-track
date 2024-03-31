import datetime
import math
from typing import List, Union
# from src.geoanalyzer.tracks.track_objects import RawTrkPoint, RawTracks, AnalyzedTrkPoint, AnalyzedTrackObject, TrackPointVector, RestTrkPoint, RestTrkPointCandidate, SeedRestPoint
from src.geo_objects.geo_points.raw_geo_points import RawTrkPoint
from src.geo_objects.geo_points.analyzed_geo_points import AnalyzedTrkPoint, RestTrkPoint, RestTrkPointCandidate
from src.geo_objects.geo_tracks.analyzed_geo_tracks import AnalyzedTrackObject

#
# def sum_delta_between_every_element(input_list: List[Union[float, datetime.timedelta]]) -> float:
#     """
#     Calculate the total of differences between successive elements in a list of values. This function
#     supports lists of either numerical values (float) for spatial attributes or `datetime.timedelta`
#     objects for temporal attributes of GPS track points. The list should be homogeneous, containing
#     elements of only one of the specified types.
#
#     Args:
#         input_list (List[Union[float, datetime.timedelta]]): A list of attribute values extracted
#         from track points. The list must be homogeneous.
#
#     Returns:
#         float: The total of differences between successive elements in the list. For temporal attributes,
#         the difference is returned in seconds.
#
#     Raises:
#         ValueError: If the input list contains fewer than two elements or is not homogeneous.
#         TypeError: If the list contains elements other than float or datetime.timedelta.
#     """
#     if len(input_list) < 2:
#         raise ValueError("Input list must contain at least two elements to calculate differences.")
#
#     # Determine the type of the first element, which we'll use to check list homogeneity
#     first_element_type = type(input_list[0])
#
#     if not all(isinstance(item, first_element_type) for item in input_list):
#         raise ValueError("Input list must be homogeneous.")
#
#     tot_delta = 0.0
#
#     for i in range(len(input_list) - 1):
#
#         delta_element = input_list[i + 1] - input_list[i]
#
#         if isinstance(delta_element, (float, int)):
#             tot_delta += delta_element
#         elif isinstance(delta_element, datetime.timedelta):
#             tot_delta += delta_element.total_seconds()
#         else:
#             raise TypeError("Element type not supported.")
#     return tot_delta


def sum_numeric_deltas(input_list: List[float]) -> float:
    """
    Calculate the sum of numerical differences between successive elements in a list.

    :param input_list: A list of numerical values. The list must contain at least two elements.
    :type input_list: List[float]
    :return: The sum of differences between each successive pair of elements in the list.
    :rtype: float
    :raises ValueError: If the input list contains fewer than two elements.
    """
    if len(input_list) < 2:
        raise ValueError("Input list must contain at least two elements to calculate differences.")
    return sum(input_list[i + 1] - input_list[i] for i in range(len(input_list) - 1))


def sum_timedelta_deltas(input_list: List[datetime.timedelta]) -> float:
    """
    Calculate the sum of timedelta differences between successive elements in a list, in seconds.

    :param input_list: A list of datetime.timedelta objects. The list must contain at least two elements.
    :type input_list: List[datetime.timedelta]
    :return: The sum of differences between each successive pair of elements in the list, in seconds.
    :rtype: float
    :raises ValueError: If the input list contains fewer than two elements.
    """
    if len(input_list) < 2:
        raise ValueError("Input list must contain at least two elements to calculate differences.")
    return sum((input_list[i + 1] - input_list[i]).total_seconds() for i in range(len(input_list) - 1))


def smoothing_tracks(input_track_point_list: List[RawTrkPoint]) -> List[RawTrkPoint]:
    """
    Smooths the GPS track data by averaging the latitude, longitude, and elevation values over a sliding window of track points.

    :param input_track_point_list: A list of RawTrkPoint objects representing the GPS track points.
    :type input_track_point_list: List[RawTrkPoint]
    :return: A list of RawTrkPoint objects representing the smoothed GPS track points.
    :rtype: List[RawTrkPoint]
    """
    def average(input_list: List[float]) -> float:
        """
        Calculates the average of a list of numbers.

        :param input_list: A list of numbers.
        :type input_list: List[float]
        :return: The average of the input list.
        :rtype: float
        """
        return sum(input_list) / len(input_list)

    averaged_tracks_list: List[RawTrkPoint] = []

    for i in range(len(input_track_point_list) - 5):
        track_point_list_segment = input_track_point_list[i:i+5]
        track_point_time = track_point_list_segment[2].time

        list_segment_lat = list(map(lambda x: x.lat, track_point_list_segment))
        list_segment_lon = list(map(lambda x: x.lon, track_point_list_segment))
        list_segment_ele = list(map(lambda x: x.elev, track_point_list_segment))

        average_lat = average(list_segment_lat)
        average_lon = average(list_segment_lon)
        average_elev = average(list_segment_ele)

        averaged_tracks_list.append(
            RawTrkPoint(
                track_point_time,
                average_lat,
                average_lon,
                average_elev
            )
        )
    return averaged_tracks_list


def do_analyzing(input_track_point_list):

    target_analyzing_track_object = AnalyzedTrackObject()
    raw_track_point_list = input_track_point_list

    for i in range(len(raw_track_point_list)-3):
        track_point_list_segment = raw_track_point_list[i:i+3]

        list_segment_lat = list(map(lambda x: x.lat, track_point_list_segment))
        list_segment_lon = list(map(lambda x: x.lon, track_point_list_segment))
        list_segment_elev = list(map(lambda x: x.elev, track_point_list_segment))
        list_segment_time = list(map(lambda x: x.time, track_point_list_segment))

        # 1 degree is 101751 meters in Lon direction
        delta_x = sum_numeric_deltas(list_segment_lon)/(len(list_segment_lon)-1) * 101751
        # 1 degree is 110757 meters in Lat direction
        delta_y = sum_numeric_deltas(list_segment_lat)/(len(list_segment_lat)-1) * 110757
        delta_z = sum_numeric_deltas(list_segment_elev)/(len(list_segment_elev)-1)
        delta_t = sum_timedelta_deltas(list_segment_time)/(len(list_segment_time)-1)

        target_analyzing_track_object.add_track_point(
            AnalyzedTrkPoint(
                track_point_list_segment[1].time,
                track_point_list_segment[1].lat,
                track_point_list_segment[1].lon,
                track_point_list_segment[1].elev,
                delta_x,
                delta_y,
                delta_z,
                delta_t
            )
        )

    return target_analyzing_track_object


def find_rest_point(input_list):

    """ finding the rest point from the gpx tracks!

    Rest Point Candidate => SeedPoint => RestTrkPoint

    Rest Point Candidate:
        First RestPointCandidate:
            the point speed X and speed Y < 0.1 can be treated as first RestPointCandidate.
        Second RestPointCandidate:
            the second RestPointCandidate's speed X and speed Y should < 0.1 also => two continuous point with low speed
        Following Point:
            if following point's speed > 0.1: check:
            total X, Y drifting distance (tot_delta X or Y) < 20 meters.
            if drifting distance < 20 meters => this anomaly high speed point is tolerance
        If total accumulate time > 60 seconds and total drifting < 20 either in X or Y distance:
            Go to next step => create SeedPoint.

    SeedPoint:
        multiple Rest Point Candidate gather together and satisfied following rule:
            1. time spend from first point to current check is > 60 seconds
            2. total drifting distance < 20 either in X or Y direction
        Taking current Rest Point Candidates' average lon and lat as location:

    RestTrkPoint:
        once SeedPoint found, the RestTrkPoint is going to create.
        The information of RestTrkPoint needed:
            1. location (lat, lon, elev)
            2. time (start time, end time)
        take SeedPoint's location as RestTrkPoint's location.
        Condition of RestTrkPoint Collection complete:
            the last point exceed 20 meters away from SeedPoint location, and moving speed > 0.1
        Create RestTrkPoint using
        (SeedPoint lat, SeedPoint lon, SeedPoint elev, RestPointCandidate StartTime, LastPoint's time as end time)

    :param input_list:
    :return:
    """

    # # Check if input_list is None or empty
    # if not input_list:
    #     raise ValueError("input_list cannot be None or empty")
    #
    # # Check if elements in input_list are instances of TrackPoint
    # if not all(isinstance(i, BasicPoint) for i in input_list):
    #     raise ValueError("All elements in input_list must be instances of the TrackPoint class")

    rest_point_list: List[RestTrkPoint] = []

    found_seed = False
    seed_rest_point = None

    rest_point_candidate = None

    for i_track_point in input_list:

        if i_track_point.get_speed_xy() < 0.1:

            # ======================= #
            # If SeedPoint is found   #
            # ======================= #
            if found_seed:
                continue

            # ============================== #
            # SeedPoint is not yet found !   #
            # ============================== #
            if rest_point_candidate is None:
                rest_point_candidate = RestTrkPointCandidate(i_track_point)

            elif isinstance(rest_point_candidate, RestTrkPointCandidate):

                if rest_point_candidate.get_tot_delta_x() > 20 or rest_point_candidate.get_tot_delta_y() > 20:
                    # =========================================== #
                    # False condition, purge RestPointCandidate   #
                    # =========================================== #
                    del rest_point_candidate
                    rest_point_candidate = None  # rest rest_point_candidate
                    continue

                if rest_point_candidate.calculate_time_spend(i_track_point) > 60:
                    # ==================================================== #
                    # True condition, go to flush this candidate as seed   #
                    # ==================================================== #
                    if not found_seed:
                        found_seed = True
                        seed_rest_point = rest_point_candidate.flush_to_rest_seed()
                        del rest_point_candidate
                        rest_point_candidate = None
                    else:
                        print("Peculiar case happen, RestPointCandidate and SeedRestPoint should not exist at the same time")
                        raise Exception

                elif rest_point_candidate.calculate_time_spend(i_track_point) <= 60:
                    # ============================== #
                    # Add new rest point candidate   #
                    # ============================== #
                    rest_point_candidate.add_candidate(i_track_point)
                    continue

                else:
                    print("Peculiar case happen, which I did not considered")
                    raise Exception

        elif i_track_point.get_speed_xy() >= 0.1:

            if found_seed:
                """ if rest point seed is found!
                check the new coming track point is located away from 20 meters either in X or Y direction or not?
                if not (within 20 meter apart from seed center), pass this iteration (continue)
                if yes, complete this rest point collection, flush rest point and reset the seed.
                """

                if seed_rest_point is None:
                    raise ValueError("Seed rest point is None when it should have been initialized.")

                x_shift = math.fabs((i_track_point.lon-seed_rest_point.lon)*110751)
                y_shift = math.fabs((i_track_point.lat-seed_rest_point.lat)*110757)
                if x_shift < 20 and y_shift < 20:
                    pass
                else:
                    # Stop to collect resting point,
                    # flush and delete all collecting object

                    if len(rest_point_list) > 0 and (seed_rest_point.start_time - rest_point_list[-1].get_end_time()).seconds < 120:
                        # ============================================================================================ #
                        # If the seed rest point's start time is too close to previous rest point's end time           #
                        # The new seeding point maybe the same rest point, Do not append this seed as new rest point   #
                        # Update the last rest point in list's setting the end time to current point time              #
                        # ============================================================================================ #
                        rest_point_list[-1].update_end_time(i_track_point.time)

                    else:
                        # ================================================================================== #
                        # Check the SeedRestPoint start time is greater than previous appended rest point!   #
                        # ================================================================================== #
                        rest_point_confirmed = RestTrkPoint(
                            seed_rest_point.start_time,
                            seed_rest_point.lat,
                            seed_rest_point.lon,
                            seed_rest_point.elev,
                            seed_rest_point.start_time,
                            i_track_point.time
                        )

                        rest_point_list.append(rest_point_confirmed)

                    # ======================= #
                    # Reset rest point seed   #
                    # ======================= #
                    del seed_rest_point
                    seed_rest_point = None
                    found_seed = False

            elif isinstance(rest_point_candidate, RestTrkPointCandidate):
                if rest_point_candidate.get_point_count() < 2 or rest_point_candidate.calculate_time_spend(i_track_point) < 60:
                    del rest_point_candidate
                    rest_point_candidate = None  # reset rest_point_candidate
                else:
                    rest_point_candidate.add_candidate(i_track_point)
            elif rest_point_candidate is None:
                pass

            else:
                print("Peculiar Case which I did not considered")
                raise Exception

    print("Finished of scanning all the point")
    return rest_point_list


class TrackAnalyzer:
    """
    The TrackAnalyzer class is responsible for analyzing raw track data. It smooths the track data, performs analysis,
    and identifies rest points.

    :param input_raw_track_object: The raw track data to be analyzed.
    """

    def __init__(self, input_raw_track_object):
        """
        Initializes the TrackAnalyzer object with the input raw track data.

        :param input_raw_track_object: The raw track data to be analyzed.
        :type input_raw_track_object: RawTrackObject
        """
        if not input_raw_track_object.get_main_tracks().get_main_tracks_points_list():
            raise ValueError("Input track object is empty.")

        input_raw_track_point_list = input_raw_track_object.get_main_tracks().get_main_tracks_points_list()
        smooth_track_list = smoothing_tracks(input_raw_track_point_list)

        self._analyzed_tracks_object = do_analyzing(smooth_track_list)
        self._analyzed_tracks_object.set_waypoint_list(input_raw_track_object.get_waypoint_list())
        self._analyzed_tracks_object.set_rest_point_list(
            find_rest_point(self._analyzed_tracks_object.get_main_tracks().get_main_tracks_points_list())
        )

    def get_main_track(self):
        """
        Returns the main track of the analyzed track object.

        :return: The main track of the analyzed track object.
        :rtype: MainTracks
        """
        return self._analyzed_tracks_object.get_main_tracks()

    def get_main_track_list(self):
        """
        Returns the main track list of the analyzed track object.

        :return: The main track list of the analyzed track object.
        :rtype: List[MainTrack]
        """
        return self._analyzed_tracks_object.get_main_tracks()

    def get_waypoint_list(self):
        """
        Returns the waypoint list of the analyzed track object.

        :return: The waypoint list of the analyzed track object.
        :rtype: List[WayPoint]
        """
        return self._analyzed_tracks_object.get_waypoint_list()

    def get_rest_point_list(self):
        """
        Returns the rest point list of the analyzed track object.

        :return: The rest point list of the analyzed track object.
        :rtype: List[RestTrkPoint]
        """
        return self._analyzed_tracks_object.get_rest_point_list()
