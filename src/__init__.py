"""Geo Hiking Track Analyzer - A library for parsing and analyzing GPX files."""

# Use relative imports to work after pip install
from .geoanalyzer.tracks.gps_parser import GpxParser
from .geoanalyzer.tracks.track_analyzer import TrackAnalyzer
from .visualizartion.map_drawer import FoliumMapDrawer
from .visualizartion.report_generator import ReportGenerator

__all__ = [
    'GpxParser',
    'TrackAnalyzer',
    'FoliumMapDrawer',
    'ReportGenerator',
]

__version__ = '0.1.0'
