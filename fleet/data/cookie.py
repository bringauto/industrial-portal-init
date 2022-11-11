

class Cookie:
    """Class to hold data for cookie (now just key-value, but later can be added more)"""

    __slots__ = ('_key', '_value')

    def __init__(self, key: str, value: str) -> None:
        self._key = key
        self._value = value

    @property
    def key(self) -> str:
        return self._key

    @key.setter
    def key(self, key: str) -> None:
        self._key = key

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        self._value = value
