import folium
from geoanalyzer.tracks.track_objects import RestTrkPoint

class FoliumMapDrawer:

    def __init__(self, location_x, location_y, zoom_start=16):

        self.fmap = folium.Map(location=[location_x, location_y], zoom_start=zoom_start)
        folium.TileLayer('openstreetmap').add_to(self.fmap)


    def add_poly_line(self, point_list, weight=8, color=None):
        self.fmap.add_child(folium.PolyLine(locations=point_list, weight=weight))

    def add_tracks(self, input_tracks, **kwargs):
        main_tracks_point_list = input_tracks.get_main_tracks_points_list()
        point_list = []
        for i in main_tracks_point_list:
            point = [i.get_lat(), i.get_lon()]
            point_list.append(point)
        self.fmap.add_child(folium.PolyLine(locations=point_list, **kwargs))


    def draw_points_on_map(self, points, point_type='marker', point_info='', point_color='green', point_radius=8, alpha=0.3):

        if not isinstance(points, list):
            points = [points]

        if not point_info=='':
            point_info+='<br>'

        for i in points:
            point_location = [i.get_lat(), i.get_lon()]

            if isinstance(i, RestTrkPoint):
                popup_info = '休息點'+'<br>'+str(i.get_start_time().strftime('%H:%M'))+' ~ '+str(i.get_end_time().strftime('%H:%M'))+'<br>'+'Elev: '+str(round(i.get_elev(), 0))+' M'
            else:
                popup_info = point_info+str(i.get_point_time().strftime('%H:%M'))+'<br>'+i.get_note()+'<br>'+str(round(i.get_elev(), 0)) +" M"

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

    def save(self, out_file:str):
        if not str(out_file).__contains__('.html'):
            out_file += '.html'
        self.fmap.save(out_file)
        print('saving map: {}'.format(out_file))


