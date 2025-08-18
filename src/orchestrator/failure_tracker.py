"""
Failure Tracker
===============

Tracks task failures, retry attempts, and determines when human intervention is required.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict

from ..schemas import FailureReport, TaskStatus, AgentType


@dataclass
class FailureRecord:
    """Record of a single task failure."""
    
    task_id: str
    agent_type: str
    error_message: str
    timestamp: datetime
    retry_attempt: int = 0
    remediation_attempted: List[str] = field(default_factory=list)


@dataclass 
class TaskFailureHistory:
    """Complete failure history for a task."""
    
    task_id: str
    agent_type: str
    failures: List[FailureRecord] = field(default_factory=list)
    total_failures: int = 0
    first_failure: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    requires_human_intervention: bool = False
    human_notified: bool = False


class FailureTracker:
    """
    Tracks failures across the system and determines intervention requirements.
    """
    
    def __init__(self, failure_threshold: int = 3, intervention_timeout: timedelta = timedelta(hours=24)):
        """
        Initialize the failure tracker.
        
        Args:
            failure_threshold: Number of failures before requiring human intervention
            intervention_timeout: Time to wait for human intervention before escalating
        """
        self.failure_threshold = failure_threshold
        self.intervention_timeout = intervention_timeout
        
        self.task_failures: Dict[str, TaskFailureHistory] = {}
        self.agent_failure_counts: Dict[str, int] = defaultdict(int)
        self.recent_failures: List[FailureRecord] = []
        
        # System-wide metrics
        self.total_failures = 0
        self.intervention_requests = 0
        self.resolved_interventions = 0
        
        logging.info(f"FailureTracker initialized with threshold={failure_threshold}")
    
    def record_failure(self, task_id: str, agent_type: str, error_message: str) -> int:
        """
        Record a task failure and return the total failure count for this task.
        
        Args:
            task_id: ID of the failed task
            agent_type: Type of agent that failed
            error_message: Description of the failure
            
        Returns:
            Total number of failures for this task
        """
        now = datetime.now()
        
        # Create failure record
        failure_record = FailureRecord(
            task_id=task_id,
            agent_type=agent_type,
            error_message=error_message,
            timestamp=now
        )
        
        # Update task failure history
        if task_id not in self.task_failures:
            self.task_failures[task_id] = TaskFailureHistory(
                task_id=task_id,
                agent_type=agent_type
            )
        
        task_history = self.task_failures[task_id]
        task_history.failures.append(failure_record)
        task_history.total_failures += 1
        task_history.last_failure = now
        
        if task_history.first_failure is None:
            task_history.first_failure = now
        
        # Update system metrics
        self.total_failures += 1
        self.agent_failure_counts[agent_type] += 1
        self.recent_failures.append(failure_record)
        
        # Keep only recent failures (last 100)
        if len(self.recent_failures) > 100:
            self.recent_failures = self.recent_failures[-100:]
        
        # Check if human intervention is required
        if task_history.total_failures >= self.failure_threshold:
            task_history.requires_human_intervention = True
            if not task_history.human_notified:
                self.intervention_requests += 1
                task_history.human_notified = True
                logging.warning(
                    f"Human intervention required for task {task_id} after {task_history.total_failures} failures"
                )
        
        logging.error(
            f"Task failure recorded: {task_id} ({agent_type}) - {error_message} "
            f"[{task_history.total_failures} total failures]"
        )
        
        return task_history.total_failures
    
    def get_failure_report(self, task_id: str) -> Optional[FailureReport]:
        """
        Generate a failure report for a specific task.
        
        Args:
            task_id: Task to generate report for
            
        Returns:
            FailureReport or None if task has no failures
        """
        if task_id not in self.task_failures:
            return None
        
        task_history = self.task_failures[task_id]
        
        failure_reasons = [f.error_message for f in task_history.failures]
        last_error = failure_reasons[-1] if failure_reasons else "Unknown error"
        
        # Generate remediation attempts based on error patterns
        remediation_attempts = self._suggest_remediations(task_history)
        
        return FailureReport(
            task_id=task_id,
            agent_type=task_history.agent_type,
            failure_count=task_history.total_failures,
            failure_reasons=failure_reasons,
            last_error=last_error,
            remediation_attempts=remediation_attempts,
            requires_human_intervention=task_history.requires_human_intervention,
            timestamp=task_history.last_failure.isoformat() if task_history.last_failure else ""
        )
    
    def get_tasks_requiring_intervention(self) -> List[str]:
        """Get list of task IDs that require human intervention."""
        return [
            task_id for task_id, history in self.task_failures.items()
            if history.requires_human_intervention and not history.human_notified
        ]
    
    def mark_intervention_resolved(self, task_id: str, resolution_notes: str = ""):
        """
        Mark a human intervention as resolved.
        
        Args:
            task_id: Task that was resolved
            resolution_notes: Notes about how it was resolved
        """
        if task_id in self.task_failures:
            task_history = self.task_failures[task_id]
            task_history.requires_human_intervention = False
            self.resolved_interventions += 1
            
            logging.info(f"Human intervention resolved for task {task_id}: {resolution_notes}")
    
    def get_failure_statistics(self) -> Dict[str, Any]:
        """Get comprehensive failure statistics."""
        
        # Agent failure breakdown
        agent_stats = dict(self.agent_failure_counts)
        
        # Recent failure rate (last hour)
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_count = len([
            f for f in self.recent_failures 
            if f.timestamp > one_hour_ago
        ])
        
        # Task failure breakdown
        task_breakdown = {}
        for task_id, history in self.task_failures.items():
            task_breakdown[task_id] = {
                "failures": history.total_failures,
                "agent": history.agent_type,
                "needs_intervention": history.requires_human_intervention,
                "first_failure": history.first_failure.isoformat() if history.first_failure else None,
                "last_failure": history.last_failure.isoformat() if history.last_failure else None
            }
        
        return {
            "total_failures": self.total_failures,
            "recent_failures_last_hour": recent_count,
            "agent_failure_counts": agent_stats,
            "tasks_needing_intervention": len(self.get_tasks_requiring_intervention()),
            "intervention_requests": self.intervention_requests,
            "resolved_interventions": self.resolved_interventions,
            "task_breakdown": task_breakdown,
            "failure_threshold": self.failure_threshold
        }
    
    def get_common_error_patterns(self) -> List[Dict[str, Any]]:
        """Identify common error patterns across failures."""
        
        error_patterns = defaultdict(int)
        
        for failure in self.recent_failures:
            # Simple pattern matching - in production this would be more sophisticated
            error_lower = failure.error_message.lower()
            
            if "network" in error_lower or "connection" in error_lower:
                error_patterns["network_errors"] += 1
            elif "permission" in error_lower or "denied" in error_lower:
                error_patterns["permission_errors"] += 1
            elif "not found" in error_lower or "missing" in error_lower:
                error_patterns["missing_resource_errors"] += 1
            elif "timeout" in error_lower:
                error_patterns["timeout_errors"] += 1
            else:
                error_patterns["other_errors"] += 1
        
        # Convert to sorted list
        patterns = [
            {"pattern": pattern, "count": count, "percentage": count / len(self.recent_failures) * 100}
            for pattern, count in error_patterns.items()
        ]
        
        patterns.sort(key=lambda x: x["count"], reverse=True)
        return patterns
    
    def _suggest_remediations(self, task_history: TaskFailureHistory) -> List[str]:
        """
        Suggest remediation steps based on failure patterns.
        
        Args:
            task_history: Task failure history to analyze
            
        Returns:
            List of suggested remediation steps
        """
        suggestions = []
        
        # Analyze error messages for patterns
        error_messages = [f.error_message.lower() for f in task_history.failures]
        all_errors = " ".join(error_messages)
        
        if "network" in all_errors or "connection" in all_errors:
            suggestions.extend([
                "Check internet connectivity",
                "Verify DNS resolution",
                "Check firewall settings",
                "Try alternative mirror/repository"
            ])
        
        if "permission" in all_errors or "denied" in all_errors:
            suggestions.extend([
                "Check file/directory permissions",
                "Verify user has required privileges",
                "Check sudo/admin access",
                "Verify authentication tokens"
            ])
        
        if "not found" in all_errors or "missing" in all_errors:
            suggestions.extend([
                "Verify required files/directories exist",
                "Check PATH environment variable",
                "Install missing dependencies",
                "Verify package repository configuration"
            ])
        
        if "timeout" in all_errors:
            suggestions.extend([
                "Increase timeout values",
                "Check system performance", 
                "Verify network speed",
                "Retry during off-peak hours"
            ])
        
        # Agent-specific suggestions
        if task_history.agent_type == "installer":
            suggestions.extend([
                "Clear package cache",
                "Update package repository",
                "Check disk space"
            ])
        elif task_history.agent_type == "authorizer":
            suggestions.extend([
                "Regenerate SSH keys",
                "Check GitHub token permissions",
                "Verify account access"
            ])
        
        # Default suggestions if no patterns matched
        if not suggestions:
            suggestions = [
                "Review error logs for specific details",
                "Check system requirements",
                "Restart the agent/service",
                "Contact system administrator"
            ]
        
        return suggestions[:5]  # Limit to top 5 suggestions
    
    def clear_resolved_tasks(self):
        """Remove resolved tasks from tracking to free memory."""
        resolved_tasks = [
            task_id for task_id, history in self.task_failures.items()
            if not history.requires_human_intervention
        ]
        
        for task_id in resolved_tasks:
            del self.task_failures[task_id]
        
        logging.info(f"Cleared {len(resolved_tasks)} resolved tasks from failure tracker")