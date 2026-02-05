import uuid
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Node:
    node_id: str
    parent_id: Optional[str]
    timestamp: str
    world_state: Dict[str, Any]
    npc_states: Dict[str, Any]
    user_action: str
    narrative: str
    choices: List[Dict[str, str]]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class NodeTree:
    """Manages branching story paths"""

    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.root_id: Optional[str] = None

    def create_node(
        self,
        user_action: str,
        world_state: Dict[str, Any],
        parent_id: Optional[str] = None,
        npc_states: Optional[Dict[str, Any]] = None
    ) -> Node:
        """Create a new story node"""
        node_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()

        node = Node(
            node_id=node_id,
            parent_id=parent_id,
            timestamp=timestamp,
            world_state=world_state,
            npc_states=npc_states or {},
            user_action=user_action,
            narrative="",
            choices=[]
        )

        self.nodes[node_id] = node

        if parent_id is None and self.root_id is None:
            self.root_id = node_id

        return node

    def get_node(self, node_id: str) -> Optional[Node]:
        """Get a node by ID"""
        return self.nodes.get(node_id)

    def get_children(self, parent_id: str) -> List[Node]:
        """Get all child nodes of a parent"""
        return [
            node for node in self.nodes.values()
            if node.parent_id == parent_id
        ]

    def get_path_to_root(self, node_id: str) -> List[Node]:
        """Get path from node to root"""
        path = []
        current = self.get_node(node_id)

        while current:
            path.append(current)
            if current.parent_id:
                current = self.get_node(current.parent_id)
            else:
                break

        return list(reversed(path))
