
# test base function and all properties getter is fine

import pytest
from src.geo_objects.geo_points.raw_geo_points import RawTrkPoint, WayPoint


def test_raw_geo_point_creation_and_getter():

    raw_point = RawTrkPoint(
        time="2023-08-31T12:34:56Z",
        lat=37.7749,
        lon=-122.4194,
        elev=15.0
    )

    assert raw_point.time == "2023-08-31T12:34:56Z"
    assert raw_point.lat == 37.7749
    assert raw_point.lon == -122.4194
    assert raw_point.elev == 15.0


def test_chain_raw_geo_point_to_list_and_iterate():

    raw_point = RawTrkPoint(
        time="2023-08-31T12:34:56Z",
        lat=37.7749,
        lon=-122.4194,
        elev=15.0
    )

    raw_point_list = []
    raw_point_list.append(raw_point)

    for point in raw_point_list:
        assert point.time == "2023-08-31T12:34:56Z"
        assert point.lat == 37.7749
        assert point.lon == -122.4194
        assert point.elev == 15.0



