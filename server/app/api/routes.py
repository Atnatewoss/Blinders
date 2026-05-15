"""FastAPI Router for the governance endpoints."""

from __future__ import annotations
from typing import Any
from fastapi import APIRouter
from pydantic import BaseModel, Field

from ..core.step2_intent_interpreter import langchain_plan
from ..core.step3_metta_verifier import SymbolicVerifier
from ..core.step5_tool_executor import execute_fantasy_action

router = APIRouter()


class VerifyRequest(BaseModel):
    request: str = Field(..., min_length=1)
    subject: str = "atnatewos"


class VerifyResponse(BaseModel):
    plan: dict[str, Any]
    decision: dict[str, Any]
    execution_results: list[str]


class StateResponse(BaseModel):
    squad: list[dict[str, Any]]
    market: list[dict[str, Any]]
    bank: float


@router.get("/state", response_model=StateResponse)
def get_state():
    engine = SymbolicVerifier().atomspace
    squad_names = set(engine.squad("blinders_elite_fc"))
    
    squad = []
    for name in squad_names:
        p = engine.players.get(name)
        if p:
            squad.append({"name": p.name, "club": p.club, "price": p.price, "pos": p.position, "status": p.status})
            
    market = []
    for name, p in engine.players.items():
        if name not in squad_names:
            market.append({"name": p.name, "club": p.club, "price": p.price, "pos": p.position, "status": p.status})
        
    return StateResponse(
        squad=squad,
        market=market,
        bank=engine.bank("blinders_elite_fc")
    )


@router.post("/verify", response_model=VerifyResponse)
def verify(payload: VerifyRequest) -> VerifyResponse:
    # 1. Interpret Intent
    plan = langchain_plan(payload.request, subject=payload.subject)
    
    # 2. Verify against MeTTa rules
    verifier = SymbolicVerifier()
    decision = verifier.verify_plan(plan)
    
    # 3. Execute
    execution_results = []
    if decision.final_decision == "ALLOW":
        for action_decision in decision.actions:
            result = execute_fantasy_action(action_decision.action)
            execution_results.append(result)
            
    return VerifyResponse(
        plan=plan.model_dump(),
        decision=decision_to_dict(decision),
        execution_results=execution_results,
    )


def decision_to_dict(decision):
    """Helper to serialize the symbolic decision for the frontend."""
    return {
        "request": decision.request,
        "subject": decision.subject,
        "team": decision.team,
        "final_decision": decision.final_decision,
        "security_events": decision.security_events,
        "actions": [
            {
                "action": act.action.model_dump(),
                "decision": act.decision,
                "allowed": act.allowed,
                "matched_rules": act.matched_rules,
                "violated_constraints": act.violated_constraints,
                "reasoning_trace": act.reasoning_trace,
                "risk": act.risk,
                "execution_status": act.execution_status
            } for act in decision.actions
        ]
    }
