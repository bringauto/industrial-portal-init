#!/usr/bin/env python3

import glob
import json
import os

from fleet import (AdminAdder, CarAdder, Credentials, OrderAdder, RouteAdder,
                   Stop, StopAdder, UserAdder, argument_parser_init,
                   config_parser_init, delete_all, delete_users, file_exists,
                   get_login_cookie, reset_tenant, set_tenant)


def run_queries(credentials: Credentials, json_config_path: str) -> None:
    with open(json_config_path, "r", encoding='utf-8') as json_file:
        json_config = json.load(json_file)

    reset_tenant()
    login_cookie = get_login_cookie(credentials.endpoint, credentials.username, credentials.password)
    set_tenant(credentials.endpoint, login_cookie)
    AdminAdder(credentials.endpoint, login_cookie, json_config["admin"]["email"], json_config["admin"]["username"],
               json_config["admin"]["password"], json_config["tenant"]).exec()

    reset_tenant()
    login_cookie = get_login_cookie(
        credentials.endpoint, json_config["admin"]["username"], json_config["admin"]["password"])
    set_tenant(credentials.endpoint, login_cookie)

    for user in json_config["users"]:
        if(user["role"].lower() == "admin"):
            raise Exception("User cannot have admin role")
        UserAdder(credentials.endpoint, login_cookie, user["email"], user["username"],
                  user["password"], user["role"]).exec()

    delete_all(credentials.endpoint, login_cookie)

    for stop in json_config["stops"]:
        StopAdder(credentials.endpoint, login_cookie, stop["name"], stop["latitude"], stop["longitude"],
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
        RouteAdder(credentials.endpoint, login_cookie,
                   route["name"], route["color"], stops).exec()

    for car in json_config["cars"]:
        CarAdder(credentials.endpoint, login_cookie, car["name"], car["hwId"], json_config["tenant"],
                 car["adminPhone"], car["underTest"]).exec()

    for order in json_config["orders"]:
        OrderAdder(credentials.endpoint, login_cookie, order["carName"], order["fromStationName"],
                   order["toStationName"], order["priority"], order["arrive"],
                   order["fromStationPhone"], order["toStationPhone"]).exec()


def main() -> None:
    args = argument_parser_init()
    if not file_exists(args.config):
        raise IOError(f"Input config file does not exist: {args.config}")
    config = config_parser_init(args.config)
    credentials = Credentials(config['DEFAULT']['Username'], config['DEFAULT']['Password'],
                              config['DEFAULT']['Url'], config['DEFAULT']['Port'])

    login_cookie = get_login_cookie(credentials.endpoint, credentials.username, credentials.password)
    delete_users(credentials.endpoint, login_cookie)
    args.directory = os.path.join(args.directory, '')
    for map_file in glob.iglob(f'{args.directory}*'):
        try:
            run_queries(credentials, map_file)
        except Exception as exception:
            print(exception)
            return
    print('Fleet database updated')


if __name__ == '__main__':
    main()
