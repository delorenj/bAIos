"""
Stub Agent Pattern
==================

Stub agents for testing and development purposes.
"""

import logging
import asyncio
import random
from typing import Dict, Any, Optional
from .base_specialized_agent import BaseSpecializedAgent
from ..schemas import AgentRequest, AgentResponse, QAResult, TaskStatus


class StubAgent(BaseSpecializedAgent):
    """Base stub agent for testing purposes."""
    
    def __init__(self, agent_type: str, success_rate: float = 1.0, execution_delay: float = 0.5):
        """
        Initialize stub agent.
        
        Args:
            agent_type: Type of agent to stub
            success_rate: Probability of success (0.0 to 1.0)
            execution_delay: Simulated execution delay in seconds
        """
        super().__init__()
        self.agent_type = agent_type
        self.success_rate = success_rate
        self.execution_delay = execution_delay
        self.execution_count = 0
        
        logging.info(f"Initialized StubAgent for {agent_type} (success_rate={success_rate})")
    
    async def _execute_task(self, request: AgentRequest) -> Dict[str, Any]:
        """Execute a stubbed task with simulated behavior."""
        self.execution_count += 1
        logging.info(f"StubAgent {self.agent_type} executing task #{self.execution_count}")
        
        # Simulate execution delay
        await asyncio.sleep(self.execution_delay)
        
        # Determine success based on success rate
        success = random.random() < self.success_rate
        
        if success:
            return self._generate_success_result(request)
        else:
            return self._generate_failure_result(request)
    
    def _generate_success_result(self, request: AgentRequest) -> Dict[str, Any]:
        """Generate a successful result based on agent type."""
        base_result = {
            "task_type": self.agent_type,
            "success": True,
            "message": f"Stubbed {self.agent_type} task completed successfully",
            "execution_count": self.execution_count
        }
        
        # Add agent-specific success data
        if self.agent_type == "researcher":
            base_result.update({
                "analysis_type": "environment_analysis",
                "requirements": {
                    "languages": ["python", "nodejs"],
                    "tools": ["zsh", "oh-my-zsh", "mise"],
                    "editors": ["nvim", "vscode"]
                },
                "validation": {"valid": True, "issues": []},
                "estimated_install_time": 15,
                "potential_issues": []
            })
        
        elif self.agent_type == "installer":
            base_result.update({
                "packages_attempted": 5,
                "packages_successful": 5,
                "overall_success": True,
                "installed_tools": ["zsh", "curl", "git", "mise"]
            })
        
        elif self.agent_type == "shell_master":
            base_result.update({
                "shell_configured": True,
                "oh_my_zsh_installed": True,
                "plugins_enabled": ["git", "zsh-autosuggestions"],
                "theme_set": "powerlevel10k"
            })
        
        elif self.agent_type == "mise_master":
            base_result.update({
                "mise_installed": True,
                "languages_configured": {"python": "3.12.9", "nodejs": "latest"},
                "global_tools_set": True
            })
        
        elif self.agent_type == "authorizer":
            base_result.update({
                "ssh_key_generated": True,
                "git_configured": True,
                "credentials_setup": True
            })
        
        elif self.agent_type == "progress_tracker":
            base_result.update({
                "tracking_active": True,
                "progress_percentage": 85,
                "completed_tasks": 12,
                "remaining_tasks": 3
            })
        
        return base_result
    
    def _generate_failure_result(self, request: AgentRequest) -> Dict[str, Any]:
        """Generate a failure result for testing error handling."""
        error_messages = [
            f"Simulated {self.agent_type} failure for testing",
            f"Network timeout during {self.agent_type} operation",
            f"Permission denied in {self.agent_type} task",
            f"Resource unavailable for {self.agent_type}"
        ]
        
        return {
            "task_type": self.agent_type,
            "success": False,
            "message": random.choice(error_messages),
            "error_code": f"{self.agent_type.upper()}_ERROR",
            "execution_count": self.execution_count,
            "retry_suggested": True
        }
    
    def get_stub_metrics(self) -> Dict[str, Any]:
        """Get metrics specific to stub agent."""
        return {
            "agent_type": self.agent_type,
            "success_rate": self.success_rate,
            "execution_delay": self.execution_delay,
            "execution_count": self.execution_count,
            "stub_mode": True
        }


