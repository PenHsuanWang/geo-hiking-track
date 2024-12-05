# tests/test_image_parser.py

import os
import json
import tempfile
from unittest.mock import patch, MagicMock
from src.geoanalyzer.images.image_parser import ImageParser
from src.geo_objects.geo_points.image_points import ImagePoint
import datetime
from PIL import Image
import pytest

def create_mock_image_with_exif(gps_info=None, date_time=None):
    image = MagicMock()
    exif_data = {}

    if gps_info:
        exif_data[34853] = gps_info  # GPSInfo tag

    if date_time:
        exif_data[36867] = date_time  # DateTimeOriginal tag

    image._getexif.return_value = exif_data
    return image

def test_image_parser_load_image_url_mapping():
    """Test loading a valid image URL mapping."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        mapping_file = os.path.join(tmpdirname, 'picture_name_url_mapping.json')
        data = [
            {'filename': 'image1.jpg', 'image_url': 'http://example.com/image1.jpg'},
            {'filename': 'image2.jpg', 'image_url': 'http://example.com/image2.jpg'}
        ]
        with open(mapping_file, 'w') as f:
            json.dump(data, f)

        parser = ImageParser(tmpdirname)
        assert parser._image_url_mapping == {
            'image1.jpg': 'http://example.com/image1.jpg',
            'image2.jpg': 'http://example.com/image2.jpg'
        }

def test_image_parser_load_image_url_mapping_invalid_json():
    """Test handling of an invalid JSON mapping file."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        mapping_file = os.path.join(tmpdirname, 'picture_name_url_mapping.json')
        with open(mapping_file, 'w') as f:
            f.write('Invalid JSON')

        parser = ImageParser(tmpdirname)
        # Since the parser handles the error internally, check that the mapping is empty
        assert parser._image_url_mapping == {}

def test_image_parser_load_image_url_mapping_missing_fields():
    """Test handling of a mapping file with missing fields."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        mapping_file = os.path.join(tmpdirname, 'picture_name_url_mapping.json')
        data = [
            {'filename': 'image1.jpg'},
            {'image_url': 'http://example.com/image2.jpg'}
        ]
        with open(mapping_file, 'w') as f:
            json.dump(data, f)

        parser = ImageParser(tmpdirname)
        # Should skip invalid entries
        assert parser._image_url_mapping == {}

def test_image_parser_parse_images():
    """Test parsing images with valid EXIF data."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Create mock images
        image_path = os.path.join(tmpdirname, 'image1.jpg')
        with open(image_path, 'w') as f:
            f.write('test')

        # Mock os.walk to return the temp directory
        with patch('os.walk') as mock_walk:
            mock_walk.return_value = [(tmpdirname, [], ['image1.jpg'])]

            # Mock Image.open and the GPS extraction
            with patch('PIL.Image.open') as mock_open:
                gps_info = {
                    1: 'N',  # GPSLatitudeRef
                    2: ((37, 1), (0, 1), (0, 1)),  # GPSLatitude
                    3: 'W',  # GPSLongitudeRef
                    4: ((122, 1), (0, 1), (0, 1)),  # GPSLongitude
                    6: (100, 1)  # GPSAltitude
                }
                date_time = '2023:10:01 12:00:00'
                mock_image = create_mock_image_with_exif(gps_info=gps_info, date_time=date_time)
                mock_open.return_value = mock_image

                parser = ImageParser(tmpdirname)
                image_points = parser.get_image_points()
                assert len(image_points) == 1
                image_point = image_points[0]
                assert image_point.lat == 37.0
                assert image_point.lon == -122.0
                assert image_point.elev == 100.0
                assert image_point.time == datetime.datetime(2023, 10, 1, 12, 0, 0)

