

class Credentials:

    __slots__ = ('apikey', 'endpoint')

    def __init__(self, apikey: str, url: str) -> None:
        self.apikey = apikey
        self.endpoint = f'{url}/v2/management'
