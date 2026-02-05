from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass

from aion_engine.core.blackboard import Blackboard
from aion_engine.core.physics import PhysicsEngine
from aion_engine.core.cognition import CognitionEngine
from aion_engine.core.narrative import NarrativeEngine


@dataclass
class StoryResult:
    world_state: dict
    npc_states: dict
    npc_actions: dict
    narrative: str
    prediction: str
    timestamp: str


class StoryEngine:
    """Main orchestrator for the 3-layer story engine"""

    def __init__(self):
        self.blackboard = Blackboard()
        self.physics_engine = PhysicsEngine()
        self.cognition_engine = CognitionEngine()
        self.narrative_engine = NarrativeEngine()

    def advance(self, user_action: str, context: Optional[Dict] = None) -> StoryResult:
        """Advance the story based on user action"""
        # Initialize context
        if context:
            for key, value in context.items():
                self.blackboard.update_world_state(key, value)

        # Initialize Isaac if not exists
        if "isaac" not in self.blackboard.npcs:
            self.blackboard.update_npc_state("isaac", "role", "scientist")
            self.blackboard.update_npc_state("isaac", "stress_level", 0.6)

        # Process user action through physics
        if "点燃" in user_action or "打翻" in user_action:
            self.blackboard.update_world_state("fire_active", True)
            self.blackboard.update_world_state("oxygen_level", 0.18)

        # Layer 1: Physics
        physics_result = self.physics_engine.process(self.blackboard)
        self.blackboard.world_state.update(physics_result.world_state)

        # Layer 2: Cognition
        cognition_result = self.cognition_engine.process(self.blackboard)

        # Layer 3: Narrative
        narrative = self.narrative_engine.generate(self.blackboard)
        prediction = self.narrative_engine.predict_next_event(self.blackboard)

        return StoryResult(
            world_state=self.blackboard.world_state.copy(),
            npc_states=self.blackboard.npcs.copy(),
            npc_actions=cognition_result.npc_actions,
            narrative=narrative,
            prediction=prediction,
            timestamp=datetime.now().isoformat()
        )