def test_image_parser_parse_images_no_exif():
    """Test handling of images without EXIF data."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        image_path = os.path.join(tmpdirname, 'image_no_exif.jpg')
        with open(image_path, 'w') as f:
            f.write('test')

        with patch('os.walk') as mock_walk:
            mock_walk.return_value = [(tmpdirname, [], ['image_no_exif.jpg'])]

            with patch('PIL.Image.open') as mock_open:
                mock_image = MagicMock()
                mock_image._getexif.return_value = None
                mock_open.return_value = mock_image

                parser = ImageParser(tmpdirname)
                image_points = parser.get_image_points()
                assert len(image_points) == 0
                _, _, skipped_no_gps, _ = parser.get_summary()
                assert skipped_no_gps == 1

def test_image_parser_parse_images_corrupted_exif():
    """Test handling of images with corrupted EXIF data."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        image_path = os.path.join(tmpdirname, 'image_corrupted_exif.jpg')
        with open(image_path, 'w') as f:
            f.write('test')

        with patch('os.walk') as mock_walk:
            mock_walk.return_value = [(tmpdirname, [], ['image_corrupted_exif.jpg'])]

            with patch('PIL.Image.open') as mock_open:
                mock_image = MagicMock()
                mock_image._getexif.side_effect = Exception('Corrupted EXIF')
                mock_open.return_value = mock_image

                parser = ImageParser(tmpdirname)
                image_points = parser.get_image_points()
                assert len(image_points) == 0
                assert len(parser._errors) == 1

def test_image_parser_parse_images_invalid_gps_data():
    """Test handling of images with invalid GPS data."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        image_path = os.path.join(tmpdirname, 'image_invalid_gps.jpg')
        with open(image_path, 'w') as f:
            f.write('test')

        with patch('os.walk') as mock_walk:
            mock_walk.return_value = [(tmpdirname, [], ['image_invalid_gps.jpg'])]

            with patch('PIL.Image.open') as mock_open:
                gps_info = {
                    1: 'N',  # GPSLatitudeRef
                    2: 'invalid_data',  # GPSLatitude
                    3: 'W',  # GPSLongitudeRef
                    4: 'invalid_data',  # GPSLongitude
                }
                date_time = '2023:10:01 12:00:00'
                mock_image = create_mock_image_with_exif(gps_info=gps_info, date_time=date_time)
                mock_open.return_value = mock_image

                parser = ImageParser(tmpdirname)
                image_points = parser.get_image_points()
                assert len(image_points) == 0
                _, _, skipped_no_gps, _ = parser.get_summary()
                assert skipped_no_gps == 1

def test_image_parser_non_image_files_with_jpg_extension():
    """Test handling of non-image files with .jpg extension."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        invalid_image_path = os.path.join(tmpdirname, 'invalid_image.jpg')
        with open(invalid_image_path, 'w') as f:
            f.write('not an image')

        with patch('os.walk') as mock_walk:
            mock_walk.return_value = [(tmpdirname, [], ['invalid_image.jpg'])]

        with patch('PIL.Image.open', side_effect=OSError('Cannot identify image file')):
            parser = ImageParser(tmpdirname)
            image_points = parser.get_image_points()
            assert len(image_points) == 0
            assert len(parser._errors) == 1

def test_image_parser_images_in_nested_directories():
    """Test parsing images in nested directories."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        nested_dir = os.path.join(tmpdirname, 'nested')
        os.makedirs(nested_dir)
        image_path = os.path.join(nested_dir, 'image1.jpg')
        with open(image_path, 'w') as f:
            f.write('test')

        with patch('os.walk') as mock_walk:
            mock_walk.return_value = [
                (tmpdirname, ['nested'], []),
                (nested_dir, [], ['image1.jpg'])
            ]

            with patch('PIL.Image.open') as mock_open:
                gps_info = {
                    1: 'N',  # GPSLatitudeRef
                    2: ((37, 1), (0, 1), (0, 1)),  # GPSLatitude
                    3: 'W',  # GPSLongitudeRef
                    4: ((122, 1), (0, 1), (0, 1)),  # GPSLongitude
                }
                date_time = '2023:10:01 12:00:00'
                mock_image = create_mock_image_with_exif(gps_info=gps_info, date_time=date_time)
                mock_open.return_value = mock_image

                parser = ImageParser(tmpdirname)
                image_points = parser.get_image_points()
                assert len(image_points) == 1

def test_image_parser_large_number_of_images():
    """Test parsing a large number of images."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        image_names = [f'image_{i}.jpg' for i in range(1000)]
        for image_name in image_names:
            image_path = os.path.join(tmpdirname, image_name)
            with open(image_path, 'w') as f:
                f.write('test')

        with patch('os.walk') as mock_walk:
            mock_walk.return_value = [(tmpdirname, [], image_names)]

            with patch('PIL.Image.open') as mock_open:
                gps_info = {
                    1: 'N',
                    2: ((37, 1), (0, 1), (0, 1)),
                    3: 'W',
                    4: ((122, 1), (0, 1), (0, 1)),
                }
                date_time = '2023:10:01 12:00:00'
                mock_image = create_mock_image_with_exif(gps_info=gps_info, date_time=date_time)
                mock_open.return_value = mock_image

                parser = ImageParser(tmpdirname)
                image_points = parser.get_image_points()
                assert len(image_points) == 1000

