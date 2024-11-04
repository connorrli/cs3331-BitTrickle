import sys
import socket

# My package imports
from utils.Globals import Env, PacketTypes
from utils.networking.UDPHandler import UDPPacketHandling, UDPPacket
from utils.server import NetworkLogger, ServerPacketHandler
from utils.Exceptions import *

server_port: int = int(sys.argv[1])
if sys.argv.__len__() != 2 or sys.argv[1].isnumeric() != True:
    print(f"Cannot run. Proper usage: python3 server.py <server_port>")
    exit()

def main():
    packet_handler = ServerPacketHandler(Env.SERVER_IP, server_port)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((Env.SERVER_IP, server_port))

    while True:
        data: bytes = server_socket.recv(UDPPacket.UDP_PACKET_SIZE)
        source_addr: tuple[str, int] = (UDPPacketHandling.get_source_ip(data), UDPPacketHandling.get_source_port(data))
        response: bytes = packet_handler.receive_packet(data)
        if response == None:
            continue
        
        server_socket.sendto(response, source_addr)

if __name__ == "__main__":
    main()