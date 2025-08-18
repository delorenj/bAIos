"""
Task Scheduler
==============

Manages task scheduling, dependencies, and execution order for the orchestrator system.
"""

import logging
from typing import Dict, List, Set, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from ..schemas import TaskRequest, TaskResponse, TaskStatus, TaskPriority


@dataclass
class ScheduledTask:
    """Represents a scheduled task with metadata."""
    
    task_id: str
    task_request: TaskRequest
    scheduled_time: datetime
    dependencies: List[str]
    priority: TaskPriority
    max_retries: int = 3
    current_retries: int = 0
    estimated_duration: float = 60.0  # seconds
    assigned_agent: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING


class TaskScheduler:
    """
    Task scheduler that manages task execution order, dependencies, and parallelization.
    """
    
    def __init__(self):
        """Initialize the task scheduler."""
        self.tasks: Dict[str, ScheduledTask] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}
        self.running_tasks: Set[str] = set()
        self.completed_tasks: Set[str] = set()
        self.failed_tasks: Set[str] = set()
        
        logging.info("TaskScheduler initialized")
    
    def schedule_task(self, task_request: TaskRequest, dependencies: Optional[List[str]] = None) -> str:
        """
        Schedule a new task for execution.
        
        Args:
            task_request: Task to schedule
            dependencies: List of task IDs this task depends on
            
        Returns:
            Task ID of the scheduled task
        """
        task_id = task_request.task_id
        dependencies = dependencies or []
        
        # Validate dependencies exist
        for dep_id in dependencies:
            if dep_id not in self.tasks:
                raise ValueError(f"Dependency task {dep_id} not found")
        
        scheduled_task = ScheduledTask(
            task_id=task_id,
            task_request=task_request,
            scheduled_time=datetime.now(),
            dependencies=dependencies,
            priority=task_request.priority,
            estimated_duration=task_request.timeout
        )
        
        self.tasks[task_id] = scheduled_task
        self.dependency_graph[task_id] = set(dependencies)
        
        logging.info(f"Scheduled task {task_id} with dependencies: {dependencies}")
        return task_id
    
    def get_ready_tasks(self) -> List[str]:
        """
        Get list of tasks that are ready to execute (all dependencies met).
        
        Returns:
            List of task IDs ready for execution
        """
        ready_tasks = []
        
        for task_id, task in self.tasks.items():
            if (task.status == TaskStatus.PENDING and 
                task_id not in self.running_tasks and
                self._are_dependencies_met(task_id)):
                ready_tasks.append(task_id)
        
        # Sort by priority (high to low) then by scheduled time
        ready_tasks.sort(key=lambda tid: (
            -self._priority_value(self.tasks[tid].priority),
            self.tasks[tid].scheduled_time
        ))
        
        logging.debug(f"Found {len(ready_tasks)} ready tasks: {ready_tasks}")
        return ready_tasks
    
    def mark_task_running(self, task_id: str):
        """Mark a task as currently running."""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        self.tasks[task_id].status = TaskStatus.IN_PROGRESS
        self.running_tasks.add(task_id)
        logging.info(f"Task {task_id} marked as running")
    
    def complete_task(self, task_id: str, result: TaskResponse):
        """Mark a task as completed."""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        self.tasks[task_id].status = TaskStatus.COMPLETED
        self.running_tasks.discard(task_id)
        self.completed_tasks.add(task_id)
        
        logging.info(f"Task {task_id} completed successfully")
    
    def fail_task(self, task_id: str, error_message: str) -> bool:
        """
        Mark a task as failed and determine if it should be retried.
        
        Args:
            task_id: Task that failed
            error_message: Error description
            
        Returns:
            True if task should be retried, False if max retries exceeded
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        task.current_retries += 1
        self.running_tasks.discard(task_id)
        
        if task.current_retries >= task.max_retries:
            task.status = TaskStatus.FAILED
            self.failed_tasks.add(task_id)
            logging.error(f"Task {task_id} failed permanently after {task.current_retries} attempts")
            return False
        else:
            task.status = TaskStatus.PENDING
            logging.warning(f"Task {task_id} failed, scheduling retry {task.current_retries}/{task.max_retries}")
            return True
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get detailed status of a specific task."""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        
        return {
            "task_id": task_id,
            "status": task.status.value,
            "priority": task.priority.value,
            "dependencies": task.dependencies,
            "scheduled_time": task.scheduled_time.isoformat(),
            "retries": f"{task.current_retries}/{task.max_retries}",
            "estimated_duration": task.estimated_duration,
            "assigned_agent": task.assigned_agent,
            "dependencies_met": self._are_dependencies_met(task_id)
        }
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of task execution status."""
        total_tasks = len(self.tasks)
        
        return {
            "total_tasks": total_tasks,
            "pending_tasks": len([t for t in self.tasks.values() if t.status == TaskStatus.PENDING]),
            "running_tasks": len(self.running_tasks),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "progress_percentage": (len(self.completed_tasks) / total_tasks * 100) if total_tasks > 0 else 0,
            "ready_for_execution": len(self.get_ready_tasks())
        }
    
    def get_critical_path(self) -> List[str]:
        """
        Calculate the critical path through the task dependency graph.
        
        Returns:
            List of task IDs representing the critical path
        """
        # Build reverse dependency graph
        reverse_deps = {}
        for task_id, deps in self.dependency_graph.items():
            for dep in deps:
                if dep not in reverse_deps:
                    reverse_deps[dep] = set()
                reverse_deps[dep].add(task_id)
        
        # Find longest path from each leaf node
        def get_path_length(task_id: str, visited: Set[str]) -> int:
            if task_id in visited:
                return 0  # Avoid cycles
            
            visited.add(task_id)
            task = self.tasks[task_id]
            max_child_length = 0
            
            if task_id in reverse_deps:
                for child_id in reverse_deps[task_id]:
                    child_length = get_path_length(child_id, visited.copy())
                    max_child_length = max(max_child_length, child_length)
            
            return task.estimated_duration + max_child_length
        
        # Find task with longest path
        longest_path_length = 0
        critical_start = None
        
        for task_id in self.tasks:
            if not self.dependency_graph[task_id]:  # Root task (no dependencies)
                path_length = get_path_length(task_id, set())
                if path_length > longest_path_length:
                    longest_path_length = path_length
                    critical_start = task_id
        
        # Build critical path
        if critical_start is None:
            return []
        
        critical_path = []
        current = critical_start
        visited = set()
        
        while current and current not in visited:
            critical_path.append(current)
            visited.add(current)
            
            # Find child with longest path
            next_task = None
            max_length = 0
            
            if current in reverse_deps:
                for child_id in reverse_deps[current]:
                    child_length = get_path_length(child_id, set())
                    if child_length > max_length:
                        max_length = child_length
                        next_task = child_id
            
            current = next_task
        
        logging.info(f"Critical path calculated: {critical_path} (estimated {longest_path_length:.1f}s)")
        return critical_path
    
    def _are_dependencies_met(self, task_id: str) -> bool:
        """Check if all dependencies for a task are completed."""
        dependencies = self.dependency_graph.get(task_id, set())
        return all(dep_id in self.completed_tasks for dep_id in dependencies)
    
    def _priority_value(self, priority: TaskPriority) -> int:
        """Convert priority enum to numeric value for sorting."""
        priority_values = {
            TaskPriority.LOW: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.HIGH: 3,
            TaskPriority.CRITICAL: 4
        }
        return priority_values.get(priority, 0)
    
    def estimate_remaining_time(self) -> float:
        """Estimate total remaining execution time."""
        pending_tasks = [t for t in self.tasks.values() if t.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]]
        
        if not pending_tasks:
            return 0.0
        
        # Simple estimation: sum of remaining task durations
        # In reality, this would account for parallelization opportunities
        total_time = sum(task.estimated_duration for task in pending_tasks)
        
        return total_time
    
    def clear_completed_tasks(self):
        """Remove completed tasks from the scheduler to free memory."""
        completed_ids = list(self.completed_tasks)
        
        for task_id in completed_ids:
            if task_id in self.tasks:
                del self.tasks[task_id]
            if task_id in self.dependency_graph:
                del self.dependency_graph[task_id]
        
        self.completed_tasks.clear()
        logging.info(f"Cleared {len(completed_ids)} completed tasks from scheduler")