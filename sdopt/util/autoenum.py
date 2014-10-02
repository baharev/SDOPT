from enum import Enum

class AutoNumber(Enum):
    def __new__(cls):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj
    def __hash__(self):
        return self.__dict__['_value_']
    def __repr__(self):
        return self.__dict__['_name_']
