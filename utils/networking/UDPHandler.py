import struct
import socket
from abc import ABC, abstractmethod
from typing import TypedDict

from utils.Exceptions import *
from utils.Globals import PacketTypes

class UDPPacketHandling:
    @staticmethod
    def create_udp_packet(
        src_ip: str, dst_ip: str, src_port: int, dst_port: int, message_type: int, payload: bytes
    ) -> bytes | Exception:
        if message_type > pow(2, 16) or len(payload) > pow(2, 16):
            raise Exception("Invalid packet, cannot generate")
        
        length: int = UDPPacket.UDP_TOTAL_HEADER_SIZE + len(payload)

        # Structure: 2 bytes (H = short) per field in struct
        header_no_checksum = struct.pack(
            "!HHHHHH4s", src_port, dst_port, length, 0, message_type, len(payload), socket.inet_aton(src_ip)
        )

        checksum: int = UDPPacketHandling.get_checksum(src_ip, dst_ip, header_no_checksum + payload)

        header_with_checksum = struct.pack(
            "!HHHHHH4s", src_port, dst_port, length, checksum, message_type, len(payload), socket.inet_aton(src_ip)
        )

        return header_with_checksum + payload
    
    @staticmethod
    def get_checksum(src_ip: str, dst_ip: str, packet: bytes) -> int:
        packet_length: int = len(packet)
        # Stucture of a pseudo-header, which is required for check sum, is:
        # Source IP - 4B
        # Destination IP - 4B
        # Reserved - 1B
        # Protocol - 1B
        # UDP Length - 2B
        pseudoheader: bytes = struct.pack(
            "!4s4sBBH", socket.inet_aton(src_ip), socket.inet_aton(dst_ip), 0, socket.IPPROTO_UDP, packet_length
        )

        full_packet: bytes = pseudoheader + packet
        full_packet_length: int = len(full_packet)

        checksum: int = 0
        # Loop over for each byte pair (word), so 2 bytes at a time
        for i in range(0, full_packet_length, 2):
            first_byte = full_packet[i] << 8

            if i + 1 < full_packet_length:
                second_byte = full_packet[i]
            else:
                second_byte = 0

            combined = first_byte + second_byte
            checksum += combined

            # Have to wrap around if sum has gone over 2 bytes
            # This means adding the overflow to least significant bit
            checksum = (checksum & 0xFFFF) + (checksum >> 16)

        # Return one's compliment
        return ~checksum & 0xFFFF
    
    @staticmethod
    def _get_field_value(packet: bytes, offset: int, size: int):
        return struct.unpack("!H", packet[offset:offset + size])[0]
    
    @staticmethod
    def get_payload_size(packet: bytes) -> int:
        return UDPPacketHandling._get_field_value(
            packet, UDPPacket.UDP_PAYLOAD_SIZE_OFFSET, UDPPacket.UDP_PAYLOAD_SIZE_SIZE
        )
    
    @staticmethod
    def get_message_type(packet: bytes) -> int:
        return UDPPacketHandling._get_field_value(
            packet, UDPPacket.UDP_MESSAGE_TYPE_OFFSET, UDPPacket.UDP_MESSAGE_TYPE_SIZE
        )
    
    @staticmethod
    def get_source_ip(packet: bytes) -> str:
        size: int = UDPPacket.UDP_SRC_IP_SIZE
        offset: int = UDPPacket.UDP_SRC_IP_OFFSET
        return socket.inet_ntoa(struct.unpack("!4s", packet[offset:offset + size])[0])
    
    @staticmethod
    def get_source_port(packet: bytes) -> int:
        return UDPPacketHandling._get_field_value(
            packet, UDPPacket.UDP_SRC_PORT_OFFSET, UDPPacket.UDP_SRC_PORT_SIZE
        )
    
    @staticmethod
    def get_payload(packet: bytes) -> bytes:
        payload_size = UDPPacketHandling.get_payload_size(packet)
        return packet[UDPPacket.UDP_TOTAL_HEADER_SIZE:(UDPPacket.UDP_TOTAL_HEADER_SIZE + payload_size)]
    
    @staticmethod
    def get_payload_string(packet: bytes):
        payload: bytes = UDPPacketHandling.get_payload(packet)
        return payload.decode("utf-8")
    
    @staticmethod
    def get_payload_string_args(packet: bytes) -> list[str]:
        payload: bytes = UDPPacketHandling.get_payload(packet)

        # Even if payload is empty, there will still be '' element without this
        if payload.decode("utf-8") == '':
            return []
        else:
            return payload.decode("utf-8").split(",")

