from typing import Dict, List, Any, Optional


class APIHandler:
    """FastAPI-based REST API handler"""

    def __init__(self):
        self.routes = {}

    def register_route(self, path: str, method: str, handler: callable):
        """Register an API route"""
        key = f"{method.upper()}:{path}"
        self.routes[key] = handler

    def handle_request(self, method: str, path: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle an API request"""
        # Try exact match first
        key = f"{method.upper()}:{path}"
        handler = self.routes.get(key)

        # If no exact match, try pattern matching
        if not handler:
            for route_key, route_handler in self.routes.items():
                if self._match_route(route_key, path):
                    handler = route_handler
                    break

        if not handler:
            return {"error": "Route not found", "status_code": 404}

        try:
            # Try calling with data first, then without
            try:
                result = handler(data)
            except TypeError:
                # If handler doesn't accept data, try without
                result = handler()
            return {"data": result, "status_code": 200}
        except Exception as e:
            return {"error": str(e), "status_code": 500}

    def _match_route(self, route: str, path: str) -> bool:
        """Match a route pattern to a path"""
        # Extract the route path from the route string (skip method prefix if present)
        # Route format is either "METHOD:/path" or "/path"
        if ':' in route:
            route_path = route.split(':', 1)[1]
        else:
            route_path = route

        route_parts = route_path.split('/')
        path_parts = path.split('/')

        if len(route_parts) != len(path_parts):
            return False

        for route_part, path_part in zip(route_parts, path_parts):
            # Match literal or parameter
            if route_part.startswith('{'):
                continue  # Parameter match
            if route_part != path_part:
                return False

        return True

    def get_session(self, session_id: str) -> Dict[str, Any]:
        """Get a story session"""
        return {
            "session_id": session_id,
            "status": "active",
            "message": "Session retrieved successfully"
        }

    def create_session(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new story session"""
        return {
            "session_id": "session-123",
            "name": data.get("name", "Untitled"),
            "status": "created",
            "message": "Session created successfully"
        }

    def get_assets(self) -> Dict[str, Any]:
        """Get all assets"""
        return {
            "assets": [
                {
                    "id": "asset-1",
                    "name": "Fire Physics Rule",
                    "type": "world_rule",
                    "price": 0.0
                }
            ],
            "total": 1
        }

    def get_marketplace_stats(self) -> Dict[str, Any]:
        """Get marketplace statistics"""
        return {
            "total_listings": 150,
            "total_transactions": 1200,
            "total_revenue": 45000.0
        }


# Initialize API handler
api = APIHandler()

# Register routes
api.register_route("/sessions/{session_id}", "GET", api.get_session)
api.register_route("/sessions", "POST", api.create_session)
api.register_route("/assets", "GET", api.get_assets)
api.register_route("/marketplace/stats", "GET", api.get_marketplace_stats)
