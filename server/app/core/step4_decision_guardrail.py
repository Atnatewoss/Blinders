"""Logic Bridge: LangChain Tools with Symbolic Interceptors."""

from __future__ import annotations

from langchain.tools import tool
from .step2_intent_interpreter import PlannedAction
from .step3_metta_verifier import SymbolicVerifier
from .step5_tool_executor import execute_fantasy_action


class GuardedToolKit:
    """A collection of tools that are protected by the MeTTa Symbolic Verifier."""

    def __init__(self, subject: str = "atnatewos", team: str = "blinders_elite_fc"):
        self.subject = subject
        self.team = team
        self.verifier = SymbolicVerifier()

    @tool
    def transfer_player(self, player_in: str, player_out: str) -> str:
        """
        Executes a player transfer in the Fantasy Premier League.
        Requires Coach level permission and respects budget/squad constraints.
        """
        action = PlannedAction(action="transfer_player", player_in=player_in, player_out=player_out)
        return self._run_guarded(action)

    @tool
    def set_captain(self, player_name: str) -> str:
        """
        Sets a player as the team captain. 
        Requires Manager level permission. Player must be fit and in the squad.
        """
        action = PlannedAction(action="set_captain", player=player_name)
        return self._run_guarded(action)

    @tool
    def update_player_status(self, player_name: str, status: str) -> str:
        """
        Updates a player's health status (e.g., 'fit', 'injured').
        Requires Medical Staff level permission.
        """
        action = PlannedAction(action="update_player_status", player=player_name, reason=status)
        return self._run_guarded(action)

    @tool
    def view_risk_report(self) -> str:
        """
        Displays a security risk assessment for the current team.
        Requires high-level Coach clearance.
        """
        action = PlannedAction(action="view_risk_report")
        return self._run_guarded(action)

    def _run_guarded(self, action: PlannedAction) -> str:
        """The Internal Interceptor: Calls MeTTa before tool execution."""
        decision = self.verifier.verify_action(self.subject, self.team, action)
        if decision.allowed:
            return execute_fantasy_action(self.team, action)
        else:
            violations = "; ".join(decision.violated_constraints)
            return f"ACCESS DENIED by Symbolic Guardrail: {violations}"


def get_fpl_tools(subject: str = "atnatewos", team: str = "blinders_elite_fc"):
    """Returns a list of LangChain tools ready for an agent."""
    kit = GuardedToolKit(subject=subject, team=team)
    return [
        kit.transfer_player,
        kit.set_captain,
        kit.update_player_status,
        kit.view_risk_report
    ]
