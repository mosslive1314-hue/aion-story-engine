import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Change:
    """Represents a change in collaborative editing"""
    change_id: str
    session_id: str
    user_id: str
    change_type: str
    content: Dict[str, Any]
    timestamp: str
    parent_change_id: Optional[str] = None


@dataclass
class Session:
    """Represents a collaborative story session"""
    session_id: str
    name: str
    owner_id: str
    collaborators: Dict[str, str] = field(default_factory=dict)  # user_id -> role
    changes: List[Change] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


class CollaborationManager:
    """Manages multi-user collaborative story editing"""

    def __init__(self):
        self.sessions: Dict[str, Session] = {}

    def create_session(self, name: str, owner_id: str) -> Session:
        """Create a new collaborative session"""
        session = Session(
            session_id=str(uuid.uuid4())[:8],
            name=name,
            owner_id=owner_id,
        )

        self.sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID"""
        return self.sessions.get(session_id)

    def add_collaborator(self, session_id: str, user_id: str, role: str = "viewer"):
        """Add a collaborator to a session"""
        if session_id in self.sessions:
            self.sessions[session_id].collaborators[user_id] = role
            self.sessions[session_id].updated_at = datetime.now().isoformat()

    def remove_collaborator(self, session_id: str, user_id: str):
        """Remove a collaborator from a session"""
        if session_id in self.sessions:
            if user_id in self.sessions[session_id].collaborators:
                del self.sessions[session_id].collaborators[user_id]
                self.sessions[session_id].updated_at = datetime.now().isoformat()

    def record_change(
        self,
        session_id: str,
        user_id: str,
        change_type: str,
        content: Dict[str, Any],
        parent_change_id: Optional[str] = None,
    ) -> Change:
        """Record a change in the session"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")

        change = Change(
            change_id=str(uuid.uuid4())[:8],
            session_id=session_id,
            user_id=user_id,
            change_type=change_type,
            content=content,
            timestamp=datetime.now().isoformat(),
            parent_change_id=parent_change_id,
        )

        self.sessions[session_id].changes.append(change)
        self.sessions[session_id].updated_at = datetime.now().isoformat()

        return change

    def check_permission(self, session_id: str, user_id: str, action: str) -> bool:
        """Check if user has permission for action"""
        if session_id not in self.sessions:
            return False

        session = self.sessions[session_id]

        # Owner has all permissions
        if user_id == session.owner_id:
            return True

        # Check collaborator role
        role = session.collaborators.get(user_id)
        if not role:
            return False

        # Define role permissions
        permissions = {
            "owner": ["view", "edit", "admin", "delete"],
            "editor": ["view", "edit"],
            "viewer": ["view"],
        }

        return action in permissions.get(role, [])

    def get_session_changes(self, session_id: str, limit: int = 100) -> List[Change]:
        """Get recent changes for a session"""
        if session_id not in self.sessions:
            return []

        changes = self.sessions[session_id].changes
        return changes[-limit:] if limit > 0 else changes

    def get_statistics(self) -> Dict[str, Any]:
        """Get collaboration statistics"""
        total_sessions = len(self.sessions)
        total_users = len(
            set(
                [s.owner_id]
                + [user for session in self.sessions.values() for user in session.collaborators.keys()]
            )
        )
        total_changes = sum(len(session.changes) for session in self.sessions.values())

        return {
            "total_sessions": total_sessions,
            "total_users": total_users,
            "total_changes": total_changes,
        }
