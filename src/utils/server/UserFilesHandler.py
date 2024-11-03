from utils.Exceptions import *

class UserFilesHandler:
    def __init__(self) -> None:
        self.shared_files: dict[str, list[str]] = dict()
    
    def add_file(self, username: str, filename: str) -> None | FileAlreadyPublished:
        # If user hasn't shared any files, create new list with filename in it
        if self.shared_files.get(username) == None:
            self.shared_files[username] = [filename]
            return
        
        # If user already sharing file, raise exception
        if self.shared_files[username].__contains__(filename):
            raise FileAlreadyPublished()
        
        self.shared_files[username].append(filename)

    def remove_file(self, username: str, filename: str) -> None | FileNotExistent:
        if self.is_sharer(username) != True:
            raise FileNotExistent()
        
        if self.shared_files.pop(filename, None) == None:
            raise FileNotExistent()

    def is_sharer(self, username: str) -> bool:
        if self.shared_files.get(username) == None:
            return False
        
        return True