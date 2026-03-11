from typing import List, Optional

from pydantic import BaseModel, Field


class UtilizationInsight(BaseModel):
    project_id: str
    average_utilization: float = Field(ge=0.0, le=1.0)
    underutilized_resources: List[str] = Field(default_factory=list)
    overutilized_resources: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class RenewalRecommendation(BaseModel):
    contract_id: str
    renewal_risk_score: float = Field(ge=0.0, le=1.0)
    key_risks: List[str] = Field(default_factory=list)
    upsell_opportunities: List[str] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)


class TimesheetEnforcementDecision(BaseModel):
    user_id: str
    missing_days: List[str] = Field(default_factory=list)
    severity: str
    notification_message: str


class ResourcePerformanceInsight(BaseModel):
    resource_id: str
    performance_score: float = Field(ge=0.0, le=1.0)
    strengths: List[str] = Field(default_factory=list)
    improvements: List[str] = Field(default_factory=list)


class ClientSentimentInsight(BaseModel):
    client_id: str
    sentiment_score: float = Field(ge=0.0, le=1.0)
    sentiment_label: str
    key_themes: List[str] = Field(default_factory=list)
    churn_risk_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class EmailSummary(BaseModel):
    subject: str
    body_markdown: str
    to_addresses: List[str]


class AgentLLMInput(BaseModel):
    """Generic input wrapper for agent prompts."""

    context: str
    data: dict

