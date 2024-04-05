from string import Template

from fleet.query.query import Query
from fleet.query.route import RoutesInfoGetter


class CarAdder(Query):
    def __init__(self, endpoint: str, apikey: str, name: str, hw_id: int,
                 carAdminPhone: str, underTest: bool) -> None:
        super().__init__(endpoint, apikey)
        self.name = name
        self.hw_id = hw_id
        self.adminPhone = carAdminPhone
        self.underTest = 'true' if underTest else 'false'

    def get_query(self) -> str:
        routes = RoutesInfoGetter(
            self.endpoint.removesuffix("/car") + "/route", self.apikey).exec("GET")
        routeId = routes[0]["id"]
        return Template("""{
  "carAdminPhone": {
    "phone": "$adminPhone"
  },
  "defaultRouteId": $routeId,
  "name": "$name",
  "platformHwId": $hwId,
  "underTest": $underTest
}""").safe_substitute({'name': self.name, 'hwId': self.hw_id,
                       'underTest': self.underTest, 'adminPhone': self.adminPhone, 'routeId': routeId})

    def handle_json_response(self, json_response: dict) -> None:
        pass


class CarInfoGetter(Query):
    """Call parent exec() function and then pass result to function get_id_from_json() to get id"""

    def __init__(self, endpoint: str, apikey: str) -> None:
        super().__init__(endpoint, apikey)

    def get_query(self) -> str:
        return ""

    def handle_json_response(self, json_response: dict) -> None:
        pass

    def get_all_ids_from_json(self, json_response: dict) -> list:
        """Extracts ids from json response"""
        ids = list()
        for car in json_response:
            ids.append(car["id"])
        return ids


class CarDeleter(Query):
    def __init__(self, endpoint: str, apikey: str) -> None:
        super().__init__(endpoint, apikey)

    def get_query(self) -> str:
        return ""

    def handle_json_response(self, json_response: dict) -> None:
        pass
