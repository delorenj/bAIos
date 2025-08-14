#!/usr/bin/env python3
"""
Agent registry for bAIos CLI agents.

This module provides a registry for managing and accessing all available agents.
"""

from typing import Dict, List, Optional
from .base import Agent
from .shelldon import Shelldon
from .bill_coordinator import BillTheCoordinator  
from .mise_master import MiseMaster
from .tzvi_windows import TzviTheWindowsWizard


class AgentRegistry:
    """Registry for managing available agents."""
    
    def __init__(self):
        """Initialize the registry."""
        self._agents: Dict[str, Agent] = {}
        self._load_agents()
    
    def _load_agents(self):
        """Load all available agents."""
        agents = [
            Shelldon(),
            BillTheCoordinator(),
            MiseMaster(),
            TzviTheWindowsWizard()
        ]
        
        for agent in agents:
            self._agents[agent.name.lower()] = agent
    
    def get_agent(self, name: str) -> Optional[Agent]:
        """
        Get an agent by name (case-insensitive).
        
        Args:
            name: The name of the agent
            
        Returns:
            The agent instance, or None if not found
        """
        return self._agents.get(name.lower())
    
    def list_agents(self) -> List[Agent]:
        """
        Get a list of all available agents.
        
        Returns:
            List of all agent instances
        """
        return list(self._agents.values())
    
    def find_agents_by_keyword(self, keyword: str) -> List[Agent]:
        """
        Find agents whose name or expertise contains the keyword.
        
        Args:
            keyword: Keyword to search for
            
        Returns:
            List of matching agents
        """
        keyword_lower = keyword.lower()
        matches = []
        
        for agent in self._agents.values():
            if (keyword_lower in agent.name.lower() or 
                keyword_lower in agent.expertise.lower()):
                matches.append(agent)
        
        return matches


# Global registry instance
agent_registry = AgentRegistry()