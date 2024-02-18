"""
The cli tools for the project.
usage cli.py --load-gpx <input_file_path> --save-dit <output_file_path>
to run the target gpx with analyzer to show the tracks
"""

import click
from src.geoanalyzer.tracks import gps_parser
from src.geoanalyzer.tracks.track_analyzer import TrackAnalyzer
from src.visualizartion.map_drawer import FoliumMapDrawer


@click.command()
@click.option('--gpx-file', type=click.Path(exists=True), required=True, help='Path to the GPX file to load.')
@click.option('--output-map', type=click.Path(), required=True, help='Directory to save the output map.')
def main(gpx_file, output_map):
    """CLI tool for parsing GPX files and generating maps."""

    try:
        # Parsing GPX file
        gpx_parser_obj = gps_parser.GpxParser(gpx_file)

        # Analyzing tracks
        tracks_object = TrackAnalyzer(gpx_parser_obj.get_raw_track_object())
        tracks = tracks_object.get_main_track()

        # Generating map
        map_drawer = FoliumMapDrawer(
            tracks.get_start_point().lat,
            tracks.get_start_point().lon
        )
        map_drawer.add_tracks(tracks, weight=4)
        map_drawer.draw_points_on_map(
            tracks_object.get_rest_point_list(),
            point_type='circle',
            point_info='休息點',
            point_color='green',
            point_radius=10,
            alpha=0.3
        )
        map_drawer.draw_points_on_map(
            tracks_object.get_waypoint_list(),
            point_type='marker',
            point_info='',
            point_color='blue',
            point_radius=None,
            alpha=None
        )
        map_drawer.save(output_map)

        click.echo(f"Map successfully generated at {output_map}")

    except Exception as e:
        click.echo(f"An error occurred: {str(e)}", err=True)


if __name__ == '__main__':
    main()
