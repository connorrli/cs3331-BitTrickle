import struct
import socket

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
        return socket.inet_ntoa(UDPPacketHandling._get_field_value(
            packet, UDPPacket.UDP_SRC_IP_OFFSET, UDPPacket.UDP_SRC_IP_SIZE
        ))
    
    @staticmethod
    def get_source_port(packet: bytes) -> int:
        return UDPPacketHandling._get_field_value(
            packet, UDPPacket.UDP_SRC_PORT_OFFSET, UDPPacket.UDP_SRC_PORT_SIZE
        )
    
    @staticmethod
    def get_payload(packet: bytes) -> bytes:
        payload_size = UDPPacketHandling.get_payload_size(packet)
        return packet[UDPPacket.UDP_TOTAL_HEADER_SIZE:(UDPPacket.UDP_TOTAL_HEADER_SIZE + payload_size)]