import sys
import socket
from _thread import *
from utils.Globals import Env
from utils.Networking.ClientServerConnector import ClientHandler

# My package imports
from utils.CommandHandler import CommandHandler

# Constants are the host and server port
host = "127.0.0.1"
if sys.argv.__len__() != 2 or sys.argv[1].isnumeric() != True:
    print(f"Cannot run. Proper usage: python3 client.py <server_port>")
    exit()

server_port: int = int(sys.argv[1])

class PrintLogging:
    @staticmethod
    def invalid_input():
        print("Invalid input, try again!")

    @staticmethod
    def invalid_num_args():
        print("Wrong number of args given, try again!")
            
def main():
    client_server_socket: socket = ClientHandler.connect_to_server(server_port)

    print(f"Welcome to BitTrickle!\nAvailable commands are: get, lap, lpf, pub, sch, unp, xit")

    while True:
        try:
            command: list[str] = CommandHandler.get_command()
            CommandHandler.execute_command(command)
        except Exception as e:
            print(e)
            continue

if __name__ == "__main__":
    main()





            


