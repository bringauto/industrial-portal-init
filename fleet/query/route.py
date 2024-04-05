from string import Template

from fleet.query.query import Query


class RouteAdder(Query):
    def __init__(self, endpoint: str, apikey: str, name: str, stops: list) -> None:
        super().__init__(endpoint, apikey)
        self.name = name
        self.stops = stops

    def get_query(self) -> str:
        return Template("""
            {
                "name": "$name",
                "stopIds": $stops
            }""").safe_substitute({'name': self.name, 'stops': self.stops})

    def handle_json_response(self, json_response: dict) -> None:
        pass


class RoutesInfoGetter(Query):
    """Call parent exec() function and then pass result to relevant member functions get ids"""

    def __init__(self, endpoint: str, apikey: str) -> None:
        super().__init__(endpoint, apikey)

    def get_query(self) -> str:
        return ""

    def handle_json_response(self, json_response: dict) -> None:
        pass

    def get_all_ids_from_json(self, json_response: dict) -> list:
        """Extracts all ids from json response"""
        ids = list()
        for route in json_response:
            ids.append(route["id"])
        return ids


class RouteDeleter(Query):
    def __init__(self, endpoint: str, apikey: str) -> None:
        super().__init__(endpoint, apikey)

    def get_query(self) -> str:
        return ""

    def handle_json_response(self, json_response: dict) -> None:
        pass
