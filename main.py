#!/usr/bin/env python3

import json
import argparse
import glob

from fleet.query.login import get_login_cookie, ENDPOINT
from fleet.query.utils import delete_all, delete_users, set_tenant, reset_tenant
from fleet.query.admin import AdminAdder
from fleet.query.car import CarAdder
from fleet.query.user import UserAdder
from fleet.query.stop import StopAdder
from fleet.query.route import RouteAdder
from fleet.query.order import OrderAdder
from fleet.data.stop import Stop


def argument_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directory', type=str, help='Directory with input files', default='config/*')
    return parser.parse_args()


def run_queries(json_config_path: str) -> None:
    with open(json_config_path, "r", encoding='utf-8') as json_file:
        json_config = json.load(json_file)

    login_cookie = get_login_cookie(ENDPOINT)
    set_tenant(login_cookie)
    AdminAdder(ENDPOINT, login_cookie, json_config["admin"]["email"], json_config["admin"]["username"],
               json_config["admin"]["password"], json_config["tenant"]).exec()

    reset_tenant()
    login_cookie = get_login_cookie(ENDPOINT, json_config["admin"]["username"], json_config["admin"]["password"])
    set_tenant(login_cookie)

    for user in json_config["users"]:
        if(user["role"].lower() == "admin"):
            raise Exception("User cannot have admin role")
        UserAdder(ENDPOINT, login_cookie, user["email"], user["username"],
                  user["password"], user["role"]).exec()

    delete_all(ENDPOINT, login_cookie)

    for stop in json_config["stops"]:
        StopAdder(ENDPOINT, login_cookie, stop["name"], stop["latitude"], stop["longitude"],
                  stop["contactPhone"]).exec()

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
        RouteAdder(ENDPOINT, login_cookie,
                   route["name"], route["color"], stops).exec()

    for car in json_config["cars"]:
        CarAdder(ENDPOINT, login_cookie, car["name"], car["hwId"], car["companyName"],
                 car["adminPhone"], car["underTest"]).exec()

    for order in json_config["orders"]:
        OrderAdder(ENDPOINT, login_cookie, order["carName"], order["fromStationName"],
                   order["toStationName"], order["priority"], order["arrive"],
                   order["fromStationPhone"], order["toStationPhone"]).exec()


def main() -> None:
    args = argument_parser()
    login_cookie = get_login_cookie(ENDPOINT)
    delete_users(ENDPOINT, login_cookie)
    for config in glob.iglob(args.directory):
        try:
            run_queries(config)
        except Exception as exception:
            print(exception)
            return
    print('Fleet database updated')


if __name__ == '__main__':
    main()
