from textwrap import dedent
from typing import Type

from pydantic import BaseModel

from .schemas import (
    ClientSentimentInsight,
    EmailSummary,
    RenewalRecommendation,
    ResourcePerformanceInsight,
    TimesheetEnforcementDecision,
    UtilizationInsight,
)


def _schema_instructions(schema_model: Type[BaseModel]) -> str:
    json_schema = schema_model.model_json_schema()
    return dedent(
        f"""
        You are a precise JSON API. Respond with a single JSON object only.
        It must fully conform to this JSON schema:

        {json_schema}

        Do not include any commentary, markdown, or text outside the JSON.
        """
    ).strip()


def utilization_prompt(context: str, data: dict) -> str:
    base = dedent(
        """
        You are a PMO analyst specializing in resource utilization for service-based companies.
        Analyze the context and data and produce utilization insights and recommendations.

        Context:
        {context}

        Data:
        {data}
        """
    ).strip()
    return base + "\n\n" + _schema_instructions(UtilizationInsight)


def renewal_prompt(context: str, data: dict) -> str:
    base = dedent(
        """
        You are a contract renewal strategist.
        Analyze the context and data about upcoming renewals.
        Identify risk, upsell opportunities, and concrete actions.

        Context:
        {context}

        Data:
        {data}
        """
    ).strip()
    return base + "\n\n" + _schema_instructions(RenewalRecommendation)


def timesheet_enforcement_prompt(context: str, data: dict) -> str:
    base = dedent(
        """
        You are responsible for timesheet policy enforcement.
        Determine missing entries and craft concise, professional notifications.

        Context:
        {context}

        Data:
        {data}
        """
    ).strip()
    return base + "\n\n" + _schema_instructions(TimesheetEnforcementDecision)


def resource_performance_prompt(context: str, data: dict) -> str:
    base = dedent(
        """
        You evaluate resource performance for project delivery.
        Provide a performance score, strengths, and improvements.

        Context:
        {context}

        Data:
        {data}
        """
    ).strip()
    return base + "\n\n" + _schema_instructions(ResourcePerformanceInsight)


def client_sentiment_prompt(context: str, data: dict) -> str:
    base = dedent(
        """
        You analyze client sentiment from interactions, tickets, and survey data.
        Provide a sentiment score, label, and key themes.

        Context:
        {context}

        Data:
        {data}
        """
    ).strip()
    return base + "\n\n" + _schema_instructions(ClientSentimentInsight)


def email_summary_prompt(context: str, data: dict) -> str:
    base = dedent(
        """
        You generate concise PMO email summaries for executives.
        Create a subject and markdown body summarizing recent PMO highlights.

        Context:
        {context}

        Data:
        {data}
        """
    ).strip()
    return base + "\n\n" + _schema_instructions(EmailSummary)

