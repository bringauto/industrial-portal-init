from fleet.query.query import Query


class OrderInfoGetter(Query):
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
        for order in json_response:
            id_tuple = (order["carId"], order["id"])
            ids.append(id_tuple)
        return ids

class OrderDeleter(Query):
    def __init__(self, endpoint: str, apikey: str) -> None:
        super().__init__(endpoint, apikey)

    def get_query(self) -> str:
        return ""

    def handle_json_response(self, json_response: dict) -> None:
        pass