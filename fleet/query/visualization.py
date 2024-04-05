from string import Template

from fleet.query.query import Query


class VisualizationAdder(Query):
    def __init__(self, endpoint: str, apikey: str, color: str, routeId: int, points: list) -> None:
        super().__init__(endpoint, apikey)
        self.color = color
        self.points = points
        self.routeId = routeId

    def get_query(self) -> str:
        return Template("""
            {
                "hexcolor": "$color",
                "routeId": $routeId,
                "points': $points
            }""").safe_substitute({'color': self.color, 'routeId': self.routeId, 'points': self.points})

    def handle_json_response(self, json_response: dict) -> None:
        pass
