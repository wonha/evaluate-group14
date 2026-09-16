from typing import Literal, Optional, List, Dict, Any
try:
    from pydantic import BaseModel, Field
except ImportError:
    from dataclasses import dataclass, field
    def Field(default=None, **kwargs):
        if default is ...:
            return field()
        return field(default=default)
    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
        def dict(self):
            return self.__dict__

# --- WorkWeek HCM Models ---
class EmployeeContact(BaseModel):
    personal_address: str = Field(..., description="Residential street address")
    personal_phone: str = Field(..., description="E.164 formatted telephone number")

class EmployeeProfile(BaseModel):
    employee_id: str
    full_name: str
    corporate_email: str
    department: str
    role: str
    manager_id: str
    hire_date: str
    is_remote: bool
    contact: EmployeeContact

class LeaveBalance(BaseModel):
    employee_id: str
    category: Literal["Vacation", "Sick"]
    accrued_days: float
    used_days: float
    remaining_balance: float

class LeaveRequestInput(BaseModel):
    employee_id: str
    leave_type: Literal["Vacation", "Sick"]
    start_date: str = Field(..., description="YYYY-MM-DD")
    end_date: str = Field(..., description="YYYY-MM-DD")
    work_days: float = Field(..., gt=0)

class LeaveRequestResult(BaseModel):
    leave_request_id: str
    employee_id: str
    status: str
    new_remaining_balance: float

# --- ServiceImmediately ITSM Models ---
class IncidentInput(BaseModel):
    requestor_id: str
    category: Literal["Hardware", "Software", "Access", "General", "HR General"]
    short_description: str
    priority: Literal["1 - Critical", "2 - High", "3 - Moderate", "4 - Low"] = "3 - Moderate"
    comments: Optional[str] = None
    shipping_address: Optional[str] = None
    source_tag: str = "Elevate-Module3-AgentRuntime"

class IncidentResult(BaseModel):
    ticket_id: str
    state: str
    assigned_group: str
    created_at: str
    ticket_url: str

# --- Policy RAG Models ---
class PolicyChunk(BaseModel):
    document_title: str
    section: str
    text_content: str
    source_url: str
    similarity_score: float

class GroundedAnswer(BaseModel):
    answer: str
    citations: List[str]
    grounding_score: float
    is_grounded: bool

# --- SAGA State Models ---
class SagaTransaction(BaseModel):
    saga_id: str
    use_case_id: str
    user_id: str
    status: Literal["IN_PROGRESS", "COMPLETED", "ROLLED_BACK", "FAILED"]
    steps_completed: List[str] = []
    pre_state_snapshots: Dict[str, Any] = {}
