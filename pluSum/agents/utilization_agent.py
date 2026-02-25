from typing import Any, Dict

from ..llm import prompts
from ..llm.schemas import UtilizationInsight
from .base import AgentAction, AgentEvaluation, AgentResult, AgentRunContext, BaseAgent


class UtilizationAgent(BaseAgent):
    @property
    def agent_type(self) -> str:
        return "utilization"

    def run(self, context: AgentRunContext) -> AgentResult:
        prompt = prompts.utilization_prompt(context=context.params.get("context", ""), data=context.params)
        insight = self.llm_router.generate(prompt, UtilizationInsight)
        payload: Dict[str, Any] = insight.model_dump()
        self.publish_event("UTILIZATION_ANALYZED", payload)
        return AgentResult(agent_type=self.agent_type, payload=payload)

    def evaluate(self, result: AgentResult) -> AgentEvaluation:
        utilization = float(result.payload.get("average_utilization", 0.0))
        severity = "low"
        if utilization < 0.5 or utilization > 0.9:
            severity = "high"
        elif utilization < 0.6 or utilization > 0.85:
            severity = "medium"
        summary = f"Average utilization {utilization:.2f}"
        return AgentEvaluation(score=utilization, summary=summary, severity=severity)

    def next_action(self, evaluation: AgentEvaluation) -> AgentAction:
        action_type = "noop"
        if evaluation.severity in {"medium", "high"}:
            action_type = "notify"
        return AgentAction(action_type=action_type, payload=evaluation.model_dump())

