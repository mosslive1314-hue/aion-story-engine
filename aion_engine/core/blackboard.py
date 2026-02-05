from typing import Dict, Any, List


class Blackboard:
    """Central data bus for all layers to share state"""

    def __init__(self):
        self.world_state: Dict[str, Any] = {}
        self.npcs: Dict[str, Any] = {}
        self.event_queue: List[Dict[str, Any]] = []
        self.timestamp: str = ""

    def update_world_state(self, key: str, value: Any):
        """Update a world state property"""
        self.world_state[key] = value

    def update_npc_state(self, npc_id: str, key: str, value: Any):
        """Update an NPC's state"""
        if npc_id not in self.npcs:
            self.npcs[npc_id] = {}
        self.npcs[npc_id][key] = value

    def add_event(self, event: Dict[str, Any]):
        """Add an event to the queue"""
        self.event_queue.append(event)
