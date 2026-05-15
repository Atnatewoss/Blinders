"""Hyperon AtomSpace Engine for MeTTa rules."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from hyperon import MeTTa

ROOT = Path(__file__).resolve().parent
RULES_PATH = ROOT / "rules.metta"
VERIF_PATH = ROOT / "verification.metta"


@dataclass(frozen=True)
class Player:
    name: str
    club: str
    position: str
    price: float
    status: str
    player_class: str


class AtomSpace:
    """Interface to the Hyperon MeTTa interpreter."""

    def __init__(self, rules_path: Path = RULES_PATH, verif_path: Path = VERIF_PATH):
        self.metta = MeTTa()
        self._load_files([rules_path, verif_path])
        self.players = self._parse_players()

    def _load_files(self, paths: list[Path]):
        """Directly injects MeTTa rules from files into the AtomSpace."""
        for path in paths:
            if path.exists():
                # Read the file and execute its contents directly
                # This is more reliable than import! with absolute Windows paths
                content = path.read_text(encoding="utf-8")
                self.metta.run(content)

    def _parse_players(self) -> dict[str, Player]:
        """Converts MeTTa player atoms into Python dataclasses for performance."""
        result = self.metta.run("!(match &self (player $name $club $pos $price $status $class) ($name $club $pos $price $status $class))")
        players = {}
        if not result or not result[0]:
            return {}
        for player_atoms in result[0]:
            # player_atoms is a list of atoms: [name, club, pos, price, status, class]
            data = [str(atom).strip('"') for atom in player_atoms.get_children()]
            players[data[0]] = Player(data[0], data[1], data[2], float(data[3]), data[4], data[5])
        return players

    def run(self, query: str) -> list[str]:
        """Runs a raw MeTTa query and returns string results."""
        result = self.metta.run(query)
        if not result: return []
        return [str(atom).strip('"') for atom in result[0]]

    def all(self, relation: str) -> list[tuple[str, ...]]:
        """Finds all facts matching a relation name."""
        result = self.metta.run(f"!(match &self ({relation} $a $b $c) ($a $b $c))")
        if not result or not result[0]:
            # Try 2-ary
            result = self.metta.run(f"!(match &self ({relation} $a $b) ($a $b))")
        
        if not result or not result[0]: return []
        
        facts = []
        for atoms in result[0]:
            facts.append(tuple(str(atom).strip('"') for atom in atoms.get_children()))
        return facts

    def inherits(self, child: str, ancestor: str) -> tuple[bool, list[str]]:
        """Checks if child inherits from ancestor using recursive MeTTa logic."""
        result = self.metta.run(f"!(inherits {child} {ancestor})")
        is_true = any(str(atom) == "True" for sublist in result for atom in sublist)
        return is_true, ["MeTTa recursive proof successful" if is_true else "No inheritance path found"]

    def permission_proof(self, role: str, permission: str) -> tuple[bool, list[str]]:
        """Symbolic proof path for permissions."""
        result = self.metta.run(f"!(permission_proof {role} {permission})")
        is_true = any(str(atom) == "True" for sublist in result for atom in sublist)
        return is_true, ["Symbolic proof found in AtomSpace" if is_true else "No permission proof possible"]

    def deny_proof(self, role: str, permission: str) -> tuple[bool, list[str]]:
        """Checks for explicit denials."""
        result = self.metta.run(f"!(has-deny {role} {permission})")
        is_true = any(str(atom) == "True" for sublist in result for atom in sublist)
        return is_true, ["Explicit DENY proof found" if is_true else "No explicit denial"]

    def law_body(self, law_id: str) -> str:
        result = self.metta.run(f"!(match &self (law {law_id} $title $body) $body)")
        if not result or not result[0]: return "Symbolic Rule"
        return str(result[0][0]).strip('"')

    def risk_for(self, action: str, target: str) -> str:
        result = self.metta.run(f"!(match &self (risk {action} {target} $lvl) $lvl)")
        if not result or not result[0]:
            result = self.metta.run(f"!(match &self (risk {action} any $lvl) $lvl)")
        
        if not result or not result[0]: return "low"
        return str(result[0][0]).strip('"')

    def constraint(self, name: str, team: str | None = None, default: float = 0) -> float:
        query = f"!(match &self (constraint {name} {team} $val) $val)" if team else f"!(match &self (constraint {name} $val) $val)"
        result = self.metta.run(query)
        if not result or not result[0]: return default
        return float(str(result[0][0]))

    def context(self, key: str) -> str | None:
        result = self.metta.run(f"!(match &self (context {key} $val) $val)")
        if not result or not result[0]: return None
        return str(result[0][0]).strip('"')

    def subject_role(self, subject: str) -> str | None:
        """Robustly finds the role for a subject, handling symbols and strings."""
        # Try as symbol first
        result = self.metta.run(f"!(match &self (subject {subject} $role) $role)")
        if not result or not result[0]:
            # Try as quoted string fallback
            result = self.metta.run(f'!(match &self (subject "{subject}" $role) $role)')
            
        if not result or not result[0]: 
            return None
            
        return str(result[0][0]).strip('"')

    def bank(self, team: str) -> float:
        result = self.metta.run(f"!(match &self (bank {team} $amt) $amt)")
        if not result or not result[0]: return 0.0
        return float(str(result[0][0]))

    def squad(self, team: str) -> list[str]:
        result = self.metta.run(f"!(match &self (squad {team} $p) $p)")
        if not result or not result[0]: return []
        return [str(atom).strip('"') for atom in result[0]]
