# tests/test_image_point.py

import datetime
import pytest
from src.geo_objects.geo_points.image_points import ImagePoint

def test_image_point_initialization_all_params():
    """Test initialization with all parameters provided."""
    file_name = 'test_image.jpg'
    time = datetime.datetime(2023, 10, 1, 12, 0, 0)
    lat = 37.7749
    lon = -122.4194
    elev = 15.5
    image_url = 'http://example.com/image.jpg'
    additional_info = 'Test image'

    image_point = ImagePoint(
        file_name=file_name,
        time=time,
        lat=lat,
        lon=lon,
        elev=elev,
        image_url=image_url,
        additional_info=additional_info
    )

    assert image_point.file_name == file_name
    assert image_point.time == time
    assert image_point.lat == lat
    assert image_point.lon == lon
    assert image_point.elev == elev
    assert image_point.image_url == image_url
    assert image_point.additional_info == additional_info

def test_image_point_initialization_missing_optional_params():
    """Test initialization with optional parameters missing."""
    file_name = 'test_image.jpg'

    image_point = ImagePoint(
        file_name=file_name,
        time=None,
        lat=None,
        lon=None,
        elev=None,
        image_url=None,
        additional_info=None
    )

    assert image_point.file_name == file_name
    assert image_point.time is None
    assert image_point.lat is None
    assert image_point.lon is None
    assert image_point.elev is None
    assert image_point.image_url is None
    assert image_point.additional_info is None

def test_image_point_initialization_empty_file_name():
    """Test initialization with an empty file name."""
    file_name = ''
    with pytest.raises(ValueError):
        ImagePoint(
            file_name=file_name,
            time=None,
            lat=None,
            lon=None,
            elev=None,
            image_url=None,
            additional_info=None
        )

def test_image_point_initialization_none_file_name():
    """Test initialization with a None file name."""
    file_name = None
    with pytest.raises(TypeError):
        ImagePoint(
            file_name=file_name,
            time=None,
            lat=None,
            lon=None,
            elev=None,
            image_url=None,
            additional_info=None
        )

def test_image_point_get_note_with_additional_info():
    """Test get_note method when additional_info is provided."""
    image_point = ImagePoint(
        file_name='test_image.jpg',
        time=None,
        lat=None,
        lon=None,
        elev=None,
        image_url=None,
        additional_info='Additional Info'
    )
    assert image_point.get_note() == 'Additional Info'

def test_image_point_get_note_without_additional_info():
    """Test get_note method when additional_info is not provided."""
    image_point = ImagePoint(
        file_name='test_image.jpg',
        time=None,
        lat=None,
        lon=None,
        elev=None,
        image_url=None,
        additional_info=None
    )
    assert image_point.get_note() == 'test_image.jpg'

def test_image_point_get_note_empty_additional_info():
    """Test get_note method when additional_info is an empty string."""
    image_point = ImagePoint(
        file_name='test_image.jpg',
        time=None,
        lat=None,
        lon=None,
        elev=None,
        image_url=None,
        additional_info=''
    )
    assert image_point.get_note() == 'test_image.jpg'

def test_image_point_get_popup_info_all_fields():
    """Test get_popup_info method with all fields provided."""
    image_point = ImagePoint(
        file_name='test_image.jpg',
        time=datetime.datetime(2023, 10, 1, 12, 0, 0),
        lat=37.7749,
        lon=-122.4194,
        elev=15.5,
        image_url='http://example.com/image.jpg',
        additional_info='Test image'
    )

    popup_info = image_point.get_popup_info()
    assert '<strong style="font-size: 1.5rem; margin-bottom: 10px;">Image Details</strong><br>' in popup_info
    assert 'Time: 12:00:00' in popup_info
    assert 'Filename: test_image.jpg' in popup_info
    assert 'Elevation: 15.5 M' in popup_info
    assert 'Info: Test image' in popup_info
    assert '<img src="http://example.com/image.jpg"' in popup_info

def test_image_point_get_popup_info_missing_optional_fields():
    """Test get_popup_info method with optional fields missing."""
    image_point = ImagePoint(
        file_name='test_image.jpg',
        time=None,
        lat=None,
        lon=None,
        elev=None,
        image_url=None,
        additional_info=None
    )

    popup_info = image_point.get_popup_info()
    assert 'Filename: test_image.jpg' in popup_info
    assert 'Time:' not in popup_info
    assert 'Elevation:' not in popup_info
    assert 'Info:' not in popup_info
    assert '<img' not in popup_info

def test_image_point_get_popup_info_special_characters():
    """Test get_popup_info method with special characters and unicode."""
    image_point = ImagePoint(
        file_name='test_image_测试.jpg',
        time=datetime.datetime(2023, 10, 1, 12, 0, 0),
        lat=0.0,
        lon=0.0,
        elev=-10.0,
        image_url='http://example.com/image_测试.jpg',
        additional_info='特殊字符信息'
    )

    popup_info = image_point.get_popup_info()
    assert 'Filename: test_image_测试.jpg' in popup_info
    assert 'Elevation: -10.0 M' in popup_info
    assert 'Info: 特殊字符信息' in popup_info
    assert '<img src="http://example.com/image_测试.jpg"' in popup_info

def test_image_point_with_zero_elevation():
    """Test handling of zero elevation."""
    image_point = ImagePoint(
        file_name='sea_level.jpg',
        time=datetime.datetime(2023, 10, 1, 12, 0, 0),
        lat=0.0,
        lon=0.0,
        elev=0.0,
        image_url='http://example.com/sea_level.jpg',
        additional_info=None
    )

    assert image_point.elev == 0.0
    popup_info = image_point.get_popup_info()
    assert 'Elevation: 0.0 M' in popup_info

def test_image_point_with_invalid_image_url():
    """Test handling of an invalid image URL."""
    image_point = ImagePoint(
        file_name='broken_link.jpg',
        time=datetime.datetime(2023, 10, 1, 12, 0, 0),
        lat=0.0,
        lon=0.0,
        elev=10.0,
        image_url='invalid_url',
        additional_info=None
    )

    popup_info = image_point.get_popup_info()
    assert '<img src="invalid_url"' in popup_info

def test_image_point_with_extreme_lat_lon():
    """Test handling of extreme latitude and longitude values."""
    image_point = ImagePoint(
        file_name='north_pole.jpg',
        time=datetime.datetime(2023, 10, 1, 12, 0, 0),
        lat=90.0,
        lon=135.0,
        elev=0.0,
        image_url='http://example.com/north_pole.jpg',
        additional_info=None
    )

    assert image_point.lat == 90.0
    assert image_point.lon == 135.0

def test_image_point_with_invalid_lat_lon():
    """Test initialization with invalid latitude and longitude values."""
    with pytest.raises(ValueError):
        ImagePoint(
            file_name='invalid_coords.jpg',
            time=datetime.datetime(2023, 10, 1, 12, 0, 0),
            lat=100.0,  # Invalid latitude
            lon=200.0,  # Invalid longitude
            elev=0.0,
            image_url='http://example.com/invalid_coords.jpg',
            additional_info=None
        )