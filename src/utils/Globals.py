class PacketTypes:
    # TYPES OF PACKETS
    AUTH = 1
    HBT = 2
    OK = 3
    ERR = 4
    GET = 5

    _packet_names = {
        AUTH: "AUTH",
        HBT: "HBT",
        OK: "OK",
        ERR: "ERR",
        GET: "GET"
    }

    @classmethod
    def get_name(cls, packet_type: int) -> str:
        return cls._packet_names.get(packet_type, "UNKNOWN")

class Env:
    CLIENT_IP = '127.0.0.1'
    SERVER_IP = '127.0.0.1'

class Sessions:
    INACTIVE_TIMEOUT = 3