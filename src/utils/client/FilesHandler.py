import os
from collections.abc import Iterator
from utils.networking.TCPHandler import TCP

class FilesHandler:
    @staticmethod
    def file_exists(filename: str) -> bool:
        # Traverse from project root folder, rel path is kind of
        # brittle, but it should be okay.
        for root, dirs, files in os.walk("."):
            for file in files:
                if file == filename:
                    return True

        return False
