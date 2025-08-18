"""
Atomic Agents Orchestrator System
=================================

Complete orchestrator system for WSL environment provisioning using specialized agents.

This system provides:
- Root orchestrator for coordinating complex provisioning tasks
- 7 specialized agents for different aspects of system setup
- Failure tracking and human-in-the-loop intervention
- QA validation with comprehensive testing
- OpenRouter API integration for LLM capabilities

Example Usage:
    from src.orchestrator import RootOrchestrator
    from src.schemas import ProvisioningRequest
    
    orchestrator = RootOrchestrator()
    
    request = ProvisioningRequest(
        environment_spec_path="docs/WSL_ENVIRONMENT_SPEC.md",
        user_preferences={"minimal_install": False},
        dry_run=True
    )
    
    response = orchestrator.run(request)
    print(f"Provisioning status: {response.status}")
"""

from .orchestrator import RootOrchestrator, AgentFactory, TaskScheduler, FailureTracker
from .agents import (
    BaseSpecializedAgent, ResearcherAgent, InstallerAgent, ShellMasterAgent,
    ProgressTrackerAgent, AuthorizerAgent, MiseMasterAgent, QAExpertAgent
)
from .schemas import (
    ProvisioningRequest, ProvisioningResponse, OrchestrationStatus,
    AgentRequest, AgentResponse, QAResult, FailureReport
)

__version__ = "1.0.0"

__all__ = [
    # Core orchestrator
    "RootOrchestrator",
    "AgentFactory", 
    "TaskScheduler",
    "FailureTracker",
    
    # Specialized agents
    "BaseSpecializedAgent",
    "ResearcherAgent",
    "InstallerAgent", 
    "ShellMasterAgent",
    "ProgressTrackerAgent",
    "AuthorizerAgent",
    "MiseMasterAgent",
    "QAExpertAgent",
    
    # Schemas
    "ProvisioningRequest",
    "ProvisioningResponse",
    "OrchestrationStatus",
    "AgentRequest",
    "AgentResponse", 
    "QAResult",
    "FailureReport"
]