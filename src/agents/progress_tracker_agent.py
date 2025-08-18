"""
Progress Tracker Agent
======================

Specialized agent for monitoring and reporting progress.
"""

import logging
from typing import Dict, Any
from datetime import datetime
from .base_specialized_agent import BaseSpecializedAgent
from ..schemas import AgentRequest


class ProgressTrackerAgent(BaseSpecializedAgent):
    """Agent specialized in tracking and reporting progress."""
    
    def __init__(self, config):
        super().__init__(config)
        self.session_metrics = {}
    
    async def _execute_task(self, request: AgentRequest) -> Dict[str, Any]:
        """Execute progress tracking tasks."""
        context = request.context
        session_id = context.get("session_id", "default")
        
        # Update session metrics
        if session_id not in self.session_metrics:
            self.session_metrics[session_id] = {
                "start_time": datetime.now(),
                "tasks_completed": 0,
                "tasks_failed": 0,
                "current_phase": "initialization"
            }
        
        session_state = context.get("session_state", {})
        metrics = self.session_metrics[session_id]
        
        # Update metrics from session state
        metrics["tasks_completed"] = len(session_state.get("completed_tasks", []))
        metrics["tasks_failed"] = len(session_state.get("failed_tasks", []))
        metrics["current_phase"] = session_state.get("current_phase", "unknown")
        
        # Calculate progress
        total_tasks = (
            len(session_state.get("completed_tasks", [])) +
            len(session_state.get("failed_tasks", [])) +
            len(session_state.get("pending_tasks", []))
        )
        
        progress_percentage = (metrics["tasks_completed"] / total_tasks * 100) if total_tasks > 0 else 0
        
        # Estimate remaining time
        elapsed_time = (datetime.now() - metrics["start_time"]).total_seconds()
        if metrics["tasks_completed"] > 0:
            avg_time_per_task = elapsed_time / metrics["tasks_completed"]
            estimated_remaining = avg_time_per_task * len(session_state.get("pending_tasks", []))
        else:
            estimated_remaining = None
        
        return {
            "task_type": "progress_tracking",
            "session_id": session_id,
            "progress_percentage": round(progress_percentage, 1),
            "tasks_completed": metrics["tasks_completed"],
            "tasks_failed": metrics["tasks_failed"],
            "pending_tasks": len(session_state.get("pending_tasks", [])),
            "current_phase": metrics["current_phase"],
            "elapsed_time_seconds": elapsed_time,
            "estimated_remaining_seconds": estimated_remaining,
            "success_rate": (metrics["tasks_completed"] / (metrics["tasks_completed"] + metrics["tasks_failed"]) * 100) if (metrics["tasks_completed"] + metrics["tasks_failed"]) > 0 else 100
        }