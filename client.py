import sys
import socket

from utils.client.CommandHandler import CommandHandler
from utils.networking.ClientServerConnector import ClientNetworkHandler
from utils.Globals import Env

# Constants
host: str = "127.0.0.1"
if sys.argv.__len__() != 2 or sys.argv[1].isnumeric() != True:
    print(f"Cannot run. Proper usage: python3 client.py <server_port>")
    exit()

server_ip: str = Env.SERVER_IP
server_port: int = int(sys.argv[1])
            
def main():
    client_server_socket: socket = ClientNetworkHandler.connect_to_server(server_port)

    print(f"Welcome to BitTrickle!\nAvailable commands are: get, lap, lpf, pub, sch, unp, xit")

    while True:
        try:
            command: list[str] = CommandHandler.get_command()
            CommandHandler.execute_command(command, client_server_socket, (server_ip, server_port))
        except Exception as e:
            print(e)
            continue

if __name__ == "__main__":
    main()





            


