import datetime
import time

from geoanalyzer.tracks import gps_parser
from geoanalyzer.tracks import track_analyzer
from geoanalyzer.tracks.track_analyzer import TrackAnalyzer


def test_smoothing_tracks():
    gpx_parser = gps_parser.GpxParser("../../gpx_file/2021-08-29-06.21.16.gpx")

    track_object = gpx_parser.get_raw_track_object()
    raw_track_list = track_object.get_main_tracks().get_main_tracks_points_list()

    track_analyzer.smoothing_tracks(raw_track_list)

    assert True


def test_sum_delta_between_every_element():
    list_a = [1, 2, 3]
    list_b = [3, 2, 1]
    list_c = [3, 1, 2]

    time_a = datetime.datetime.now()
    time.sleep(1)
    time_b = datetime.datetime.now()
    list_time = [time_a, time_b]

    assert track_analyzer.sum_delta_between_every_element(list_a) == 2
    assert track_analyzer.sum_delta_between_every_element(list_b) == -2
    assert track_analyzer.sum_delta_between_every_element(list_c) == -1
    assert track_analyzer.sum_delta_between_every_element(list_time) == 1


def test_lambda_expression_get_track_point_time():
    gpx_parser = gps_parser.GpxParser("../../gpx_file/2021-08-29-06.21.16.gpx")

    track_object = gpx_parser.get_raw_track_object()
    raw_track_list = track_object.get_main_tracks().get_main_tracks_points_list()

    list_time = list(map(lambda x: x.get_point_time(), raw_track_list))

    #
    tot_time_delta = track_analyzer.sum_delta_between_every_element(list_time)
    print(tot_time_delta)

    assert True


def test_do_analyzing():
    gpx_parser = gps_parser.GpxParser("../../gpx_file/2021-08-29-06.21.16.gpx")

    track_object = gpx_parser.get_raw_track_object()
    raw_track_list = track_object.get_main_tracks().get_main_tracks_points_list()

    analyzed_track_object = track_analyzer.do_analyzing(raw_track_list)

    track_point_list = analyzed_track_object.get_main_tracks().get_main_tracks_points_list()

    # print(len(track_point_list))
    for i in track_point_list:
        print(i.get_point_time())

    assert True


def test_find_rest_point():
    gpx_parser = gps_parser.GpxParser("../../gpx_file/2021-08-29-06.21.16.gpx")

    track_object = gpx_parser.get_raw_track_object()
    raw_track_list = track_object.get_main_tracks().get_main_tracks_points_list()

    analyzed_track_object = track_analyzer.do_analyzing(raw_track_list)

    track_point_list = analyzed_track_object.get_main_tracks().get_main_tracks_points_list()

    rest_point = track_analyzer.find_rest_point(track_point_list)

    for i in rest_point:
        print(i.get_start_time(), i.get_end_time())

    assert True
