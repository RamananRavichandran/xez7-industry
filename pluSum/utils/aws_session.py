from functools import lru_cache
from typing import Any

import boto3

from ..config import get_settings


@lru_cache()
def get_boto3_session() -> boto3.session.Session:
    """
    Return a cached boto3 session.

    Uses IAM roles or environment-based credentials in Lambda.
    """

    settings = get_settings()
    return boto3.session.Session(region_name=settings.aws_region)


def get_boto3_client(service_name: str, **kwargs: Any) -> Any:
    """
    Return a boto3 client for the given service.
    """

    session = get_boto3_session()
    return session.client(service_name, **kwargs)

