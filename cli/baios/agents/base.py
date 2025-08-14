#!/usr/bin/env python3
"""
Base Agent class for bAIos CLI specialized agents.

This module provides the abstract base class that all specialized agents inherit from,
defining the common interface and core functionality.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import platform
import subprocess
import os
from pathlib import Path


class Agent(ABC):
    """
    Abstract base class for bAIos specialized agents.
    
    Each agent represents a domain expert that can answer questions and provide
    guidance within their area of expertise.
    """
    
    def __init__(self, name: str, expertise: str, personality: str = ""):
        """
        Initialize the agent.
        
        Args:
            name: The agent's display name
            expertise: Brief description of agent's expertise area
            personality: Optional personality description
        """
        self.name = name
        self.expertise = expertise
        self.personality = personality
        
    @abstractmethod
    def ask(self, question: str) -> str:
        """
        Ask the agent a question and get an expert response.
        
        Args:
            question: The question to ask the agent
            
        Returns:
            The agent's response as a string
        """
        pass
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get basic system information that all agents can use.
        
        Returns:
            Dictionary containing system information
        """
        return {
            "platform": platform.system(),
            "platform_release": platform.release(), 
            "platform_version": platform.platform(),
            "architecture": platform.machine(),
            "processor": platform.processor() or "Unknown",
            "python_version": platform.python_version(),
            "home_dir": str(Path.home()),
            "current_dir": str(Path.cwd()),
            "user": os.environ.get("USER", os.environ.get("USERNAME", "Unknown"))
        }
    
    def run_command(self, command: str, capture_output: bool = True) -> Optional[str]:
        """
        Run a system command safely.
        
        Args:
            command: Command to execute
            capture_output: Whether to capture and return output
            
        Returns:
            Command output if capture_output is True and command succeeds, None otherwise
        """
        try:
            if capture_output:
                result = subprocess.run(
                    command.split(),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                return result.stdout.strip() if result.returncode == 0 else None
            else:
                result = subprocess.run(command.split(), timeout=10)
                return None
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            return None
    
    def check_command_available(self, command: str) -> bool:
        """
        Check if a command is available on the system.
        
        Args:
            command: Command name to check
            
        Returns:
            True if command is available, False otherwise
        """
        return self.run_command(f"which {command}") is not None
    
    def __str__(self) -> str:
        """String representation of the agent."""
        return f"{self.name} - {self.expertise}"
    
    def __repr__(self) -> str:
        """Developer representation of the agent."""
        return f"Agent(name='{self.name}', expertise='{self.expertise}')"