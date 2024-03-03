import pytest
from datetime import datetime, timedelta
from src.geo_objects.geo_points.raw_geo_points import RawTrkPoint
from src.geo_objects.geo_points.analyzed_geo_points import AnalyzedTrkPoint
from src.geo_objects.geo_tracks.raw_geo_tracks import RawTrackObject
from src.geoanalyzer.tracks.track_analyzer import TrackAnalyzer, smoothing_tracks, find_rest_point


class MockTrackObject(RawTrackObject):
    def __init__(self, points):
        super().__init__()
        for point in points:
            self.add_track_point(point)


def generate_mock_track_points(num_points, start_lat, start_lon, lat_increment, lon_increment, start_time, time_increment_sec):
    points = []
    for i in range(num_points):
        lat = start_lat + (i * lat_increment)
        lon = start_lon + (i * lon_increment)
        time = start_time + timedelta(seconds=i * time_increment_sec)
        elev = 100  # Assuming a constant elevation for simplicity
        points.append(RawTrkPoint(time, lat, lon, elev))
    return points


@pytest.fixture
def mock_track_points():
    start_time = datetime.now()
    return generate_mock_track_points(10, 0.0, 0.0, 0.001, 0.001, start_time, 60)


@pytest.fixture
def mock_analyzed_track_points():
    start_time = datetime.now()
    # Assuming an arbitrary speed calculation fitting the scenario
    return generate_mock_analyzed_points(10, start_time, 60, 0.0, 0.0, 0.0001, 0.0001, 100, 0.1, 0.1, 0, 1)

def generate_mock_analyzed_points(num_points, start_time, time_increment_sec, start_lat, start_lon, lat_increment, lon_increment, elev, dx, dy, dz, dt):
    points = []
    for i in range(num_points):
        time = start_time + timedelta(seconds=i * time_increment_sec)
        lat = start_lat + (i * lat_increment)
        lon = start_lon + (i * lon_increment)
        point = AnalyzedTrkPoint(time, lat, lon, elev, dx, dy, dz, dt)
        points.append(point)
    return points

def test_smoothing_tracks(mock_track_points):
    smoothed_points = smoothing_tracks(mock_track_points)
    assert len(smoothed_points) < len(mock_track_points), "Smoothing should reduce the number of points."


def test_analyzing_tracks(mock_track_points):
    mock_track_object = MockTrackObject(mock_track_points)
    analyzer = TrackAnalyzer(mock_track_object)
    analyzed_tracks = analyzer.get_main_track()
    assert len(analyzed_tracks.get_main_tracks_points_list()) > 0, "No tracks were analyzed."


def test_find_rest_point(mock_analyzed_track_points):
    rest_points = find_rest_point(mock_analyzed_track_points)
    assert isinstance(rest_points, list), "Expected a list of rest points."
    # Add specific assertions based on expected rest points characteristics


@pytest.mark.xfail(reason="TrackAnalyzer not designed to handle empty track object input.")
def test_error_handling_with_empty_input():
    mock_track_points = []  # Empty list of points
    mock_track_object = MockTrackObject(mock_track_points)
    with pytest.raises(ValueError):
        TrackAnalyzer(mock_track_object)
