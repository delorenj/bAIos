"""
Agent Schema Definitions
========================

Defines input/output schemas for all specialized agents in the orchestrator system.
"""

from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pydantic import Field, validator
from atomic_agents import BaseIOSchema


class AgentType(str, Enum):
    """Types of specialized agents in the system."""
    RESEARCHER = "researcher"
    INSTALLER = "installer"
    SHELL_MASTER = "shell_master"
    PROGRESS_TRACKER = "progress_tracker"
    AUTHORIZER = "authorizer"
    MISE_MASTER = "mise_master"
    QA_EXPERT = "qa_expert"


class TaskPriority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    REQUIRES_HUMAN = "requires_human"


class AgentRequest(BaseIOSchema):
    """Request schema for agent execution."""
    
    agent_type: AgentType = Field(..., description="Type of agent to execute")
    task_description: str = Field(..., description="Detailed task description")
    context: Dict[str, Any] = Field(default_factory=dict, description="Task context and parameters")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority")
    timeout_seconds: int = Field(default=300, description="Maximum execution time")
    retry_count: int = Field(default=0, description="Current retry attempt number")
    dependencies: List[str] = Field(default_factory=list, description="Task dependencies")


class AgentResponse(BaseIOSchema):
    """Response schema from agent execution."""
    
    agent_type: AgentType = Field(..., description="Agent that executed the task")
    status: TaskStatus = Field(..., description="Task execution status")
    result: Optional[Dict[str, Any]] = Field(None, description="Task execution results")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    logs: List[str] = Field(default_factory=list, description="Execution logs")
    execution_time: float = Field(..., description="Time taken to execute task")
    resources_used: Dict[str, Any] = Field(default_factory=dict, description="Resources consumed")


class AgentStatus(BaseIOSchema):
    """Current status of an agent."""
    
    agent_id: str = Field(..., description="Unique agent identifier")
    agent_type: AgentType = Field(..., description="Type of agent")
    current_task: Optional[str] = Field(None, description="Current task ID if executing")
    status: str = Field(..., description="Agent status (idle, busy, error, etc.)")
    last_activity: str = Field(..., description="ISO timestamp of last activity")
    performance_metrics: Dict[str, float] = Field(default_factory=dict, description="Performance metrics")


class QAResult(BaseIOSchema):
    """Result from QA Expert validation."""
    
    task_id: str = Field(..., description="Task that was validated")
    validation_passed: bool = Field(..., description="Whether validation passed")
    success_criteria_met: List[str] = Field(default_factory=list, description="Criteria that passed")
    failures: List[str] = Field(default_factory=list, description="Criteria that failed")
    remediation_suggestions: List[str] = Field(default_factory=list, description="Suggested fixes")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence in validation")
    detailed_report: Optional[str] = Field(None, description="Detailed validation report")


class FailureReport(BaseIOSchema):
    """Report of task failures for human intervention tracking."""
    
    task_id: str = Field(..., description="Failed task identifier")
    agent_type: AgentType = Field(..., description="Agent that failed")
    failure_count: int = Field(..., description="Number of consecutive failures")
    failure_reasons: List[str] = Field(..., description="Reasons for failures")
    last_error: str = Field(..., description="Most recent error message")
    remediation_attempts: List[str] = Field(default_factory=list, description="Attempted fixes")
    requires_human_intervention: bool = Field(..., description="Whether human help is needed")
    timestamp: str = Field(..., description="ISO timestamp of failure")