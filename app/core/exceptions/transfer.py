class TransferError(Exception):
    pass

class InvalidTransferAmountError(TransferError):
    pass

class SelfTransferError(TransferError):
    pass

class InsufficientBalanceError(TransferError):
    pass

class SenderTooNewError(TransferError):
    pass

class ReceiverLimitExceededError(TransferError):
    pass