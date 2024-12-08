# tests/test_visualization/test_map_drawer.py

import folium
from src.visualizartion.map_drawer import FoliumMapDrawer
from src.geo_objects.geo_points.image_points import ImagePoint
from src.geo_objects.geo_points.analyzed_geo_points import RestTrkPoint
import datetime
import pytest


def test_map_drawer_initialization():
    """Test initialization with valid parameters."""
    drawer = FoliumMapDrawer(37.7749, -122.4194, zoom_start=12)
    assert isinstance(drawer.fmap, folium.Map)
    assert drawer.fmap.location == [37.7749, -122.4194]
    assert drawer.fmap.options['zoom'] == 12


def test_map_drawer_initialization_invalid_coordinates():
    """Test initialization with invalid coordinates."""
    with pytest.raises(ValueError):
        FoliumMapDrawer('invalid_lat', 'invalid_lon', zoom_start=12)


def test_map_drawer_initialization_with_map_names():
    """Test initialization with valid map_names."""
    map_tiles = ['OpenStreetMap', 'Stamen Terrain']
    map_attrs = ['Map data © OpenStreetMap contributors', 'Map tiles by Stamen Design']
    map_names = ['OSM Base', 'Stamen Terrain']

    drawer = FoliumMapDrawer(
        37.7749, -122.4194,
        zoom_start=12,
        map_tiles=map_tiles,
        map_attrs=map_attrs,
        map_names=map_names
    )

    # Verify that the map title is set correctly
    map_html = drawer.fmap.get_root().render()
    assert f"Map: {map_names[0]}" in map_html

    # Verify that LayerControl includes the map_names
    for name in map_names:
        assert name in map_html  # Ensure the names appear in the LayerControl section of the HTML


def test_map_drawer_initialization_with_default_map_names():
    """Test initialization without providing map_names (should default to map_tiles)."""
    map_tiles = ['OpenStreetMap', 'Stamen Terrain']
    map_attrs = ['Map data © OpenStreetMap contributors', 'Map tiles by Stamen Design']

    drawer = FoliumMapDrawer(
        37.7749, -122.4194,
        zoom_start=12,
        map_tiles=map_tiles,
        map_attrs=map_attrs
    )

    map_html = drawer.fmap.get_root().render()
    for tile in map_tiles:
        assert tile in map_html  # Ensure the default names (map_tiles) appear in LayerControl


def test_map_drawer_initialization_mismatched_map_names():
    """Test initialization with mismatched number of map_names (should raise ValueError)."""
    map_tiles = ['OpenStreetMap', 'Stamen Terrain']
    map_attrs = ['Map data © OpenStreetMap contributors', 'Map tiles by Stamen Design']
    map_names = ['OSM Base']  # Only one map_name provided

    with pytest.raises(ValueError, match="The number of map_tiles, map_attrs, and map_names must be the same."):
        FoliumMapDrawer(
            37.7749, -122.4194,
            zoom_start=12,
            map_tiles=map_tiles,
            map_attrs=map_attrs,
            map_names=map_names
        )


def test_map_drawer_add_multiple_tile_layers_with_map_names():
    """Test adding multiple tile layers with custom map_names."""
    map_tiles = ['OpenStreetMap', 'Stamen Terrain', 'Stamen Watercolor']
    map_attrs = [
        'Map data © OpenStreetMap contributors',
        'Map tiles by Stamen Design',
        'Map tiles by Stamen Design'
    ]
    map_names = ['OSM Base', 'Stamen Terrain', 'Stamen Watercolor']

    drawer = FoliumMapDrawer(
        37.7749, -122.4194,
        zoom_start=12,
        map_tiles=map_tiles,
        map_attrs=map_attrs,
        map_names=map_names
    )

    map_html = drawer.fmap.get_root().render()
    for name in map_names:
        assert name in map_html


def test_map_drawer_add_multiple_tile_layers_without_map_names():
    """Test adding multiple tile layers without providing map_names."""
    map_tiles = ['OpenStreetMap', 'Stamen Terrain', 'Stamen Watercolor']
    map_attrs = [
        'Map data © OpenStreetMap contributors',
        'Map tiles by Stamen Design',
        'Map tiles by Stamen Design'
    ]

    drawer = FoliumMapDrawer(
        37.7749, -122.4194,
        zoom_start=12,
        map_tiles=map_tiles,
        map_attrs=map_attrs
    )

    map_html = drawer.fmap.get_root().render()
    for tile in map_tiles:
        assert tile in map_html


