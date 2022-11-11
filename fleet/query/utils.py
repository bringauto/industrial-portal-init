import argparse
from os.path import isfile
from configparser import ConfigParser

from fleet.data.cookie import Cookie
from fleet.query.car import CarDeleter
from fleet.query.query import Query
from fleet.query.route import RouteDeleter
from fleet.query.stop import StopDeleter
from fleet.query.user import UserDeleter, UserInfoAboutMe


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
                  StopQuery{
                    stops{
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
                    users{
                        nodes{
                            userName
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
    for station_node in all_ids_json["data"]["StopQuery"]["stops"]["nodes"]:
        StopDeleter(station_node["id"], endpoint, login_cookie).exec()


class UsersGetter(Query):
    def get_query(self) -> str:
        return """
            query{
                UserQuery{
                    users{
                        nodes{
                            userName
                            roles
                        }
                    }
                }
            }
            """

    def handle_json_response(self, json_response: dict) -> None:
        pass


def delete_users(endpoint: str, login_cookie: Cookie) -> None:
    users_ids = UsersGetter(endpoint, login_cookie).exec()
    for user_node in users_ids["data"]["UserQuery"]["users"]["nodes"]:
        if user_node["userName"] != "Admin":
            UserDeleter(endpoint, login_cookie, user_node["userName"]).exec()


def set_tenant(endpoint: str, cookie: Cookie) -> None:
    user_info = UserInfoAboutMe(endpoint, cookie).exec()
    Query.tenant_id = str(user_info["data"]["UserQuery"]["me"]["tenants"]["nodes"][0]["id"])


def reset_tenant() -> None:
    Query.tenant_id = "-1"


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
