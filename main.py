#!/usr/bin/env python3

import glob
import json
import os

from fleet import argument_parser_init, config_parser_init, delete_all, file_exists
from fleet_management_http_client_python import (ApiClient, Configuration, StopApi, Stop, GNSSPosition,
                                                 RouteApi, Route, RouteVisualization, PlatformHWApi,
                                                 PlatformHW, CarApi, Car, MobilePhone)


def run_queries(api_client: ApiClient, json_config_path: str, already_added_cars: list) -> None:
    with open(json_config_path, "r", encoding='utf-8') as json_file:
        json_config = json.load(json_file)

    stop_api = StopApi(api_client)
    created_stops = list()
    for stop in json_config["stops"]:
        print(f"Creating stop, name: {stop['name']}")
        created_stops.append(stop_api.create_stop(Stop(
            name=stop["name"],
            position=GNSSPosition(latitude=stop["latitude"], longitude=stop["longitude"]),
            notificationPhone=MobilePhone(phone=stop["contactPhone"])
        )))

    route_api = RouteApi(api_client)
    created_routes = list()
    for route in json_config["routes"]:
        stops = route["stops"]
        stop_ids = list()
        visualization_stops = list()
        for stop in stops:
            visualization_stops.append(GNSSPosition(
                latitude=stop["latitude"],
                longitude=stop["longitude"]
            ))
            if stop["stationName"] == None:
                continue
            for created_stop in created_stops:
                if created_stop.name == stop["stationName"]:
                    stop_ids.append(created_stop.id)
        print(f"Creating route, name: {route['name']}")
        created_routes.append(route_api.create_route(Route(
            name=route["name"],
            stopIds=stop_ids
        )))
        for created_route in created_routes:
            if created_route.name == route["name"]:
                print(f"Setting route visualization for route {created_route.id}")
                route_api.redefine_route_visualization(RouteVisualization(
                    routeId=created_route.id,
                    hexcolor=route["color"],
                    points=visualization_stops
                ))
    
    platform_api = PlatformHWApi(api_client)
    car_api = CarApi(api_client)
    for car in json_config["cars"]:
        if car["name"] in already_added_cars:
            print(f"Car with name {car['name']} is already created; skipping\n")
            continue
        print(f"Creating platform hw, name: {car['name']}")
        new_platform = platform_api.create_hw(PlatformHW(name=car["name"]))
        print(f"Creating car, name: {car['name']}\n")
        car_api.create_car(Car(
            platformHwId=new_platform.id,
            name=car["name"],
            carAdminPhone=MobilePhone(phone=car["adminPhone"]),
            underTest=car["underTest"]
        ))
        already_added_cars.append(car["name"])


def main() -> None:
    args = argument_parser_init()
    if not file_exists(args.config):
        raise IOError(f"Input config file does not exist: {args.config}")
    config = config_parser_init(args.config)
    api_client = ApiClient(Configuration(
        host=config['DEFAULT']['Url'],
        api_key={'APIKeyAuth': config['DEFAULT']['ApiKey']}
    ))

    args.directory = os.path.join(args.directory, '')
    delete_all(api_client)
    print('Fleet management deleted\n')
    already_added_cars = list()
    for map_file in glob.iglob(f'{args.directory}*'):
        print(f"Processing file: {map_file}")
        try:
            run_queries(api_client, map_file, already_added_cars)
        except Exception as exception:
            print(exception)
            return
    print('Fleet management updated')


if __name__ == '__main__':
    main()
