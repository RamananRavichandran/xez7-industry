import json
from typing import Any, Dict, Type, TypeVar

from botocore.exceptions import BotoCoreError, ClientError
from pydantic import BaseModel, ValidationError

from ..config import get_settings
from ..utils.aws_session import get_boto3_client
from ..utils.errors import LLMError
from ..utils.logging import get_logger
from ..utils.retry import retry


T = TypeVar("T", bound=BaseModel)

logger = get_logger(__name__)


class BedrockClient:
    """Thin wrapper around AWS Bedrock text generation for JSON responses."""

    def __init__(self) -> None:
        settings = get_settings()
        self._model_id = settings.bedrock_model_id
        self._client = get_boto3_client("bedrock-runtime")

    @retry(exceptions=(BotoCoreError, ClientError, LLMError))
    def generate_json(self, prompt: str, response_model: Type[T]) -> T:
        try:
            response = self._client.invoke_model(
                modelId=self._model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(
                    {
                        "messages": [
                            {
                                "role": "user",
                                "content": [{"type": "text", "text": prompt}],
                            }
                        ],
                        "max_tokens": 1024,
                        "temperature": 0.1,
                    }
                ),
            )
        except (BotoCoreError, ClientError) as exc:
            logger.error("Bedrock invocation failed: %s", exc)
            raise

        body_bytes: bytes = response.get("body").read()
        try:
            parsed = json.loads(body_bytes)
            output_text = parsed["output"]["message"]["content"][0]["text"]
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to parse Bedrock response: %s", exc)
            raise LLMError("Bedrock response parsing error") from exc

        try:
            payload: Dict[str, Any] = json.loads(output_text)
        except json.JSONDecodeError as exc:
            logger.error("Failed to decode Bedrock JSON content: %s", exc)
            raise LLMError("Bedrock response was not valid JSON") from exc

        try:
            return response_model.model_validate(payload)
        except ValidationError as exc:
            logger.error("Bedrock response did not match schema: %s", exc)
            raise LLMError("Bedrock response failed schema validation") from exc

