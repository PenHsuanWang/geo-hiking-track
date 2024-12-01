"""
The cli tools for the project.
usage cli.py --load-gpx <input_file_path> --save-dit <output_file_path>
to run the target gpx with analyzer to show the tracks
"""

import click
import os
from src.geoanalyzer.tracks import gps_parser
from src.geoanalyzer.tracks.track_analyzer import TrackAnalyzer
from src.geoanalyzer.images.image_parser import ImageParser
from src.visualizartion.map_drawer import FoliumMapDrawer
from src.visualizartion.report_generator import ReportGenerator

@click.command()
@click.option('--gpx-file', type=click.Path(exists=True), required=True, help='Path to the GPX file to load.')
@click.option('--output-map', type=click.Path(), required=True, help='Directory to save the output map.')
@click.option('--map-tile', type=str, required=False, default='OpenStreetMap', help='The map tile provider to use.')
@click.option('--map-attr', type=str, required=False,
              default='Map data © OpenStreetMap contributors', help='The attribution of the map.')
@click.option('--output-report', type=click.Path(), required=False, help='Directory to save the output report.')
@click.option('--picture-folder', type=click.Path(exists=True), required=False, help='Folder containing pictures to parse.')
def main(gpx_file, output_map, map_tile, map_attr, output_report, picture_folder):
    """CLI tool for parsing GPX files and generating maps."""

    try:
        # Parsing GPX file
        gpx_parser_obj = gps_parser.GpxParser(gpx_file)

        # Analyzing tracks
        tracks_object = TrackAnalyzer(gpx_parser_obj.get_raw_track_object())
        tracks = tracks_object.get_main_track()

        # If provided, parse images and get image points
        image_points = []
        if picture_folder:
            image_parser = ImageParser(picture_folder)
            image_points = image_parser.get_image_points()
            processed_files, skipped_non_jpg, skipped_no_gps, errors = image_parser.get_summary()

            # Display summary to the user
            click.echo(f"Processed {processed_files} JPG files.")
            click.echo(f"Skipped {skipped_non_jpg} non-JPG files.")
            click.echo(f"Skipped {skipped_no_gps} JPG files without GPS data.")
            if errors:
                click.echo("Errors encountered during image parsing:")
                for error in errors:
                    click.echo(f"- {error}")

        # Report Generation (same as before)
        if output_report:
            # check the file extension name exist and support txt format and other relevant format like markdown
            # check  the output_report file path is valid
            if not output_report.endswith('.txt'):
                output_report = output_report + '.txt'

            # the output_report file path can be absolute or relative path.
            # thus `/` or `\` is used to split the path
            # parsing the file and directory path. exclude the file name and the rest is the directory path
            file_path, file_name = os.path.split(output_report)
            if not os.path.exists(file_path):
                print(f"Directory {file_path} does not exist. Creating directory...")

            reporter = ReportGenerator(tracks_object)
            reporter.generate_report(saved_file=output_report, saved_format='txt')

        # Generating map
        map_drawer = FoliumMapDrawer(
            tracks.get_start_point().lat,
            tracks.get_start_point().lon,
            map_tiles=map_tile,
            map_attr=map_attr
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
        # Add image points to the map
        if image_points:
            map_drawer.draw_points_on_map(
                image_points,
                point_type='marker',
                point_info='Image',
                point_color='red',
                point_radius=None,
                alpha=None
            )
        map_drawer.save(output_map)

        click.echo(f"Map successfully generated at {output_map}")

    except Exception as e:
        click.echo(f"An error occurred: {str(e)}", err=True)


if __name__ == '__main__':
    main()
