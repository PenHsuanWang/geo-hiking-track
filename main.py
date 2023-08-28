from src.geoanalyzer.tracks import gps_parser
from src.geoanalyzer.tracks import track_analyzer
from src.geoanalyzer.tracks.track_analyzer import TrackAnalyzer
from src.visualizartion.map_drawer import FoliumMapDrawer

gpx_parser = gps_parser.GpxParser("./gpx_file/2021-08-29-06.21.16.gpx")

tracks_object = TrackAnalyzer(gpx_parser.get_raw_track_object())
tracks = tracks_object.get_main_track()


mapDrawer = FoliumMapDrawer(tracks.get_start_point().get_lat(), tracks.get_start_point().get_lon())
mapDrawer.add_tracks(tracks, weight=4)
mapDrawer.draw_points_on_map(tracks_object.get_rest_point_list(), point_type='circle', point_info='休息點', point_color='green', point_radius=10, alpha=0.3)
mapDrawer.draw_points_on_map(tracks_object.get_waypoint_list(), point_type='marker', point_info='', point_color='blue', point_radius=None, alpha=None)
# mapDrawer.save('./output_map/map_2021-08-29-06.21.16')