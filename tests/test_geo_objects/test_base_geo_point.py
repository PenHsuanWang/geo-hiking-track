import pytest
from datetime import datetime
from src.geo_objects.geo_points.basic_point import BasicPoint  # replace 'your_module' with the actual module name where BasicPoint is defined


# Test the BasicPoint class
def test_basic_point_creation():
    point = BasicPoint(datetime(2023, 8, 31, 12, 34, 56), 37.7749, -122.4194, 15.0)

    # Test if properties return the correct values
    assert point.time == datetime(2023, 8, 31, 12, 34, 56)
    assert point.lat == 37.7749
    assert point.lon == -122.4194
    assert point.elev == 15.0
    assert point.is_empty == False


# Test the BasicPoint class with None
def test_basic_point_with_none():
    point = BasicPoint(None, None, None, None)

    # Test if properties return the correct values
    assert point.time is None
    assert point.lat is None
    assert point.lon is None
    assert point.elev is None
    assert point.is_empty == True


# Test if we can't set the properties (they should be read-only)
def test_basic_point_properties_are_read_only():
    point = BasicPoint(datetime(2023, 8, 31, 12, 34, 56), 37.7749, -122.4194, 15.0)

    with pytest.raises(AttributeError):
        point.time = datetime(2022, 8, 31, 12, 34, 56)

    with pytest.raises(AttributeError):
        point.lat = 10.0

    with pytest.raises(AttributeError):
        point.lon = 10.0

    with pytest.raises(AttributeError):
        point.elev = 10.0

    with pytest.raises(AttributeError):
        point.is_empty = True
