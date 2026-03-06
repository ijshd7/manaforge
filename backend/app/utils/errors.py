class ServiceError(Exception):
    """Raised when an external service call fails."""

    def __init__(self, service: str, message: str, status_code: int = 500):
        self.service = service
        self.message = message
        self.status_code = status_code
        super().__init__(message)

    def to_dict(self) -> dict:
        return {
            "service": self.service,
            "detail": self.message,
            "status_code": self.status_code,
        }
