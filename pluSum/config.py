from functools import lru_cache
from typing import List, Optional

from pydantic import AnyHttpUrl, BaseSettings, Field


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # General
    app_name: str = Field(default="PluSum", env="PLUSUM_APP_NAME")
    environment: str = Field(default="local", env="PLUSUM_ENVIRONMENT")

    # OpenAI
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL")

    # Bedrock
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    bedrock_model_id: str = Field(default="anthropic.claude-3-sonnet-20240229-v1:0", env="BEDROCK_MODEL_ID")

    # DynamoDB
    dynamodb_user_table: str = Field(default="plusum_users", env="DDB_USER_TABLE")
    dynamodb_agent_table: str = Field(default="plusum_agents", env="DDB_AGENT_TABLE")
    dynamodb_logs_table: str = Field(default="plusum_logs", env="DDB_LOGS_TABLE")
    dynamodb_projects_table: str = Field(default="plusum_projects", env="DDB_PROJECTS_TABLE")

    # S3
    s3_bucket_attachments: str = Field(default="plusum-attachments", env="S3_BUCKET_ATTACHMENTS")
    s3_bucket_exports: str = Field(default="plusum-exports", env="S3_BUCKET_EXPORTS")
    s3_bucket_snapshots: str = Field(default="plusum-snapshots", env="S3_BUCKET_SNAPSHOTS")

    # Slack / Teams / Jira
    slack_bot_token: Optional[str] = Field(default=None, env="SLACK_BOT_TOKEN")
    slack_default_channel: Optional[str] = Field(default=None, env="SLACK_DEFAULT_CHANNEL")
    teams_webhook_urls: List[AnyHttpUrl] = Field(default_factory=list, env="TEAMS_WEBHOOK_URLS")

    jira_base_url: Optional[AnyHttpUrl] = Field(default=None, env="JIRA_BASE_URL")
    jira_email: Optional[str] = Field(default=None, env="JIRA_EMAIL")
    jira_api_token: Optional[str] = Field(default=None, env="JIRA_API_TOKEN")

    # SES
    ses_region: str = Field(default="us-east-1", env="SES_REGION")
    ses_sender_email: Optional[str] = Field(default=None, env="SES_SENDER_EMAIL")

    # Cognito
    cognito_user_pool_id: str = Field(default="us-east-1_example", env="COGNITO_USER_POOL_ID")
    cognito_region: str = Field(default="us-east-1", env="COGNITO_REGION")
    cognito_app_client_id: str = Field(default="example-client-id", env="COGNITO_APP_CLIENT_ID")
    cognito_jwks_url: Optional[AnyHttpUrl] = Field(default=None, env="COGNITO_JWKS_URL")

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Return cached application settings.

    Using lru_cache keeps this Lambda-safe (no mutable global state),
    while avoiding repeated environment parsing.
    """

    return Settings()

