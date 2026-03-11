from typing import Any, Dict

from ..llm import prompts
from ..llm.schemas import TimesheetEnforcementDecision
from .base import AgentAction, AgentEvaluation, AgentResult, AgentRunContext, BaseAgent


class TimesheetEnforcementAgent(BaseAgent):
    @property
    def agent_type(self) -> str:
        return "timesheet_enforcement"

    def run(self, context: AgentRunContext) -> AgentResult:
        prompt = prompts.timesheet_enforcement_prompt(
            context=context.params.get("context", ""), data=context.params
        )
        decision = self.llm_router.generate(prompt, TimesheetEnforcementDecision)
        payload: Dict[str, Any] = decision.model_dump()
        self.publish_event("TIMESHEET_ENFORCEMENT_ANALYZED", payload)
        return AgentResult(agent_type=self.agent_type, payload=payload)

    def evaluate(self, result: AgentResult) -> AgentEvaluation:
        missing_days = result.payload.get("missing_days", []) or []
        severity = result.payload.get("severity", "low")
        score = min(len(missing_days) / 5.0, 1.0)
        summary = f"{len(missing_days)} missing timesheet days"
        return AgentEvaluation(score=score, summary=summary, severity=severity)

    def next_action(self, evaluation: AgentEvaluation) -> AgentAction:
        action_type = "noop"
        if evaluation.score > 0.0:
            action_type = "notify"
        return AgentAction(action_type=action_type, payload=evaluation.model_dump())

