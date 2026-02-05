from typing import Dict, List, Any, Tuple
import random


class MediciSynapse:
    """Cross-domain innovation engine"""

    def __init__(self):
        self.domain_knowledge = {
            "physics": ["quantum", "thermodynamics", "relativity", "entropy"],
            "biology": ["evolution", "adaptation", "symbiosis", "mutation"],
            "psychology": ["cognition", "emotion", "memory", "perception"],
            "computer_science": ["algorithm", "network", "optimization", "learning"],
            "magic": ["spell", "curse", "enchantment", "transmutation"],
        }

    def generate_innovation(
        self, domain1: str, domain2: str, problem: str
    ) -> Dict[str, Any]:
        """Generate innovation by combining two domains"""
        # Simple innovation generation
        concepts1 = self.domain_knowledge.get(domain1.lower(), [domain1])
        concepts2 = self.domain_knowledge.get(domain2.lower(), [domain2])

        # Create innovation
        concept1 = random.choice(concepts1)
        concept2 = random.choice(concepts2)

        innovation = {
            "name": f"{concept1.title()} + {concept2.title()} Hybrid",
            "domain1": domain1,
            "domain2": domain2,
            "core_concept": f"Combining {concept1} with {concept2}",
            "description": f"A novel approach that applies {concept1} principles to {concept2} problems",
            "mechanism": f"Use {concept1} to influence or control {concept2}",
            "applications": [
                f"Apply to {problem}",
                "Generate new story elements",
                "Create unique world rules",
            ],
            "confidence": random.uniform(0.6, 0.95),
        }

        return innovation

    def create_asset_from_innovation(self, innovation: Dict[str, Any]) -> Dict[str, Any]:
        """Convert innovation to asset suggestion"""
        return {
            "asset_type": "world_rule",
            "name": innovation["name"],
            "description": innovation["description"],
            "content": {
                "domains": [innovation["domain1"], innovation["domain2"]],
                "mechanism": innovation["mechanism"],
                "applications": innovation["applications"],
            },
            "metadata": {
                "source": "medici_synapse",
                "confidence": innovation["confidence"],
                "generated_at": "2025-02-05",
            },
            "tags": ["innovation", "cross-domain", innovation["domain1"], innovation["domain2"]],
        }
