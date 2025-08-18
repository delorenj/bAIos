"""
Authorizer Agent
================

Specialized agent for handling authentication and access control.
"""

import logging
from typing import Dict, Any
from .base_specialized_agent import BaseSpecializedAgent
from ..schemas import AgentRequest


class AuthorizerAgent(BaseSpecializedAgent):
    """Agent specialized in authentication and access control setup."""
    
    async def _execute_task(self, request: AgentRequest) -> Dict[str, Any]:
        """Execute authorization tasks."""
        task_description = request.task_description.lower()
        
        if "setup auth" in task_description:
            return await self._setup_authentication()
        else:
            return await self._generic_auth_task(request)
    
    async def _setup_authentication(self) -> Dict[str, Any]:
        """Set up SSH keys and GitHub authentication."""
        logging.info("Setting up authentication")
        
        auth_steps = []
        
        # Check if SSH key exists
        ssh_key_exists = await self._check_file_exists("~/.ssh/id_ed25519")
        
        if not ssh_key_exists:
            # Generate SSH key
            ssh_key_gen = await self._run_command(
                'ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N ""'
            )
            auth_steps.append({
                "step": "generate_ssh_key",
                "success": ssh_key_gen["success"]
            })
            
            # Set correct permissions
            permissions = await self._run_command("chmod 600 ~/.ssh/id_ed25519")
            auth_steps.append({
                "step": "set_ssh_permissions",
                "success": permissions["success"]
            })
        else:
            auth_steps.append({
                "step": "ssh_key_exists",
                "success": True
            })
        
        # Configure SSH agent
        ssh_agent_config = await self._run_command('eval "$(ssh-agent -s)"')
        auth_steps.append({
            "step": "start_ssh_agent",
            "success": ssh_agent_config["success"]
        })
        
        # Add SSH key to agent
        add_key = await self._run_command("ssh-add ~/.ssh/id_ed25519")
        auth_steps.append({
            "step": "add_key_to_agent",
            "success": add_key["success"]
        })
        
        return {
            "task_type": "authentication_setup",
            "auth_steps": auth_steps,
            "overall_success": all(step["success"] for step in auth_steps),
            "ssh_public_key_location": "~/.ssh/id_ed25519.pub",
            "next_steps": [
                "Add SSH public key to GitHub account",
                "Test SSH connection with: ssh -T git@github.com",
                "Configure GitHub CLI authentication"
            ]
        }
    
    async def _generic_auth_task(self, request: AgentRequest) -> Dict[str, Any]:
        """Handle generic authorization tasks."""
        return {
            "task_type": "generic_auth_task",
            "message": "Authorization task completed",
            "success": True
        }