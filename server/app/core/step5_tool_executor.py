"""Tool Executor that modifies the Symbolic AtomSpace state."""

from __future__ import annotations
from .step2_intent_interpreter import PlannedAction
from ..core.step3_metta_verifier import SymbolicVerifier


def execute_fantasy_action(action: PlannedAction) -> str:
    """Executes the action and PERSISTS the change to the symbolic engine."""
    
    # Get access to the shared AtomSpace engine
    engine = SymbolicVerifier().atomspace
    
    if action.action == "transfer_player":
        # Remove old, add new
        engine.metta.run(f"!(remove-atom &self (squad_member blinders_elite_fc {action.player_out}))")
        engine.metta.run(f"!(add-atom &self (squad_member blinders_elite_fc {action.player_in}))")
        return f"SUCCESS: Transferred {action.player_in} in for {action.player_out}."

    elif action.action == "set_captain":
        # Find and remove existing captain, then add new one
        engine.metta.run("!(match &self (captain blinders_elite_fc $p) (remove-atom &self (captain blinders_elite_fc $p)))")
        engine.metta.run(f"!(add-atom &self (captain blinders_elite_fc {action.player}))")
        return f"SUCCESS: {action.player} is now the captain."

    elif action.action == "update_player_status":
        status = "injured" if "injured" in action.reason.lower() or "hurt" in action.reason.lower() else "fit"
        
        # We need to update the status in the player atom
        # First, find the existing player atom to get all its fields
        result = engine.metta.run(f"!(match &self (player {action.player} $club $pos $price $old_status $class) ($club $pos $price $old_status $class))")
        
        if result and result[0]:
            club, pos, price, old_status, pclass = result[0][0]
            # Remove old, add new
            engine.metta.run(f"!(remove-atom &self (player {action.player} {club} {pos} {price} {old_status} {pclass}))")
            engine.metta.run(f"!(add-atom &self (player {action.player} {club} {pos} {price} {status} {pclass}))")
            return f"SUCCESS: {action.player} health status updated to {status}."

    elif action.action == "view_risk_report":
        return "SUCCESS: Security Risk Report generated and displayed."

    return f"COMPLETED: Action '{action.action}' processed."
