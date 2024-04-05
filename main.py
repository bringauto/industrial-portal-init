#!/usr/bin/env python3

import glob
import json
import os

from fleet import (CarAdder, Credentials, PlatformAdder, PlatformInfoGetter,
                   RouteAdder, RoutesInfoGetter, StopAdder, StopInfoGetter,
                   VisualizationAdder, argument_parser_init, config_parser_init,
                   delete_all, file_exists)


def run_queries(credentials: Credentials, json_config_path: str) -> None:
    with open(json_config_path, "r", encoding='utf-8') as json_file:
        json_config = json.load(json_file)

    for stop in json_config["stops"]:
        StopAdder(credentials.endpoint + "/stop", credentials.apikey, stop["name"], stop["latitude"], stop["longitude"],
                  stop["contactPhone"]).exec("POST")

    for route in json_config["routes"]:
        stops_js = route["stops"]
        stopIds = list()
        visualizationStops = list()
        for stop_js in stops_js:
            visualizationStops.append(stop_js)
            if stop_js["stationName"] == None:
                continue
            stopInfoGetter = StopInfoGetter(credentials.endpoint + "/stop", credentials.apikey)
            stopIds.append(stopInfoGetter.get_id_from_json(stopInfoGetter.exec("GET"), stop_js["stationName"]))
        RouteAdder(credentials.endpoint + "/route", credentials.apikey,
                   route["name"], stopIds).exec("POST")
        routesInfo= RoutesInfoGetter(credentials.endpoint + "/route", credentials.apikey).exec("GET")
        #for createdRoute in routesInfo:
        #    if createdRoute["name"] == route["name"]:
        #        VisualizationAdder(credentials.endpoint + "/route-visualization", credentials.apikey,
        #                           route["color"], createdRoute["id"], visualizationStops).exec("POST")

    already_added_cars = list()
    for car in json_config["cars"]:
        if car["name"] in already_added_cars:
            print(f"Car with name {car['name']} is already created; skipping")
            continue
        PlatformAdder(credentials.endpoint + "/platformhw", credentials.apikey, car["name"]).exec("POST")
        platformInfoGetter = PlatformInfoGetter(credentials.endpoint + "/platformhw", credentials.apikey)
        platformId = platformInfoGetter.get_id_from_json(platformInfoGetter.exec("GET"), car["name"])
        CarAdder(credentials.endpoint + "/car", credentials.apikey, car["name"], platformId,
                 car["adminPhone"], car["underTest"]).exec("POST")
        already_added_cars.append(car["name"])


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
