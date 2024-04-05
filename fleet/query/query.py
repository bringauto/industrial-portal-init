import json
from typing import Any
import requests
from abc import ABC, abstractmethod


class Query(ABC):
    """Parent class for queries that add entities to portal."""

    def __init__(self, endpoint: str, apikey: str) -> None:
        self.endpoint = endpoint
        self.apikey = apikey

    def exec(self, method: str) -> Any:
        response = self.call_query(self.get_query(), self.endpoint + "?api_key=" + self.apikey, method)
        if "errors" in response.json():
            raise Exception("Query problem: " + json.dumps(response.json()))
        self.handle_json_response(response.json())
        return response.json()

    @staticmethod
    def call_query(query: str, endpoint: str, method: str) -> requests.models.Response:
        print(f"\nEndpoint: {endpoint}")
        print(f"Method: {method}")
        print(f"Query: {query}")
        json_query = None
        response = None
        if method == "GET":
            response = requests.get(
                endpoint, json=json_query)
        elif method == "POST":
            json_query = json.loads(query)
            response = requests.post(
                endpoint, json=json_query)
        elif method == "DELETE":
            response = requests.delete(
                endpoint, json=json_query)
        if response.status_code == 200:
            return response
        else:
            raise Exception(f"Query failed {response.status_code}")

    @abstractmethod
    def get_query(self) -> str:
        """This is implemented in each child class - creates query for each case (adding Car, User, ...)"""
        pass

    @abstractmethod
    def handle_json_response(self, json_response: dict) -> None:
        """If user sends bad data in query to server, he will get error response, but responses differ, so has to be
        implemented for different cases"""
        pass
