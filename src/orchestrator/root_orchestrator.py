"""
Root Orchestrator Agent
=======================

Main orchestrator agent that coordinates all specialized agents for WSL environment provisioning.
Uses the Atomic Agents framework with OpenRouter API integration.
"""

import os
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import uuid4

import instructor
from openai import OpenAI
from atomic_agents import AtomicAgent, AgentConfig
from atomic_agents.context import ChatHistory, SystemPromptGenerator

from ..schemas import (
    ProvisioningRequest, ProvisioningResponse, OrchestrationStatus,
    AgentRequest, AgentResponse, TaskStatus, ProvisioningPhase,
    ExecutionPlan, HumanInterventionRequest
)
from .agent_factory import AgentFactory
from .task_scheduler import TaskScheduler
from .failure_tracker import FailureTracker


class RootOrchestrator(AtomicAgent[ProvisioningRequest, ProvisioningResponse]):
    """
    Root orchestrator that manages the entire WSL provisioning process.
    
    Coordinates specialized agents:
    - Researcher: Analyzes environment specs and gathers information
    - Installer: Handles package and tool installation
    - ShellMaster: Manages shell configuration and environment setup
    - ProgressTracker: Monitors and reports progress
    - Authorizer: Handles authentication and access control
    - MiseMaster: Manages version-controlled tools via mise
    - QAExpert: Performs validation and quality assurance
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize the root orchestrator."""
        if config is None:
            config = self._create_default_config()
        
        super().__init__(config)
        
        # Initialize components
        self.session_id = str(uuid4())
        self.agent_factory = AgentFactory()
        self.task_scheduler = TaskScheduler()
        self.failure_tracker = FailureTracker()
        
        # State management
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.agent_status: Dict[str, Dict[str, Any]] = {}
        self.system_metrics = {
            "start_time": datetime.now().isoformat(),
            "total_sessions": 0,
            "successful_sessions": 0,
            "failed_sessions": 0
        }
        
        logging.info(f"RootOrchestrator initialized with session ID: {self.session_id}")
    
    def _create_default_config(self) -> AgentConfig:
        """Create default configuration with OpenRouter integration."""
        
        # Get API key from environment or use the provided key
        api_key = os.getenv("OPENROUTER_API_KEY", "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")
        
        # Setup OpenRouter client
        client = instructor.from_openai(
            OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
            )
        )
        
        # Create system prompt generator
        system_prompt_generator = SystemPromptGenerator(
            background=[
                "You are the Root Orchestrator for WSL environment provisioning.",
                "You coordinate specialized agents to provision complete development environments.",
                "You manage task scheduling, failure recovery, and quality assurance.",
                "You ensure all components are properly installed and configured."
            ],
            steps=[
                "1. Parse the provisioning request and validate the environment specification",
                "2. Create an execution plan with proper task dependencies",
                "3. Initialize and coordinate specialized agents for each task type",
                "4. Monitor progress and handle failures with appropriate retry logic",
                "5. Perform quality assurance through the QA Expert agent",
                "6. Handle human intervention requests when automation fails",
                "7. Generate comprehensive reports and status updates"
            ],
            output_instructions=[
                "Always provide structured responses with clear status information",
                "Track progress as percentage and provide time estimates",
                "Report failures with detailed error messages and remediation suggestions",
                "Coordinate agents efficiently to minimize total provisioning time",
                "Ensure all success criteria are met before marking tasks complete"
            ]
        )
        
        return AgentConfig(
            client=client,
            model="anthropic/claude-3.5-sonnet",
            history=ChatHistory(),
            system_prompt_generator=system_prompt_generator,
            model_api_parameters={
                "max_tokens": 4096,
                "temperature": 0.1  # Low temperature for consistent orchestration
            }
        )
    
    async def provision_environment(self, request: ProvisioningRequest) -> ProvisioningResponse:
        """
        Main entry point for environment provisioning.
        
        Args:
            request: Provisioning request with environment spec and preferences
            
        Returns:
            ProvisioningResponse with status and progress information
        """
        session_id = str(uuid4())
        start_time = datetime.now()
        
        try:
            logging.info(f"Starting provisioning session {session_id}")
            
            # Initialize session state
            session_state = {
                "session_id": session_id,
                "request": request.dict(),
                "start_time": start_time.isoformat(),
                "current_phase": ProvisioningPhase.INITIALIZATION,
                "status": TaskStatus.IN_PROGRESS,
                "completed_tasks": [],
                "failed_tasks": [],
                "pending_tasks": [],
                "human_interventions": 0
            }
            self.active_sessions[session_id] = session_state
            
            # Phase 1: Environment Analysis
            await self._execute_phase(
                session_id, 
                ProvisioningPhase.INITIALIZATION,
                "Analyzing environment specification and creating execution plan"
            )
            
            # Create execution plan
            execution_plan = await self._create_execution_plan(request)
            session_state["execution_plan"] = execution_plan.dict()
            
            # Execute all phases
            for phase in execution_plan.phases:
                if phase not in request.skip_phases:
                    await self._execute_phase(session_id, phase, f"Executing {phase.value}")
                    
            # Final validation
            qa_result = await self._perform_final_validation(session_id)
            
            # Calculate final metrics
            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds()
            
            # Update system metrics
            self.system_metrics["total_sessions"] += 1
            if qa_result.validation_passed:
                self.system_metrics["successful_sessions"] += 1
            else:
                self.system_metrics["failed_sessions"] += 1
            
            # Create response
            response = ProvisioningResponse(
                session_id=session_id,
                status=TaskStatus.COMPLETED if qa_result.validation_passed else TaskStatus.FAILED,
                current_phase=ProvisioningPhase.CLEANUP,
                progress_percentage=100.0,
                completed_tasks=session_state["completed_tasks"],
                failed_tasks=session_state["failed_tasks"],
                pending_tasks=session_state["pending_tasks"],
                total_execution_time=total_time,
                human_interventions_required=session_state["human_interventions"]
            )
            
            logging.info(f"Provisioning session {session_id} completed with status: {response.status}")
            return response
            
        except Exception as e:
            logging.error(f"Provisioning session {session_id} failed: {str(e)}")
            
            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds()
            
            self.system_metrics["total_sessions"] += 1
            self.system_metrics["failed_sessions"] += 1
            
            return ProvisioningResponse(
                session_id=session_id,
                status=TaskStatus.FAILED,
                current_phase=session_state.get("current_phase", ProvisioningPhase.INITIALIZATION),
                progress_percentage=0.0,
                completed_tasks=session_state.get("completed_tasks", []),
                failed_tasks=session_state.get("failed_tasks", []) + [str(e)],
                pending_tasks=session_state.get("pending_tasks", []),
                total_execution_time=total_time,
                human_interventions_required=session_state.get("human_interventions", 0)
            )
    
    async def _execute_phase(self, session_id: str, phase: ProvisioningPhase, description: str):
        """Execute a specific provisioning phase."""
        logging.info(f"Session {session_id}: Starting phase {phase.value}")
        
        session_state = self.active_sessions[session_id]
        session_state["current_phase"] = phase
        
        # Get tasks for this phase
        tasks = await self._get_phase_tasks(session_id, phase)
        session_state["pending_tasks"].extend([task["task_id"] for task in tasks])
        
        # Execute tasks with appropriate agents
        for task in tasks:
            try:
                result = await self._execute_task_with_agent(session_id, task)
                if result.status == TaskStatus.COMPLETED:
                    session_state["completed_tasks"].append(task["task_id"])
                    if task["task_id"] in session_state["pending_tasks"]:
                        session_state["pending_tasks"].remove(task["task_id"])
                else:
                    await self._handle_task_failure(session_id, task, result)
                    
            except Exception as e:
                logging.error(f"Task {task['task_id']} failed with exception: {str(e)}")
                await self._handle_task_failure(session_id, task, None, str(e))
        
        logging.info(f"Session {session_id}: Completed phase {phase.value}")
    
    async def _create_execution_plan(self, request: ProvisioningRequest) -> ExecutionPlan:
        """Create detailed execution plan based on environment spec."""
        
        # Read environment specification
        spec_content = await self._read_environment_spec(request.environment_spec_path)
        
        # Use Researcher agent to analyze spec and create plan
        researcher_request = AgentRequest(
            agent_type="researcher",
            task_description=f"Analyze environment specification and create execution plan",
            context={
                "spec_content": spec_content,
                "user_preferences": request.user_preferences,
                "skip_phases": request.skip_phases
            }
        )
        
        researcher = self.agent_factory.create_agent("researcher")
        analysis_result = await researcher.run_async(researcher_request)
        
        # Create execution plan from analysis
        phases = [phase for phase in ProvisioningPhase if phase not in request.skip_phases]
        
        return ExecutionPlan(
            session_id=self.session_id,
            phases=phases,
            task_dependencies=[],  # Will be populated by task scheduler
            estimated_duration=3600.0,  # Default 1 hour
            parallel_execution_groups=[],
            critical_path=[],
            resource_requirements={}
        )
    
    async def _get_phase_tasks(self, session_id: str, phase: ProvisioningPhase) -> List[Dict[str, Any]]:
        """Get list of tasks for a specific phase."""
        
        # Phase-specific task mapping
        phase_tasks = {
            ProvisioningPhase.INITIALIZATION: [
                {"task_id": "validate_wsl", "agent_type": "researcher", "description": "Validate WSL installation"},
                {"task_id": "check_prerequisites", "agent_type": "researcher", "description": "Check system prerequisites"}
            ],
            ProvisioningPhase.SYSTEM_SETUP: [
                {"task_id": "setup_shell", "agent_type": "shell_master", "description": "Configure shell environment"},
                {"task_id": "setup_auth", "agent_type": "authorizer", "description": "Setup authentication"}
            ],
            ProvisioningPhase.TOOL_INSTALLATION: [
                {"task_id": "install_base_tools", "agent_type": "installer", "description": "Install base tools"},
                {"task_id": "install_mise_tools", "agent_type": "mise_master", "description": "Install mise-managed tools"}
            ],
            ProvisioningPhase.CONFIGURATION: [
                {"task_id": "configure_tools", "agent_type": "installer", "description": "Configure installed tools"},
                {"task_id": "setup_symlinks", "agent_type": "shell_master", "description": "Create necessary symlinks"}
            ],
            ProvisioningPhase.VALIDATION: [
                {"task_id": "validate_installation", "agent_type": "qa_expert", "description": "Validate complete installation"}
            ],
            ProvisioningPhase.CLEANUP: [
                {"task_id": "cleanup_temp", "agent_type": "installer", "description": "Clean up temporary files"}
            ]
        }
        
        return phase_tasks.get(phase, [])
    
    async def _execute_task_with_agent(self, session_id: str, task: Dict[str, Any]) -> AgentResponse:
        """Execute a task using the appropriate specialized agent."""
        
        agent_type = task["agent_type"]
        agent = self.agent_factory.create_agent(agent_type)
        
        request = AgentRequest(
            agent_type=agent_type,
            task_description=task["description"],
            context={
                "session_id": session_id,
                "task_id": task["task_id"],
                "session_state": self.active_sessions[session_id]
            }
        )
        
        logging.info(f"Executing task {task['task_id']} with {agent_type} agent")
        
        try:
            result = await agent.run_async(request)
            logging.info(f"Task {task['task_id']} completed with status: {result.status}")
            return result
        except Exception as e:
            logging.error(f"Task {task['task_id']} failed: {str(e)}")
            return AgentResponse(
                agent_type=agent_type,
                status=TaskStatus.FAILED,
                error_message=str(e),
                logs=[f"Exception during task execution: {str(e)}"],
                execution_time=0.0
            )
    
    async def _handle_task_failure(self, session_id: str, task: Dict[str, Any], result: Optional[AgentResponse], error: Optional[str] = None):
        """Handle task failure and determine retry or escalation."""
        
        task_id = task["task_id"]
        session_state = self.active_sessions[session_id]
        
        # Track failure
        failure_count = self.failure_tracker.record_failure(
            task_id, 
            task["agent_type"],
            error or (result.error_message if result else "Unknown error")
        )
        
        session_state["failed_tasks"].append(task_id)
        if task_id in session_state["pending_tasks"]:
            session_state["pending_tasks"].remove(task_id)
        
        # Check if human intervention is required (3+ failures)
        if failure_count >= 3:
            logging.warning(f"Task {task_id} requires human intervention after {failure_count} failures")
            
            intervention_request = HumanInterventionRequest(
                session_id=session_id,
                task_id=task_id,
                agent_type=task["agent_type"],
                failure_count=failure_count,
                failure_reason=error or (result.error_message if result else "Unknown error"),
                context={
                    "task": task,
                    "last_result": result.dict() if result else None,
                    "session_state": session_state
                },
                suggested_actions=[
                    "Check system requirements",
                    "Verify network connectivity", 
                    "Check permissions",
                    "Review error logs"
                ]
            )
            
            # In a real implementation, this would notify external systems
            logging.info(f"Human intervention requested: {intervention_request.dict()}")
            session_state["human_interventions"] += 1
    
    async def _perform_final_validation(self, session_id: str):
        """Perform comprehensive validation using QA Expert."""
        
        qa_agent = self.agent_factory.create_agent("qa_expert")
        session_state = self.active_sessions[session_id]
        
        validation_request = AgentRequest(
            agent_type="qa_expert",
            task_description="Perform comprehensive validation of WSL environment provisioning",
            context={
                "session_id": session_id,
                "completed_tasks": session_state["completed_tasks"],
                "failed_tasks": session_state["failed_tasks"],
                "session_state": session_state
            }
        )
        
        validation_result = await qa_agent.run_async(validation_request)
        logging.info(f"Final validation completed: {validation_result.status}")
        
        return validation_result
    
    async def _read_environment_spec(self, spec_path: str) -> str:
        """Read the environment specification file."""
        try:
            with open(spec_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            logging.warning(f"Environment spec file not found: {spec_path}")
            # Return default spec for testing
            return """
# WSL Development Environment Specification
This is a sample specification for testing the orchestrator system.
The actual specification would contain detailed requirements.
            """
    
    def get_orchestration_status(self) -> OrchestrationStatus:
        """Get current status of the orchestration system."""
        
        return OrchestrationStatus(
            orchestrator_id=self.session_id,
            active_sessions=list(self.active_sessions.keys()),
            agent_status=self.agent_status,
            system_health={"status": "healthy", "uptime": "active"},
            resource_usage={"cpu": 0.1, "memory": 0.2},
            recent_activities=[f"Session {sid} - {state.get('current_phase', 'unknown')}" 
                              for sid, state in list(self.active_sessions.items())[-5:]],
            uptime=(datetime.now() - datetime.fromisoformat(self.system_metrics["start_time"])).total_seconds()
        )

    def run(self, user_input: ProvisioningRequest) -> ProvisioningResponse:
        """Synchronous wrapper for the async provisioning process."""
        return asyncio.run(self.provision_environment(user_input))