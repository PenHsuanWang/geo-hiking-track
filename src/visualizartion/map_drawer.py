import folium
from src.geo_objects.geo_points.analyzed_geo_points import RestTrkPoint


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

        map_tiles = kwargs.get('map_tiles', 'openstreetmap')
        map_attr = kwargs.get('map_attr', 'Warning: No attribution specified. please set the attr by --map-attr option.')

        self.fmap = folium.Map(location=[location_x, location_y], zoom_start=zoom_start, tiles=map_tiles, attr=map_attr)
        # folium.TileLayer(map_tiles).add_to(self.fmap)

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
        self.fmap.add_child(folium.PolyLine(locations=point_list, weight=weight))

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
            point = [i.lat, i.lon]
            point_list.append(point)
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

        if not point_info == '':
            point_info += '<br>'

        for i in points:
            point_location = [i.lat, i.lon]

            if isinstance(i, RestTrkPoint):
                popup_info = ('休息點' + '<br>' +
                              str(i.get_start_time().strftime('%H:%M')) + ' ~ ' + str(i.get_end_time().strftime('%H:%M')) +
                              '<br>' + 'Elev: ' + str(round(i.elev, 0)) + ' M')
            else:
                popup_info = point_info+str(i.time.strftime('%H:%M'))+'<br>'+i.get_note()+'<br>'+str(round(i.elev, 0)) + " M"

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
        if not str(out_file).__contains__('.html'):
            out_file += '.html'
        self.fmap.save(out_file)
        print('saving map: {}'.format(out_file))
