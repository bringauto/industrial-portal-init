from string import Template

from fleet.query.query import Query


class StopAdder(Query):
    def __init__(self, endpoint: str, apikey: str, name: str,
                 latitude: float, longitude: float, contact_phone: str) -> None:
        super().__init__(endpoint, apikey)
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.contact_phone = contact_phone

    def get_query(self):
        return Template("""
            {
                "name": "$name",
                "notificationPhone": {
                    "phone": "$contactPhone"
                },
                "position": {
                    "altitude": 0,
                    "latitude": $latitude,
                    "longitude": $longitude
                }
            }""").safe_substitute({'name': self.name, 'latitude': self.latitude, 'longitude': self.longitude,
                                   'contactPhone': self.contact_phone})

    def handle_json_response(self, json_response: dict):
        pass


class StopInfoGetter(Query):
    """Call parent exec() function and then pass result to relevant member functions get ids"""

    def __init__(self, endpoint: str, apikey: str) -> None:
        super().__init__(endpoint, apikey)

    def get_query(self) -> str:
        return ""

    def handle_json_response(self, json_response: dict) -> None:
        pass

    def get_id_from_json(self, json_response: dict, station_name: str) -> int:
        """Extracts id from json response"""
        for station in json_response:
            if station["name"] == station_name:
                return station["id"]
        raise Exception(
                f"Station with name {station_name} doesn't exist!")
    
    def get_all_ids_from_json(self, json_response: dict) -> list:
        """Extracts all ids from json response"""
        ids = list()
        for stop in json_response:
            ids.append(stop["id"])
        return ids


class StopDeleter(Query):
    def __init__(self, endpoint: str, apikey: str) -> None:
        super().__init__(endpoint, apikey)

    def get_query(self) -> str:
        return ""

    def handle_json_response(self, json_response: dict) -> None:
        pass
