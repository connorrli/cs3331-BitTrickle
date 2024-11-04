from utils.Exceptions import *

class UserFilesHandler:
    def __init__(self) -> None:
        self.shared_files: dict[str, list[str]] = dict()
    
    def add_file(self, username: str, filename: str) -> None | FileAlreadyPublished:    
        # If file hasn't been shared before, create list for it
        if self.shared_files.get(filename) == None:
            self.shared_files[filename] = []
        
        # If user already sharing file, raise exception
        if self.is_sharer(filename, username):
            raise FileAlreadyPublished()
        
        self.shared_files[filename].append(username)

    def remove_file(self, username: str, filename: str) -> None | FileNotExistent:
        if self.shared_files[filename] == None:
            raise FileNotExistent()

        if self.is_sharer(filename, username) != True:
            raise FileNotExistent()
        
        self.shared_files[filename].remove(username)

    def is_sharer(self, filename: str, username: str) -> bool:
        if self.shared_files[filename].count(username) <= 0:
            return False
        
        return True
    
    def get_shared_by(self, username: str) -> list[str]:
        published_files: list[str] = []
        for file, sharers in self.shared_files.items():
            if username in sharers:
                published_files.append(file)
        

        return published_files
    
    def get_file_sharers(self, filename: str) -> list[str]:
        if self.shared_files[filename] == None:
            raise FileNotExistent()
        
        if len(self.shared_files[filename]) <= 0:
            raise FileNotExistent()
        
        # Return all sharers
        return self.shared_files[filename]