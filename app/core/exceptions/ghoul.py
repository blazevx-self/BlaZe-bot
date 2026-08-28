class GhoulError(Exception):
    pass

class GhoulNotFound(GhoulError):
    pass

class KaguneInitializationError(GhoulError):
    pass

class InvalidStatError(GhoulError):
    pass