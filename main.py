#!/usr/bin/env python3

import glob
import json
import os

from fleet import (CarAdder, Credentials, PlatformAdder, PlatformInfoGetter,
                   RouteAdder, StopAdder, StopInfoGetter, argument_parser_init,
                   config_parser_init, delete_all, file_exists,)


def run_queries(credentials: Credentials, json_config_path: str) -> None:
    with open(json_config_path, "r", encoding='utf-8') as json_file:
        json_config = json.load(json_file)

    for stop in json_config["stops"]:
        StopAdder(credentials.endpoint + "/stop", credentials.apikey, stop["name"], stop["latitude"], stop["longitude"],
                  stop["contactPhone"]).exec("POST")

    for route in json_config["routes"]:
        stops_js = route["stops"]
        stopIds = list()
        for stop_js in stops_js:
            if stop_js["stationName"] == None:
                continue
            stopInfoGetter = StopInfoGetter(credentials.endpoint + "/stop", credentials.apikey)
            stopInfo = stopInfoGetter.exec("GET")
            stopIds.append(stopInfoGetter.get_id_from_json(stopInfo, stop_js["stationName"]))
        RouteAdder(credentials.endpoint + "/route", credentials.apikey,
                   route["name"], stopIds).exec("POST")

    for car in json_config["cars"]:
        PlatformAdder(credentials.endpoint + "/platformhw", credentials.apikey, car["name"]).exec("POST")
        platformInfoGetter = PlatformInfoGetter(credentials.endpoint + "/platformhw", credentials.apikey)
        platformInfo = platformInfoGetter.exec("GET")
        platformId = platformInfoGetter.get_id_from_json(platformInfo, car["name"])
        CarAdder(credentials.endpoint + "/car", credentials.apikey, car["name"], platformId,
                 car["adminPhone"], car["underTest"]).exec("POST")


def main() -> None:
    args = argument_parser_init()
    if not file_exists(args.config):
        raise IOError(f"Input config file does not exist: {args.config}")
    config = config_parser_init(args.config)
    credentials = Credentials(config['DEFAULT']['ApiKey'], config['DEFAULT']['Url'])

    args.directory = os.path.join(args.directory, '')
    delete_all(credentials.endpoint, credentials.apikey)
    for map_file in glob.iglob(f'{args.directory}*'):
        try:
            run_queries(credentials, map_file)
        except Exception as exception:
            print(exception)
            return
    print('Fleet management updated')


if __name__ == '__main__':
    main()
