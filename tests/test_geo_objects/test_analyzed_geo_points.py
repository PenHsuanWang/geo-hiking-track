import pytest
from datetime import datetime, timedelta
from src.geo_objects.geo_points.analyzed_geo_points import AnalyzedTrkPoint, RestTrkPoint, RestTrkPointCandidate, \
    SeedRestPoint  # Replace 'your_module' with the actual module name


# Tests for AnalyzedTrkPoint
def test_AnalyzedTrkPoint():
    point = AnalyzedTrkPoint(datetime.now(), 40.7128, -74.0060, 10, 1, 1, 1, 1)

    point.set_point_integral_dst(50)  # Newly added to cover set_point_integral_dst
    assert point.get_point_integral_dst() == 50  # Newly added to cover get_point_integral_dst

    assert point.get_delta_x() == 1
    assert point.get_delta_y() == 1
    assert point.get_delta_z() == 1
    assert point.get_delta_xy() == pytest.approx(1.4142, 0.0001)
    assert point.get_point_delta_time() == 1  # Newly added to cover get_point_delta_time
    assert point.get_speed_x() == 1
    assert point.get_speed_y() == 1
    assert point.get_speed_z() == 1
    assert point.get_speed_xy() == pytest.approx(1.4142, 0.0001)
    assert point.get_velocity_xy() == [1, 1]
    assert point.get_velocity_xyx() == [1, 1, 1]


# Tests for RestTrkPoint
def test_RestTrkPoint():
    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=5)
    rest_point = RestTrkPoint(start_time, 40.7128, -74.0060, 10, start_time, end_time)

    assert rest_point.get_start_time() == start_time
    assert rest_point.get_end_time() == end_time
    assert rest_point.get_rest_time_spend() == 5  # This should pass now

    # Newly added to cover update_start_time and update_end_time
    new_start_time = start_time - timedelta(minutes=2)
    new_end_time = end_time + timedelta(minutes=2)
    rest_point.update_start_time(new_start_time)
    rest_point.update_end_time(new_end_time)

    assert rest_point.get_start_time() == new_start_time
    assert rest_point.get_end_time() == new_end_time
    assert rest_point.get_rest_time_spend() == 9  # Changed from 5 to 9 due to updated times


# Tests for RestTrkPointCandidate
def test_RestTrkPointCandidate():
    point1 = AnalyzedTrkPoint(datetime.now(), 40.7128, -74.0060, 10, 1, 1, 1, 1)
    point2 = AnalyzedTrkPoint(datetime.now() + timedelta(seconds=1), 40.7129, -74.0061, 11, 1, 1, 1, 1)

    # Test initializing with invalid type
    with pytest.raises(TypeError):
        RestTrkPointCandidate("InvalidType")

    candidate = RestTrkPointCandidate(point1)
    assert candidate.get_point_count() == 1

    # Test adding candidate with invalid type
    with pytest.raises(TypeError):
        candidate.add_candidate("InvalidType")

    assert candidate.calculate_time_spend(point2) == 1

    tot_delta_x_before = candidate.get_tot_delta_x()
    candidate.add_candidate(point2)
    tot_delta_x_after = candidate.get_tot_delta_x()

    # Check that the total delta_x increased correctly
    assert tot_delta_x_after == tot_delta_x_before + point2.get_delta_x()
    # ... rest of your test cases


# Tests for SeedRestPoint
def test_SeedRestPoint():
    start_time = datetime.now()
    seed_point = SeedRestPoint(40.7128, -74.0060, 10, start_time)

    assert seed_point.lat == 40.7128  # changed get_lat() to lat property
    assert seed_point.lon == -74.0060  # changed get_lon() to lon property
    assert seed_point.elev == 10  # changed get_elev() to elev property
    assert seed_point.start_time == start_time  # changed get_start_time() to start_time property
