import json
import requests
from abc import ABC, abstractmethod
from string import Template

LOGIN_USERNAME = "Admin"
LOGIN_PASSWORD = "Admin1"
COOKIE_KEY = ".AspNetCore.Identity.Application"
ENDPOINT = "http://localhost:8011/graphql"


def login_query(username: str, password: str) -> str:
    """Gets query to login into portal - is used to get cookie and than use it later"""
    text_template = Template("""
        query UserLogin {
            UserQuery {
        login(login: {password: "$password", userName: "$username"}) {
          email
          roles
        }
        }
    }
    """)
    return text_template.safe_substitute({'password': password, 'username': username})


class LoginCookie:
    """Class to hold data for cookie (now just key-value, but later can be added more)"""

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def get_key(self):
        return self.key

    def get_value(self):
        return self.value


def get_login_cookie(endpoint: str) -> LoginCookie:
    """Logins to portal, which will response with cookie and function extracts it and returns it"""
    headers = {}
    query = login_query(LOGIN_USERNAME, LOGIN_PASSWORD)
    response = Query.call_query(query, headers, endpoint)
    all_cookies = response.cookies.get_dict()
    login_cookie = LoginCookie(COOKIE_KEY, all_cookies[COOKIE_KEY])
    return login_cookie


class Query(ABC):
    """Parent class for queries that add entities to portal."""

    def __init__(self, endpoint, login_cookie):
        self.endpoint = endpoint
        self.login_cookie = login_cookie

    def exec(self):
        headers = {"Cookie": f"{self.login_cookie.get_key()}={self.login_cookie.get_value()}"}
        response = self.call_query(self.get_query(), headers, self.endpoint)
        if "errors" in response.json():
            raise Exception("Query problem: " + json.dumps(response.json()))
        # Portal sometimes responds with error (if adding user with short password etc.)
        self.handle_json_response(response.json())
        return response.json()

    @staticmethod
    def call_query(query: str, headers, endpoint: str):
        response = requests.post(endpoint, json={"query": query}, headers=headers)
        if response.status_code == 200:
            return response
        else:
            raise Exception(f"Query failed {response.status_code}")

    @abstractmethod
    def get_query(self) -> str:
        """This is implemented in each child class - creates query for each case (adding Car, User, ...)"""
        pass

    @abstractmethod
    def handle_json_response(self, json_response):
        """If user sends bad data in query to server, he will get error response, but responses differ, so has to be
        implemented for different cases"""
        pass


class UserAdder(Query):
    def __init__(self, endpoint, login_cookie, email: str, username: str, password: str, role: str):
        super().__init__(endpoint, login_cookie)
        self.email = email
        self.username = username
        self.password = password
        self.role = role

    def get_query(self):
        return Template("""
              mutation M{
              UserMutation{add(user : {
                    email : "$email",
                    password : "$password",
                    roles: "$role",
                    userName: "$username"
                }){
                succeeded
                errors {description, code}
              }
              }
            }
        """).safe_substitute(
            {'email': self.email, 'username': self.username, 'password': self.password, 'role': self.role})

    def handle_json_response(self, json_response):
        if not json_response["data"]["UserMutation"]["add"]["succeeded"]:
            print("-----PROBLEM-----")
            print(json_response)
            print("-------------")


class CarAdder(Query):
    def __init__(self, endpoint, login_cookie, name: str, hw_id: str, comapanyName: str,
                 carAdminPhone: str, underTest: bool):
        super().__init__(endpoint, login_cookie)
        self.name = name
        self.hw_id = hw_id
        self.companyName = comapanyName
        self.adminPhone = carAdminPhone
        self.underTest = underTest

    def get_query(self):
        t = Template("""
            mutation M{
              CarMutation{
              addCar(car : {name : "$name", hwId : "$hwId", companyName: "$companyName",
                underTest: true, carAdminPhone: "$adminPhone"
               }){
                id
                name
                token
                companyName
                carAdminPhone
              }
              }
            }
        """).safe_substitute({'name': self.name, 'hwId': self.hw_id, 'companyName': self.companyName,
                              'underTest': self.underTest, 'adminPhone': self.adminPhone})
        return t

    def handle_json_response(self, json_response):
        # Car adding does not return any errors, always success even if car already exists
        print(json_response)


