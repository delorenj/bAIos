"""
Orchestrator Schema Definitions
===============================

Defines schemas for the root orchestrator and overall system coordination.
"""

from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pydantic import Field, validator
from atomic_agents import BaseIOSchema
from .agent_schemas import AgentType, TaskStatus, TaskPriority


class ProvisioningPhase(str, Enum):
    """Phases of the WSL environment provisioning process."""
    INITIALIZATION = "initialization"
    SYSTEM_SETUP = "system_setup"
    TOOL_INSTALLATION = "tool_installation"
    CONFIGURATION = "configuration"
    VALIDATION = "validation"
    CLEANUP = "cleanup"


class ProvisioningRequest(BaseIOSchema):
    """Request to provision a WSL development environment."""
    
    environment_spec_path: str = Field(..., description="Path to the WSL environment specification")
    user_preferences: Dict[str, Any] = Field(default_factory=dict, description="User-specific preferences")
    skip_phases: List[ProvisioningPhase] = Field(default_factory=list, description="Phases to skip")
    force_reinstall: bool = Field(default=False, description="Force reinstallation of existing tools")
    dry_run: bool = Field(default=False, description="Perform validation without actual changes")
    notification_webhook: Optional[str] = Field(None, description="Webhook for progress notifications")


class ProvisioningResponse(BaseIOSchema):
    """Response from provisioning operation."""
    
    session_id: str = Field(..., description="Unique session identifier")
    status: TaskStatus = Field(..., description="Overall provisioning status")
    current_phase: ProvisioningPhase = Field(..., description="Current provisioning phase")
    progress_percentage: float = Field(..., ge=0.0, le=100.0, description="Overall progress percentage")
    completed_tasks: List[str] = Field(default_factory=list, description="Completed task IDs")
    failed_tasks: List[str] = Field(default_factory=list, description="Failed task IDs")
    pending_tasks: List[str] = Field(default_factory=list, description="Pending task IDs")
    total_execution_time: float = Field(..., description="Total time elapsed")
    estimated_remaining_time: Optional[float] = Field(None, description="Estimated time to completion")
    human_interventions_required: int = Field(default=0, description="Number of tasks requiring human help")


class OrchestrationStatus(BaseIOSchema):
    """Current status of the orchestration system."""
    
    orchestrator_id: str = Field(..., description="Orchestrator instance ID")
    active_sessions: List[str] = Field(default_factory=list, description="Active provisioning sessions")
    agent_status: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Status of all agents")
    system_health: Dict[str, Any] = Field(default_factory=dict, description="System health metrics")
    resource_usage: Dict[str, float] = Field(default_factory=dict, description="Resource utilization")
    recent_activities: List[str] = Field(default_factory=list, description="Recent system activities")
    uptime: float = Field(..., description="System uptime in seconds")


class TaskDependency(BaseIOSchema):
    """Dependency relationship between tasks."""
    
    task_id: str = Field(..., description="Task identifier")
    depends_on: List[str] = Field(..., description="Tasks this depends on")
    dependency_type: str = Field(default="hard", description="Type of dependency (hard, soft)")
    optional: bool = Field(default=False, description="Whether dependency is optional")


class ExecutionPlan(BaseIOSchema):
    """Execution plan for a provisioning session."""
    
    session_id: str = Field(..., description="Session identifier")
    phases: List[ProvisioningPhase] = Field(..., description="Ordered list of phases")
    task_dependencies: List[TaskDependency] = Field(..., description="Task dependency graph")
    estimated_duration: float = Field(..., description="Estimated total duration in seconds")
    parallel_execution_groups: List[List[str]] = Field(..., description="Tasks that can run in parallel")
    critical_path: List[str] = Field(..., description="Critical path task IDs")
    resource_requirements: Dict[str, Any] = Field(default_factory=dict, description="Resource requirements")


class HumanInterventionRequest(BaseIOSchema):
    """Request for human intervention when automation fails."""
    
    session_id: str = Field(..., description="Session requiring intervention")
    task_id: str = Field(..., description="Task that failed")
    agent_type: AgentType = Field(..., description="Agent that encountered the issue")
    failure_count: int = Field(..., description="Number of consecutive failures")
    failure_reason: str = Field(..., description="Reason for failure")
    context: Dict[str, Any] = Field(..., description="Context information for debugging")
    suggested_actions: List[str] = Field(default_factory=list, description="Suggested manual actions")
    urgency: TaskPriority = Field(default=TaskPriority.HIGH, description="Intervention urgency")
    timeout: Optional[int] = Field(None, description="Timeout for intervention in seconds")