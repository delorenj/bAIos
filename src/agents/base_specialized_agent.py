"""
Base Specialized Agent
=====================

Base class for all specialized agents in the orchestrator system.
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from atomic_agents import AtomicAgent, AgentConfig
from ..schemas import AgentRequest, AgentResponse, TaskStatus


class BaseSpecializedAgent(AtomicAgent[AgentRequest, AgentResponse]):
    """
    Base class for all specialized agents.
    
    Provides common functionality for task execution, logging, and error handling.
    """
    
    def __init__(self, config: AgentConfig):
        """Initialize the base specialized agent."""
        super().__init__(config)
        self.agent_type = self.__class__.__name__.lower().replace("agent", "")
        self.execution_history: List[Dict[str, Any]] = []
        
        logging.info(f"Initialized {self.agent_type} agent")
    
    def run(self, user_input: AgentRequest) -> AgentResponse:
        """
        Execute a task request synchronously.
        
        Args:
            user_input: Agent request with task details
            
        Returns:
            Agent response with execution results
        """
        return asyncio.run(self.run_async(user_input))
    
    async def run_async(self, user_input: AgentRequest) -> AgentResponse:
        """
        Execute a task request asynchronously.
        
        Args:
            user_input: Agent request with task details
            
        Returns:
            Agent response with execution results
        """
        start_time = datetime.now()
        task_id = user_input.context.get("task_id", "unknown")
        
        logging.info(f"{self.agent_type} agent starting task: {task_id}")
        
        try:
            # Validate request
            self._validate_request(user_input)
            
            # Execute the specific agent logic
            result = await self._execute_task(user_input)
            
            # Calculate execution time
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Create success response
            response = AgentResponse(
                agent_type=user_input.agent_type,
                status=TaskStatus.COMPLETED,
                result=result,
                logs=self._get_execution_logs(),
                execution_time=execution_time,
                resources_used={"cpu_time": execution_time, "memory_mb": self._estimate_memory_usage()}
            )
            
            # Record execution history
            self._record_execution(user_input, response)
            
            logging.info(f"{self.agent_type} agent completed task {task_id} in {execution_time:.2f}s")
            return response
            
        except Exception as e:
            # Calculate execution time for failed task
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            error_message = str(e)
            logging.error(f"{self.agent_type} agent failed task {task_id}: {error_message}")
            
            # Create failure response
            response = AgentResponse(
                agent_type=user_input.agent_type,
                status=TaskStatus.FAILED,
                error_message=error_message,
                logs=self._get_execution_logs() + [f"ERROR: {error_message}"],
                execution_time=execution_time,
                resources_used={"cpu_time": execution_time, "memory_mb": self._estimate_memory_usage()}
            )
            
            # Record execution history
            self._record_execution(user_input, response)
            
            return response
    
    async def _execute_task(self, request: AgentRequest) -> Dict[str, Any]:
        """
        Execute the specific agent task logic.
        
        This method should be overridden by each specialized agent.
        
        Args:
            request: Agent request with task details
            
        Returns:
            Task execution results
        """
        raise NotImplementedError("Specialized agents must implement _execute_task method")
    
    def _validate_request(self, request: AgentRequest):
        """
        Validate the agent request.
        
        Args:
            request: Request to validate
            
        Raises:
            ValueError: If request is invalid
        """
        if not request.task_description:
            raise ValueError("Task description is required")
        
        if request.agent_type != self.agent_type.replace("_", ""):
            raise ValueError(f"Agent type mismatch: expected {self.agent_type}, got {request.agent_type}")
    
    def _get_execution_logs(self) -> List[str]:
        """
        Get execution logs for the current task.
        
        Returns:
            List of log messages
        """
        # In a real implementation, this would collect logs from the agent's operations
        return [
            f"Task started at {datetime.now().isoformat()}",
            f"Agent type: {self.agent_type}",
            "Task execution in progress..."
        ]
    
    def _estimate_memory_usage(self) -> float:
        """
        Estimate memory usage for the agent.
        
        Returns:
            Estimated memory usage in MB
        """
        # Simple estimation - in production this would use actual metrics
        base_memory = 50.0  # Base agent memory
        history_memory = len(self.execution_history) * 0.1  # History overhead
        return base_memory + history_memory
    
    def _record_execution(self, request: AgentRequest, response: AgentResponse):
        """
        Record execution history for debugging and metrics.
        
        Args:
            request: Original request
            response: Response generated
        """
        execution_record = {
            "timestamp": datetime.now().isoformat(),
            "task_id": request.context.get("task_id", "unknown"),
            "task_description": request.task_description,
            "status": response.status.value,
            "execution_time": response.execution_time,
            "success": response.status == TaskStatus.COMPLETED
        }
        
        self.execution_history.append(execution_record)
        
        # Keep only recent history (last 100 executions)
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-100:]
    
    def get_agent_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for this agent.
        
        Returns:
            Dictionary of performance metrics
        """
        if not self.execution_history:
            return {
                "total_executions": 0,
                "success_rate": 0.0,
                "average_execution_time": 0.0,
                "recent_activity": []
            }
        
        successful_executions = sum(1 for record in self.execution_history if record["success"])
        total_executions = len(self.execution_history)
        success_rate = successful_executions / total_executions * 100
        
        execution_times = [record["execution_time"] for record in self.execution_history]
        average_time = sum(execution_times) / len(execution_times)
        
        # Get recent activity (last 5 executions)
        recent_activity = self.execution_history[-5:] if len(self.execution_history) >= 5 else self.execution_history
        
        return {
            "agent_type": self.agent_type,
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": total_executions - successful_executions,
            "success_rate": round(success_rate, 2),
            "average_execution_time": round(average_time, 2),
            "min_execution_time": min(execution_times),
            "max_execution_time": max(execution_times),
            "recent_activity": recent_activity
        }
    
    async def _run_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """
        Run a system command and return results.
        
        Args:
            command: Command to execute
            timeout: Timeout in seconds
            
        Returns:
            Command execution results
        """
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            return {
                "command": command,
                "return_code": process.returncode,
                "stdout": stdout.decode('utf-8') if stdout else "",
                "stderr": stderr.decode('utf-8') if stderr else "",
                "success": process.returncode == 0
            }
            
        except asyncio.TimeoutError:
            raise Exception(f"Command timed out after {timeout}s: {command}")
        except Exception as e:
            raise Exception(f"Command execution failed: {command} - {str(e)}")
    
    async def _check_file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file exists, False otherwise
        """
        result = await self._run_command(f"test -f {file_path}")
        return result["success"]
    
    async def _check_directory_exists(self, dir_path: str) -> bool:
        """
        Check if a directory exists.
        
        Args:
            dir_path: Directory path to check
            
        Returns:
            True if directory exists, False otherwise
        """
        result = await self._run_command(f"test -d {dir_path}")
        return result["success"]