class StubQAExpertAgent(StubAgent):
    """Specialized stub for QA Expert agent that returns QAResult."""
    
    def __init__(self, success_rate: float = 0.9):
        super().__init__("qa_expert", success_rate)
    
    async def _execute_task(self, request: AgentRequest) -> QAResult:
        """Execute QA validation with stubbed behavior."""
        self.execution_count += 1
        logging.info(f"StubQAExpert executing validation #{self.execution_count}")
        
        # Simulate execution delay
        await asyncio.sleep(self.execution_delay)
        
        # Determine success
        success = random.random() < self.success_rate
        
        if success:
            return QAResult(
                task_id=request.context.get("task_id", "stub_validation"),
                validation_passed=True,
                success_criteria_met=[
                    "stub_zsh_check", "stub_mise_check", "stub_python_check",
                    "stub_nodejs_check", "stub_git_check"
                ],
                failures=[],
                remediation_suggestions=[],
                confidence_score=0.95,
                detailed_report="Stub QA validation passed - all checks successful"
            )
        else:
            return QAResult(
                task_id=request.context.get("task_id", "stub_validation"),
                validation_passed=False,
                success_criteria_met=["stub_zsh_check", "stub_git_check"],
                failures=[
                    "stub_mise_check: Command not found",
                    "stub_python_check: Version mismatch"
                ],
                remediation_suggestions=[
                    "Install mise: curl https://mise.run | sh",
                    "Install Python 3.12: mise install python@3.12.9"
                ],
                confidence_score=0.6,
                detailed_report="Stub QA validation failed - some checks need attention"
            )


class StubAgentFactory:
    """Factory for creating stub agents for testing."""
    
    def __init__(self, default_success_rate: float = 0.9, default_delay: float = 0.5):
        """
        Initialize stub agent factory.
        
        Args:
            default_success_rate: Default success rate for stub agents
            default_delay: Default execution delay for stub agents
        """
        self.default_success_rate = default_success_rate
        self.default_delay = default_delay
        self.stub_agents = {}
        
        # Define different success rates for different agent types
        self.agent_success_rates = {
            "researcher": 0.95,  # Research usually succeeds
            "installer": 0.85,   # Installation can fail
            "shell_master": 0.90,
            "mise_master": 0.88,
            "authorizer": 0.92,
            "progress_tracker": 0.98,  # Tracking rarely fails
            "qa_expert": 0.80   # QA might find issues
        }
    
    def create_stub_agent(self, agent_type: str, success_rate: Optional[float] = None) -> StubAgent:
        """
        Create a stub agent of the specified type.
        
        Args:
            agent_type: Type of agent to create
            success_rate: Override default success rate
        
        Returns:
            Configured stub agent
        """
        if agent_type in self.stub_agents:
            return self.stub_agents[agent_type]
        
        # Use provided success rate or type-specific rate or default
        actual_success_rate = (
            success_rate or 
            self.agent_success_rates.get(agent_type, self.default_success_rate)
        )
        
        # Create appropriate stub agent
        if agent_type == "qa_expert":
            stub_agent = StubQAExpertAgent(actual_success_rate)
        else:
            stub_agent = StubAgent(agent_type, actual_success_rate, self.default_delay)
        
        # Cache the agent
        self.stub_agents[agent_type] = stub_agent
        
        logging.info(f"Created stub agent: {agent_type} (success_rate={actual_success_rate})")
        return stub_agent
    
    def create_failure_prone_agent(self, agent_type: str, failure_rate: float = 0.7) -> StubAgent:
        """Create a stub agent that fails frequently for testing error handling."""
        success_rate = 1.0 - failure_rate
        return self.create_stub_agent(agent_type, success_rate)
    
    def get_all_stub_agents(self) -> Dict[str, StubAgent]:
        """Get all created stub agents."""
        return self.stub_agents.copy()
    
    def reset_agents(self):
        """Reset all stub agents (clear cache and metrics)."""
        self.stub_agents.clear()
        logging.info("All stub agents reset")