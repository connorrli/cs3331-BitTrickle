class FileAlreadyPublished(Exception):
    pass

class FileNotExistent(Exception):
    pass

class CorruptPacketError(Exception):
    pass

class InvalidPacketTypeError(Exception):
    pass

class UserAuthError(Exception):
    pass

class NoActiveSharers(Exception):
    pass