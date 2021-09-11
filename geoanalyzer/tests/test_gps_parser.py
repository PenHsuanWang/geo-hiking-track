import os

from geoanalyzer.tracks import gps_parser


def test_parse_time():
    try:
        time = gps_parser.parse_time(None)
    except ValueError:
        print("time parsing format issue")
        assert True
    except Exception as e:
        e.with_traceback()
        assert False

    assert True


def test_gpx_parser():

    gpx_parser = gps_parser.GpxParser("../../gpx_file/2021-08-29-06.21.16.gpx")

    track_object = gpx_parser.get_raw_track_object()
    waypoint = track_object.get_waypoint_list()
    for i in waypoint:
        note = i.get_note()
        print(note)

    assert True
