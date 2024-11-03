import socket
import threading
import time

from utils.Globals import Env, PacketTypes
from utils.networking.UDPHandler import UDPPacketHandling, UDPPacket, UDPHbtPacket

class ClientHandler:
    @staticmethod
    def new_client(connection, address):
        print(f"New connection established with {address}!")

    @staticmethod
    def listen(self):
        tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_socket.bind(("", 0))
        tcp_socket.listen()
        while True:
            connection, address = tcp_socket.accept()
            client_thread = threading.Thread(target=self.new_client, args=(connection, address))
            break # just temporary

    def heart_beat_mechanism(socket: socket.socket, username: str, server_port: int):
        while True:
            time.sleep(2)
            heart_beat_packet = UDPHbtPacket.create_packet(
                Env.CLIENT_IP, Env.SERVER_IP, socket.getsockname()[1], server_port,
                username
            )

            socket.sendto(heart_beat_packet, (Env.SERVER_IP, server_port))

    @staticmethod
    def connect_to_server(server_port: int) -> socket:
        client_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_server_socket.bind((Env.CLIENT_IP, 0))

        client_server_port: int = client_server_socket.getsockname()[1]

        # Socket will throw timeout exception if takes more than 5 seconds for response.
        client_server_socket.settimeout(5.0)

        while True:
            username: str = input("Enter username: ")
            password: str = input("Enter Password: ")
            auth_payload: str = f"{username},{password}"

            payload: bytes = UDPPacketHandling.create_udp_packet(
                Env.CLIENT_IP, Env.SERVER_IP, client_server_port, server_port, 
                PacketTypes.AUTH, auth_payload.encode("utf-8")
            )

            client_server_socket.sendto(payload, (Env.SERVER_IP, server_port))

            try:
                response = client_server_socket.recvfrom(UDPPacket.UDP_PACKET_SIZE)[0]
                response_type: int = UDPPacketHandling.get_message_type(response)

                if (response_type != PacketTypes.OK):
                    raise Exception("Authentication failed. Please try again.")
                
                break
            except socket.timeout:
                print(f"Connection request has timed out, try again")
            except Exception as e:
                print(f"{e}")
        
        threading.Thread(
            target=ClientHandler.heart_beat_mechanism,
            args=(client_server_socket, username, server_port),
            daemon=True
        ).start()
        
        return client_server_socket
