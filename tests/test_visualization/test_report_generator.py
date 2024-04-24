import pytest
from unittest.mock import Mock, patch, mock_open
from reportlab.lib.pagesizes import letter
from src.geo_objects.geo_tracks.analyzed_geo_tracks import AnalyzedTrackObject
from src.visualizartion.report_generator import ReportGenerator


# Test the default behavior of generate_report
def test_generate_report_default_behavior():
    mock_waypoint = Mock()
    mock_waypoint.time = "2023-08-28T00:00:00Z"
    mock_waypoint.get_note.return_value = "Note1"

    mock_waypoint2 = Mock()
    mock_waypoint2.time = "2023-08-28T01:00:00Z"
    mock_waypoint2.get_note.return_value = "Note2"

    mock_track_object = Mock(spec=AnalyzedTrackObject)
    mock_track_object.get_waypoint_list.return_value = [mock_waypoint, mock_waypoint2]

    report_generator = ReportGenerator(mock_track_object)

    with patch('builtins.open', new_callable=mock_open) as mock_file:
        report_generator.generate_report()

    mock_file.assert_called_once_with('default_report.txt', 'w')
    mock_file().write.assert_any_call("2023-08-28T00:00:00Z Note1\n")
    mock_file().write.assert_any_call("2023-08-28T01:00:00Z Note2\n")


# Test the behavior of generate_report when saved_format is 'pdf'
def test_generate_report_pdf_format():
    mock_waypoint = Mock()
    mock_waypoint.time = "2023-08-28T00:00:00Z"
    mock_waypoint.get_note.return_value = "Note1"

    mock_waypoint2 = Mock()
    mock_waypoint2.time = "2023-08-28T01:00:00Z"
    mock_waypoint2.get_note.return_value = "Note2"

    mock_track_object = Mock(spec=AnalyzedTrackObject)
    mock_track_object.get_waypoint_list.return_value = [mock_waypoint, mock_waypoint2]

    report_generator = ReportGenerator(mock_track_object)

    with patch('reportlab.pdfgen.canvas.Canvas') as mock_canvas:
        report_generator.generate_report(saved_file='default_report.txt', saved_format='pdf')

    width, height = letter
    mock_canvas.assert_called_once_with('default_report.txt.pdf', pagesize=letter)
    mock_canvas().drawString.assert_any_call(10, height - 10, "2023-08-28T00:00:00Z Note1")
    mock_canvas().drawString.assert_any_call(10, height - 20, "2023-08-28T01:00:00Z Note2")
    mock_canvas().save.assert_called_once()


# Test the behavior of generate_report when saved_file does not match saved_format
def test_generate_report_mismatched_file_and_format():
    mock_waypoint = Mock()
    mock_waypoint.time = "2023-08-28T00:00:00Z"
    mock_waypoint.get_note.return_value = "Note1"

    mock_waypoint2 = Mock()
    mock_waypoint2.time = "2023-08-28T01:00:00Z"
    mock_waypoint2.get_note.return_value = "Note2"

    mock_track_object = Mock(spec=AnalyzedTrackObject)
    mock_track_object.get_waypoint_list.return_value = [mock_waypoint, mock_waypoint2]

    report_generator = ReportGenerator(mock_track_object)

    with patch('builtins.open', new_callable=mock_open) as mock_file:
        report_generator.generate_report(saved_file='report.pdf', saved_format='txt')

    mock_file.assert_called_once_with('report.pdf.txt', 'w')
    mock_file().write.assert_any_call("2023-08-28T00:00:00Z Note1\n")
    mock_file().write.assert_any_call("2023-08-28T01:00:00Z Note2\n")


# Test the behavior of generate_report when saved_file is None
def test_generate_report_no_saved_file():
    mock_waypoint = Mock()
    mock_waypoint.time = "2023-08-28T00:00:00Z"
    mock_waypoint.get_note.return_value = "Note1"

    mock_waypoint2 = Mock()
    mock_waypoint2.time = "2023-08-28T01:00:00Z"
    mock_waypoint2.get_note.return_value = "Note2"

    mock_track_object = Mock(spec=AnalyzedTrackObject)
    mock_track_object.get_waypoint_list.return_value = [mock_waypoint, mock_waypoint2]

    report_generator = ReportGenerator(mock_track_object)

    with patch('builtins.open', new_callable=mock_open) as mock_file:
        report_generator.generate_report(saved_file=None)

    mock_file.assert_called_once_with('default_report.txt', 'w')
    mock_file().write.assert_any_call("2023-08-28T00:00:00Z Note1\n")
    mock_file().write.assert_any_call("2023-08-28T01:00:00Z Note2\n")


# Test the behavior of generate_report when saved_format is None
def test_generate_report_no_saved_format():
    mock_waypoint = Mock()
    mock_waypoint.time = "2023-08-28T00:00:00Z"
    mock_waypoint.get_note.return_value = "Note1"

    mock_waypoint2 = Mock()
    mock_waypoint2.time = "2023-08-28T01:00:00Z"
    mock_waypoint2.get_note.return_value = "Note2"

    mock_track_object = Mock(spec=AnalyzedTrackObject)
    mock_track_object.get_waypoint_list.return_value = [mock_waypoint, mock_waypoint2]

    report_generator = ReportGenerator(mock_track_object)

    with patch('builtins.open', new_callable=mock_open) as mock_file:
        report_generator.generate_report(saved_format=None)

    mock_file.assert_called_once_with('default_report.txt', 'w')
    mock_file().write.assert_any_call("2023-08-28T00:00:00Z Note1\n")
    mock_file().write.assert_any_call("2023-08-28T01:00:00Z Note2\n")


# Test the behavior of generate_report when saved_format is not 'txt' or 'pdf'
def test_generate_report_invalid_saved_format():
    mock_waypoint = Mock()
    mock_waypoint.time = "2023-08-28T00:00:00Z"
    mock_waypoint.get_note.return_value = "Note1"

    mock_waypoint2 = Mock()
    mock_waypoint2.time = "2023-08-28T01:00:00Z"
    mock_waypoint2.get_note.return_value = "Note2"

    mock_track_object = Mock(spec=AnalyzedTrackObject)
    mock_track_object.get_waypoint_list.return_value = [mock_waypoint, mock_waypoint2]

    report_generator = ReportGenerator(mock_track_object)

    with pytest.raises(ValueError):
        report_generator.generate_report(saved_format='doc')


# Test the behavior of generate_report when waypoint_time_note_dict is empty
def test_generate_report_empty_waypoint_list():
    mock_track_object = Mock(spec=AnalyzedTrackObject)
    mock_track_object.get_waypoint_list.return_value = []

    report_generator = ReportGenerator(mock_track_object)

    with patch('builtins.open', new_callable=mock_open) as mock_file:
        report_generator.generate_report()

    mock_file.assert_called_once_with('default_report.txt', 'w')
    assert not mock_file().write.called