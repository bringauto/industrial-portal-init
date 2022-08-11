#!/usr/bin/env python3

import json
import argparse
import glob

from fleet.query.login import get_login_cookie, ENDPOINT
from fleet.query.utils import delete_all
from fleet.query.query import Query
from fleet.query.car import CarAdder
from fleet.query.user import UserAdder, UserInfoAboutMe
from fleet.query.station import StationAdder
from fleet.query.route import RouteAdder
from fleet.query.order import OrderAdder
from fleet.data.cookie import Cookie
from fleet.data.stop import Stop


def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', type=str, help='Directory with input files', default='config/*')
    return parser.parse_args()


def run_queries(json_config_path: str, endpoint: str, login_cookie: Cookie) -> None:
    with open(json_config_path, "r", encoding='utf-8') as json_file:
        json_config = json.load(json_file)
    if (len(json_config["users"]) > 1):
        raise Exception("Only one user is allowed")
    for user in json_config["users"]:
        UserAdder(endpoint, login_cookie, user["email"], user["username"],
                  user["password"], user["role"], json_config["tenant"]).exec()
    login_cookie = get_login_cookie(ENDPOINT, json_config["users"][0]["username"], json_config["users"][0]["password"])
    user_info = UserInfoAboutMe(endpoint, login_cookie).exec()
    Query.tenant_id = str(user_info["data"]["UserQuery"]["me"]["tenants"]["nodes"][0]["id"])
    delete_all(ENDPOINT, login_cookie)
    for station in json_config["stations"]:
        StationAdder(endpoint, login_cookie, station["name"], station["latitude"], station["longitude"],
                     station["contactPhone"]).exec()
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
    args = argument_parser()
    for config in glob.iglob(args.directory):
        Query.reset_tenant()
        try:
            login_cookie = get_login_cookie(ENDPOINT)
            run_queries(config, ENDPOINT, login_cookie)
        except Exception as exception:
            print(exception)
        else:
            print('Fleet database updated')


if __name__ == '__main__':
    main()
