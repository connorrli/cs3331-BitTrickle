from utils.networking.UDPHandler import *
from utils.server.UserSessionsHandler import UserSessionsHandler
from utils.server.UserFilesHandler import UserFilesHandler
from utils.Globals import PacketTypes
from utils.Exceptions import *
from utils.server.Logger import NetworkLogger

class ServerPacketHandler:
    def __init__(self, files_handler: UserFilesHandler, users_handler: UserSessionsHandler, 
                 server_ip: str, server_port: int) -> None:
        self.files_handler = files_handler
        self.users_handler = users_handler
        self.server_ip = server_ip
        self.server_port = server_port

    def receive_packet(self, packet: bytes):
        message_type: int = UDPPacketHandling.get_message_type(packet)
        source_ip: str = UDPPacketHandling.get_source_ip(packet)
        source_port: int = UDPPacketHandling.get_source_port(packet)

        if message_type != PacketTypes.AUTH:
            # If the user is no longer active, then return error (I guess?)
            if self.users_handler.is_active_user(
                (source_ip, source_port)
            ) != True:
                raise UserAuthError()
            
        username: str = self.users_handler.get_user_from_addr((source_ip, source_port))
        source: str = f"{source_ip}:{source_port}" if username == None else username 

        NetworkLogger.log_received_event(
            message_type, 
            source_port, 
            source
        )

        match message_type:
            case PacketTypes.AUTH:
                return self.handle_auth(packet, (source_ip, source_port))
            case PacketTypes.HBT:
                return self.handle_hbt(packet)
            case PacketTypes.LAP:
                return self.handle_lap(packet, (source_ip, source_port))
            case PacketTypes.PUB:
                return self.handle_pub(packet, (source_ip, source_port))
            case PacketTypes.LPF:
                return self.handle_lpf(packet, (source_ip, source_port))
            case PacketTypes.UNP:
                return self.handle_unp(packet, (source_ip, source_port))
            case PacketTypes.GET:
                return self.handle_get(packet, (source_ip, source_port))
            case PacketTypes.SCH:
                return self.handle_sch(packet, (source_ip, source_port))
            case _:
                return None
    
    def handle_auth(self, packet: bytes, src_address: tuple[str, int]) -> bytes:
        data: UDPAuthPacketData = UDPAuthPacket.get_data(packet)

        self.users_handler.generate_session(data["username"], data["password"], data["listening_port"], src_address)

        return UDPPacketHandling.create_udp_packet(
            self.server_ip, src_address[0], 
            self.server_port, src_address[1], 
            PacketTypes.OK, "".encode("utf-8")
        )
        
    def handle_hbt(self, packet: bytes) -> None:
        data: UDPHbtPacketData = UDPHbtPacket.get_data(packet)
        self.users_handler.renew_session(data["username"])

        return None
        
    def handle_lap(self, packet: bytes, src_address: tuple[str, int]) -> bytes:
        src_username: str = self.users_handler.get_user_from_addr(src_address)

        active_users: list[str] = self.users_handler.get_active_users()
        active_users.remove(src_username)

        return UDPPacketHandling.create_udp_packet(
            self.server_ip, src_address[0], 
            self.server_port, src_address[1],
            PacketTypes.OK, ",".join(active_users).encode("utf-8")
        )
    
    def handle_pub(self, packet: bytes, src_address: tuple[str, int]) -> bytes:
        src_username: str = self.users_handler.get_user_from_addr(src_address)

        data: UDPPubPacketData = UDPPubPacket.get_data(packet)

        self.files_handler.add_file(src_username, data["filename"])

        return UDPPacketHandling.create_udp_packet(
            self.server_ip, src_address[0],
            self.server_port, src_address[1],
            PacketTypes.OK, "".encode("utf-8")
        )
    
    def handle_lpf(self, packet: bytes, src_address: tuple[str, int]) -> bytes:
        src_username: str = self.users_handler.get_user_from_addr(src_address)

        shared_files: list[str] = self.files_handler.get_shared_by(src_username)

        return UDPPacketHandling.create_udp_packet(
            self.server_ip, src_address[0], 
            self.server_port, src_address[1],
            PacketTypes.OK, ",".join(shared_files).encode("utf-8")
        )
    
    def handle_unp(self, packet: bytes, src_address: tuple[str, int]) -> bytes:
        src_username: str = self.users_handler.get_user_from_addr(src_address)

        data: UDPUnpPacketData = UDPUnpPacket.get_data(packet)

        self.files_handler.remove_file(src_username, data["filename"])

        return UDPPacketHandling.create_udp_packet(
            self.server_ip, src_address[0],
            self.server_port, src_address[1],
            PacketTypes.OK, "".encode("utf-8")
        )
    
    def handle_get(self, packet: bytes, src_address: tuple[str, int]) -> bytes:
        src_username: str = self.users_handler.get_user_from_addr(src_address)

        data: UDPGetPacketData = UDPGetPacket.get_data(packet)

        sharers: list[str] = self.files_handler.get_file_sharers(data["filename"])

        selected_sharer: tuple[str, int] = None
        for sharer in sharers:
            listening_address: tuple[str, int] = self.users_handler.get_listening_address(sharer)
            if listening_address == None:
                continue

            selected_sharer = listening_address
            break

        if selected_sharer == None:
            raise NoActiveSharers()

        return UDPPacketHandling.create_udp_packet(
            self.server_ip, src_address[0],
            self.server_port, src_address[1],
            PacketTypes.OK, f"{selected_sharer[0]},{selected_sharer[1]}".encode("utf-8")
        )
    
    def handle_sch(self, packet: bytes, src_address: tuple[str, int]) -> bytes:
        data: UDPSchPacketData = UDPSchPacket.get_data(packet)

        matching_files: list[str] = self.files_handler.get_matching(data["substring"])

        return UDPPacketHandling.create_udp_packet(
            self.server_ip, src_address[0],
            self.server_port, src_address[1],
            PacketTypes.OK, ",".join(matching_files).encode("utf-8")
        )



        


            
                