from datetime import datetime
from utils.Globals import PacketTypes

class NetworkLogger:
    @staticmethod
    def log_received_event(message_type: int, source_port: int, source: str) -> None:
        print(f"{NetworkLogger.get_time()}: {source_port}: Received {PacketTypes.get_name(message_type)} from {source}")

    @staticmethod
    def log_sent_event(message_type: int, target_port: int, target: str) -> None:
        print(f"{NetworkLogger.get_time()}: {target_port}: Sent {PacketTypes.get_name(message_type)} to {target}")

    @staticmethod
    def get_time() -> str:
        # time() returns number of seconds as float
        current_time: datetime = datetime.now()

        # 24 hour time
        hours = current_time.hour
        minutes: int = current_time.minute
        seconds: int = current_time.second
        milliseconds: int = current_time.microsecond // 1000

        return f"{hours}:{minutes}:{seconds}:{milliseconds}"

