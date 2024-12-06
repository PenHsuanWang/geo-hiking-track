# src/visualization/map_drawer.py

import folium
from folium import Map, TileLayer, LayerControl
from src.geo_objects.geo_points.analyzed_geo_points import RestTrkPoint
from src.geo_objects.geo_points.image_points import ImagePoint

class FoliumMapDrawer:
    """
    A class used to represent a Map Drawer using the Folium library.

    :param location_x: The latitude of the location where the map will be centered
    :type location_x: float
    :param location_y: The longitude of the location where the map will be centered
    :type location_y: float
    :param zoom_start: The initial zoom level of the map, defaults to 16
    :type zoom_start: int, optional
    """

    def __init__(self, location_x, location_y, zoom_start=16, **kwargs):
        map_tiles = kwargs.get('map_tiles', ['openstreetmap'])
        map_attrs = kwargs.get('map_attrs', ['Warning: No attribution specified. Please set the attr by --map-attr option.'])

        if len(map_tiles) != len(map_attrs):
            raise ValueError("The number of map_tiles and map_attrs must be the same.")

        # Initialize the map without default tiles
        self.fmap = Map(
            location=[location_x, location_y],
            zoom_start=zoom_start,
            tiles=None  # We'll add tile layers manually
        )

        # Add each tile layer
        self.tile_layers = []
        for tile, attr in zip(map_tiles, map_attrs):
            if tile.lower() in ['openstreetmap', 'stamenterrain', 'stamenwatercolor', 'cartodbpositron', 'cartodbdark_matter']:
                # For built-in tile providers
                tile_layer = TileLayer(tile, name=tile, attr=attr, control=True)
            else:
                # For custom tile URLs
                tile_layer = TileLayer(tiles=tile, name=tile, attr=attr, control=True)
            tile_layer.add_to(self.fmap)
            self.tile_layers.append(tile_layer)

        # Add LayerControl to switch between tile layers
        LayerControl().add_to(self.fmap)

    def add_poly_line(self, point_list, weight=8, color=None):
        """
        Adds a polyline to the map.

        :param point_list: A list of points defining the polyline
        :type point_list: list
        :param weight: The weight of the polyline, defaults to 8
        :type weight: int, optional
        :param color: The color of the polyline, defaults to None
        :type color: str, optional
        """
        if not point_list:
            # Skip adding PolyLine if the point list is empty
            print("Warning: PolyLine point list is empty. Skipping addition.")
            return
        self.fmap.add_child(folium.PolyLine(locations=point_list, weight=weight, color=color))

    def add_tracks(self, input_tracks, **kwargs):
        """
        Adds tracks to the map.

        :param input_tracks: An object that represents geographic tracks
        :type input_tracks: object
        :param **kwargs: Additional keyword arguments for the polyline
        """
        main_tracks_point_list = input_tracks.get_main_tracks_points_list()
        point_list = []
        for i in main_tracks_point_list:
            # Validate point attributes
            if not isinstance(i.lat, (int, float)) or not isinstance(i.lon, (int, float)):
                raise ValueError(f"Invalid latitude or longitude for track point: {i}")
            point = [i.lat, i.lon]
            point_list.append(point)
        if not point_list:
            print("Warning: Track point list is empty. Skipping addition.")
            return
        self.fmap.add_child(folium.PolyLine(locations=point_list, **kwargs))

    def draw_points_on_map(self, points, point_type='marker', point_info='', point_color='green', point_radius=8, alpha=0.3):
        """
        Draws points on the map.

        :param points: A list of points to be drawn on the map
        :type points: list
        :param point_type: The type of the points ('marker' or 'circle'), defaults to 'marker'
        :type point_type: str, optional
        :param point_info: Additional information about the points, defaults to ''
        :type point_info: str, optional
        :param point_color: The color of the points, defaults to 'green'
        :type point_color: str, optional
        :param point_radius: The radius of the points (if point_type is 'circle'), defaults to 8
        :type point_radius: int, optional
        :param alpha: The opacity of the points (if point_type is 'circle'), defaults to 0.3
        :type alpha: float, optional
        """
        if not isinstance(points, list):
            points = [points]

        if point_info != '':
            point_info += '<br>'

        for i in points:
            # Validate point attributes
            if not isinstance(i.lat, (int, float)) or not isinstance(i.lon, (int, float)):
                raise ValueError(f"Invalid latitude or longitude for point: {i}")
            if not hasattr(i.time, 'strftime'):
                raise ValueError(f"Invalid time attribute for point: {i}")
            if not isinstance(i.elev, (int, float)):
                raise ValueError(f"Invalid elevation for point: {i}")

            point_location = [i.lat, i.lon]

            if isinstance(i, RestTrkPoint):
                # Existing logic for RestTrkPoint remains unchanged
                popup_info = ('休息點' + '<br>' +
                              str(i.get_start_time().strftime('%H:%M')) + ' ~ ' + str(i.get_end_time().strftime('%H:%M')) +
                              '<br>' + 'Elev: ' + str(round(i.elev, 0)) + ' M')
                popup = folium.Popup(
                    popup_info,
                    max_width=150,
                    min_width=70
                )
                if point_type == 'marker':
                    self.fmap.add_child(
                        folium.Marker(
                            location=point_location,
                            icon=folium.Icon(color=point_color, icon='info-sign', prefix='glyphicon'),
                            popup=popup
                        )
                    )
                else:
                    self.fmap.add_child(
                        folium.Circle(
                            location=point_location,
                            color=point_color,
                            radius=point_radius,
                            popup=popup,
                            fill=True,
                            fill_opacity=alpha
                        )
                    )

            elif isinstance(i, ImagePoint):
                popup_html = i.get_popup_info()
                popup = folium.Popup(
                    popup_html,
                    max_width='none',  # Disable max width to allow percentage-based styling
                    min_width='none',  # Disable min width
                    parse_html=False,
                    options={
                        'autoPan': True,
                        'keepInView': True,
                        'autoPanPadding': [20, 20]
                    }
                )

                # Use a custom icon for image points (e.g., a camera icon)
                icon = folium.Icon(color=point_color, icon='camera', prefix='fa')

                self.fmap.add_child(
                    folium.Marker(
                        location=point_location,
                        icon=icon,
                        popup=popup
                    )
                )

            else:
                # Existing logic for other points (e.g., waypoints) remains unchanged
                popup_info = point_info + str(i.time.strftime('%H:%M')) + '<br>' + i.get_note() + '<br>' + str(round(i.elev, 0)) + " M"
                popup = folium.Popup(
                    popup_info,
                    max_width=150,
                    min_width=70
                )
                if point_type == 'marker':
                    self.fmap.add_child(
                        folium.Marker(
                            location=point_location,
                            icon=folium.Icon(color=point_color, icon='info-sign', prefix='glyphicon'),
                            popup=popup
                        )
                    )
                else:
                    self.fmap.add_child(
                        folium.Circle(
                            location=point_location,
                            color=point_color,
                            radius=point_radius,
                            popup=popup,
                            fill=True,
                            fill_opacity=alpha
                        )
                    )

    def save(self, out_file: str):
        """
        Saves the map to a specified file.

        :param out_file: The path of the file where the map will be saved
        :type out_file: str
        """
        if not out_file.endswith('.html'):
            out_file += '.html'
        self.fmap.save(out_file)
        print('Saving map: {}'.format(out_file))
