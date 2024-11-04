import os
from pathlib import Path

class FilesHandler:
    @staticmethod
    def file_exists(filename: str) -> bool:
        file = Path(os.getcwd() + "/" + filename)

        return file.exists()