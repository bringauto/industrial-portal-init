#!/usr/bin/env python3

import json

from fleet.query.Query import Query
from fleet.query.Login import get_login_cookie, ENDPOINT
from fleet.query.Car import CarAdder, CarDeleter
from fleet.query.User import UserAdder, UserDeleter
from fleet.query.Station import StationAdder, StationDeleter
from fleet.query.Route import RouteAdder, RouteDeleter
from fleet.query.Order import OrderAdder
from fleet.data.Cookie import Cookie
from fleet.data.Stop import Stop


class AllIdGetter(Query):
    def get_query(self) -> str:
        return """
                query QQ{
                  CarQuery{
                    cars{
                      nodes{
                        id
                      }
                    }
                  }
                  StationQuery{
                    stations{
                      nodes{
                        id
                      }
                    }
                  }
                  OrderQuery{
                    orders{
                    nodes{
                      id
                    }
                   }
                  }
                  RouteQuery{
                        routes{
                          nodes{
                            id
                          }
                       }
                    }
                  UserQuery{
                    all{
                        nodes{
                            email
                            userName
                            roles
                        }
                    }
                  }

                }
            """

    def handle_json_response(self, json_response: dict) -> None:
        pass


def delete_all(endpoint: str, login_cookie: Cookie) -> None:
    """Orders are deleted automatically after all other things deleted (I hope...)"""
    all_ids_json = AllIdGetter(endpoint, login_cookie).exec()
    for car_node in all_ids_json["data"]["CarQuery"]["cars"]["nodes"]:
        CarDeleter(car_node["id"], endpoint, login_cookie).exec()
    for route_node in all_ids_json["data"]["RouteQuery"]["routes"]["nodes"]:
        RouteDeleter(route_node["id"], endpoint, login_cookie).exec()
    for station_node in all_ids_json["data"]["StationQuery"]["stations"]["nodes"]:
        StationDeleter(station_node["id"], endpoint, login_cookie).exec()
    for user_node in all_ids_json["data"]["UserQuery"]["all"]["nodes"]:
        UserDeleter(user_node, endpoint, login_cookie).exec()


def run_queries(json_config_path: str, endpoint: str, login_cookie: Cookie) -> None:
    with open(json_config_path, "r", encoding='utf-8') as json_file:
        json_config = json.load(json_file)
    for station in json_config["stations"]:
        StationAdder(endpoint, login_cookie, station["name"], station["latitude"], station["longitude"],
                     station["contactPhone"]).exec()
    for user in json_config["users"]:
        UserAdder(endpoint, login_cookie, user["email"], user["username"],
                  user["password"], user["role"]).exec()
    for route in json_config["routes"]:
        stops_js = route["stops"]
        stops = list()
        # No need to write order numbers in json - stops are written in array, so order is guaranteed and
        # here are orders created programmatically
        order_counter = 0
        for stop_js in stops_js:
            stops.append(Stop(
                stop_js["latitude"], stop_js["longitude"], order_counter, stop_js["stationName"]))
            order_counter += 1
        RouteAdder(endpoint, login_cookie,
                   route["name"], route["color"], stops).exec()
    for car in json_config["cars"]:
        CarAdder(endpoint, login_cookie, car["name"], car["hwId"], car["companyName"],
                 car["adminPhone"], car["underTest"]).exec()
    for order in json_config["orders"]:
        OrderAdder(endpoint, login_cookie, order["carName"], order["fromStationName"],
                   order["toStationName"], order["priority"], order["arrive"],
                   order["fromStationPhone"], order["toStationPhone"]).exec()


def main() -> None:
    try:
        login_cookie = get_login_cookie(ENDPOINT)
        delete_all(ENDPOINT, login_cookie)
        run_queries("config.json", ENDPOINT, login_cookie)
    except Exception as exception:
        print(exception)
    else:
        print('Fleet database updated')


if __name__ == '__main__':
    main()
