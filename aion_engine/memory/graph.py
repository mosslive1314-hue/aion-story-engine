from typing import Dict, List, Any, Tuple
from collections import defaultdict
import uuid
from dataclasses import dataclass


@dataclass
class Concept:
    """A concept node in the memory graph"""
    name: str
    related_assets: List[str]
    usage_count: int
    satisfaction: float
    strength: float = 1.0


class MemoryGraph:
    """Knowledge graph for concept relationships"""

    def __init__(self):
        self.concepts: Dict[str, Concept] = {}
        self.relationships: Dict[Tuple[str, str], float] = {}

    def add_concept(
        self,
        name: str,
        related_assets: List[str] = None,
        initial_strength: float = 1.0,
    ) -> Concept:
        """Add a new concept"""
        concept = Concept(
            name=name,
            related_assets=related_assets or [],
            usage_count=0,
            satisfaction=0.0,
            strength=initial_strength,
        )

        self.concepts[name] = concept
        return concept

    def get_concept(self, name: str) -> Concept:
        """Get a concept by name"""
        return self.concepts.get(name)

    def add_relationship(self, concept1: str, concept2: str, strength: float):
        """Add relationship between two concepts"""
        key = tuple(sorted([concept1, concept2]))
        self.relationships[key] = strength

    def get_related_concepts(self, concept_name: str) -> List[str]:
        """Get all concepts related to the given concept"""
        related = []
        key1 = (concept_name, concept_name)

        for (c1, c2), strength in self.relationships.items():
            if c1 == concept_name or c2 == concept_name:
                other = c2 if c1 == concept_name else c1
                if strength > 0.5:  # Only include strong relationships
                    related.append(other)

        return related

    def update_usage(self, concept_name: str):
        """Update usage count for a concept"""
        if concept_name in self.concepts:
            self.concepts[concept_name].usage_count += 1

    def update_satisfaction(self, concept_name: str, rating: float):
        """Update satisfaction score for a concept"""
        if concept_name in self.concepts:
            current = self.concepts[concept_name].satisfaction
            # Exponential moving average
            self.concepts[concept_name].satisfaction = 0.7 * current + 0.3 * rating

    def get_top_concepts(self, limit: int = 10) -> List[Tuple[str, Concept]]:
        """Get top concepts by usage"""
        sorted_concepts = sorted(
            self.concepts.items(),
            key=lambda x: x[1].usage_count,
            reverse=True,
        )
        return sorted_concepts[:limit]

    def get_concept_suggestions(self, concept_name: str) -> List[str]:
        """Get suggested related concepts"""
        if concept_name not in self.concepts:
            return []

        suggestions = []
        for related in self.get_related_concepts(concept_name):
            if related in self.concepts:
                # Prioritize by relationship strength and satisfaction
                strength = self.relationships.get(
                    tuple(sorted([concept_name, related])), 0.0
                )
                satisfaction = self.concepts[related].satisfaction
                score = strength * 0.6 + satisfaction / 5.0 * 0.4
                suggestions.append((related, score))

        # Sort by score
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return [concept for concept, _ in suggestions[:5]]

    def get_statistics(self) -> Dict[str, Any]:
        """Get memory graph statistics"""
        total_concepts = len(self.concepts)
        total_relationships = len(self.relationships)
        total_usage = sum(c.usage_count for c in self.concepts.values())
        avg_satisfaction = (
            sum(c.satisfaction for c in self.concepts.values()) / total_concepts
            if total_concepts > 0
            else 0.0
        )

        return {
            "total_concepts": total_concepts,
            "total_relationships": total_relationships,
            "total_usage": total_usage,
            "avg_satisfaction": avg_satisfaction,
        }
