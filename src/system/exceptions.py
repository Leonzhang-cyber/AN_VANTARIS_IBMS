# src/system/exceptions.py
class DIDError(Exception):
    pass

class DIDAlreadyExistsError(DIDError):
    pass

class PermissionDeniedError(DIDError):
    pass

class VCInvalidError(DIDError):
    pass

class VPInvalidError(DIDError):
    pass


class PermissionDenied:
    pass

# src/system/exceptions.py
class NotFoundError(Exception):
    pass


class DuplicateError(Exception):
    pass


# src/system/exceptions.py
class NotFoundError(Exception):
    def __init__(self, message="Resource not found"):
        self.message = message
        super().__init__(self.message)

class DuplicateError(Exception):
    def __init__(self, message="Duplicate entry"):
        self.message = message
        super().__init__(self.message)