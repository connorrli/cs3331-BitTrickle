import socket
import os

from utils.networking.UDPHandler import *
from utils.Globals import Env, PacketTypes
from utils.client.FilesHandler import FilesHandler

class CommandHandler:
    @staticmethod
    def execute_command(command: list[str], client_server_socket: socket, server_address: tuple[str, int]):
        invalid_cmd: str = "Invalid command. Correct usage:"
        match command[0]:
            case "get":
                if (command.__len__() != 2):
                    raise Exception(f"{invalid_cmd} get <filename>")
            case "lap":
                if (command.__len__() != 1):
                    raise Exception(f"{invalid_cmd} lap")
                CommandHandler.handle_lap(client_server_socket, server_address)
            case "lpf":
                if (command.__len__() != 1):
                    raise Exception(f"{invalid_cmd} lpf")
            case "pub":
                if (command.__len__() != 2):
                    raise Exception(f"{invalid_cmd} pub <filename>")
                CommandHandler.handle_pub(client_server_socket, server_address, command[1])
            case "sch":
                # For this one, I'm not sure if this is going to work because it depends
                # on what the substring looks like. I might have to rethink my approach
                if (command.__len__() != 2):
                    raise Exception(f"{invalid_cmd} sch")
            case "unp":
                if (command.__len__() != 2):
                    raise Exception(f"{invalid_cmd} unp <filename>")
            case "xit":
                if (command.__len__() != 1):
                    raise Exception(f"{invalid_cmd} xit")
                CommandHandler.handle_exit()
            case _:
                raise Exception("Unknown command. Try again.")
            
    @staticmethod
    def get_command() -> list[str] | Exception:
        command_input: str = input(f"What would you like to do? ")
        if isinstance(command_input, str) != True:
            raise Exception("Input should be a string.")


        if (command_input.__len__() <= 0):
            raise Exception("No input given.")

        return command_input.split(" ", -1)
    
    @staticmethod
    def handle_exit():
        exit()

    @staticmethod
    def handle_lap(client_server_socket: socket.socket, server_address: tuple[str, int]) -> None:
        request = UDPPacketHandling.create_udp_packet(
            client_server_socket.getsockname()[0], server_address[0], 
            client_server_socket.getsockname()[1], server_address[1],
            PacketTypes.LAP, "".encode("utf-8")
        )
        client_server_socket.sendto(request, server_address)
        response: bytes = client_server_socket.recv(UDPPacket.UDP_PACKET_SIZE)

        active_users: list[str] = UDPPacketHandling.get_payload_string_args(response)

        if len(active_users) <= 0:
            print(f"No active peers")
            return
                
        print(f"{len(active_users)} active peer{'s' if len(active_users) != 1 else ''}")
        print(f"\n".join(active_users))
    
    @staticmethod
    def handle_pub(client_server_socket: socket.socket, server_address: tuple[str, int], filename: str):
        # The spec does say it'll be a valid file, but still better to do check
        if FilesHandler.file_exists(filename) != True:
            print(f"File does not exist!")
            return
        
        request: UDPPubPacketData = UDPPubPacket.create_packet(
            client_server_socket.getsockname()[0], server_address[0], 
            client_server_socket.getsockname()[1], server_address[1],
            filename
        )

        client_server_socket.sendto(request, server_address)

        response: bytes = client_server_socket.recv(UDPPacket.UDP_PACKET_SIZE)
        message_type: int = UDPPacketHandling.get_message_type(response)

        if message_type != PacketTypes.OK:
            print(f"Unable to publish file, you may have already published it.")
        else:
            print(f"File published successfully")


