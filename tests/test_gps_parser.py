import pytest
import datetime
from unittest.mock import Mock, patch
from src.geoanalyzer.tracks.gps_parser import parse_gpx, extract_waypoint_from_xmldoc, extract_track_point_from_xmldoc, parse_time, GpxParser

from src.geoanalyzer.tracks.gps_parser import GpxParser
from xml.dom.minidom import Document

def create_mock_node_with_child(parent_name, child_name, child_value):
    doc = Document()
    parent_node = doc.createElement(parent_name)
    child_node = doc.createElement(child_name)
    text_node = doc.createTextNode(child_value)
    child_node.appendChild(text_node)
    parent_node.appendChild(child_node)
    return parent_node

# Testing parse_gpx function
# def test_parse_gpx():
#     with patch('xml.dom.minidom.parse') as mock_parse:
#         parse_gpx('test.gpx')
#         mock_parse.assert_called_once_with('test.gpx')

# Testing extract_waypoint_from_xmldoc function
def test_extract_waypoint_from_xmldoc():
    mock_xmldoc = Mock()
    mock_xmldoc.getElementsByTagName.return_value = 'test_waypoint'
    assert extract_waypoint_from_xmldoc(mock_xmldoc) == 'test_waypoint'

# Testing extract_track_point_from_xmldoc function
def test_extract_track_point_from_xmldoc():
    mock_xmldoc = Mock()
    mock_xmldoc.getElementsByTagName.return_value = 'test_track_point'
    assert extract_track_point_from_xmldoc(mock_xmldoc) == 'test_track_point'

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
