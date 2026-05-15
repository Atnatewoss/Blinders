"""FastAPI server for the neuro-symbolic governance system."""

from __future__ import annotations

from typing import Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load API keys from .env
load_dotenv()

from .core.step2_intent_interpreter import langchain_plan
from .core.step3_metta_verifier import SymbolicVerifier
from .core.step5_tool_executor import execute_fantasy_action


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


app = FastAPI(
    title="AI Fantasy League Commissioner API",
    description="Symbolic constitutional guardrail for autonomous agents.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "authority": "metta_atomspace"}


@app.post("/api/verify", response_model=VerifyResponse)
def verify(payload: VerifyRequest) -> VerifyResponse:
    # 1. Interpret Intent
    plan = langchain_plan(payload.request, subject=payload.subject)
    
    # 2. Verify against MeTTa rules
    verifier = SymbolicVerifier()
    decision = verifier.verify_plan(plan)
    
    # 3. Execute only if allowed
    execution_results = []
    if decision.allowed:
        for action_decision in decision.actions:
            if action_decision.allowed:
                execution_results.append(execute_fantasy_action(plan.team, action_decision.action))
    else:
        execution_results.append("BLOCKED: symbolic constitutional firewall denied execution.")

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

@app.get("/api/state", response_model=StateResponse)
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