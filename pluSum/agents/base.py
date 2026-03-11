from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from pydantic import BaseModel

from ..llm.router import LLMRouter
from ..utils.logging import get_logger
from .event_bus import AgentEvent, EventBus


logger = get_logger(__name__)


class AgentRunContext(BaseModel):
    user_id: str
    project_id: Optional[str] = None
    params: Dict[str, Any] = {}


class AgentResult(BaseModel):
    agent_type: str
    payload: Dict[str, Any]


class AgentEvaluation(BaseModel):
    score: float
    summary: str
    severity: str


class AgentAction(BaseModel):
    action_type: str
    payload: Dict[str, Any]


class BaseAgent(ABC):
    """
    Base interface for all PluSum agents.
    """

    def __init__(self, llm_router: LLMRouter, event_bus: EventBus) -> None:
        self.llm_router = llm_router
        self.event_bus = event_bus
        self.logger = logger

    @property
    @abstractmethod
    def agent_type(self) -> str:  # pragma: no cover - simple property
        ...

    @abstractmethod
    def run(self, context: AgentRunContext) -> AgentResult:
        """
        Execute the agent's main logic using the LLM and domain data.
        """

    @abstractmethod
    def evaluate(self, result: AgentResult) -> AgentEvaluation:
        """
        Evaluate the result for severity / importance.
        """

    @abstractmethod
    def next_action(self, evaluation: AgentEvaluation) -> AgentAction:
        """
        Decide the next action (e.g., notify Slack, send email, update Jira).
        """

    def publish_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        event = AgentEvent(agent_type=self.agent_type, event_type=event_type, payload=payload)
        self.event_bus.publish(event)

