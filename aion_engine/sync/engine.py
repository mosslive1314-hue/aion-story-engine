from typing import Dict, List, Any, Optional
import json
import os
from dataclasses import asdict


class SyncEngine:
    """Cloud synchronization engine"""

    def __init__(self, sync_dir: str = "data/sync"):
        self.sync_dir = sync_dir
        self.local_changes: Dict[str, Any] = {}
        self.remote_changes: Dict[str, Any] = {}

    def create_change_set(self, session_id: str, changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a change set"""
        change_set = {
            "session_id": session_id,
            "changes": changes,
            "timestamp": "2025-02-05T18:00:00Z",
        }
        return change_set

    def export_changes(self, session_id: str, filepath: str):
        """Export changes to file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(self.local_changes.get(session_id, {}), f)

    def import_changes(self, session_id: str, filepath: str) -> Dict[str, Any]:
        """Import changes from file"""
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                data = json.load(f)
                self.remote_changes[session_id] = data
                return data
        return {}

    def detect_conflicts(self, local_changes: Dict[str, Any], remote_changes: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect conflicts between local and remote changes"""
        conflicts = []
        # Simple conflict detection
        for key in local_changes:
            if key in remote_changes:
                if local_changes[key] != remote_changes[key]:
                    conflicts.append({"key": key, "local": local_changes[key], "remote": remote_changes[key]})
        return conflicts

    def merge_changes(self, local_changes: Dict[str, Any], remote_changes: Dict[str, Any]) -> Dict[str, Any]:
        """Merge local and remote changes"""
        merged = {}
        all_keys = set(local_changes.keys()) | set(remote_changes.keys())
        for key in all_keys:
            if key in local_changes and key in remote_changes:
                # Conflict: use last write wins (simplified)
                merged[key] = local_changes[key]
            elif key in local_changes:
                merged[key] = local_changes[key]
            else:
                merged[key] = remote_changes[key]
        return merged
