import sys
import socket
from _thread import *
import threading

class PrintLogging:
    @staticmethod
    def invalid_input():
        print("Invalid input, try again!")

    @staticmethod
    def invalid_num_args():
        print("Wrong number of args given, try again!")

def main():
    host = "127.0.0.1"
    server_port: int = sys.argv[1]

    main_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    main_socket.bind(host, server_port)

    listening_socket = 

    while (True):
        command_input: str = input("What would you like to do? ")
        if isinstance(command_input, str) != True:
            PrintLogging.invalid_input()
            continue

        if (command_input.__len__() <= 0):
            PrintLogging.invalid_input()

        command_and_args: list[str] = command_input.split(" ", -1)

        match command_and_args[0]:
            case "get":
                if (command_and_args.__len__() != 2):
                    PrintLogging.invalid_num_args()

if __name__ == '__main__':
    main()





            


