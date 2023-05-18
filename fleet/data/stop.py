

class Stop:
    """Holds info about stop"""

    __slots__ = ('latitude', 'longitude', 'order', 'station_name')

    def __init__(self, latitude: float, longitude: float, order: int, station_name: str) -> None:
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.order = order
        self.station_name = station_name
