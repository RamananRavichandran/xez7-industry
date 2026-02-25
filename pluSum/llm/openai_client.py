import json
from typing import Any, Dict, Type, TypeVar

from openai import OpenAI
from pydantic import BaseModel, ValidationError

from ..config import get_settings
from ..utils.errors import LLMError
from ..utils.logging import get_logger
from ..utils.retry import retry


T = TypeVar("T", bound=BaseModel)

logger = get_logger(__name__)


class OpenAIClient:
    """Thin wrapper around OpenAI chat completions."""

    def __init__(self) -> None:
        settings = get_settings()
        if not settings.openai_api_key:
            raise LLMError("OPENAI_API_KEY not configured")
        self._client = OpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_model

    @retry()
    def generate_json(self, prompt: str, response_model: Type[T]) -> T:
        """
        Call OpenAI and parse the response as JSON into the given Pydantic model.
        """

        logger.info("Calling OpenAI model=%s", self._model)
        completion = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": "You are a helpful PMO assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )
        content = completion.choices[0].message.content or ""
        try:
            payload: Dict[str, Any] = json.loads(content)
        except json.JSONDecodeError as exc:
            logger.error("Failed to decode OpenAI JSON response: %s", exc)
            raise LLMError("OpenAI response was not valid JSON") from exc

        try:
            return response_model.model_validate(payload)
        except ValidationError as exc:
            logger.error("OpenAI response did not match schema: %s", exc)
            raise LLMError("OpenAI response failed schema validation") from exc

