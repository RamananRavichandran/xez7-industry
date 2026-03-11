from typing import Any, Dict

from mangum import Mangum

from ..api.main import app


asgi_handler = Mangum(app)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """AWS Lambda entrypoint wrapping FastAPI via Mangum."""

    return asgi_handler(event, context)

