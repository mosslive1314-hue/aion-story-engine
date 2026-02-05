import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import asdict

from aion_engine.nodes import NodeTree
from aion_engine.engine import StoryEngine


class Session:
    """Manages a story creation session"""

    def __init__(self, session_dir: str, title: str, node_tree: Optional[NodeTree] = None):
        self.session_id = str(uuid.uuid4())[:8]
        self.title = title
        self.session_dir = session_dir
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.node_tree = node_tree or NodeTree()
        self.engine = StoryEngine()
        self.metadata: Dict[str, Any] = {}

    @classmethod
    def create(cls, base_dir: str, title: str) -> 'Session':
        """Create a new session"""
        session_id = str(uuid.uuid4())[:8]
        session_dir = os.path.join(base_dir, session_id)
        os.makedirs(session_dir, exist_ok=True)

        return cls(session_dir, title)

    def advance(self, user_action: str, context: Optional[Dict] = None):
        """Advance the story"""
        result = self.engine.advance(user_action, context)

        # Create node
        self.node_tree.create_node(
            user_action=user_action,
            world_state=result.world_state,
            npc_states=result.npc_states
        )

        self.updated_at = datetime.now().isoformat()
        return result

    def save(self):
        """Save session to disk"""
        # Save metadata
        metadata = {
            "session_id": self.session_id,
            "title": self.title,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata
        }

        with open(os.path.join(self.session_dir, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)

        # Save nodes
        nodes_data = {
            "root_id": self.node_tree.root_id,
            "nodes": {
                node_id: asdict(node)
                for node_id, node in self.node_tree.nodes.items()
            }
        }

        with open(os.path.join(self.session_dir, "nodes.json"), "w") as f:
            json.dump(nodes_data, f, indent=2)

    @classmethod
    def load(cls, session_dir: str) -> 'Session':
        """Load session from disk"""
        # Load metadata
        with open(os.path.join(session_dir, "metadata.json"), "r") as f:
            metadata = json.load(f)

        # Create session
        session = cls(session_dir, metadata["title"])
        session.session_id = metadata["session_id"]
        session.created_at = metadata["created_at"]
        session.updated_at = metadata["updated_at"]
        session.metadata = metadata.get("metadata", {})

        # Load nodes
        with open(os.path.join(session_dir, "nodes.json"), "r") as f:
            nodes_data = json.load(f)

        # Reconstruct node tree
        # (simplified - would need full Node reconstruction logic)

        return session
