from UDPHandler import UDPPacketHandling

class IncomingPacketHandler:
    def parse(packet: bytes):
        match UDPPacketHandling.get_message_type(packet):
            case GET:
                