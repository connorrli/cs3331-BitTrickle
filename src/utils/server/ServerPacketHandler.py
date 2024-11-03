from utils.networking.UDPHandler import *
from utils.server.UserSessionsHandler import UserSessionsHandler
from utils.server.UserFilesHandler import UserFilesHandler
from utils.Globals import PacketTypes
from utils.Exceptions import *
from utils.server.Logger import NetworkLogger

class ServerPacketHandler:
    def __init__(self, server_ip: str, server_port: int) -> None:
        self.files_handler = UserFilesHandler()
        self.users_handler = UserSessionsHandler()
        self.server_ip = server_ip
        self.server_port = server_port

    def receive_packet(self, packet: bytes):
        try:
            message_type: int = UDPPacketHandling.get_message_type(packet)
            source_ip: str = UDPPacketHandling.get_source_ip(packet)
            source_port: int = UDPPacketHandling.get_source_port(packet)

            if message_type != PacketTypes.AUTH:
                # If the user is no longer active, then return error (I guess?)
                if self.users_handler.is_active_user(
                    (source_ip, source_port)
                ) != True:
                    raise UserAuthError()

                NetworkLogger.log_received_event(
                    message_type, 
                    source_port, 
                    self.users_handler.get_user_from_addr(
                        (source_ip, source_port)
                    )
                )

            match message_type:
                case PacketTypes.AUTH:
                    return self.handle_auth(packet, (source_ip, source_port))
                case PacketTypes.HBT:
                    return self.handle_hbt(packet)
                case PacketTypes.LAP:
                    return self.handle_lap(packet, (source_ip, source_port))

        except CorruptPacketError:
            # If for some reason the packet is invalid in some way, drop it
            return None
        except Exception:
            # For all other uncaught exceptions, return an ERR packet
            NetworkLogger.log_sent_event(
                PacketTypes.ERR, 
                source_port, 
                self.users_handler.get_user_from_addr(
                    (source_ip, source_port)
                )
            )

            return UDPPacketHandling.create_udp_packet(
                self.server_ip, source_ip, self.server_port, source_port, 
                PacketTypes.ERR, "".encode("utf-8")
            )
    
    def handle_auth(self, packet: bytes, src_address: tuple[str, int]) -> bytes:
        data: UDPAuthPacketData = UDPAuthPacket.get_data(packet)

        NetworkLogger.log_received_event(
            PacketTypes.AUTH, 
            src_address[0], 
            data["username"]
        )

        try:
            self.users_handler.generate_session(data["username"], data["password"], src_address)

            # Successful authentication response
            NetworkLogger.log_sent_event(
                PacketTypes.OK, 
                src_address[1], 
                data['username']
            )

            return UDPPacketHandling.create_udp_packet(
                self.server_ip, src_address[0], self.server_port, src_address[1], 
                PacketTypes.OK, "Welcome to BitTrickle!".encode("utf-8")
            )
        except UserAuthError:
            # Failed authentication response. Logging has to be done separately because
            # there is no src_addr -> username mapping yet.
            NetworkLogger.log_sent_event(
                PacketTypes.ERR, 
                src_address[1], 
                data['username']
            )

            return UDPPacketHandling.create_udp_packet(
                self.server_ip, src_address[0], self.server_port, src_address[1], 
                PacketTypes.ERR, "".encode("utf-8")
            )
        
    def handle_hbt(self, packet: bytes):
        data: UDPHbtPacketData = UDPHbtPacket.get_data(packet)
        self.users_handler.renew_session(data["username"])

        return None
        
    def handle_lap(self, packet: bytes, src_address: tuple[str, int]):
        src_username: str = self.users_handler.get_user_from_addr(src_address)

        active_users: list[str] = self.users_handler.get_active_users()
        active_users.remove(src_username)

        NetworkLogger.log_sent_event(
                PacketTypes.OK, 
                src_address[1], 
                self.users_handler.get_user_from_addr(src_address)
            )

        return UDPPacketHandling.create_udp_packet(
            self.server_ip, src_address[0], self.server_port, src_address[1],
            PacketTypes.OK, ",".join(active_users).encode("utf-8")
        )



        # AUTH has to be treated differently, because there's not yet any
        # session, so can't fetch the username from the sessions
        # if message_type != PacketTypes.AUTH:
        #     username = self.users_handler.get_user_from_addr((source_ip, source_port))
        #     NetworkLogger.log_received_event(
        #         message_type, 
        #         source_port, 
        #         username
        #     )
        
        # try:
        #     match message_type:
        #         case PacketTypes.GET:
        #             data: UDPGetPacketData = UDPGetPacket.get_data(packet)
        #         case PacketTypes.AUTH:
        #             data: UDPAuthPacketData = UDPAuthPacket.get_data(packet)
        #             username = data['username']

        #             NetworkLogger.log_received_event(
        #                 message_type, 
        #                 source_port, 
        #                 data['username']
        #             )

        #             self.users_handler.generate_session(
        #                 data['username'], 
        #                 data['password'], 
        #                 (UDPPacketHandling.get_source_ip(packet), UDPPacketHandling.get_source_port(packet))
        #             )

        #             res = UDPPacketHandling.create_udp_packet(
        #                 self.server_ip, source_ip, self.server_port, source_port, PacketTypes.OK, "Welcome to BitTrickle!".encode("utf-8")
        #             )
        #         case PacketTypes.HBT:
        #             data: UDPHbtPacketData = UDPHbtPacket.get_data(packet)
        #             UserSessionsHandler.renew_session(data['username'])

        #             res = None
        #         case _:
        #             raise InvalidPacketTypeError()
            
        #     NetworkLogger.log_sent_event(message_type, source_port, username)
        #     return res
                
        # except Exception:
        #     if message_type == PacketTypes.AUTH:
        #         NetworkLogger.log_sent_event(PacketTypes.ERR, source_port, username)
        #     else:
        #         NetworkLogger.log_sent_event(PacketTypes.ERR, source_port, self.users_handler.get_user_from_addr((source_ip, source_port)))

        #     return UDPPacketHandling.create_udp_packet(
        #         self.server_ip, source_ip, self.server_port, source_port, 
        #         PacketTypes.ERR, "".encode("utf-8")
        #     )

            
                