class StationAdder(Query):
    def __init__(self, endpoint, login_cookie, name: str, latitude: float, longitude: float, contact_phone):
        super().__init__(endpoint, login_cookie)
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.contact_phone = contact_phone

    def get_query(self):
        return Template("""
                mutation Q{
                  StationMutation{addStation(station: {name: "$name", latitude: $latitude, longitude: $longitude,
                                contactPhone: "$contactPhone"}){
                    id
                  }
                  }
                }
            """).safe_substitute({'name': self.name, 'latitude': self.latitude, 'longitude': self.longitude,
                                  'contactPhone': self.contact_phone})

    def handle_json_response(self, json_response):
        pass


class CarInfoGetter(Query):
    """Call parent exec() function and then pass result to function get_id_from_json() to get id"""
    def __init__(self, endpoint, login_cookie, car_name):
        super().__init__(endpoint, login_cookie)
        self.car_name = car_name

    def get_query(self) -> str:
        return Template("""
            query Q{
              CarQuery{
                cars(where: {name: "$name"}){
                  nodes{
                    id
                    name
                  }
                }
              }
        }
        """).safe_substitute({'name': self.car_name})

    def handle_json_response(self, json_response):
        pass

    def get_id_from_json(self, json_response):
        """Extracts id from json response"""
        cars = json_response["data"]["CarQuery"]["cars"]["nodes"]
        if len(cars) == 0:
            raise Exception(f"Car with name {self.car_name} doesn't exists!")
        if len(cars) > 1:
            raise Exception(f"There is more ({len(cars)}) cars with name {self.car_name}!")
        return cars[0]["id"]


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

                }
            """

    def handle_json_response(self, json_response):
        pass


class RouteDeleter(Query):
    def __init__(self, route_id: int, endpoint, login_cookie):
        super().__init__(endpoint, login_cookie)
        self.route_id = route_id

    def get_query(self) -> str:
        return Template("""
            mutation DeleteRoute{
              RouteMutation{
                deleteRoute(routeId: $routeId){
                  id
                }
              }
            }
        """).safe_substitute({'routeId': self.route_id})

    def handle_json_response(self, json_response):
        pass


class CarDeleter(Query):
    def __init__(self, car_id: int, endpoint, login_cookie):
        super().__init__(endpoint, login_cookie)
        self.car_id = car_id

    def get_query(self) -> str:
        templ = Template("""
            mutation DeleteCar{
              CarMutation{
                deleteCar(carId: $carId){
                  id
                }
              }
            }
        """).safe_substitute({'carId': self.car_id})
        return templ

    def handle_json_response(self, json_response):
        pass


class StationDeleter(Query):
    def __init__(self, station_id: int, endpoint, login_cookie):
        super().__init__(endpoint, login_cookie)
        self.station_id = station_id

    def get_query(self) -> str:
        return Template("""
            mutation DeleteStation{
              StationMutation{
                deleteStation(stationId: $stationId){
                  id
                }
              }
            }
        """).safe_substitute({'stationId': self.station_id})

    def handle_json_response(self, json_response):
        pass


def delete_all(endpoint, login_cookie):
    """Doesn't delete users! Orders are deleted automatically after all other things deleted (I hope...)"""
    all_ids_json = AllIdGetter(endpoint, login_cookie).exec()
    for car_node in all_ids_json["data"]["CarQuery"]["cars"]["nodes"]:
        CarDeleter(car_node["id"], endpoint, login_cookie).exec()
    for route_node in all_ids_json["data"]["RouteQuery"]["routes"]["nodes"]:
        RouteDeleter(route_node["id"], endpoint, login_cookie).exec()
    for station_node in all_ids_json["data"]["StationQuery"]["stations"]["nodes"]:
        StationDeleter(station_node["id"], endpoint, login_cookie).exec()


class StationInfoGetter(Query):
    """Call parent exec() function and then pass result to function get_id_from_json() to get id"""
    def __init__(self, endpoint, login_cookie, station_name):
        super().__init__(endpoint, login_cookie)
        self.station_name = station_name

    def get_query(self) -> str:
        return Template("""
            query Q{
              StationQuery{
                stations(where: {name:"$name"}){
                  nodes{id name}
                }
              }
            }
        """).safe_substitute({'name': self.station_name})

    def handle_json_response(self, json_response):
        pass

    def get_id_from_json(self, json_response):
        """Extracts id from json response"""
        stations = json_response["data"]["StationQuery"]["stations"]["nodes"]
        if len(stations) == 0:
            raise Exception(f"Station with name {self.station_name} doesn't exists!")
        if len(stations) > 1:
            raise Exception(f"There is more ({len(stations)}) stations with name {self.station_name}!")
        return stations[0]["id"]


