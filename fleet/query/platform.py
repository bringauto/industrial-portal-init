from string import Template

from fleet.query.query import Query


class PlatformAdder(Query):
    def __init__(self, endpoint: str, apikey: str, name: str) -> None:
        super().__init__(endpoint, apikey)
        self.name = name

    def get_query(self) -> str:
        return Template("""
            {
                "name": "$name"
            }""").safe_substitute({'name': self.name})

    def handle_json_response(self, json_response: dict) -> None:
        pass

class PlatformInfoGetter(Query):
    """Call parent exec() function and then pass result to relevant member functions get ids"""

    def __init__(self, endpoint: str, apikey: str) -> None:
        super().__init__(endpoint, apikey)

    def get_query(self) -> str:
        return ""

    def handle_json_response(self, json_response: dict) -> None:
        pass

    def get_id_from_json(self, json_response: dict, platform_name: str) -> int:
        """Extracts id from json response"""
        for platform in json_response:
            if platform["name"] == platform_name:
                return platform["id"]
        raise Exception(
                f"Platform with name {platform_name} doesn't exist!")
    
    def get_all_ids_from_json(self, json_response: dict) -> list:
        """Extracts all ids from json response"""
        ids = list()
        for platform in json_response:
            ids.append(platform["id"])
        return ids
    
class PlatformDeleter(Query):
    def __init__(self, endpoint: str, apikey: str) -> None:
        super().__init__(endpoint, apikey)

    def get_query(self) -> str:
        return ""

    def handle_json_response(self, json_response: dict) -> None:
        pass