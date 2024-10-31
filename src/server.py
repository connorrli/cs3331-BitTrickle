import sys
import socket
from utils.Globals import Env

server_port: int = sys.argv[1]
if sys.argv.__len__() != 2 or sys.argv[1].isnumeric() != True:
    print(f"Cannot run. Proper usage: python3 server.py <server_port>")
    exit()

active_clients: dict = dict()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((Env.SERVER_IP, server_port))

    while True:
        server_socket.listen()





if __name__ == "main":
    main()