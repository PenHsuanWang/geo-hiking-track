class BasicPoint:
    """
    Basic point object provide a template for all other types of geography gps point to save point
    """
    def __init__(self, time: str, lat: float, lon: float, elev: float):
        """
        Initializes a BasicPoint object, provide the basic information of a point
        input the gps track point's time, latitude, longitude, elevation
        :param time: datetime object
        :param lat: float
        :param lon: float
        :param elev: float
        """

        if time is not None:
            self._time = time
            self._lat = lat
            self._lon = lon
            self._elev = elev
            self._is_empty = False
        else:
            self._time = None
            self._lat = None
            self._lon = None
            self._elev = None
            self._is_empty = True

    @property
    def time(self):
        return self._time

    @property
    def lat(self):
        return self._lat

    @property
    def lon(self):
        return self._lon

    @property
    def elev(self):
        return self._elev

    @property
    def is_empty(self):
        return self._is_empty
    #
    # def get_point_time(self):
    #     return self._time
    #
    # def get_lat(self):
    #     return self._lat
    #
    # def get_lon(self):
    #     return self._lon
    #
    # def get_elev(self):
    #     return self._elev
    #
    # def is_empty(self):
    #     return self._is_empty
