from fleet.query.query import Query


class OrderInfoGetter(Query):
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
        for order in json_response:
            ids.append(order["id"])
        return ids

class OrderDeleter(Query):
    def __init__(self, endpoint: str, apikey: str) -> None:
        super().__init__(endpoint, apikey)

    def get_query(self) -> str:
        return ""

    def handle_json_response(self, json_response: dict) -> None:
        pass