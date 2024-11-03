import time
import os
from utils.Exceptions import *

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
            if len(split) < 2:
                continue

            credentials_dictionary[split[0]] = split[1]
        
        return credentials_dictionary
    
    def isValidLogin(self, username: str, password: str) -> bool:
        if self.credentials.get(username) == None:
            return False
        
        if self.credentials[username] != password:
            return False
        
        return True

class UserSession:
    def __init__(self, username: str, address: tuple[str, int]):
        self.last_active: time = time.time()
        self.username: str = username
        self.address: str = address
    
    def renew(self):
        # HBT was sent after already expired, don't renew
        if (self.is_active() != True):
            return

        self.last_active: time = time.time()
    
    def is_active(self):
        if time.time() - self.last_active < 3:
            return True
        
        return False
    
    def get_username(self) -> str:
        return self.username

class UserSessionsHandler:
    # This is kinda gross, but if timers aren't stored in the sessions handler separately
    # instead of within the session objects themselves, it becomes a hassle resetting the timer
    # since it calls a method in this class
    def __init__(self):
        self.user_sessions: dict[str | tuple[str, int], UserSession] = dict()
        self.authenticator: Authenticate = Authenticate()

    def generate_session(self, username: str, password: str, user_address: tuple[str, int]) -> None | UserAuthError:
        if self.authenticator.isValidLogin(username, password) != True:
            raise UserAuthError()

        if self.user_sessions.__contains__(username):
            if self.user_sessions[username].is_active():
                raise UserAuthError()
        
        new_session: UserSession = UserSession(username, user_address)
        self.user_sessions[username] = new_session
        self.user_sessions[user_address] = new_session

    def renew_session(self, username: str):
        # If HBT sent but session doesn't exist for some reason, don't attempt renew
        if self.user_sessions[username] == None:
            return
        
        self.user_sessions[username].renew()

    def remove_session(self, username: str):
        self.user_sessions.pop(username, None)

    def is_active_user(self, src_address: tuple[str, int]) -> bool:
        username = self.get_user_from_addr(src_address)

        if (username == None):
            return False
        
        if (
            self.user_sessions[username] == None or
            self.user_sessions[username].is_active() != True
        ):
            return False
        
        return True
    
    def get_user_from_addr(self, addr: tuple[str, int]) -> str | None:
        if self.user_sessions.get(addr) == None:
            return None
        
        return self.user_sessions[addr].get_username()
    
    def get_active_users(self) -> list[str]:
        active_users: list[str] = []
        for session in set(self.user_sessions.values()):
            if session.is_active():
                active_users.append(session.get_username())

        return active_users