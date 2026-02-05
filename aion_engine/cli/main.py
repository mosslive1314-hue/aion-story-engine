from typing import Optional, Dict, Any


class CLIInterface:
    """Command-line interface for AION Story Engine"""

    def __init__(self):
        self.commands = {
            "create": self.create_story,
            "continue": self.continue_story,
            "save": self.save_story,
            "load": self.load_story,
            "marketplace": self.show_marketplace,
            "assets": self.list_assets,
        }

    def execute(self, command: str, args: Dict[str, Any]) -> str:
        """Execute a CLI command"""
        cmd_func = self.commands.get(command)
        if not cmd_func:
            return f"Error: Unknown command '{command}'"

        try:
            result = cmd_func(args)
            return result
        except Exception as e:
            return f"Error: {str(e)}"

    def create_story(self, args: Dict[str, Any]) -> str:
        """Create a new story"""
        name = args.get("name", "Untitled Story")
        return f"Creating new story: {name}"

    def continue_story(self, args: Dict[str, Any]) -> str:
        """Continue an existing story"""
        session_id = args.get("session_id")
        if not session_id:
            return "Error: session_id required"

        return f"Continuing story session: {session_id}"

    def save_story(self, args: Dict[str, Any]) -> str:
        """Save the current story"""
        return "Story saved successfully"

    def load_story(self, args: Dict[str, Any]) -> str:
        """Load a saved story"""
        session_id = args.get("session_id")
        if not session_id:
            return "Error: session_id required"

        return f"Loading story session: {session_id}"

    def show_marketplace(self, args: Dict[str, Any]) -> str:
        """Show the asset marketplace"""
        return """
🏪 Asset Marketplace

Featured Assets:
- Fire Physics Rules (Free) ⭐⭐⭐⭐⭐
- Medieval Magic System ($9.99) ⭐⭐⭐⭐
- Quantum Enchantments ($19.99) ⭐⭐⭐⭐⭐

Total Assets: 150
"""

    def list_assets(self, args: Dict[str, Any]) -> str:
        """List user's assets"""
        return """
📦 Your Assets

1. Laboratory Fire Pattern (Used 5 times)
2. Scientist NPC Template (Used 3 times)
3. Thermodynamics Rules (Used 8 times)

Total Assets: 3
"""


# Initialize CLI
cli = CLIInterface()
