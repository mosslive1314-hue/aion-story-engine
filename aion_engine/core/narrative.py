from typing import List


class NarrativeEngine:
    """Layer 3: Narrative engine for story generation"""

    def __init__(self):
        self.narrative_templates = {
            "fire": "艾萨克看着燃烧的{}，{}",
            "extinguish": "艾萨克{}，试图{}",
            "escape": "火焰已经{}，艾萨克{}"
        }

    def generate(self, blackboard) -> str:
        """Generate narrative based on current state"""
        narrative_parts = []

        # Fire description
        if blackboard.world_state.get("fire_active", False):
            fuel = blackboard.world_state.get("fire_fuel", "植物")
            npc = self._get_npc_state("isaac", blackboard)
            stress = npc.get("stress_level", 0)

            if stress > 0.7:
                narrative_parts.append(
                    "艾萨克看着火焰蔓延，他的眼神充满了恐慌。"
                )
            else:
                narrative_parts.append(
                    "艾萨克注意到植物开始燃烧，表情变得严肃。"
                )

        # NPC actions
        for npc_id, npc_state in blackboard.npcs.items():
            action = npc_state.get("current_action")
            if action:
                narrative_parts.append(f"艾萨克{action}。")

        return " ".join(narrative_parts)

    def predict_next_event(self, blackboard) -> str:
        """Predict what might happen next"""
        if blackboard.world_state.get("fire_active", False):
            return "火灾可能会继续蔓延，除非被扑灭"

        return "艾萨克将继续他的研究工作"

    def _get_npc_state(self, npc_id: str, blackboard) -> dict:
        """Helper to get NPC state"""
        return blackboard.npcs.get(npc_id, {})
