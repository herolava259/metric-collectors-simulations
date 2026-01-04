from enum import Enum 


class ExchangeType(str, Enum):
    Direct = "direct"
    Default = ""
    Fanout = "fanout"

class DeliveryMode(int, Enum):
    Basic = 1
    Persistent = 2 