def test_map_drawer_duplicate_map_names():
    """Test initialization with duplicate map_names."""
    map_tiles = ['OpenStreetMap', 'Stamen Terrain']
    map_attrs = ['Map data © OpenStreetMap contributors', 'Map tiles by Stamen Design']
    map_names = ['Duplicate Name', 'Duplicate Name']

    drawer = FoliumMapDrawer(
        37.7749, -122.4194,
        zoom_start=12,
        map_tiles=map_tiles,
        map_attrs=map_attrs,
        map_names=map_names
    )

    map_html = drawer.fmap.get_root().render()
    for name in map_names:
        assert name in map_html


def test_map_drawer_layer_control_presence():
    """Test that LayerControl is added to the map."""
    map_tiles = ['OpenStreetMap', 'Stamen Terrain']
    map_attrs = ['Map data © OpenStreetMap contributors', 'Map tiles by Stamen Design']
    map_names = ['OSM Base', 'Stamen Terrain']

    drawer = FoliumMapDrawer(
        37.7749, -122.4194,
        zoom_start=12,
        map_tiles=map_tiles,
        map_attrs=map_attrs,
        map_names=map_names
    )

    # Check for LayerControl in the map's children
    layer_controls = [
        child for child in drawer.fmap._children.values()
        if isinstance(child, folium.map.LayerControl)
    ]
    assert len(layer_controls) == 1


def test_map_drawer_save_with_map_names(tmp_path):
    """Test saving the map with multiple tile layers and map_names."""
    map_tiles = ['OpenStreetMap', 'Stamen Terrain']
    map_attrs = ['Map data © OpenStreetMap contributors', 'Map tiles by Stamen Design']
    map_names = ['OSM Base', 'Stamen Terrain']

    drawer = FoliumMapDrawer(
        37.7749, -122.4194,
        zoom_start=12,
        map_tiles=map_tiles,
        map_attrs=map_attrs,
        map_names=map_names
    )
    output_file = tmp_path / "test_map_with_names.html"
    drawer.save(str(output_file))

    assert output_file.exists()

    # Optionally, verify that the saved HTML contains the map title
    with open(output_file, 'r', encoding='utf-8') as f:
        map_html = f.read()
    assert f"Map: {map_names[0]}" in map_html

    # Verify that the layer names are present in the HTML
    for name in map_names:
        assert f'"{name}"' in map_html  # LayerControl uses JSON to define layers


# Existing test cases below...

def test_map_drawer_add_poly_line():
    """Test adding a valid polyline."""
    drawer = FoliumMapDrawer(0, 0)
    point_list = [[0, 0], [1, 1], [2, 2]]
    drawer.add_poly_line(point_list, weight=5, color='blue')

    polylines = [child for child in drawer.fmap._children.values() if isinstance(child, folium.vector_layers.PolyLine)]
    assert len(polylines) == 1


def test_map_drawer_add_poly_line_empty_list():
    """Test adding a polyline with an empty point list."""
    drawer = FoliumMapDrawer(0, 0)
    drawer.add_poly_line([], weight=5, color='blue')

    polylines = [child for child in drawer.fmap._children.values() if isinstance(child, folium.vector_layers.PolyLine)]
    assert len(polylines) == 0  # No PolyLine should be added


def test_map_drawer_add_poly_line_invalid_points():
    """Test adding a polyline with invalid points."""
    drawer = FoliumMapDrawer(0, 0)
    point_list = [[0, 0], ['invalid', 'point'], [2, 2]]
    with pytest.raises(ValueError):
        drawer.add_poly_line(point_list, weight=5, color='blue')


def test_map_drawer_draw_points_on_map_image_point():
    """Test drawing ImagePoint on the map."""
    drawer = FoliumMapDrawer(0, 0)
    image_point = ImagePoint(
        file_name='test_image.jpg',
        time=datetime.datetime(2023, 10, 1, 12, 0, 0),
        lat=37.7749,
        lon=-122.4194,
        elev=15.5,
        image_url='http://example.com/image.jpg',
        additional_info='Test image'
    )
    drawer.draw_points_on_map([image_point], point_color='red')

    markers = [child for child in drawer.fmap._children.values() if isinstance(child, folium.map.Marker)]
    assert len(markers) == 1


