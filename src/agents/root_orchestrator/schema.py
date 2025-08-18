"""Schema definitions for Root Orchestrator Agent."""

from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class ChecklistItem(BaseModel):
    """Individual item in the provisioning checklist."""
    
    id: str = Field(..., description="Unique identifier for the checklist item")
    title: str = Field(..., description="Human-readable title of the task")
    description: str = Field(..., description="Detailed description of what needs to be done")
    commands: List[str] = Field(default=[], description="Commands to execute for this item")
    status: Literal["pending", "in_progress", "completed", "failed"] = Field(
        default="pending", description="Current status of the item"
    )
    assigned_agent: Optional[str] = Field(None, description="Agent type assigned to handle this item")
    failure_count: int = Field(default=0, description="Number of consecutive failures")
    failure_reasons: List[str] = Field(default=[], description="Reasons for failures from QA")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


class ChecklistStatus(BaseModel):
    """Overall status of the provisioning checklist."""
    
    total_items: int = Field(..., description="Total number of items")
    completed: int = Field(default=0, description="Number of completed items")
    pending: int = Field(..., description="Number of pending items")
    in_progress: int = Field(default=0, description="Number of items in progress")
    failed: int = Field(default=0, description="Number of failed items")
    progress_percentage: float = Field(..., description="Overall completion percentage")


class AgentResponse(BaseModel):
    """Response from a specialized agent after completing work."""
    
    agent_type: str = Field(..., description="Type of agent that performed the work")
    agent_id: str = Field(..., description="Unique ID of the agent instance")
    item_id: str = Field(..., description="ID of the checklist item worked on")
    status: Literal["completed", "failed"] = Field(..., description="Final status of the work")
    output: str = Field(..., description="Detailed output from the agent's work")
    commands_executed: List[str] = Field(default=[], description="Commands that were executed")
    errors: List[str] = Field(default=[], description="Any errors encountered")
    timestamp: datetime = Field(default_factory=datetime.now)


class QAResult(BaseModel):
    """Result from QA Expert verification."""
    
    item_id: str = Field(..., description="ID of the checklist item verified")
    result: Literal["SUCCESS", "FAIL"] = Field(..., description="QA verification result")
    reason: str = Field(..., description="Explanation for the result")
    verification_steps: List[str] = Field(default=[], description="Steps taken to verify")
    timestamp: datetime = Field(default_factory=datetime.now)


class ProvisioningSpec(BaseModel):
    """Complete provisioning specification parsed from markdown."""
    
    title: str = Field(..., description="Title of the specification")
    overview: str = Field(..., description="Overview description")
    checklist_items: List[ChecklistItem] = Field(..., description="All items to be provisioned")
    environment_variables: Dict[str, str] = Field(default={}, description="Required environment variables")
    created_at: datetime = Field(default_factory=datetime.now)


class SystemState(BaseModel):
    """Current state of the system being provisioned."""
    
    installed_packages: List[str] = Field(default=[], description="Currently installed packages")
    configured_tools: List[str] = Field(default=[], description="Tools that are configured")
    environment_vars: Dict[str, Optional[str]] = Field(default={}, description="Current environment variables")
    shell_config: Dict[str, str] = Field(default={}, description="Shell configuration status")
    last_updated: datetime = Field(default_factory=datetime.now)


class HumanEscalation(BaseModel):
    """Request for human intervention."""
    
    item_id: str = Field(..., description="ID of the problematic checklist item")
    failure_count: int = Field(..., description="Number of failures that triggered escalation")
    failure_history: List[QAResult] = Field(..., description="History of QA failures")
    suggested_actions: List[str] = Field(..., description="Suggested manual interventions")
    created_at: datetime = Field(default_factory=datetime.now)