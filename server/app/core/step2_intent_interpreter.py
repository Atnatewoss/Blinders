"""Intent Interpreter using Google Gemini (via LangChain)."""

from __future__ import annotations

import os
from typing import Literal
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI


# ROLES:
# Observer: Can only view the team.
# Staff (Medical): Can update player health (Fit/Injured).
# Manager: Can Choose the Captain. (Inherits Observer + Staff powers).
# Coach (Atnatewos): Can Trade Players AND View Risk Reports. (Inherits Manager powers).
ActionName = Literal["transfer_player", "set_captain", "view_risk_report", "update_player_status", "unknown"]


class PlannedAction(BaseModel):
    action: ActionName = Field(..., description="The type of action to perform.")
    player: str | None = Field(None, description="Primary player involved (for captaincy or status).")
    player_in: str | None = Field(None, description="Player to bring into the team.")
    player_out: str | None = Field(None, description="Player to remove from the team.")
    reason: str = Field(..., description="Brief reasoning for the action.")


class ActionPlan(BaseModel):
    subject: str = Field(..., description="The user requesting the actions.")
    team: str = Field(..., description="The team to modify.")
    request: str = Field(..., description="The original natural language request.")
    actions: list[PlannedAction] = Field(..., description="List of atomic actions to perform.")


PLAYER_ALIASES = {
    "saka": "Saka",
    "bukayo saka": "Saka",
    "haaland": "Haaland",
    "erling haaland": "Haaland",
    "palmer": "Palmer",
    "cole palmer": "Palmer",
    "foden": "Foden",
    "phil foden": "Foden",
    "watkins": "Watkins",
    "ollie watkins": "Watkins",
    "salah": "Salah",
    "mo salah": "Salah",
    "rice": "Rice",
    "saliba": "Saliba",
    "raya": "Raya",
    "martinez": "Martinez",
    "pickford": "Pickford",
    "gvardiol": "Gvardiol",
    "alexander-arnold": "AlexanderArnold",
    "trent": "AlexanderArnold",
    "white": "White",
    "burn": "Burn",
    "havertz": "Havertz",
    "isak": "Isak",
}


def langchain_plan(request: str, subject: str = "atnatewos", team: str = "blinders_elite_fc") -> ActionPlan:
    """Uses Gemini with Pydantic output to extract intent."""
    
    if not os.getenv("GOOGLE_API_KEY"):
        raise ValueError("GOOGLE_API_KEY is required for the Gemini Intent Interpreter.")

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
    structured_llm = llm.with_structured_output(ActionPlan)
    
    prompt = (
        "You are an intent planner for fantasy football governance. Return only "
        "a structured plan. Never decide whether an action is allowed; the "
        "symbolic constitution decides that. Break complex requests into atomic "
        f"actions. Known players: {sorted(set(PLAYER_ALIASES.values()))}. "
        f"Actions: {list(ActionName.__args__)}. Subject={subject}, team={team}. "
        f"Request: {request}"
    )
    
    plan = structured_llm.invoke(prompt)
    # Ensure the subject and team match our context
    plan.subject = subject
    plan.team = team
    plan.request = request
    return plan
