"""Integration Health read-model errors."""


class IntegrationHealthError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