def test_map_drawer_draw_points_on_map_rest_trk_point():
    """Test drawing RestTrkPoint on the map."""
    drawer = FoliumMapDrawer(0, 0)
    rest_point = RestTrkPoint(
        time=datetime.datetime(2023, 10, 1, 10, 0, 0),
        start_time=datetime.datetime(2023, 10, 1, 10, 0, 0),
        end_time=datetime.datetime(2023, 10, 1, 10, 15, 0),
        lat=37.7749,
        lon=-122.4194,
        elev=10
    )
    drawer.draw_points_on_map([rest_point], point_color='green')

    markers = [child for child in drawer.fmap._children.values() if isinstance(child, folium.map.Marker)]
    assert len(markers) == 1


def test_map_drawer_draw_points_on_map_unknown_point():
    """Test drawing an unknown point type on the map."""
    drawer = FoliumMapDrawer(0, 0)

    class UnknownPoint:
        def __init__(self):
            self.lat = 37.7749
            self.lon = -122.4194
            self.time = datetime.datetime(2023, 10, 1, 12, 0, 0)
            self.elev = 15

        def get_note(self):
            return 'Unknown Point'

    unknown_point = UnknownPoint()
    drawer.draw_points_on_map([unknown_point], point_color='blue')

    markers = [child for child in drawer.fmap._children.values() if isinstance(child, folium.map.Marker)]
    assert len(markers) == 1


def test_map_drawer_draw_points_on_map_empty_list():
    """Test drawing points when the list is empty."""
    drawer = FoliumMapDrawer(0, 0)
    drawer.draw_points_on_map([], point_color='blue')

    markers = [child for child in drawer.fmap._children.values() if isinstance(child, folium.map.Marker)]
    assert len(markers) == 0  # No markers should be added


def test_map_drawer_draw_points_on_map_invalid_point():
    """Test drawing a point with invalid data."""
    drawer = FoliumMapDrawer(0, 0)

    class InvalidPoint:
        def __init__(self):
            self.lat = 'invalid_lat'
            self.lon = 'invalid_lon'
            self.time = 'invalid_time'
            self.elev = 'invalid_elev'

        def get_note(self):
            return 'Invalid Point'

    invalid_point = InvalidPoint()
    with pytest.raises(ValueError):
        drawer.draw_points_on_map([invalid_point], point_color='blue')


def test_map_drawer_save(tmp_path):
    """Test saving the map to a valid path."""
    drawer = FoliumMapDrawer(0, 0)
    output_file = tmp_path / "test_map.html"
    drawer.save(str(output_file))

    assert output_file.exists()


def test_map_drawer_save_invalid_path():
    """Test saving the map to an invalid path."""
    drawer = FoliumMapDrawer(0, 0)
    with pytest.raises(Exception):
        drawer.save('/invalid/path/test_map.html')


def test_map_drawer_add_tracks():
    """Test adding tracks to the map."""
    drawer = FoliumMapDrawer(0, 0)

    class Point:
        def __init__(self, lat, lon):
            self.lat = lat
            self.lon = lon

    class MockTracks:
        def get_main_tracks_points_list(self):
            return [Point(0, 0), Point(1, 1), Point(2, 2)]

    mock_tracks = MockTracks()
    drawer.add_tracks(mock_tracks, color='green', weight=3)

    polylines = [child for child in drawer.fmap._children.values() if isinstance(child, folium.vector_layers.PolyLine)]
    assert len(polylines) == 1


def test_map_drawer_add_tracks_empty():
    """Test adding tracks with an empty point list."""
    drawer = FoliumMapDrawer(0, 0)

    class MockTracks:
        def get_main_tracks_points_list(self):
            return []

    mock_tracks = MockTracks()
    drawer.add_tracks(mock_tracks, color='green', weight=3)

    polylines = [child for child in drawer.fmap._children.values() if isinstance(child, folium.vector_layers.PolyLine)]
    assert len(polylines) == 0  # No PolyLine should be added


def test_map_drawer_add_tracks_invalid_points():
    """Test adding tracks with invalid point data."""
    drawer = FoliumMapDrawer(0, 0)

    class Point:
        def __init__(self, lat, lon):
            self.lat = lat
            self.lon = lon

    class MockTracks:
        def get_main_tracks_points_list(self):
            return [Point(0, 0), Point('invalid_lat', 'invalid_lon')]

    mock_tracks = MockTracks()
    with pytest.raises(ValueError):
        drawer.add_tracks(mock_tracks, color='green', weight=3)