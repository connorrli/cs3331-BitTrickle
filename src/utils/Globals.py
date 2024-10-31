class PacketTypes:
    # TYPES OF PACKETS
    AUTH = 1
    HBT = 2
    OK = 3
    ERR = 4

    _packet_names = {
        AUTH: "AUTH",
        HBT: "HBT",
        OK: "OK",
        ERR: "ERR"
    }

    @classmethod
    def get_name(cls, packet_type: int) -> str:
        return cls._packet_names.get(packet_type, "UNKNOWN")

class Env:
    CLIENT_IP = '127.0.0.1'
    SERVER_IP = '127.0.0.1'