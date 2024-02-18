"""
This module contains the model of raw track point and way point which is getting from gpx file.
The basic information of a point is time, latitude, longitude, elevation.
for waypoint, addition point information is note.
"""

from src.geo_objects.geo_points.basic_point import BasicPoint


class WayPoint(BasicPoint):
    """
    Way point object is the model to save waypoint
    row information which extracting directory from gpx file.
    """
    def __init__(self, time=None, lat=None, lon=None, elev=None, note=None):
        super(WayPoint, self).__init__(time, lat, lon, elev)
        self._note = note

    def get_note(self):
        return self._note


class RawTrkPoint(BasicPoint):
    """
    Raw track point object is the model to save track point
    row information which extracting directory from gpx file.
    """

    def __init__(self, time=None, lat=None, lon=None, elev=None):
        super(RawTrkPoint, self).__init__(time, lat, lon, elev)
