from typing import Dict, List, Any, Optional
from collections import Counter
from .manager import Change


class ConsensusEngine:
    """Resolves conflicts in collaborative editing"""

    def __init__(self):
        self.conflict_resolution_strategies = [
            "last_writer_wins",
            "majority_vote",
            "owner_decides",
        ]

    def resolve_conflict(self, changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Resolve conflicting changes"""
        if not changes:
            return {"error": "No changes to resolve"}

        # Group changes by type
        change_groups = {}
        for change in changes:
            change_type = change.get("change_type")
            if change_type not in change_groups:
                change_groups[change_type] = []
            change_groups[change_type].append(change)

        # Resolve each group of changes
        resolved_changes = []
        for change_type, group in change_groups.items():
            if len(group) == 1:
                # No conflict, keep the change
                resolved_changes.append(group[0])
            else:
                # Conflict, resolve it
                resolved = self._resolve_group(group)
                resolved_changes.append(resolved)

        return {
            "original_changes": changes,
            "resolved_changes": resolved_changes,
            "strategy": "majority_vote",
        }

    def _resolve_group(self, changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Resolve a group of conflicting changes using majority vote"""
        # Simple majority vote based on user_id frequency
        user_votes = Counter(change["user_id"] for change in changes)
        winner_user = user_votes.most_common(1)[0][0]

        # Return the change from the user with most votes
        for change in changes:
            if change["user_id"] == winner_user:
                return change

        # Fallback to first change
        return changes[0]

    def detect_conflicts(self, changes: List[Change]) -> List[Dict[str, Any]]:
        """Detect potential conflicts in a list of changes"""
        conflicts = []

        # Group changes by parent
        change_groups = {}
        for change in changes:
            parent_id = change.parent_change_id
            if parent_id not in change_groups:
                change_groups[parent_id] = []
            change_groups[parent_id].append(change)

        # Check for conflicts in each group
        for parent_id, group in change_groups.items():
            if len(group) > 1:
                # Multiple changes from same parent = potential conflict
                conflict = {
                    "parent_change_id": parent_id,
                    "conflicting_changes": [c.change_id for c in group],
                    "users": [c.user_id for c in group],
                }
                conflicts.append(conflict)

        return conflicts

    def merge_changes(self, changes: List[Change]) -> List[Change]:
        """Merge non-conflicting changes"""
        # Detect conflicts
        conflicts = self.detect_conflict(changes)

        if conflicts:
            # Resolve conflicts first
            conflict_changes = [c for c in changes if c.parent_change_id in [conf["parent_change_id"] for conf in conflicts]]
            non_conflict_changes = [c for c in changes if c.parent_change_id not in [conf["parent_change_id"] for conf in conflicts]]

            # Resolve conflicts
            resolved = []
            for conflict in conflicts:
                conflicting = [c for c in conflict_changes if c.parent_change_id == conflict["parent_change_id"]]
                # Use consensus engine to resolve
                resolved_change = self._resolve_changes(conflicting)
                resolved.append(resolved_change)

            return non_conflict_changes + resolved
        else:
            # No conflicts, return all changes
            return changes

    def _resolve_changes(self, changes: List[Change]) -> Change:
        """Resolve a list of conflicting changes"""
        # Simple strategy: last change wins
        sorted_changes = sorted(changes, key=lambda c: c.timestamp)
        return sorted_changes[-1]
