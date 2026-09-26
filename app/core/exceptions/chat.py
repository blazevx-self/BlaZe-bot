class ChatError(Exception):
    pass

class ChatNotFoundError(ChatError):
    pass

class ChatValidationError(ChatError):
    pass

class ChatStateError(ChatError):
    pass

class ChatMemberNotFoundError(ChatError):
    pass

class ModerationError(ChatError):
    pass

class ReportError(ChatError):
    pass