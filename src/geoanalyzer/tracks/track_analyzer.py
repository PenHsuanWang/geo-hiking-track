import datetime
import math
from src.geoanalyzer.tracks.track_objects import RawTrkPoint, RawTracks, AnalyzedTrkPoint, AnalyzedTrackObject, TrackPointVector, RestTrkPoint, RestTrkPointCandidate, SeedRestPoint


def sum_delta_between_every_element(input_list):
    tot_delta = 0
    for i in range(len(input_list) - 1):

        delta_element = input_list[i + 1] - input_list[i]

        if isinstance(delta_element, (float, int)):
            tot_delta += delta_element
        elif isinstance(delta_element, datetime.timedelta):
            tot_delta += delta_element.seconds
        else:
            raise TypeError

    return tot_delta


def smoothing_tracks(input_track_point_list) -> list:
    def average(input_list):
        return sum(input_list) / len(input_list)

    raw_track_point_list = input_track_point_list
    averaged_tracks_list = []

    for i in range(len(raw_track_point_list) - 5):
        track_point_list_segment = raw_track_point_list[i:i+5]

        track_point_time = track_point_list_segment[2].get_point_time()

        list_segment_lat = list(map(lambda x: x.get_lat(), track_point_list_segment))
        list_segment_lon = list(map(lambda x: x.get_lon(), track_point_list_segment))
        list_segment_ele = list(map(lambda x: x.get_elev(), track_point_list_segment))

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

        list_segment_lat = list(map(lambda x: x.get_lat(), track_point_list_segment))
        list_segment_lon = list(map(lambda x: x.get_lon(), track_point_list_segment))
        list_segment_elev = list(map(lambda x: x.get_elev(), track_point_list_segment))
        list_segment_time = list(map(lambda x: x.get_point_time(), track_point_list_segment))

        # 1 degree is 101751 meters in Lon direction
        delta_x = sum_delta_between_every_element(list_segment_lon)/(len(list_segment_lon)-1) * 101751
        # 1 degree is 110757 meters in Lat direction
        delta_y = sum_delta_between_every_element(list_segment_lat)/(len(list_segment_lat)-1) * 110757
        delta_z = sum_delta_between_every_element(list_segment_elev)/(len(list_segment_elev)-1)
        delta_t = sum_delta_between_every_element(list_segment_time)/(len(list_segment_time)-1)

        target_analyzing_track_object.add_track_point(
            AnalyzedTrkPoint(
                track_point_list_segment[1].get_point_time(),
                track_point_list_segment[1].get_lat(),
                track_point_list_segment[1].get_lon(),
                track_point_list_segment[1].get_elev(),
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
            the point speed X and speed Y < 0.1 can be treat as first RestPointCandidate.
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

    rest_point_list = []

    found_seed = False
    seed_rest_point = None

    rest_point_candidate = None
    rest_candidate_list_tot_delta_x = 0
    rest_candidate_list_tot_delta_y = 0

    for i_track_point in input_list:

        if i_track_point.get_speed_xy() < 0.1:

            #=======================#
            # If SeedPoint is found #
            #=======================#
            if found_seed:
                continue

            #==============================#
            # SeedPoint is not yet found ! #
            #==============================#
            if rest_point_candidate is None:
                rest_point_candidate = RestTrkPointCandidate(i_track_point)

            elif isinstance(rest_point_candidate, RestTrkPointCandidate):

                if rest_point_candidate.get_tot_delta_x() > 20 or rest_point_candidate.get_tot_delta_y() > 20:
                    #===========================================#
                    # False condition, purge RestPointCandidate #
                    #===========================================#
                    del rest_point_candidate
                    rest_point_candidate = None  # rest rest_point_candidate
                    continue

                if rest_point_candidate.calculate_time_spend(i_track_point) > 60:
                    #====================================================#
                    # True condition, go to flush this candidate as seed #
                    #====================================================#
                    if not found_seed:
                        found_seed = True
                        seed_rest_point = rest_point_candidate.flush_to_rest_seed()
                        del rest_point_candidate
                        rest_point_candidate = None
                    else:
                        print("Peculiar case happen, RestPointCandidate and SeedRestPoint should not exist at the same time")
                        raise Exception

                elif rest_point_candidate.calculate_time_spend(i_track_point) <= 60:
                    #==============================#
                    # Add new rest point candidate #
                    #==============================#
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
                x_shift = math.fabs((i_track_point.get_lon()-seed_rest_point.get_lon())*110751)
                y_shift = math.fabs((i_track_point.get_lat()-seed_rest_point.get_lat())*110757)
                if x_shift < 20 and y_shift < 20:
                    continue
                else:
                    # Stop to collect resting point,
                    # flush and delete all collecting object

                    if len(rest_point_list) > 0 and (seed_rest_point.get_start_time() - rest_point_list[-1].get_end_time()).seconds < 120:
                        #============================================================================================#
                        # If the seed rest point's start time is too close to previous rest point's end time         #
                        # The new seeding point maybe the same rest point, Do not append this seed as new rest point #
                        # Update the last rest point in list's setting the end time to current point time            #
                        #============================================================================================#
                        rest_point_list[-1].update_end_time(i_track_point.get_point_time())

                    else:
                        #==================================================================================#
                        # Check the SeedRestPoint start time is greater than previous appended rest point! #
                        #==================================================================================#
                        rest_point_confirmed = RestTrkPoint(
                            seed_rest_point.get_start_time(),
                            seed_rest_point.get_lat(),
                            seed_rest_point.get_lon(),
                            seed_rest_point.get_elev(),
                            seed_rest_point.get_start_time(),
                            i_track_point.get_point_time()
                        )

                        rest_point_list.append(rest_point_confirmed)

                    #=======================#
                    # Reset rest point seed #
                    #=======================#
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
                continue

            else:
                print("Peculiar Case which I did not considered")
                raise Exception

    print("Finished of scanning all the point")
    return rest_point_list


class TrackAnalyzer:

    def __init__(self, input_raw_track_object):

        input_raw_track_point_list = input_raw_track_object.get_main_tracks().get_main_tracks_points_list()
        smooth_track_list = smoothing_tracks(input_raw_track_point_list)

        self._analyzed_tracks_object = do_analyzing(smooth_track_list)
        self._analyzed_tracks_object.set_waypoint_list(input_raw_track_object.get_waypoint_list())
        self._analyzed_tracks_object.set_rest_point_list(
            find_rest_point(self._analyzed_tracks_object.get_main_tracks().get_main_tracks_points_list())
        )

    def get_main_track(self):
        return self._analyzed_tracks_object.get_main_tracks()

    def get_main_track_list(self):
        return self._analyzed_tracks_object.get_main_tracks()

    def get_waypoint_list(self):
        return self._analyzed_tracks_object.get_waypoint_list()

    def get_rest_point_list(self):
        return self._analyzed_tracks_object.get_rest_point_list()

