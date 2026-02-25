from typing import Any, Dict

from ..llm import prompts
from ..llm.schemas import RenewalRecommendation
from .base import AgentAction, AgentEvaluation, AgentResult, AgentRunContext, BaseAgent


class ContractRenewalAgent(BaseAgent):
    @property
    def agent_type(self) -> str:
        return "contract_renewal"

    def run(self, context: AgentRunContext) -> AgentResult:
        prompt = prompts.renewal_prompt(context=context.params.get("context", ""), data=context.params)
        rec = self.llm_router.generate(prompt, RenewalRecommendation)
        payload: Dict[str, Any] = rec.model_dump()
        self.publish_event("CONTRACT_RENEWAL_ANALYZED", payload)
        return AgentResult(agent_type=self.agent_type, payload=payload)

    def evaluate(self, result: AgentResult) -> AgentEvaluation:
        risk = float(result.payload.get("renewal_risk_score", 0.0))
        severity = "low"
        if risk > 0.7:
            severity = "high"
        elif risk > 0.4:
            severity = "medium"
        summary = f"Contract renewal risk {risk:.2f}"
        return AgentEvaluation(score=risk, summary=summary, severity=severity)

    def next_action(self, evaluation: AgentEvaluation) -> AgentAction:
        action_type = "noop"
        if evaluation.severity in {"medium", "high"}:
            action_type = "notify"
        return AgentAction(action_type=action_type, payload=evaluation.model_dump())

