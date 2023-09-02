import pytest
from datetime import datetime, timedelta
from src.geoanalyzer.tracks.track_analyzer import sum_delta_between_every_element, smoothing_tracks, do_analyzing, find_rest_point, \
    TrackAnalyzer
from unittest.mock import Mock


# Testing sum_delta_between_every_element
def test_sum_delta_between_every_element():
    assert sum_delta_between_every_element([1, 2, 3]) == 2
    assert sum_delta_between_every_element([1.0, 2.0, 3.0]) == 2.0
    assert sum_delta_between_every_element([datetime(2023, 8, 28, 1, 0), datetime(2023, 8, 28, 1, 1)]) == 60

    with pytest.raises(TypeError):
        sum_delta_between_every_element(['a', 'b'])


# Mocking classes for other test functions
# class MockRawTrkPoint:
#     def __init__(self, time, lat, lon, elev):
#         self.time = time
#         self.lat = lat
#         self.lon = lon
#         self.elev = elev
#
#     def get_point_time(self):
#         return self.time
#
#     def get_lat(self):
#         return self.lat
#
#     def get_lon(self):
#         return self.lon
#
#     def get_elev(self):
#         return self.elev


# Testing smoothing_tracks
# def test_smoothing_tracks():
#     input_list = [MockRawTrkPoint(datetime(2023, 8, 28, 1, i, 0), 37 + i, -122 + i, 100 + i) for i in range(6)]
#     output = smoothing_tracks(input_list)
#     assert len(output) == 1  # Based on how your function is written, the length should be 1

#
# # Testing do_analyzing
# def test_do_analyzing():
#     input_list = [MockRawTrkPoint(datetime(2023, 8, 28, 1, i, 0), 37 + i, -122 + i, 100 + i) for i in range(4)]
#     output = do_analyzing(input_list)
#     # Write assertions based on what you expect the output to contain
#
#
# # Testing find_rest_point
# def test_find_rest_point():
#     input_list = [MockRawTrkPoint(datetime(2023, 8, 28, 1, i, 0), 37 + i, -122 + i, 100 + i) for i in range(6)]
#     output = find_rest_point(input_list)
#     # Write assertions based on what you expect the output to contain
#
#
# # Testing TrackAnalyzer class
# def test_TrackAnalyzer():
#     mock_raw_track_object = Mock()
#     mock_raw_track_object.get_main_tracks().get_main_tracks_points_list.return_value = [
#         MockRawTrkPoint(datetime(2023, 8, 28, 1, i, 0), 37 + i, -122 + i, 100 + i) for i in range(6)]
#
#     analyzer = TrackAnalyzer(mock_raw_track_object)
#     expected_main_track = # whatever you expect this to be
#     expected_main_track_list = # whatever you expect this to be
#     expected_waypoint_list = # whatever you expect this to be
#     expected_rest_point_list = # whatever you expect this to be
#
#     assert analyzer.get_main_track() == expected_main_track
#     assert analyzer.get_main_track_list() == expected_main_track_list
#     assert analyzer.get_waypoint_list() == expected_waypoint_list
#     assert analyzer.get_rest_point_list() == expected_rest_point_list