class UDPPacket:
    # The whole point of this class it to keep the structure of the UDP packet used
    # in BitTrickle easily maintained. For example, if I want to add another custom header
    # field, all I need to do is tack on its size and offset, and append it to total size

    # Source port
    UDP_SRC_PORT_OFFSET = 0
    UDP_SRC_PORT_SIZE = 2

    # Destination port
    UDP_DST_PORT_OFFSET = UDP_SRC_PORT_OFFSET + UDP_SRC_PORT_SIZE
    UDP_DST_PORT_SIZE = 2

    # Packet length
    UDP_LENGTH_OFFSET = UDP_DST_PORT_OFFSET + UDP_DST_PORT_SIZE
    UDP_LENGTH_SIZE = 2

    # Checksum
    UDP_CHECKSUM_OFFSET = UDP_LENGTH_OFFSET + UDP_LENGTH_SIZE
    UDP_CHECKSUM_SIZE = 2

    # Message type (HBT, AUTH etc.)
    UDP_MESSAGE_TYPE_OFFSET = UDP_CHECKSUM_OFFSET + UDP_CHECKSUM_SIZE
    UDP_MESSAGE_TYPE_SIZE = 2

    # Payload size
    UDP_PAYLOAD_SIZE_OFFSET = UDP_MESSAGE_TYPE_OFFSET + UDP_MESSAGE_TYPE_SIZE
    UDP_PAYLOAD_SIZE_SIZE = 2

    # Source IP
    UDP_SRC_IP_OFFSET = UDP_PAYLOAD_SIZE_OFFSET + UDP_PAYLOAD_SIZE_SIZE
    UDP_SRC_IP_SIZE = 4

    # Total header size
    UDP_TOTAL_HEADER_SIZE = (
        UDP_SRC_PORT_SIZE + 
        UDP_DST_PORT_SIZE + 
        UDP_LENGTH_SIZE + 
        UDP_CHECKSUM_SIZE + 
        UDP_MESSAGE_TYPE_SIZE + 
        UDP_PAYLOAD_SIZE_SIZE + 
        UDP_SRC_IP_SIZE
    )

    # UDP Packet Size
    UDP_MAX_PAYLOAD_SIZE = 1024
    UDP_PACKET_SIZE = UDP_MAX_PAYLOAD_SIZE + UDP_TOTAL_HEADER_SIZE

# TYPED DICTS TO KEEP STRUCTURE OF UDP PACKET TYPES EASILY KNOWN AND CHANGED

class UDPGetPacketData(TypedDict):
    """Class to define data structure of a GET packet"""

    filename: str

class UDPAuthPacketData(TypedDict):
    """Class to define data structure of an AUTH packet"""

    username: str
    password: str
    listening_port: int

class UDPHbtPacketData(TypedDict):
    """Class to define data structure of an AUTH packet"""

    username: str

class UDPPubPacketData(TypedDict):
    """Class to define data structure of an AUTH packet"""

    filename: str

class UDPUnpPacketData(TypedDict):
    """Class to define data structure of an AUTH packet"""

    filename: str

class UDPSchPacketData(TypedDict):
    """Class to define data structure of an SCH packet"""

    substring: str

class UDPGenericPacket(ABC):
    """
     An abstract class inherited by all other UDP packet classes
    """

    @abstractmethod
    def create_packet(
        src_ip: str, dst_ip: str, src_port: int, dst_port: int, filename: str
    ):
        """
        A method to create a packet of the specific type

        Parameters
        ----------
        src_ip: str
            string representing the source IP address
        dst_ip: str
            string representing the destination IP address
        src_port: int
            integer representing the source port binded to by socket
        dst_port: int
            integer representing the destination port binded to by destination socket
        """

        pass

    @abstractmethod
    def get_data(packet: bytes):
        """
        A method to get all the packet's data in the required form

        Parameters
        ----------
        packet: bytes
            the packet that is to be broken down into its data components
        """

        pass
    
class UDPGetPacket(UDPGenericPacket):
    """
     A class to create and parse UDP GET packets
    """

    NUM_ARGS: int = len(UDPGetPacketData.__annotations__)

    @staticmethod
    def create_packet(
        src_ip: str, dst_ip: str, src_port: int, dst_port: int, filename: str
    ) -> bytes:
        return UDPPacketHandling.create_udp_packet(
            src_ip, dst_ip, src_port, dst_port, PacketTypes.GET, filename.encode("utf-8")
        )

    @staticmethod
    def get_data(packet: bytes) -> UDPGetPacketData:
        args: list[str] = UDPPacketHandling.get_payload_string_args(packet)

        if args.__len__() != UDPGetPacket.NUM_ARGS:
            raise CorruptPacketError()

        return UDPGetPacketData(
            filename=args[0]
        )

