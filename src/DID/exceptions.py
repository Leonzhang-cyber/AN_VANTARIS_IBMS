# src/DID/exceptions.py
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