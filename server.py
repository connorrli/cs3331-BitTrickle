import sys
import socket

from utils.Globals import Env, PacketTypes
from utils.networking.UDPHandler import UDPPacketHandling, UDPPacket
from utils.server import ServerPacketHandler
from utils.Exceptions import *
from utils.server.UserSessionsHandler import UserSessionsHandler
from utils.server.UserFilesHandler import UserFilesHandler
from utils.server.Logger import NetworkLogger

# Constants
server_port: int = int(sys.argv[1])
if sys.argv.__len__() != 2 or sys.argv[1].isnumeric() != True:
    print(f"Cannot run. Proper usage: python3 server.py <server_port>")
    exit()

def main():
    files_handler = UserFilesHandler()
    users_handler = UserSessionsHandler()

    packet_handler = ServerPacketHandler(files_handler, users_handler, Env.SERVER_IP, server_port)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((Env.SERVER_IP, server_port))

    while True:
        data: bytes = server_socket.recv(UDPPacket.UDP_PACKET_SIZE)
        source_address: tuple[str, int] = (UDPPacketHandling.get_source_ip(data), UDPPacketHandling.get_source_port(data))
        try:
            response: bytes = packet_handler.receive_packet(data)

            username: str = users_handler.get_user_from_addr((source_address[0], source_address[1]))
            target: str = f"{source_address[0]}:{source_address[1]}" if username == None else username
            NetworkLogger.log_sent_event(
                PacketTypes.OK, 
                source_address[1], 
                target
            )
        except CorruptPacketError:
            response: bytes = None
        except Exception:
            NetworkLogger.log_sent_event(
                PacketTypes.ERR, 
                source_address[1], 
                users_handler.get_user_from_addr(source_address)
            )

            response: bytes = UDPPacketHandling.create_udp_packet(
                Env.SERVER_IP, source_address[0], 
                server_port, source_address[1], 
                PacketTypes.ERR, "".encode("utf-8")
            )

        if response == None:
            continue
        
        server_socket.sendto(response, source_address)

if __name__ == "__main__":
    main()