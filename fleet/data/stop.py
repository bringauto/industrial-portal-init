

class Stop:
    """Holds info about stop"""

    def __init__(self, latitude: float, longitude: float, order: int, station_name: str) -> None:
        self.latitude = latitude
        self.longitude = longitude
        self.order = order
        self.station_name = station_name
