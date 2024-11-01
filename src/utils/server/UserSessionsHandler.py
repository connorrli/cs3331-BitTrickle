import time
import os

class UserSession:
    def __init__(self, user_ip: str):
        self.last_active: time = time.time()
        self.ip: str = user_ip
    
    def renew(self):
        # HBT was sent after already expired, don't renew
        if (self.is_active() != True):
            return

        self.last_active: time = time.time()
    
    def is_active(self):
        if time.time() - self.last_active < 3:
            return True
        
        return False

class UserSessionsHandler:
    # This is kinda gross, but if timers aren't stored in the sessions handler separately
    # instead of within the session objects themselves, it becomes a hassle resetting the timer
    # since it calls a method in this class
    active_sessions: dict[str, UserSession] = dict()

    def generate_session(self, username: str, user_ip: str) -> None:
        if self.active_sessions.__contains__(username):
            raise Exception()

        self.active_sessions[username] = UserSession(user_ip)

    def renew_session(self, username: str):
        # If HBT sent but session doesn't exist for some reason, don't attempt renew
        if self.active_sessions.__contains__(username) != True:
            return
        
        self.active_sessions[username].renew()

    def remove_session(self, username: str):
        self.active_sessions.pop(username, None)

class Authenticate:
    def __init__(self):
        self.credentials: dict = self.get_credentials()
    
    def get_credentials(self) -> list[str]:
        credentials = None

        # Traverse from project root folder, rel path is kind of
        # brittle, but it should be okay.
        for root, dirs, files in os.walk("../"):
            for file in files:
                if file == "credentials.txt":
                    credentials = open(os.path.join(root, file))
        
        if credentials == None:
            return []

        credentials_list: list[str] = credentials.readlines()

        credentials_dictionary: dict[str, str] = dict()
        for credential in credentials_list:
            # Credentials are stored as "John Password123", so sep on " "
            split = credential.strip().split(" ", 1)

            # All credentials will be valid, but still good practice I guess
            if split.__len__() < 2:
                continue

            credentials_dictionary[split[0]] = split[1]
        
        return credentials_dictionary
    
    def isValidLogin(self, username: str, password: str) -> bool:
        if self.credentials.get(username) == None:
            return False
        
        if self.credentials[username] != password:
            return False
        
        return True