import sys
import socket

# My package imports
from utils import Env, PacketTypes
from utils.networking import UDPPacketHandling
from utils.server import Authenticate, NetworkLogger

server_port: int = int(sys.argv[1])
if sys.argv.__len__() != 2 or sys.argv[1].isnumeric() != True:
    print(f"Cannot run. Proper usage: python3 server.py <server_port>")
    exit()

authenticator: Authenticate = Authenticate()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((Env.SERVER_IP, server_port))

    while True:
        data: bytes = server_socket.recv(1024)
        received_credentials: list[str] = UDPPacketHandling.get_payload(data).decode("utf-8").split(",")
        client_port: int = UDPPacketHandling.get_source_port(data)
        message_type: int = UDPPacketHandling.get_message_type(data)

        NetworkLogger.log_received_event(message_type, client_port, received_credentials[0])

        if authenticator.isValidLogin(received_credentials[0], received_credentials[1]):
            payload: bytes = UDPPacketHandling.create_udp_packet(
                Env.SERVER_IP, Env.CLIENT_IP, server_port, client_port, 
                PacketTypes.OK, "".encode("utf-8")
            )
            NetworkLogger.log_sent_event(PacketTypes.OK, client_port, received_credentials[0])
        else:
            payload: bytes = UDPPacketHandling.create_udp_packet(
                Env.SERVER_IP, Env.CLIENT_IP, server_port, client_port, 
                PacketTypes.ERR, "".encode("utf-8")
            )
            NetworkLogger.log_sent_event(PacketTypes.ERR, client_port, received_credentials[0])
        
        server_socket.sendto(payload, (Env.CLIENT_IP, client_port))

if __name__ == "__main__":
    main()