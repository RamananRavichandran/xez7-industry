from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, DefaultDict, Dict, List

from ..utils.logging import get_logger


logger = get_logger(__name__)


@dataclass
class AgentEvent:
    agent_type: str
    event_type: str
    payload: Dict[str, Any]


class EventBus:
    """
    Simple in-process event bus abstraction.

    In AWS Step Functions deployments, events can be serialized and passed
    between Lambda states using this same structure.
    """

    def __init__(self) -> None:
        self._subscribers: DefaultDict[str, List[Callable[[AgentEvent], None]]] = DefaultDict(list)

    def publish(self, event: AgentEvent) -> None:
        logger.info("Publishing event %s from agent %s", event.event_type, event.agent_type)
        for handler in self._subscribers[event.event_type]:
            handler(event)

    def subscribe(self, event_type: str, handler: Callable[[AgentEvent], None]) -> None:
        self._subscribers[event_type].append(handler)

