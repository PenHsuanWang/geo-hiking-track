import pytest
import datetime
from unittest.mock import Mock, patch
from unittest.mock import MagicMock
from src.geoanalyzer.tracks.gps_parser import parse_gpx, extract_waypoint_from_xmldoc, extract_track_point_from_xmldoc, parse_time, GpxParser

from src.geoanalyzer.tracks.gps_parser import GpxParser
from xml.dom.minidom import Document, Node



def create_mock_node_with_child(parent_name, child_name, child_value):
    doc = Document()
    parent_node = doc.createElement(parent_name)
    child_node = doc.createElement(child_name)
    text_node = doc.createTextNode(child_value)
    child_node.appendChild(text_node)
    parent_node.appendChild(child_node)
    return parent_node


# Helper function to create a mock Element with specified attributes
def create_mock_element(tag_name: str, attributes: dict = None, text_content: str = None) -> MagicMock:
    element = MagicMock(spec=Node)  # Use Node as a broader spec if necessary
    element.tagName = tag_name

    # Ensure attributes is always a dictionary
    attributes = attributes or {}

    for attr, value in attributes.items():
        setattr(element, attr, MagicMock(return_value=value))

    # Set getAttribute to mock the behavior of the get method on the attributes dictionary
    element.getAttribute = MagicMock(side_effect=attributes.get)

    if text_content is not None:
        text_node = MagicMock()
        text_node.data = text_content
        element.firstChild = text_node
    else:
        element.firstChild = None

    return element

# Adjusted test cases
def test_extract_waypoint_from_xmldoc():
    mock_xmldoc = Mock()
    mock_waypoint = create_mock_element("wpt", text_content="test_waypoint")
    mock_xmldoc.getElementsByTagName.return_value = [mock_waypoint]  # Return a list of mock Elements
    result = extract_waypoint_from_xmldoc(mock_xmldoc, "wpt")
    assert result == [mock_waypoint]

def test_extract_track_point_from_xmldoc():
    mock_xmldoc = Mock()
    mock_track_point = create_mock_element("trkpt", text_content="test_track_point")
    mock_xmldoc.getElementsByTagName.return_value = [mock_track_point]  # Return a list of mock Elements
    result = extract_track_point_from_xmldoc(mock_xmldoc, "trkpt")
    assert result == [mock_track_point]

# Testing parse_time function
def test_parse_time():
    assert parse_time('2023-08-28T01:00:00Z') == datetime.datetime(2023, 8, 28, 9, 0)

    with pytest.raises(ValueError):
        parse_time('invalid_time')

# GpxParser class tests
def test_GpxParser_init():
    # Create mock XML nodes with time information embedded in 'wpt' and 'trkpt' nodes
    # Create a Document object
    doc = Document()

    # Create mock XML node 'wpt' with lat, lon, time, ele, and name attributes
    mock_waypoint = doc.createElement("wpt")
    mock_waypoint.setAttribute("lat", "40.7128")
    mock_waypoint.setAttribute("lon", "74.0060")

    time_node = doc.createElement("time")
    time_node.appendChild(doc.createTextNode("2023-08-28T00:00:00Z"))

    ele_node = doc.createElement("ele")
    ele_node.appendChild(doc.createTextNode("100.0"))

    name_node = doc.createElement("name")
    name_node.appendChild(doc.createTextNode("Note"))

    mock_waypoint.appendChild(time_node)
    mock_waypoint.appendChild(ele_node)
    mock_waypoint.appendChild(name_node)

    # Add similarly for mock_track_point (omitting the 'name' tag)
    mock_track_point = doc.createElement("trkpt")
    mock_track_point.setAttribute("lat", "40.7128")
    mock_track_point.setAttribute("lon", "74.0060")

    time_node_trkpt = doc.createElement("time")
    time_node_trkpt.appendChild(doc.createTextNode("2023-08-28T00:01:00Z"))

    ele_node_trkpt = doc.createElement("ele")
    ele_node_trkpt.appendChild(doc.createTextNode("100.0"))

    mock_track_point.appendChild(time_node_trkpt)
    mock_track_point.appendChild(ele_node_trkpt)

    # Existing mocking and test logic
    with patch('src.geoanalyzer.tracks.gps_parser.parse_gpx') as mock_parse_gpx, \
            patch('src.geoanalyzer.tracks.gps_parser.extract_waypoint_from_xmldoc') as mock_extract_waypoint, \
            patch('src.geoanalyzer.tracks.gps_parser.extract_track_point_from_xmldoc') as mock_extract_track_point:
        mock_parse_gpx.return_value = 'xmldoc'
        mock_extract_waypoint.return_value = [mock_waypoint]
        mock_extract_track_point.return_value = [mock_track_point]

        gpx_parser = GpxParser('test.gpx')

        # Add your assertions here
        assert gpx_parser._extract_waypoint == [mock_waypoint]
        assert gpx_parser._extract_track_point == [mock_track_point]


# Helper function to create a GPX node with optional children
def create_gpx_node(tag_name: str, attributes=None, children=None):
    doc = Document()
    node = doc.createElement(tag_name)
    if attributes:
        for key, value in attributes.items():
            node.setAttribute(key, value)
    if children:
        for child_tag, child_value in children.items():
            child_node = doc.createElement(child_tag)
            child_node.appendChild(doc.createTextNode(child_value))
            node.appendChild(child_node)
    return node

# Test cases for _gpx_extract_point_time_str_utc
@pytest.mark.parametrize("time_str,expected", [
    ("2023-01-01T12:00:00Z", "2023-01-01T12:00:00Z"),  # Valid time string
    (None, None),  # No time tag
    ("", None),  # Empty time string
    ("not-a-time", "not-a-time")  # Malformed time string returns as is
])
def test_gpx_extract_point_time_str_utc(time_str, expected):
    node = create_gpx_node("trkpt", children={"time": time_str} if time_str else {})
    result = GpxParser._gpx_extract_point_time_str_utc(node)
    assert result == expected, f"The extracted time string should match the expected result: {expected}"


# Test cases for _gpx_extract_point_elevation
@pytest.mark.parametrize("elevation_str,expected", [
    ("100.0", 100.0),  # Valid elevation
    (None, None),  # No elevation tag
    ("", None),  # Empty elevation string
    ("not-a-number", None)  # Non-numeric elevation string
])
def test_gpx_extract_point_elevation(elevation_str, expected):
    node = create_gpx_node("trkpt", children={"ele": elevation_str} if elevation_str else {})
    result = GpxParser._gpx_extract_point_elevation(node)
    assert result == expected, "The extracted elevation should match the expected result."

# Test cases for _gpx_extract_point_note
@pytest.mark.parametrize("note,expected", [
    ("This is a note", "This is a note"),  # Valid note
    (None, None),  # No note tag
    ("", None)  # Empty note string
])
def test_gpx_extract_point_note(note, expected):
    node = create_gpx_node("trkpt", children={"name": note} if note else {})
    result = GpxParser._gpx_extract_point_note(node)
    assert result == expected, "The extracted note should match the expected result."

