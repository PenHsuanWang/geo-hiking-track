import math

class TrackPointVector:

    def __init__(self, track_point_1, track_point_2):
        """
        Provide two track points and get the vector (point2 - point1)
        :param track_point_1: vector start point
        :param track_point_2: vector end point
        """

        self._track_point_1 = track_point_1
        self._track_point_2 = track_point_2

    def get_x_component(self):
        return(self._track_point_2.lon - self._track_point_1.lon) * 101751

    def get_y_component(self):
        return(self._track_point_2.lat - self._track_point_1.lat) * 110757

    def get_length(self):
        return math.sqrt( math.pow(self.get_x_component(), 2) + math.pow(self.get_y_component(), 2) )

    def get_vector(self):
        return [self.get_x_component(), self.get_y_component()]

    def get_init_point(self):
        return self._track_point_1

    def get_end_point(self):
        return self._track_point_2

