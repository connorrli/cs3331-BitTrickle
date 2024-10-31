from threading import Timer
import time

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