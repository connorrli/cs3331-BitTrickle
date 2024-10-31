from threading import Timer
import time
import os

class UserSessionsHandler:
    active_sessions = dict()

    def generate_session(self, username: str, user_ip: str) -> None:
        if self.active_sessions.__contains__(username):
            raise Exception()
        
        newSession: UserSession = UserSession(user_ip, Timer(3, self.remove_session(username)))
        self.active_sessions[username] = newSession

    def renew_session(self, username: str):
        # If heartbeat received, but no longer active, drop packet?
        # This behaviour doesn't seem to be mentioned in the spec
        if self.active_sessions.__contains__(username) != True:
            return
        
        session: UserSession = self.active_sessions.get(username)

        session.renew_timer()

    def remove_session(self, username: str):
        self.active_sessions.pop(username, None)


class UserSession:
    def __init__(self, user_sessions: UserSessionsHandler, user_ip: str, timer: Timer):
        self.creator: UserSessionsHandler = user_sessions
        self.last_active: time = time.time()
        self.timer: Timer = timer
        self.ip: str = user_ip
    
    def renew_timer(self):
        self.last_active = time.time()

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

        credentials_dictionary: dict = dict()
        for credential in credentials_list:
            # Credentials are stored as "John Password123", so sep on " "
            split = credential.strip().split(" ", 1)

            # All credentials will be valid, but still good practice I guess
            if split.__len__() < 2:
                continue

            credentials_dictionary[split[0]] = split[1]
        
        return credentials_dictionary
    
    def isValidLogin(self, username: str, password: str) -> bool:
        print(repr(password))
        if self.credentials.get(username) == None:
            return False
        
        if self.credentials[username] != password:
            return False
        
        return True