def test_image_parser_images_with_missing_date_time():
    """Test handling of images missing date/time EXIF data."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        image_path = os.path.join(tmpdirname, 'image_missing_time.jpg')
        with open(image_path, 'w') as f:
            f.write('test')

        with patch('os.walk') as mock_walk:
            mock_walk.return_value = [(tmpdirname, [], ['image_missing_time.jpg'])]

            with patch('PIL.Image.open') as mock_open:
                gps_info = {
                    1: 'N',
                    2: ((37, 1), (0, 1), (0, 1)),
                    3: 'W',
                    4: ((122, 1), (0, 1), (0, 1)),
                }
                mock_image = create_mock_image_with_exif(gps_info=gps_info)
                mock_open.return_value = mock_image

                parser = ImageParser(tmpdirname)
                image_points = parser.get_image_points()
                assert len(image_points) == 1
                image_point = image_points[0]
                assert image_point.time is None

def test_image_parser_images_with_invalid_date_time_format():
    """Test handling of images with invalid date/time formats."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        image_path = os.path.join(tmpdirname, 'image_invalid_time.jpg')
        with open(image_path, 'w') as f:
            f.write('test')

        with patch('os.walk') as mock_walk:
            mock_walk.return_value = [(tmpdirname, [], ['image_invalid_time.jpg'])]

            with patch('PIL.Image.open') as mock_open:
                gps_info = {
                    1: 'N',
                    2: ((37, 1), (0, 1), (0, 1)),
                    3: 'W',
                    4: ((122, 1), (0, 1), (0, 1)),
                }
                date_time = 'invalid_date_time'
                mock_image = create_mock_image_with_exif(gps_info=gps_info, date_time=date_time)
                mock_open.return_value = mock_image

                parser = ImageParser(tmpdirname)
                image_points = parser.get_image_points()
                # Should handle invalid date time gracefully
                assert len(image_points) == 1
                image_point = image_points[0]
                assert image_point.time is None

def test_image_parser_mapping_file_with_duplicates():
    """Test handling of duplicate entries in the mapping file."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        mapping_file = os.path.join(tmpdirname, 'picture_name_url_mapping.json')
        data = [
            {'filename': 'image1.jpg', 'image_url': 'http://example.com/image1.jpg'},
            {'filename': 'image1.jpg', 'image_url': 'http://example.com/duplicate.jpg'}
        ]
        with open(mapping_file, 'w') as f:
            json.dump(data, f)

        parser = ImageParser(tmpdirname)
        # The last occurrence should overwrite previous ones
        assert parser._image_url_mapping == {
            'image1.jpg': 'http://example.com/duplicate.jpg'
        }

def test_image_parser_large_image_files():
    """Test handling of large image files."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        image_path = os.path.join(tmpdirname, 'large_image.jpg')
        with open(image_path, 'wb') as f:
            f.seek((1024 * 1024 * 10) - 1)  # 10 MB file
            f.write(b'\0')

        with patch('os.walk') as mock_walk:
            mock_walk.return_value = [(tmpdirname, [], ['large_image.jpg'])]

            with patch('PIL.Image.open') as mock_open:
                gps_info = {
                    1: 'N',
                    2: ((37, 1), (0, 1), (0, 1)),
                    3: 'W',
                    4: ((122, 1), (0, 1), (0, 1)),
                }
                date_time = '2023:10:01 12:00:00'
                mock_image = create_mock_image_with_exif(gps_info=gps_info, date_time=date_time)
                mock_open.return_value = mock_image

                parser = ImageParser(tmpdirname)
                image_points = parser.get_image_points()
                assert len(image_points) == 1