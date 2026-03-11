from typing import Type, TypeVar

from pydantic import BaseModel

from ..utils.errors import LLMError
from ..utils.logging import get_logger
from .bedrock_client import BedrockClient
from .openai_client import OpenAIClient


T = TypeVar("T", bound=BaseModel)

logger = get_logger(__name__)


class LLMRouter:
    """
    Route calls to OpenAI by default with automatic fallback to Bedrock.
    """

    def __init__(self) -> None:
        self._openai_client = None
        self._bedrock_client = None

    @property
    def openai_client(self) -> OpenAIClient:
        if self._openai_client is None:
            self._openai_client = OpenAIClient()
        return self._openai_client

    @property
    def bedrock_client(self) -> BedrockClient:
        if self._bedrock_client is None:
            self._bedrock_client = BedrockClient()
        return self._bedrock_client

    def generate(self, prompt: str, response_model: Type[T]) -> T:
        """
        Generate a structured response using OpenAI, with Bedrock fallback.
        """

        try:
            return self.openai_client.generate_json(prompt, response_model)
        except LLMError as primary_exc:
            logger.warning("OpenAI failed, falling back to Bedrock: %s", primary_exc)
            try:
                return self.bedrock_client.generate_json(prompt, response_model)
            except LLMError as fallback_exc:
                logger.error("Bedrock fallback also failed: %s", fallback_exc)
                raise

