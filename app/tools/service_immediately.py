"""ServiceImmediately ITSM MCP Tool Integrations with Priority & Lifecycle Rules."""
import time
from typing import Dict, Any, Optional
from app.config import settings

MOCK_TICKETS: Dict[str, Dict[str, Any]] = {
    "INC-12345": {
        "ticket_id": "INC-12345",
        "state": "In Progress",
        "priority": "3 - Moderate",
        "category": "Software",
        "short_description": "Email client sync failure",
        "assignee": "IT Tier 2",
        "created_at": "2026-09-15T10:00:00Z"
    }
}

class ServiceImmediatelyTools:
    def __init__(self, mcp_token: str = settings.mcp_token):
        self.mcp_token = mcp_token

    def get_ticket_details(self, ticket_id: str) -> Dict[str, Any]:
        """Query status, priority, and metadata for an incident ticket."""
        ticket = MOCK_TICKETS.get(ticket_id, {
            "ticket_id": ticket_id,
            "state": "Active",
            "priority": "3 - Moderate",
            "category": "General",
            "short_description": "IT Support Request",
            "assignee": "Service Desk",
            "created_at": "2026-09-16T00:00:00Z"
        })
        return {"status": "SUCCESS", "data": ticket}

    def create_incident_ticket(self, requestor_id: str, category: str, short_description: str, priority: str = "3 - Moderate", comments: Optional[str] = None, shipping_address: Optional[str] = None) -> Dict[str, Any]:
        """Open a new incident ticket."""
        ticket_id = f"INC-{int(time.time()) % 100000}"
        
        # Priority mapping verification
        desc_lower = short_description.lower()
        if any(w in desc_lower for w in ["system down", "outage", "security breach"]):
            priority = "1 - Critical"
        elif "on-call" in desc_lower or "vpn" in desc_lower:
            priority = "2 - High"
            
        record = {
            "ticket_id": ticket_id,
            "requestor_id": requestor_id,
            "category": category,
            "short_description": short_description,
            "priority": priority,
            "state": "New",
            "assigned_group": "People Operations Queue" if "HR" in category else "Workplace Logistics",
            "created_at": "2026-09-16T01:30:00Z",
            "ticket_url": f"https://mock-saas.aishprabhat.demo.altostrat.com/incidents/{ticket_id}"
        }
        MOCK_TICKETS[ticket_id] = record
        return {"status": "CREATED", "data": record}

    def update_ticket_status(self, ticket_id: str, new_status: str, resolution_notes: Optional[str] = None) -> Dict[str, Any]:
        """Update incident lifecycle state."""
        if ticket_id in MOCK_TICKETS:
            MOCK_TICKETS[ticket_id]["state"] = new_status
            if resolution_notes:
                MOCK_TICKETS[ticket_id]["resolution_notes"] = resolution_notes
        return {"status": "SUCCESS", "data": {"ticket_id": ticket_id, "state": new_status}}

itsm_tools = ServiceImmediatelyTools()
