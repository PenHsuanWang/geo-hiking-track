"""
The CLI tools for the project.
Usage:
    cli.py --gpx-file <input_file_path> --output-map <output_file_path> \
           --map-tile <tile1> --map-attr <attr1> [--map-name <name1>] \
           [--map-tile <tile2> --map-attr <attr2> [--map-name <name2>]] ... \
           [--output-report <report_path>] \
           [--picture-folder <pictures_folder>]
To run the target GPX with analyzer and show the tracks.
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
@click.option('--output-map', type=click.Path(), required=True, help='Path to save the output map HTML file.')
@click.option('--map-tile', type=str, required=False, multiple=True, default=['OpenStreetMap'],
              help='The map tile providers or URLs to use. Can be specified multiple times.')
@click.option('--map-attr', type=str, required=False, multiple=True,
              default=['Map data © OpenStreetMap contributors'],
              help='The attributions of the map tiles. Should match the number of map tiles.')
@click.option('--map-name', type=str, required=False, multiple=True,
              help='The display names for the map tiles. Should align with the map tiles.')
@click.option('--output-report', type=click.Path(), required=False, help='Path to save the output report (e.g., .txt or .md).')
@click.option('--picture-folder', type=click.Path(exists=True), required=False, help='Folder containing pictures to parse.')
def main(gpx_file, output_map, map_tile, map_attr, map_name, output_report, picture_folder):
    """CLI tool for parsing GPX files and generating interactive maps."""

    try:
        # Validate that the number of map tiles and attributions match
        if len(map_tile) != len(map_attr):
            click.echo("Error: The number of --map-tile and --map-attr options must be the same.", err=True)
            return

        # Validate that the number of map names does not exceed map tiles
        if len(map_name) > len(map_tile):
            click.echo("Error: The number of --map-name options cannot exceed the number of --map-tile options.", err=True)
            return

        # Pair map_tiles, map_attrs, and map_names
        # If a map_name is not provided for a map_tile, use the map_tile URL as its name
        paired_map_layers = []
        for i in range(len(map_tile)):
            tile = map_tile[i]
            attr = map_attr[i]
            name = map_name[i] if i < len(map_name) else tile
            paired_map_layers.append({
                'tile': tile,
                'attr': attr,
                'name': name
            })

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

        # Report Generation
        if output_report:
            # Ensure the report file has a supported extension (e.g., .txt or .md)
            if not output_report.endswith(('.txt', '.md')):
                click.echo("Error: The --output-report file must have a '.txt' or '.md' extension.", err=True)
                return

            # Ensure the output directory exists
            file_path, _ = os.path.split(output_report)
            if not os.path.exists(file_path) and file_path != '':
                click.echo(f"Directory {file_path} does not exist. Creating directory...", err=True)
                os.makedirs(file_path)

            reporter = ReportGenerator(tracks_object)
            reporter.generate_report(saved_file=output_report, saved_format=os.path.splitext(output_report)[1][1:])
            click.echo(f"Report successfully generated at {output_report}")

        # Generating map
        # Extract the starting point from the tracks for centering the map
        start_point = tracks.get_start_point()
        map_drawer = FoliumMapDrawer(
            location_x=start_point.lat,
            location_y=start_point.lon,
            zoom_start=15,
            map_tiles=[layer['tile'] for layer in paired_map_layers],
            map_attrs=[layer['attr'] for layer in paired_map_layers],
            map_names=[layer['name'] for layer in paired_map_layers]
        )

        # Add tracks to the map
        map_drawer.add_tracks(tracks, weight=4, color='blue')

        # Draw rest points as green circles
        map_drawer.draw_points_on_map(
            tracks_object.get_rest_point_list(),
            point_type='circle',
            point_info='休息點',
            point_color='green',
            point_radius=10,
            alpha=0.3
        )

        # Draw waypoints as blue markers
        map_drawer.draw_points_on_map(
            tracks_object.get_waypoint_list(),
            point_type='marker',
            point_info='',
            point_color='blue',
            point_radius=None,
            alpha=None
        )

        # Add image points to the map as red markers, if any
        if image_points:
            map_drawer.draw_points_on_map(
                image_points,
                point_type='marker',
                point_info='',
                point_color='red',
                point_radius=None,
                alpha=None
            )

        # Save the generated map to the specified output path
        map_drawer.save(output_map)

        click.echo(f"Map successfully generated at {output_map}")

    except Exception as e:
        click.echo(f"An error occurred: {str(e)}", err=True)


if __name__ == '__main__':
    main()
