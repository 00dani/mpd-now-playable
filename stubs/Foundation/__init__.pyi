from typing import Type

class CGSize:
    width: float
    height: float

class NSMutableDictionary(dict[str, object]):
    @classmethod
    def dictionary(cls: Type[NSMutableDictionary]) -> NSMutableDictionary: ...