class UDPAuthPacket(UDPGenericPacket):
    """
     A class to create and parse UDP AUTH packets
    """

    NUM_ARGS: int = len(UDPAuthPacketData.__annotations__)

    @staticmethod
    def create_packet(
        src_ip: str, dst_ip: str, src_port: int, dst_port: int, credentials: str
    ) -> bytes:
        return UDPPacketHandling.create_udp_packet(
            src_ip, dst_ip, src_port, dst_port, PacketTypes.AUTH, credentials
        )
    
    @staticmethod
    def get_data(packet: bytes) -> UDPAuthPacketData:
        args: list[str] = UDPPacketHandling.get_payload_string_args(packet)

        if args.__len__() != UDPAuthPacket.NUM_ARGS:
            raise CorruptPacketError()

        return UDPAuthPacketData(
            username=args[0],
            password=args[1],
            listening_port=int(args[2])
        )

class UDPHbtPacket(UDPGenericPacket):
    """
     A class to create and parse UDP HBT packets
    """

    NUM_ARGS: int = len(UDPHbtPacketData.__annotations__)

    @staticmethod
    def create_packet(
        src_ip: str, dst_ip: str, src_port: int, dst_port: int, username: str
    ) -> bytes:
        return UDPPacketHandling.create_udp_packet(
            src_ip, dst_ip, src_port, dst_port, PacketTypes.HBT, username.encode("utf-8")
        )
    
    @staticmethod
    def get_data(packet: bytes) -> UDPAuthPacketData:
        args: list[str] = UDPPacketHandling.get_payload_string_args(packet)

        if len(args) != UDPHbtPacket.NUM_ARGS:
            raise CorruptPacketError()

        return UDPAuthPacketData(
            username=args[0]
        )

class UDPPubPacket(UDPGenericPacket):
    """
     A class to create and parse UDP PUB packets
    """

    NUM_ARGS: int = len(UDPPubPacketData.__annotations__)

    @staticmethod
    def create_packet(
        src_ip: str, dst_ip: str, src_port: int, dst_port: int, filename: str
    ) -> bytes:
        return UDPPacketHandling.create_udp_packet(
            src_ip, dst_ip, src_port, dst_port, PacketTypes.PUB, filename.encode("utf-8")
        )
    
    @staticmethod
    def get_data(packet: bytes) -> UDPPubPacketData:
        args: list[str] = UDPPacketHandling.get_payload_string_args(packet)

        if len(args) != UDPPubPacket.NUM_ARGS:
            raise CorruptPacketError()

        return UDPPubPacketData(
            filename=args[0]
        )

class UDPUnpPacket(UDPGenericPacket):
    """
     A class to create and parse UDP LPF packets
    """

    NUM_ARGS: int = len(UDPUnpPacketData.__annotations__)

    @staticmethod
    def create_packet(
        src_ip: str, dst_ip: str, src_port: int, dst_port: int, filename: str
    ) -> bytes:
        return UDPPacketHandling.create_udp_packet(
            src_ip, dst_ip, src_port, dst_port, PacketTypes.UNP, filename.encode("utf-8")
        )
    
    @staticmethod
    def get_data(packet: bytes) -> UDPUnpPacketData:
        args: list[str] = UDPPacketHandling.get_payload_string_args(packet)

        if len(args) != UDPUnpPacket.NUM_ARGS:
            raise CorruptPacketError()

        return UDPUnpPacketData(
            filename=args[0]
        )

class UDPSchPacket(UDPGenericPacket):
    """
     A class to create and parse UDP SCH packets
    """

    NUM_ARGS: int = len(UDPSchPacketData.__annotations__)

    @staticmethod
    def create_packet(
        src_ip: str, dst_ip: str, src_port: int, dst_port: int, substring: str
    ) -> bytes:
        return UDPPacketHandling.create_udp_packet(
            src_ip, dst_ip, src_port, dst_port, PacketTypes.SCH, substring.encode("utf-8")
        )

    @staticmethod
    def get_data(packet: bytes) -> UDPSchPacketData:
        args: list[str] = UDPPacketHandling.get_payload_string_args(packet)

        if args.__len__() != UDPSchPacket.NUM_ARGS:
            raise CorruptPacketError()

        return UDPSchPacketData(
            substring=args[0]
        )