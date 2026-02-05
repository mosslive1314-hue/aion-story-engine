import uuid
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Pattern:
    """Represents a discovered pattern from events"""
    id: str
    name: str
    description: str
    events: List[Dict[str, Any]]
    usage_count: int
    success_rate: float
    created_at: str
    metadata: Dict[str, Any]


@dataclass
class PatternMatch:
    """Represents a pattern match in a new scenario"""
    pattern: Pattern
    confidence: float
    matched_events: List[Dict[str, Any]]
    unmatched_events: List[Dict[str, Any]]


class AbstractionEngine:
    """Layer 4: Abstraction Engine for pattern recognition and knowledge storage"""

    def __init__(self):
        self.patterns: Dict[str, Pattern] = {}
        self.knowledge_base: Dict[str, Any] = {}

    def extract_patterns(self, events: List[Dict[str, Any]]) -> List[Pattern]:
        """Extract patterns from a sequence of events"""
        patterns = []

        # Simple pattern detection: look for fire-related chains
        fire_events = [e for e in events if "fire" in str(e.get("type", "")).lower()]

        if len(fire_events) >= 1:
            # Create a fire chain pattern
            pattern = self.create_pattern(
                name="Fire Chain Reaction",
                description="Fire events tend to chain together",
                events=events,
            )
            patterns.append(pattern)

        return patterns

    def create_pattern(
        self,
        name: str,
        description: str,
        events: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Pattern:
        """Create a new pattern"""
        pattern = Pattern(
            id=str(uuid.uuid4())[:8],
            name=name,
            description=description,
            events=events,
            usage_count=0,
            success_rate=1.0,
            created_at=datetime.now().isoformat(),
            metadata=metadata or {},
        )
        return pattern

    def save_pattern(self, pattern: Pattern) -> None:
        """Save a pattern to the knowledge base"""
        self.patterns[pattern.id] = pattern

    def get_pattern(self, pattern_id: str) -> Optional[Pattern]:
        """Retrieve a pattern by ID"""
        return self.patterns.get(pattern_id)

    def apply_patterns(
        self, events: List[Dict[str, Any]], min_confidence: float = 0.5
    ) -> List[PatternMatch]:
        """Apply stored patterns to new events"""
        matches = []

        for pattern in self.patterns.values():
            # Simple matching: check if pattern events are subset of new events
            confidence = self._calculate_confidence(pattern, events)

            if confidence >= min_confidence:
                matched_events = self._find_matched_events(pattern.events, events)
                unmatched_events = [e for e in events if e not in matched_events]

                matches.append(
                    PatternMatch(
                        pattern=pattern,
                        confidence=confidence,
                        matched_events=matched_events,
                        unmatched_events=unmatched_events,
                    )
                )

        return sorted(matches, key=lambda m: m.confidence, reverse=True)

    def _calculate_confidence(self, pattern: Pattern, events: List[Dict[str, Any]]) -> float:
        """Calculate confidence of pattern match"""
        if not pattern.events or not events:
            return 0.0

        matched = sum(1 for p_event in pattern.events if any(self._event_matches(p_event, e) for e in events))
        return matched / len(pattern.events)

    def _find_matched_events(
        self, pattern_events: List[Dict[str, Any]], target_events: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Find which events match the pattern"""
        matched = []
        for p_event in pattern_events:
            for target_event in target_events:
                if self._event_matches(p_event, target_event):
                    matched.append(target_event)
                    break
        return matched

    def _event_matches(self, pattern_event: Dict[str, Any], target_event: Dict[str, Any]) -> bool:
        """Check if a target event matches a pattern event"""
        for key, value in pattern_event.items():
            if key not in target_event:
                return False
            if target_event[key] != value:
                # Partial match for 'type' field
                if key == "type" and value.lower() in target_event[key].lower():
                    continue
                return False
        return True

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about stored patterns"""
        return {
            "total_patterns": len(self.patterns),
            "total_usage": sum(p.usage_count for p in self.patterns.values()),
            "avg_success_rate": (
                sum(p.success_rate for p in self.patterns.values()) / len(self.patterns)
                if self.patterns else 0.0
            ),
        }
