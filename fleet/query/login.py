from string import Template

from fleet.query.query import Query
from fleet.data.cookie import Cookie


def login_query(username: str, password: str) -> str:
    """Gets query to login into portal - is used to get cookie and than use it later"""
    text_template = Template("""
        query UserLogin {
            UserQuery {
        login(login: {password: "$password", userName: "$username"}) {
          email
          roles
          tenants{nodes{id name}}
        }
        }
    }
    """)
    return text_template.safe_substitute({'password': password, 'username': username})


def get_login_cookie(endpoint: str, username: str, password: str) -> Cookie:
    """Logins to portal, which will response with cookie and function extracts it and returns it"""
    headers = {}
    query = login_query(username, password)
    response = Query.call_query(query, headers, endpoint)
    all_cookies = response.cookies.get_dict()
    cookie_key = ".AspNetCore.Identity.Application"
    login_cookie = Cookie(cookie_key, all_cookies[cookie_key])
    return login_cookie
