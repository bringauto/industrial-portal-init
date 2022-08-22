from string import Template

from fleet.query.query import Query
from fleet.data.cookie import Cookie


class AdminAdder(Query):
    def __init__(self, endpoint: str, login_cookie: Cookie,
                 email: str, username: str, password: str, tenant: str) -> None:
        super().__init__(endpoint, login_cookie)
        self.email = email
        self.username = username
        self.password = password
        self.tenant = tenant

    def get_query(self) -> str:
        return Template("""
              mutation M{
              UserMutation{add(user : {
                    email : "$email",
                    password : "$password",
                    roles: "Admin",
                    userName: "$username"
                    newTenantName: "$tenant"
                }){
                succeeded
                errors {description, code}
              }
              }
            }
        """).safe_substitute(
            {'email': self.email, 'username': self.username, 'password': self.password,
             'tenant': self.tenant})

    def handle_json_response(self, json_response: dict) -> None:
        pass
