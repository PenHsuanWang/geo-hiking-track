# src/visualization/map_drawer.py

import folium
from folium import Map, TileLayer, LayerControl, Element
from folium.plugins import Draw
from src.geo_objects.geo_points.analyzed_geo_points import RestTrkPoint
from src.geo_objects.geo_points.image_points import ImagePoint


class FoliumMapDrawer:
    """
    A class used to draw a Folium map and visualize GPS track data, waypoints, rest points, and images.

    This class creates an interactive map using Folium, supports multiple tile layers,
    and provides methods to add various points and tracks. It also allows for custom CSS injection
    to ensure that images displayed in popups are properly scaled in smaller containers.

    Attributes:
        fmap (folium.Map): The main Folium map object.
        tile_layers (list): A list of tile layers added to the map.
    """

    def __init__(self, location_x: float, location_y: float, zoom_start: int = 16, **kwargs):
        """
        Initialize a FoliumMapDrawer instance.

        :param location_x: Latitude of the map center.
        :param location_y: Longitude of the map center.
        :param zoom_start: Initial zoom level for the map, defaults to 16.
        :param kwargs:
            - map_tiles: A list of tile URLs or providers.
            - map_attrs: A list of attributions for each tile.
            - map_names: A list of display names for each tile layer.
        :raises ValueError: If the lengths of map_tiles, map_attrs, and map_names differ.
        """
        map_tiles = kwargs.get('map_tiles', ['openstreetmap'])
        map_attrs = kwargs.get('map_attrs', ['Warning: No attribution specified. Please set the attr by --map-attr option.'])
        map_names = kwargs.get('map_names', [tile for tile in map_tiles])

        # Validate that the lengths of map_tiles, map_attrs, and map_names match
        if not (len(map_tiles) == len(map_attrs) == len(map_names)):
            raise ValueError("The number of map_tiles, map_attrs, and map_names must be the same.")

        # Initialize the map without default tiles
        self.fmap = Map(
            location=[location_x, location_y],
            zoom_start=zoom_start,
            tiles=None
        )

        # Add a title to the map (optional)
        title_html = f'''
        <h3 align="center" style="font-size:20px"><b>Map: {map_names[0]}</b></h3>
        '''
        self.fmap.get_root().html.add_child(Element(title_html))

        # Inject custom CSS to control image sizes inside popups
        self._inject_css()

        # Add each tile layer with custom names
        self.tile_layers = []
        for tile, attr, name in zip(map_tiles, map_attrs, map_names):
            if tile.lower() in [
                'openstreetmap',
                'stamenterrain',
                'stamenwatercolor',
                'cartodbpositron',
                'cartodbdark_matter'
            ]:
                tile_layer = TileLayer(tile, name=name, attr=attr, control=True)
            else:
                tile_layer = TileLayer(tiles=tile, name=name, attr=attr, control=True)
            tile_layer.add_to(self.fmap)
            self.tile_layers.append(tile_layer)

        # Add a toolbar for drawing using leaflet.pm
        draw = Draw(
            draw_options={
                'polyline': True,
                'polygon': True,
                'circle': True,
                'rectangle': True,
                'marker': True,
            },
            edit_options={
                'edit': True,
                'remove': True,
            }
        )
        draw.add_to(self.fmap)

        # Add LayerControl for switching between tile layers
        LayerControl().add_to(self.fmap)

    def _inject_css(self):
        """
        Inject a CSS style block to constrain image sizes within leaflet popups.

        This ensures that images do not overflow popup boundaries, which is particularly
        helpful when the map is embedded inside a smaller container.
        """
        style_html = '''
        <style>
            /* Limit image widths inside popups to prevent overflow */
            .leaflet-popup-content img {
                max-width: 300px;
                height: auto;
            }
        </style>
        '''
        self.fmap.get_root().html.add_child(Element(style_html))

    def add_poly_line(self, point_list, weight=8, color=None):
        """
        Add a polyline to the map.

        :param point_list: A list of [lat, lon] pairs defining the polyline.
        :param weight: The line weight, defaults to 8.
        :param color: The line color, defaults to None.
        """
        if not point_list:
            print("Warning: PolyLine point list is empty. Skipping addition.")
            return
        self.fmap.add_child(folium.PolyLine(locations=point_list, weight=weight, color=color))

    def add_tracks(self, input_tracks, **kwargs):
        """
        Add tracks (polylines) to the map from an input track object.

        :param input_tracks: An object providing `get_main_tracks_points_list()` method,
                             which returns a list of points each with lat, lon attributes.
        :param kwargs: Additional keyword arguments for the polyline (e.g., color, weight).
        :raises ValueError: If any track point has invalid lat/lon.
        """
        main_tracks_point_list = input_tracks.get_main_tracks_points_list()
        point_list = []
        for i in main_tracks_point_list:
            if not isinstance(i.lat, (int, float)) or not isinstance(i.lon, (int, float)):
                raise ValueError(f"Invalid latitude or longitude for track point: {i}")
            point_list.append([i.lat, i.lon])

        if not point_list:
            print("Warning: Track point list is empty. Skipping addition.")
            return

        self.fmap.add_child(folium.PolyLine(locations=point_list, **kwargs))

    def draw_points_on_map(
        self,
        points,
        point_type='marker',
        point_info='',
        point_color='green',
        point_radius=8,
        alpha=0.3
    ):
        """
        Draw points on the map.

        Points can be rendered as markers or circles. Popups provide additional info.

        :param points: A single point or a list of points, each must have lat, lon, time, elev.
        :param point_type: 'marker' or 'circle', defaults to 'marker'.
        :param point_info: Additional info for the popup, appended to each point's info.
        :param point_color: Color of the point marker/circle.
        :param point_radius: Radius if using circle markers.
        :param alpha: Opacity for circle markers.
        :raises ValueError: If lat/lon/time/elev are invalid for any point.
        """
        if not isinstance(points, list):
            points = [points]

        if point_info:
            point_info += '<br>'

        for i in points:
            if not isinstance(i.lat, (int, float)) or not isinstance(i.lon, (int, float)):
                raise ValueError(f"Invalid latitude or longitude for point: {i}")
            if not hasattr(i.time, 'strftime'):
                raise ValueError(f"Invalid time attribute for point: {i}")
            if not isinstance(i.elev, (int, float)):
                raise ValueError(f"Invalid elevation for point: {i}")

            point_location = [i.lat, i.lon]

            # Handle RestTrkPoint
            if isinstance(i, RestTrkPoint):
                popup_info = (
                    '休息點' + '<br>' +
                    f"{i.get_start_time().strftime('%H:%M')} ~ {i.get_end_time().strftime('%H:%M')}" +
                    '<br>' + f"Elev: {round(i.elev, 0)} M"
                )
                popup = folium.Popup(popup_info, max_width=150, min_width=70)
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

            # Handle ImagePoint
            elif isinstance(i, ImagePoint):
                popup_html = i.get_popup_info()
                popup = folium.Popup(
                    popup_html,
                    max_width='none',
                    min_width='none',
                    parse_html=False,
                    options={
                        'autoPan': True,
                        'keepInView': True,
                        'autoPanPadding': [20, 20]
                    }
                )
                icon = folium.Icon(color=point_color, icon='camera', prefix='fa')
                self.fmap.add_child(
                    folium.Marker(
                        location=point_location,
                        icon=icon,
                        popup=popup
                    )
                )

            # Handle other types of points
            else:
                popup_info = (
                    point_info +
                    f"{i.time.strftime('%H:%M')}<br>" +
                    f"{i.get_note()}<br>" +
                    f"{round(i.elev, 0)} M"
                )
                popup = folium.Popup(popup_info, max_width=150, min_width=70)

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
        Save the map to an HTML file.

        :param out_file: The output file path. If it doesn't end with .html, '.html' is appended.
        """
        if not out_file.endswith('.html'):
            out_file += '.html'
        self.fmap.save(out_file)
        print(f"Saving map: {out_file}")
