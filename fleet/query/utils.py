from fleet.query.query import Query
from fleet.query.car import CarDeleter
from fleet.query.user import UserDeleter
from fleet.query.stop import StopDeleter
from fleet.query.route import RouteDeleter
from fleet.data.cookie import Cookie
from fleet.query.user import UserInfoAboutMe
from fleet.query.login import ENDPOINT


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
                    stop{
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
    for station_node in all_ids_json["data"]["StopQuery"]["stop"]["nodes"]:
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


def set_tenant(cookie: Cookie):
    user_info = UserInfoAboutMe(ENDPOINT, cookie).exec()
    Query.tenant_id = str(user_info["data"]["UserQuery"]["me"]["tenants"]["nodes"][0]["id"])


def reset_tenant():
    Query.tenant_id = "-1"
