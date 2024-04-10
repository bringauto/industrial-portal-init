import argparse
from os.path import isfile
from configparser import ConfigParser

from fleet.query.car import CarDeleter, CarInfoGetter
from fleet.query.order import OrderDeleter, OrderInfoGetter
from fleet.query.platform import PlatformDeleter, PlatformInfoGetter
from fleet.query.route import RouteDeleter, RoutesInfoGetter
from fleet.query.stop import StopDeleter, StopInfoGetter


def delete_all(endpoint: str, apikey: str) -> None:
    order_info_getter = OrderInfoGetter(endpoint + "/order", apikey)
    order_info = order_info_getter.exec("GET")
    order_ids = order_info_getter.get_all_ids_from_json(order_info)
    for order_id in order_ids:
        OrderDeleter(endpoint + "/order/" + str(order_id[0]) + "/" + str(order_id[1]), apikey).exec("DELETE")
    car_info_getter = CarInfoGetter(endpoint + "/car", apikey)
    car_info = car_info_getter.exec("GET")
    car_ids = car_info_getter.get_all_ids_from_json(car_info)
    for car_id in car_ids:
        CarDeleter(endpoint + "/car/" + str(car_id), apikey).exec("DELETE")
    platform_info_getter = PlatformInfoGetter(endpoint + "/platformhw", apikey)
    platform_info = platform_info_getter.exec("GET")
    platform_ids = platform_info_getter.get_all_ids_from_json(platform_info)
    for platform_id in platform_ids:
        PlatformDeleter(endpoint + "/platformhw/" + str(platform_id), apikey).exec("DELETE")
    route_info_getter = RoutesInfoGetter(endpoint + "/route", apikey)
    route_info = route_info_getter.exec("GET")
    route_ids = route_info_getter.get_all_ids_from_json(route_info)
    for route_id in route_ids:
        RouteDeleter(endpoint + "/route/" + str(route_id), apikey).exec("DELETE")
    stop_info_getter = StopInfoGetter(endpoint + "/stop", apikey)
    stop_info = stop_info_getter.exec("GET")
    stop_ids = stop_info_getter.get_all_ids_from_json(stop_info)
    for stop_id in stop_ids:
        StopDeleter(endpoint + "/stop/" + str(stop_id), apikey).exec("DELETE")


def argument_parser_init() -> argparse.Namespace:
    """
    Initialize argument parser

    Return
    ------
    argparse.Namespace : object with atributes
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', type=str,
                        help='Config file, default is config/config.ini', default='config/config.ini')
    parser.add_argument('-d', '--directory', type=str,
                        help='Directory with input files, default is maps/', default='maps/')
    return parser.parse_args()


def config_parser_init(filename: str) -> ConfigParser:
    """
    Initialize config parser

    Parameters
    ----------
    filename : str
        Input config file

    Return
    ------
    ConfigParser : config parser
    """
    config = ConfigParser()
    config.read(filename)
    return config


def file_exists(filename: str) -> bool:
    """
    Check if file exists

    Parameters
    ----------
    filename : str
        File to check

    Return
    ------
    bool : True if exists otherwise False
    """
    return isfile(filename)
