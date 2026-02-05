from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class CognitionResult:
    npc_states: dict
    npc_actions: dict
    decisions: list


class CognitionEngine:
    """Layer 2: Cognition engine for NPC decision-making"""

    def __init__(self):
        self.npcs = {}

    def process(self, blackboard) -> CognitionResult:
        """Process NPC cognition based on world state"""
        new_npc_states = blackboard.npcs.copy()
        npc_actions = {}
        decisions = []

        # Process each NPC
        for npc_id, npc_state in blackboard.npcs.items():
            action = self._decide_action(npc_id, npc_state, blackboard.world_state)
            npc_actions[npc_id] = [action]

        return CognitionResult(
            npc_states=new_npc_states,
            npc_actions=npc_actions,
            decisions=decisions
        )

    def _decide_action(self, npc_id: str, npc_state: dict, world_state: dict) -> dict:
        """Decide NPC action based on state and world"""
        # Scientist NPC responds to fire
        if npc_state.get("role") == "scientist":
            if world_state.get("fire_active", False):
                stress = npc_state.get("stress_level", 0)
                if stress > 0.5:
                    return {
                        "action": "extinguish_fire",
                        "confidence": 0.9,
                        "reasoning": "High stress from fire, attempting to extinguish"
                    }
                else:
                    return {
                        "action": "prioritize_notes",
                        "confidence": 0.8,
                        "reasoning": "Fire detected, protecting research notes first"
                    }

        return {
            "action": "continue_task",
            "confidence": 0.5,
            "reasoning": "No immediate threat detected"
        }
