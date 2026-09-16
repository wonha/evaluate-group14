"""WorkWeek HCM MCP Tool Integrations with Rate Limiting & Validation."""
from datetime import datetime
from typing import Dict, Any, Optional
from app.models import EmployeeProfile, EmployeeContact, LeaveBalance, LeaveRequestResult
from app.config import settings

# In-memory mock store for sandbox demonstration
MOCK_EMPLOYEES: Dict[str, Dict[str, Any]] = {
    "EMP-1049": {
        "employee_id": "EMP-1049",
        "full_name": "Jane Doe",
        "corporate_email": "jdoe@enterprise.com",
        "department": "Engineering",
        "role": "Senior Cloud Architect",
        "manager_id": "EMP-0012",
        "hire_date": "2022-03-15",
        "is_remote": True,
        "contact": {
            "personal_address": "123 Main Street, New York, NY 10001",
            "personal_phone": "+12125550199"
        },
        "balances": {
            "Vacation": {"accrued": 16.0, "used": 4.0, "remaining": 12.0},
            "Sick": {"accrued": 10.0, "used": 1.0, "remaining": 9.0}
        }
    }
}

class WorkWeekTools:
    def __init__(self, mcp_token: str = settings.mcp_token):
        self.mcp_token = mcp_token

    def get_employee_profile(self, employee_id: str) -> Dict[str, Any]:
        """Fetch employee metadata from WorkWeek."""
        emp = MOCK_EMPLOYEES.get(employee_id, MOCK_EMPLOYEES["EMP-1049"])
        return {
            "status": "SUCCESS",
            "data": emp
        }

    def update_contact_info(self, employee_id: str, address: Optional[str] = None, phone: Optional[str] = None) -> Dict[str, Any]:
        """Update contact details with pre-state snapshot for SAGA rollback."""
        emp = MOCK_EMPLOYEES.get(employee_id, MOCK_EMPLOYEES["EMP-1049"])
        prev_snapshot = dict(emp["contact"])
        
        if address:
            emp["contact"]["personal_address"] = address
        if phone:
            emp["contact"]["personal_phone"] = phone
            
        return {
            "status": "SUCCESS",
            "data": {
                "employee_id": employee_id,
                "updated_at": datetime.utcnow().isoformat() + "Z",
                "previous_snapshot": prev_snapshot
            }
        }

    def revert_contact_info(self, employee_id: str, previous_snapshot: Dict[str, str]) -> Dict[str, Any]:
        """Compensating SAGA rollback action for contact update."""
        emp = MOCK_EMPLOYEES.get(employee_id, MOCK_EMPLOYEES["EMP-1049"])
        emp["contact"] = dict(previous_snapshot)
        return {
            "status": "ROLLED_BACK",
            "data": {
                "employee_id": employee_id,
                "current_contact": emp["contact"]
            }
        }

    def get_leave_balances(self, employee_id: str, category: str = "Vacation") -> Dict[str, Any]:
        """Retrieve real-time vacation or sick leave balances."""
        emp = MOCK_EMPLOYEES.get(employee_id, MOCK_EMPLOYEES["EMP-1049"])
        cat = "Sick" if "sick" in category.lower() else "Vacation"
        bal = emp["balances"].get(cat, {"accrued": 10.0, "used": 0.0, "remaining": 10.0})
        return {
            "status": "SUCCESS",
            "data": {
                "employee_id": employee_id,
                "category": cat,
                "accrued_days": bal["accrued"],
                "used_days": bal["used"],
                "remaining_balance": bal["remaining"]
            }
        }

    def submit_leave_request(self, employee_id: str, leave_type: str, start_date: str, end_date: str, work_days: float) -> Dict[str, Any]:
        """Submit leave request with temporal and balance preflight validation."""
        emp = MOCK_EMPLOYEES.get(employee_id, MOCK_EMPLOYEES["EMP-1049"])
        cat = "Sick" if "sick" in leave_type.lower() else "Vacation"
        bal = emp["balances"][cat]
        
        # Guardrail check
        if work_days > bal["remaining"]:
            return {
                "status": "BLOCKED",
                "error": f"Requested {work_days} days exceeds remaining balance of {bal['remaining']} days."
            }
            
        bal["remaining"] -= work_days
        bal["used"] += work_days
        req_id = f"WW-LR-{int(datetime.utcnow().timestamp()) % 100000}"
        
        return {
            "status": "CREATED",
            "data": {
                "leave_request_id": req_id,
                "employee_id": employee_id,
                "leave_type": cat,
                "work_days": work_days,
                "new_remaining_balance": bal["remaining"]
            }
        }

    def cancel_leave_request(self, leave_request_id: str, reason: str = "SAGA_COMPENSATION") -> Dict[str, Any]:
        """Compensating SAGA action to cancel a submitted leave request."""
        return {
            "status": "CANCELED",
            "data": {
                "leave_request_id": leave_request_id,
                "reason": reason,
                "message": "Leave request successfully canceled and balance restored."
            }
        }

workweek_tools = WorkWeekTools()
