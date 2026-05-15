"""Symbolic constitutional verifier."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
import re

from ..atomspace.step1_atomspace_engine import AtomSpace
from .step2_intent_interpreter import ActionPlan, PlannedAction


@dataclass
class ActionDecision:
    action: PlannedAction
    decision: str
    allowed: bool
    matched_rules: list[str] = field(default_factory=list)
    violated_constraints: list[str] = field(default_factory=list)
    reasoning_trace: list[str] = field(default_factory=list)
    risk: str = "low"
    execution_status: str = "blocked"


@dataclass
class GuardrailDecision:
    request: str
    subject: str
    team: str
    final_decision: str
    actions: list[ActionDecision]
    security_events: list[str] = field(default_factory=list)

    @property
    def allowed(self) -> bool:
        return self.final_decision == "ALLOW"


class SymbolicVerifier:
    def __init__(self, atomspace: AtomSpace | None = None):
        self.atomspace = atomspace or AtomSpace()

    def verify_plan(self, plan: ActionPlan) -> GuardrailDecision:
        simulated_squad = self.atomspace.squad(plan.team)
        decisions: list[ActionDecision] = []
        for action in plan.actions:
            decision = self.verify_action(plan.subject, plan.team, action, simulated_squad)
            decisions.append(decision)
            if decision.allowed and action.action == "transfer_player":
                simulated_squad = self._apply_transfer(simulated_squad, action)

        final = "ALLOW" if decisions and all(decision.allowed for decision in decisions) else "DENY"
        return GuardrailDecision(plan.request, plan.subject, plan.team, final, decisions, [])

    def verify_action(
        self, subject: str, team: str, action: PlannedAction, current_squad: list[str] | None = None
    ) -> ActionDecision:
        current_squad = current_squad or self.atomspace.squad(team)
        decision = ActionDecision(action=action, decision="ALLOW", allowed=True)

        if action.action == "unknown":
            self._deny(decision, "No constitutional action matched the request.", "UNKNOWN")
            return decision

        # 1. Permission Check (Inheritance Proof)
        self._check_permission(subject, action, decision)
        
        # 2. Context Check (Deadline/Status)
        self._check_context(action, decision)

        # 3. Constraint Checks (Budget/Squad/Quota)
        for constraint_name, law_id in self._action_constraints(action.action):
            if constraint_name == "max_squad_size":
                self._check_squad_size(team, action, current_squad, decision, law_id)
            elif constraint_name == "max_players_per_club":
                self._check_club_quota(action, current_squad, decision, law_id)
            elif constraint_name == "budget_non_negative":
                self._check_budget(team, action, decision, law_id)
            elif constraint_name == "captain_must_be_in_squad":
                self._check_captain_in_squad(action, current_squad, decision, law_id)
            elif constraint_name == "captain_must_be_fit":
                self._check_captain_fit(action, decision, law_id)
            elif constraint_name == "captain_class_candidate":
                self._check_captain_class(action, decision, law_id)

        # 4. Risk Assessment
        decision.risk = self.atomspace.risk_for(action.action, "any")
        if decision.risk in {"high", "critical"}:
            decision.reasoning_trace.append(f"LOG: High risk action detected ({decision.risk}).")

        if decision.allowed:
            decision.execution_status = "ready"
        return decision

    def _check_permission(self, subject: str, action: PlannedAction, decision: ActionDecision) -> None:
        # Law L1: Role-Based Authorization Proof
        role = self.atomspace.subject_role(subject)
        if not role:
            self._deny(decision, f"Subject {subject} has no assigned role.", "L1")
            return
            
        # Recursive proof: Does the role (or its parents) have permission for this action?
        allowed, proof = self.atomspace.permission_proof(role, action.action)
        if allowed:
            decision.matched_rules.append("L1 role_authority")
            decision.reasoning_trace.append(f"Authority verified for {role} -> {action.action}.")
        else:
            self._deny(decision, f"{role} lacks permission {action.action}.", "L1")

    def _check_context(self, action: PlannedAction, decision: ActionDecision) -> None:
        for action_name, key, expected, law_id in self.atomspace.all("requires_context"):
            if action_name != action.action:
                continue
            actual = self.atomspace.context(key)
            if actual == expected:
                decision.matched_rules.append(f"{law_id} context")
            else:
                self._deny(decision, f"Context gate {key} failed (Expected {expected}, got {actual}).", law_id)

    def _action_constraints(self, action_name: str) -> list[tuple[str, str]]:
        return [(constraint, law_id) for name, constraint, law_id in self.atomspace.all("action_constraint") if name == action_name]

    def _check_squad_size(self, team: str, action: PlannedAction, squad: list[str], decision: ActionDecision, law_id: str) -> None:
        projected = self._apply_transfer(squad, action)
        expected = int(self.atomspace.constraint("max_squad_size"))
        if len(projected) == expected:
            decision.matched_rules.append(f"{law_id} max_squad_size")
        else:
            self._deny(decision, f"Squad size {len(projected)} must equal {expected}.", law_id)

    def _check_club_quota(self, action: PlannedAction, squad: list[str], decision: ActionDecision, law_id: str) -> None:
        projected = self._apply_transfer(squad, action)
        max_per_club = int(self.atomspace.constraint("max_players_per_club"))
        counts = Counter(self.atomspace.players[player].club for player in projected if player in self.atomspace.players)
        for club, count in counts.items():
            if count > max_per_club:
                self._deny(decision, f"{club} exceeds quota ({count}/{max_per_club}).", law_id)
                return
        decision.matched_rules.append(f"{law_id} club_quota")

    def _check_budget(self, team: str, action: PlannedAction, decision: ActionDecision, law_id: str) -> None:
        if action.action != "transfer_player":
            return
        bought = self.atomspace.players[action.player_in].price if action.player_in in self.atomspace.players else 0
        sold = self.atomspace.players[action.player_out].price if action.player_out in self.atomspace.players else 0
        remaining = self.atomspace.bank(team) + sold - bought
        if remaining >= 0:
            decision.matched_rules.append(f"{law_id} budget_integrity")
        else:
            self._deny(decision, f"Insufficient funds (Short by {abs(remaining):.1f}M).", law_id)

    def _check_captain_in_squad(self, action: PlannedAction, squad: list[str], decision: ActionDecision, law_id: str) -> None:
        if action.player in squad:
            decision.matched_rules.append(f"{law_id} captain_in_squad")
        else:
            self._deny(decision, f"{action.player} is not in your squad.", law_id)

    def _check_captain_fit(self, action: PlannedAction, decision: ActionDecision, law_id: str) -> None:
        player = self.atomspace.players.get(action.player or "")
        if player and player.status == "fit":
            decision.matched_rules.append(f"{law_id} captain_health")
        else:
            status = player.status if player else "unknown"
            self._deny(decision, f"{action.player} is {status}; must be fit.", law_id)

    def _check_captain_class(self, action: PlannedAction, decision: ActionDecision, law_id: str) -> None:
        player = self.atomspace.players.get(action.player or "")
        if not player: return
        ok, _ = self.atomspace.inherits(player.player_class, "captain_candidate")
        if ok:
            decision.matched_rules.append(f"{law_id} class_validation")
        else:
            self._deny(decision, f"{player.player_class} is not a valid captain candidate.", law_id)

    def _apply_transfer(self, squad: list[str], action: PlannedAction) -> list[str]:
        if action.action != "transfer_player":
            return list(squad)
        projected = [p for p in squad if p != action.player_out]
        if action.player_in: projected.append(action.player_in)
        return projected

    def _deny(self, decision: ActionDecision, message: str, law_id: str) -> None:
        decision.allowed = False
        decision.decision = "DENY"
        decision.violated_constraints.append(f"{law_id}: {message}")
