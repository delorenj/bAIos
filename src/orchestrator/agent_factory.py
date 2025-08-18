"""
Agent Factory
=============

Factory for creating and managing specialized agents in the orchestrator system.
"""

import os
import logging
from typing import Dict, Any, Type
import instructor
from openai import OpenAI
from atomic_agents import AtomicAgent, AgentConfig
from atomic_agents.context import ChatHistory, SystemPromptGenerator

from ..agents import (
    ResearcherAgent,
    InstallerAgent, 
    ShellMasterAgent,
    ProgressTrackerAgent,
    AuthorizerAgent,
    MiseMasterAgent,
    QAExpertAgent
)
from ..schemas import AgentRequest, AgentResponse


class AgentFactory:
    """Factory for creating and managing specialized agents."""
    
    def __init__(self):
        """Initialize the agent factory."""
        self.agent_cache: Dict[str, AtomicAgent] = {}
        self.agent_classes = {
            "researcher": ResearcherAgent,
            "installer": InstallerAgent,
            "shell_master": ShellMasterAgent,
            "progress_tracker": ProgressTrackerAgent,
            "authorizer": AuthorizerAgent,
            "mise_master": MiseMasterAgent,
            "qa_expert": QAExpertAgent
        }
        
        logging.info("AgentFactory initialized with agent types: %s", list(self.agent_classes.keys()))
    
    def create_agent(self, agent_type: str) -> AtomicAgent[AgentRequest, AgentResponse]:
        """
        Create an agent of the specified type.
        
        Args:
            agent_type: Type of agent to create
            
        Returns:
            Configured agent instance
        """
        if agent_type in self.agent_cache:
            logging.debug(f"Returning cached agent: {agent_type}")
            return self.agent_cache[agent_type]
        
        if agent_type not in self.agent_classes:
            raise ValueError(f"Unknown agent type: {agent_type}. Available types: {list(self.agent_classes.keys())}")
        
        agent_class = self.agent_classes[agent_type]
        config = self._create_agent_config(agent_type)
        
        agent = agent_class(config)
        self.agent_cache[agent_type] = agent
        
        logging.info(f"Created new agent: {agent_type}")
        return agent
    
    def _create_agent_config(self, agent_type: str) -> AgentConfig:
        """Create configuration for a specific agent type."""
        
        # Get API key from environment or use the provided key
        api_key = os.getenv("OPENROUTER_API_KEY", "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")
        
        # Setup OpenRouter client
        client = instructor.from_openai(
            OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
            )
        )
        
        # Agent-specific system prompts
        system_prompts = {
            "researcher": {
                "background": [
                    "You are the Researcher Agent in the WSL provisioning system.",
                    "You analyze environment specifications, gather system information, and research solutions.",
                    "You validate prerequisites and provide detailed analysis for other agents."
                ],
                "steps": [
                    "1. Parse and validate environment specifications",
                    "2. Gather current system state and configuration",
                    "3. Research optimal installation and configuration approaches", 
                    "4. Identify potential issues and dependencies",
                    "5. Provide detailed reports with recommendations"
                ]
            },
            "installer": {
                "background": [
                    "You are the Installer Agent responsible for package and tool installation.",
                    "You handle system packages, applications, and development tools.",
                    "You ensure proper installation order and dependency resolution."
                ],
                "steps": [
                    "1. Analyze installation requirements and dependencies",
                    "2. Execute installation commands in proper order",
                    "3. Verify successful installation of each component",
                    "4. Handle installation errors and conflicts",
                    "5. Report installation status and any issues"
                ]
            },
            "shell_master": {
                "background": [
                    "You are the Shell Master Agent managing shell configuration and environment setup.",
                    "You configure zsh, oh-my-zsh, environment variables, and shell integrations.",
                    "You create and manage symlinks, aliases, and shell customizations."
                ],
                "steps": [
                    "1. Configure shell environment (zsh, oh-my-zsh)",
                    "2. Set up environment variables and PATH",
                    "3. Create necessary symlinks and aliases",
                    "4. Configure shell integrations and plugins",
                    "5. Test and validate shell configuration"
                ]
            },
            "progress_tracker": {
                "background": [
                    "You are the Progress Tracker Agent monitoring system provisioning progress.",
                    "You track task completion, calculate progress percentages, and estimate time remaining.",
                    "You provide detailed status reports and progress updates."
                ],
                "steps": [
                    "1. Monitor task execution and completion status",
                    "2. Calculate progress percentages and time estimates",
                    "3. Track system resource usage and performance",
                    "4. Generate progress reports and status updates",
                    "5. Alert on delays or potential issues"
                ]
            },
            "authorizer": {
                "background": [
                    "You are the Authorizer Agent handling authentication and access control.",
                    "You manage SSH keys, GitHub authentication, API tokens, and permissions.",
                    "You ensure secure configuration of all authentication mechanisms."
                ],
                "steps": [
                    "1. Generate and configure SSH keys",
                    "2. Set up GitHub authentication (CLI, SSH)",
                    "3. Configure API tokens and credentials",
                    "4. Set up secure permission and access controls",
                    "5. Validate all authentication mechanisms"
                ]
            },
            "mise_master": {
                "background": [
                    "You are the Mise Master Agent managing version-controlled development tools.",
                    "You configure and manage tools like Python, Node.js, and other development runtimes via mise.",
                    "You ensure proper tool versions and environment activation."
                ],
                "steps": [
                    "1. Configure mise for tool version management",
                    "2. Install specified tool versions (Python, Node.js, etc.)",
                    "3. Set up tool environment activation",
                    "4. Configure tool-specific settings and paths",
                    "5. Validate tool installations and versions"
                ]
            },
            "qa_expert": {
                "background": [
                    "You are the QA Expert Agent responsible for validation and quality assurance.",
                    "You perform comprehensive testing of installed systems and configurations.",
                    "You validate success criteria and identify issues requiring remediation."
                ],
                "steps": [
                    "1. Execute comprehensive validation checklists",
                    "2. Test all installed tools and configurations",
                    "3. Verify success criteria are met",
                    "4. Identify and report any failures or issues",
                    "5. Provide remediation recommendations for failures"
                ]
            }
        }
        
        prompt_config = system_prompts.get(agent_type, {
            "background": [f"You are the {agent_type} agent in the WSL provisioning system."],
            "steps": ["1. Execute assigned tasks", "2. Report results"]
        })
        
        system_prompt_generator = SystemPromptGenerator(
            background=prompt_config["background"],
            steps=prompt_config["steps"],
            output_instructions=[
                "Always provide structured responses using the defined schemas",
                "Include detailed logs and error messages for debugging",
                "Report progress and status clearly",
                "Handle errors gracefully and provide recovery suggestions"
            ]
        )
        
        return AgentConfig(
            client=client,
            model="anthropic/claude-3.5-sonnet",
            history=ChatHistory(),
            system_prompt_generator=system_prompt_generator,
            model_api_parameters={
                "max_tokens": 2048,
                "temperature": 0.2  # Low temperature for consistent task execution
            }
        )
    
    def get_agent_status(self, agent_type: str) -> Dict[str, Any]:
        """Get status information for an agent."""
        if agent_type in self.agent_cache:
            agent = self.agent_cache[agent_type]
            return {
                "type": agent_type,
                "status": "ready",
                "cached": True,
                "history_length": len(agent.history.history) if agent.history else 0
            }
        else:
            return {
                "type": agent_type,
                "status": "not_created",
                "cached": False
            }
    
    def clear_cache(self):
        """Clear the agent cache."""
        self.agent_cache.clear()
        logging.info("Agent cache cleared")
    
    def get_available_agent_types(self) -> list:
        """Get list of available agent types."""
        return list(self.agent_classes.keys())