class OrderAdder(Query):
    """We can't set id of cars and stations, so in config file, we have to connect order to car by name and
    then here in constructor find id associated to it"""
    def __init__(self, endpoint: str, login_cookie: LoginCookie, car_name, from_station_name, to_station_name, priority,
                 arrive, from_station_phone, to_station_phone):
        super().__init__(endpoint, login_cookie)
        self.car_name = car_name
        self.from_station_name = from_station_name
        self.to_station_name = to_station_name
        self.priority = priority
        self.arrive = arrive
        self.from_station_phone = from_station_phone
        self.to_station_phone = to_station_phone
        car_info_getter = CarInfoGetter(self.endpoint, self.login_cookie, car_name)
        self.car_id = car_info_getter.get_id_from_json(car_info_getter.exec())
        station_info_getter = StationInfoGetter(self.endpoint, self.login_cookie, from_station_name)
        self.from_station_id = station_info_getter.get_id_from_json(station_info_getter.exec())
        station_info_getter = StationInfoGetter(self.endpoint, self.login_cookie, to_station_name)
        self.to_station_id = station_info_getter.get_id_from_json(station_info_getter.exec())

    def get_query(self) -> str:
        return Template("""
            mutation M{
              OrderMutation{
                addOrder(order:{arrive : "$arrive",
                         carId: $carId,
                         priority: $priority,
                         fromStationId: $fromStationId, 
                         toStationId: $toStationId,
                         toStationPhone: "$toStationPhone",
                         fromStationPhone: "$fromStationPhone"})
                {
                id
              }
              }
            }
        """).safe_substitute({'arrive': self.arrive, 'carId': self.car_id, 'priority': self.priority,
                              'fromStationId': self.from_station_id, 'toStationId': self.to_station_id,
                              'toStationPhone': self.to_station_phone,
                              'fromStationPhone': self.from_station_phone})

    def handle_json_response(self, json_response):
        pass


class Stop:
    """Holds info about stop"""

    def __init__(self, latitude, longitude, order, station_name: str):
        self.latitude = latitude
        self.longitude = longitude
        self.order = order
        self.station_name = station_name


class RouteAdder(Query):
    def __init__(self, endpoint, login_cookie, name, color, stops):
        super().__init__(endpoint, login_cookie)
        self.name = name
        self.color = color
        self.stops = stops

    def get_query(self):
        stops_query_part = ""
        i = 0
        for stop in self.stops:  # creates string of stops in GraphQL format. Example:
            # {latitude: 2.68, longitude: 5.3, $order: 1}, ...
            station_query_part = "station: null"
            if stop.station_name is not None:
                station_info = StationInfoGetter(self.endpoint, self.login_cookie, stop.station_name)
                station_id = station_info.get_id_from_json(station_info.exec())
                station_query_part = Template("station: { id: $station_id }").safe_substitute({'station_id': station_id})
            stops_query_part += Template("""{
                latitude: $latitude,
                longitude: $longitude,
                order: $order,
                $station_query_part
            }""").safe_substitute(
                {'latitude': stop.latitude, 'longitude': stop.longitude, 'order': stop.order,
                 'station_query_part': station_query_part}
            )
            if i < (len(self.stops) - 1):
                stops_query_part += ","  # comma between except last stop
            i += 1
        return Template("""
                    mutation M{
                      RouteMutation{addRoute(route : {name: "$name", color: "$color", stops: [
                        $stops
                      ]}){
                        id
                      }
                      }
                    }
            """).safe_substitute({'name': self.name, 'color': self.color, 'stops': stops_query_part})

    def handle_json_response(self, json_response):
        pass


def run_queries(json_config_path: str, endpoint, login_cookie: LoginCookie):
    with open(json_config_path, "r") as json_file:
        json_config = json.load(json_file)
    for car in json_config["cars"]:
        CarAdder(endpoint, login_cookie, car["name"], car["hwId"], car["companyName"],
                 car["adminPhone"], car["underTest"]).exec()
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
            stops.append(Stop(stop_js["latitude"], stop_js["longitude"], order_counter, stop_js["stationName"]))
            order_counter += 1
        RouteAdder(endpoint, login_cookie, route["name"], route["color"], stops).exec()
    for order in json_config["orders"]:
        OrderAdder(endpoint, login_cookie, order["carName"], order["fromStationName"],
                   order["toStationName"], order["priority"], order["arrive"],
                   order["fromStationPhone"], order["toStationPhone"]).exec()


if __name__ == '__main__':
    login_cookie = get_login_cookie(ENDPOINT)
    delete_all(ENDPOINT, login_cookie)
    run_queries("config.json", ENDPOINT, login_cookie)
