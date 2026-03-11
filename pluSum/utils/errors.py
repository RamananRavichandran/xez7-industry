from typing import Optional


class PluSumError(Exception):
    """Base exception for all PluSum errors."""


class IntegrationError(PluSumError):
    """Raised when an external integration fails."""

    def __init__(self, message: str, *, provider: Optional[str] = None) -> None:
        super().__init__(message)
        self.provider = provider


class LLMError(PluSumError):
    """Raised when the LLM layer fails."""


class AuthError(PluSumError):
    """Raised when authentication/authorization fails."""


class ValidationError(PluSumError):
    """Raised when a request or configuration is invalid."""

