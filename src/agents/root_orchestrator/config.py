"""Configuration for Root Orchestrator Agent."""

from atomic_agents.lib.base.base_agent import BaseAgentConfig
from pydantic import Field


class RootOrchestratorConfig(BaseAgentConfig):
    """Configuration for the Root Orchestrator Agent."""

    openrouter_api_key: str = Field(
        ..., 
        description="OpenRouter API key for LLM access"
    )
    
    model_name: str = Field(
        default="anthropic/claude-3.5-sonnet",
        description="Model to use for orchestration decisions"
    )
    
    max_parallel_agents: int = Field(
        default=5,
        description="Maximum number of agents to run in parallel"
    )
    
    max_failure_retries: int = Field(
        default=3,
        description="Maximum number of retries before human escalation"
    )
    
    qa_verification_required: bool = Field(
        default=True,
        description="Whether QA verification is required for all items"
    )
    
    agent_timeout_seconds: int = Field(
        default=300,
        description="Timeout for individual agent tasks in seconds"
    )
    
    system_state_check_interval: int = Field(
        default=30,
        description="Interval in seconds to check system state changes"
    )
    
    human_escalation_enabled: bool = Field(
        default=True,
        description="Whether to enable human escalation for persistent failures"
    )