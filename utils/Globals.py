class PacketTypes:
    # TYPES OF PACKETS, CAN REPRESENT UP TO 2^16 DIFFERENT TYPES.
    # IF NUMBER OF TYPES BECOMES DISGUSTING TO TRACK HERE, CAN ALWAYS
    # FIND A NEW WAY TO DO THIS.
    AUTH = 1
    HBT = 2
    OK = 3
    ERR = 4
    GET = 5
    LAP = 6
    PUB = 7
    LPF = 8
    UNP = 9
    SCH = 10

    _packet_names = {
        AUTH: "AUTH",
        HBT: "HBT",
        OK: "OK",
        ERR: "ERR",
        GET: "GET",
        LAP: "LAP",
        PUB: "PUB",
        LPF: "LPF",
        UNP: "UNP",
        SCH: "SCH"
    }

    @classmethod
    def get_name(cls, packet_type: int) -> str:
        return cls._packet_names.get(packet_type, "UNKNOWN")

class Env:
    CLIENT_IP = '127.0.0.1'
    SERVER_IP = '127.0.0.1'

class Sessions:
    INACTIVE_TIMEOUT = 3