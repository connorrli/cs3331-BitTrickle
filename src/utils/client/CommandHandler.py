import socket
from utils.networking.UDPHandler import UDPPacketHandling, UDPPacket
from utils.Globals import Env, PacketTypes

class CommandHandler:
    @staticmethod
    def execute_command(command: list[str], client_server_socket: socket, server_port: int):
        invalid_cmd: str = "Invalid command. Correct usage:"
        match command[0]:
            case "get":
                if (command.__len__() != 2):
                    raise Exception(f"{invalid_cmd} get <filename>")
            case "lap":
                if (command.__len__() != 1):
                    raise Exception(f"{invalid_cmd} lap")
                CommandHandler.handle_lap(client_server_socket, server_port)
            case "lpf":
                if (command.__len__() != 1):
                    raise Exception(f"{invalid_cmd} lpf")
            case "pub":
                if (command.__len__() != 2):
                    raise Exception(f"{invalid_cmd} pub <filename>")
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
    def handle_lap(client_server_socket: socket.socket, server_port: int) -> None:
        request = UDPPacketHandling.create_udp_packet(
            Env.CLIENT_IP, Env.SERVER_IP, 
            client_server_socket.getsockname()[1], server_port,
            PacketTypes.LAP, "".encode("utf-8")
        )
        client_server_socket.sendto(request, (Env.SERVER_IP, server_port))
        response: bytes = client_server_socket.recv(UDPPacket.UDP_PACKET_SIZE)

        active_users: list[str] = UDPPacketHandling.get_payload_string_args(response)

        if len(active_users) <= 0:
            print(f"No active peers")
            return
                
        print(f"{len(active_users)} active peer{'s' if len(active_users) != 1 else ''}")
        print(f"\n".join(active_users))


