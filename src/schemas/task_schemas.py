"""
Task Schema Definitions
=======================

Defines schemas for task management, checklists, and execution tracking.
"""

from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pydantic import Field, validator
from atomic_agents import BaseIOSchema
from .agent_schemas import TaskStatus, TaskPriority


class ChecklistItemType(str, Enum):
    """Types of checklist items."""
    COMMAND = "command"
    FILE_CHECK = "file_check"
    SERVICE_CHECK = "service_check"
    VALIDATION = "validation"
    MANUAL = "manual"


class TaskRequest(BaseIOSchema):
    """Request for task execution."""
    
    task_id: str = Field(..., description="Unique task identifier")
    title: str = Field(..., description="Human-readable task title")
    description: str = Field(..., description="Detailed task description")
    agent_type: str = Field(..., description="Type of agent to execute task")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Task-specific parameters")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority")
    timeout: int = Field(default=300, description="Task timeout in seconds")
    retry_policy: Dict[str, Any] = Field(default_factory=dict, description="Retry configuration")
    success_criteria: List[str] = Field(..., description="Criteria for successful completion")


class TaskResponse(BaseIOSchema):
    """Response from task execution."""
    
    task_id: str = Field(..., description="Task identifier")
    status: TaskStatus = Field(..., description="Execution status")
    result: Optional[Dict[str, Any]] = Field(None, description="Task results")
    output: List[str] = Field(default_factory=list, description="Command outputs or logs")
    error: Optional[str] = Field(None, description="Error message if failed")
    duration: float = Field(..., description="Execution duration in seconds")
    resource_usage: Dict[str, Any] = Field(default_factory=dict, description="Resources consumed")
    artifacts: List[str] = Field(default_factory=list, description="Generated artifacts")


class ChecklistItem(BaseIOSchema):
    """Individual item in a validation checklist."""
    
    item_id: str = Field(..., description="Unique item identifier")
    title: str = Field(..., description="Item title")
    description: str = Field(..., description="Detailed description")
    type: ChecklistItemType = Field(..., description="Type of check to perform")
    command: Optional[str] = Field(None, description="Command to run for validation")
    expected_output: Optional[str] = Field(None, description="Expected command output")
    file_path: Optional[str] = Field(None, description="File path to check")
    service_name: Optional[str] = Field(None, description="Service name to check")
    validation_script: Optional[str] = Field(None, description="Custom validation script")
    depends_on: List[str] = Field(default_factory=list, description="Dependencies on other items")
    timeout: int = Field(default=30, description="Timeout for check in seconds")
    retry_count: int = Field(default=3, description="Number of retries on failure")
    critical: bool = Field(default=False, description="Whether failure blocks overall success")


class ChecklistResult(BaseIOSchema):
    """Result of checklist execution."""
    
    checklist_id: str = Field(..., description="Checklist identifier")
    total_items: int = Field(..., description="Total number of items")
    passed_items: int = Field(..., description="Number of items that passed")
    failed_items: int = Field(..., description="Number of items that failed")
    skipped_items: int = Field(..., description="Number of items that were skipped")
    item_results: List[Dict[str, Any]] = Field(..., description="Results for each item")
    overall_success: bool = Field(..., description="Whether overall checklist passed")
    execution_time: float = Field(..., description="Total execution time")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for failures")


class ProgressUpdate(BaseIOSchema):
    """Progress update for a running task or session."""
    
    session_id: str = Field(..., description="Session identifier")
    current_task: Optional[str] = Field(None, description="Currently executing task")
    completed_count: int = Field(..., description="Number of completed tasks")
    total_count: int = Field(..., description="Total number of tasks")
    percentage: float = Field(..., ge=0.0, le=100.0, description="Progress percentage")
    estimated_remaining: Optional[float] = Field(None, description="Estimated remaining time")
    current_phase: str = Field(..., description="Current provisioning phase")
    status_message: str = Field(..., description="Human-readable status message")
    timestamp: str = Field(..., description="ISO timestamp of update")


class RetryPolicy(BaseIOSchema):
    """Configuration for task retry behavior."""
    
    max_retries: int = Field(default=3, description="Maximum number of retries")
    retry_delay: float = Field(default=1.0, description="Delay between retries in seconds")
    backoff_multiplier: float = Field(default=2.0, description="Backoff multiplier for delays")
    max_delay: float = Field(default=60.0, description="Maximum delay between retries")
    retry_on_errors: List[str] = Field(default_factory=list, description="Error types to retry on")
    stop_on_errors: List[str] = Field(default_factory=list, description="Error types to not retry")